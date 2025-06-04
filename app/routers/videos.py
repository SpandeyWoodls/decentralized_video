# decentralized_video/app/routers/videos.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from pydantic import BaseModel
from worker.tasks import process_video
from ..crud import create_video, get_video, list_chunks
from ..main import get_db
from ..services.ipfs import fetch_chunk
from ..models import Video
 # Celery task for background processing

router = APIRouter()

class UploadResponse(BaseModel):
    video_id: uuid.UUID

class PlaylistResponse(BaseModel):
    chunks: List[str]

# --- Upload endpoint: accept file, save, enqueue processing, return video ID ---
@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_video(
    file: UploadFile = File(...),
    uploader: str = "anonymous",
    db: Session = Depends(get_db),
):
    # Save upload to temporary path
    tmp_dir = "tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    file_location = os.path.join(tmp_dir, file.filename)
    with open(file_location, "wb+") as f:
        content = await file.read()
        f.write(content)

    # Create initial video record (metadata will be updated by task)
    video = create_video(db, uploader=uploader, video_hash="", metadata_uri="")

    # Enqueue background processing (transcoding, IPFS pinning, on-chain register)
    process_video.delay(str(video.id), uploader, file_location)

    return {"video_id": video.id}

# --- Playlist endpoint: list CIDs for a video ---
@router.get(
    "/{video_id}/playlist",
    response_model=PlaylistResponse,
)
def get_playlist(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    video = get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    chunks = list_chunks(db, video_id)
    cids = [chunk.cid for chunk in chunks]
    return {"chunks": cids}

# --- Chunk retrieval endpoint: fetch raw chunk bytes ---
@router.get("/chunks/{cid}")
def get_chunk(cid: str):
    data = fetch_chunk(cid)
    if data is None:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return Response(content=data, media_type="application/octet-stream")

# --- List all videos ---
class VideoInfo(BaseModel):
    id: uuid.UUID
    uploader: str
    video_hash: str
    metadata_uri: str

    class Config:
        orm_mode = True

@router.get("/", response_model=List[VideoInfo])
def list_videos(db: Session = Depends(get_db)):
    return db.query(Video).all()

# --- Get video metadata ---
@router.get("/{video_id}", response_model=VideoInfo)
def get_video_info(video_id: uuid.UUID, db: Session = Depends(get_db)):
    video = get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

# --- Get thumbnails for a video ---
class ThumbnailsResponse(BaseModel):
    thumbnails: List[str]

@router.get("/{video_id}/thumbnails", response_model=ThumbnailsResponse)
def get_thumbnails(video_id: uuid.UUID):
    thumb_dir = os.path.join("tmp", str(video_id))
    if not os.path.isdir(thumb_dir):
        raise HTTPException(status_code=404, detail="Thumbnails not found")
    files = sorted([f for f in os.listdir(thumb_dir) if f.startswith("thumb")])
    return {"thumbnails": files}
