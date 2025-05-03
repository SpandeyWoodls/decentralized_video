# decentralized_video/worker/tasks.py

import os
import json
import uuid
from pathlib import Path

from celery import Celery

from decentralized_video.worker.celery_app import celery_app
from decentralized_video.app.services.transcoder import transcode_to_hls, generate_chunk_bytes
from decentralized_video.app.services.ipfs import add_chunk, pin
from decentralized_video.app.services.ethereum import register_video
from decentralized_video.app.crud import create_chunk, get_video
from decentralized_video.app.db import SessionLocal
from decentralized_video.app.models import Video

@celery_app.task
def process_video(video_id: str, uploader: str, file_path: str):
    """
    Celery task to process an uploaded video:
      1. Transcode input video into HLS segments.
      2. Upload each segment to IPFS and record in DB.
      3. Create and upload metadata JSON to IPFS.
      4. Update Video record with hash and metadata URI.
      5. Register the video on-chain.
    """
    db = SessionLocal()
    try:
        # 1) Transcode to HLS
        out_dir = os.path.join("tmp", video_id)
        segment_paths = transcode_to_hls(file_path, out_dir)

        # 2) Upload segments to IPFS & record in DB
        cid_list = []
        for idx, path in enumerate(segment_paths):
            data = Path(path).read_bytes()
            cid = add_chunk(data)
            pin(cid)
            create_chunk(
                db,
                video_id=uuid.UUID(video_id),
                cid=cid,
                index=idx,
            )
            cid_list.append(cid)

        # 3) Build metadata JSON, upload to IPFS
        metadata = {"video_id": video_id, "uploader": uploader, "chunks": cid_list}
        metadata_bytes = json.dumps(metadata).encode("utf-8")
        metadata_cid = add_chunk(metadata_bytes)
        metadata_uri = f"ipfs://{metadata_cid}"
        video_hash = metadata_cid

        # 4) Update the Video row
        video = get_video(db, uuid.UUID(video_id))
        video.video_hash = video_hash
        video.metadata_uri = metadata_uri
        db.commit()

        # 5) Register on-chain
        register_video(video_hash, metadata_uri)

    finally:
        db.close()
