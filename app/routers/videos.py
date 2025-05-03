# decentralized_video/app/routers/videos.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from pydantic import BaseModel

from decentralized_video.worker.tasks import process_video
from decentralized_video.app.crud import create_video, get_video, list_chunks
from decentralized_video.app.main import get_db
from decentralized_video.app.services.ipfs import fetch_chunk

router = APIRouter()

class UploadResponse(BaseModel):
    video_id: uuid.UUID

class PlaylistResponse(BaseModel):
    chunks: List[str]

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
    tmp_dir = "tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    file_location = os.path.join(tmp_dir, file.filename)
    with open(file_location, "wb+") as f:
        f.write(await file.read())

    video = create_video(db, uploader=uploader, video_hash="", metadata_uri="")
    process_video.delay(str(video.id), uploader, file_location)
    return {"video_id": video.id}

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
    return {"chunks": [chunk.cid for chunk in chunks]}

@router.get("/chunks/{cid}")
def get_chunk(cid: str):
    data = fetch_chunk(cid)
    if data is None:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return Response(content=data, media_type="application/octet-stream")
