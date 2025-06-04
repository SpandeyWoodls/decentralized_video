import uuid
import importlib
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient


def create_test_client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    # required env vars for app startup
    monkeypatch.setenv("WEB3_RPC_URL", "http://localhost")
    monkeypatch.setenv("WEB3_PRIVATE_KEY", "0x" + "1" * 64)
    monkeypatch.setenv("VIDEO_REGISTRY_ADDRESS", "0x" + "1" * 40)
    monkeypatch.setenv("STORAGE_STAKING_ADDRESS", "0x" + "2" * 40)



    # reload modules so they pick up env vars
    import app.db as db
    importlib.reload(db)
    import app.main as main
    importlib.reload(main)
    import app.crud as crud
    import app.models as models
    import worker.tasks as tasks

    # adjust CRUD helpers for string UUIDs
    def get_video_str(db_session, video_id):
        return db_session.query(models.Video).filter(models.Video.id == str(video_id)).first()

    def create_chunk_str(db_session, video_id, cid, index):
        chunk = models.Chunk(video_id=str(video_id), cid=cid, index=index)
        db_session.add(chunk)
        db_session.commit()
        db_session.refresh(chunk)
        return chunk

    monkeypatch.setattr(crud, "get_video", get_video_str)
    monkeypatch.setattr(crud, "create_chunk", create_chunk_str)

    # patch external services
    monkeypatch.setattr(main.ipfs, "init_client", lambda *a, **k: None)
    monkeypatch.setattr(main.ipfs, "close_client", lambda: None)
    monkeypatch.setattr(main.ipfs, "fetch_chunk", lambda cid: b"data")

    import app.services.ethereum as eth
    monkeypatch.setattr(eth, "init_web3", lambda *a, **k: None)
    monkeypatch.setattr(eth, "close_web3", lambda: None)
    monkeypatch.setattr(eth, "register_video", lambda *a, **k: None)

    def fake_process(video_id: str, uploader: str, file_path: str):
        session = db.SessionLocal()
        video = crud.get_video(session, video_id)
        video.video_hash = "hash"
        video.metadata_uri = "ipfs://meta"
        session.commit()
        thumb_dir = Path("tmp") / video_id
        thumb_dir.mkdir(exist_ok=True)
        (thumb_dir / "thumb1.jpg").write_bytes(b"thumb")
        session.close()

    monkeypatch.setattr(tasks.process_video, "delay", fake_process)

    importlib.reload(main)
    client = TestClient(main.app)
    client.__enter__()
    return client


@pytest.fixture
def client(tmp_path, monkeypatch):
    client = create_test_client(tmp_path, monkeypatch)
    yield client
    client.__exit__(None, None, None)


def upload_sample_video(client, tmp_path):
    video_path = tmp_path / "video.mp4"
    video_path.write_bytes(b"data")
    with video_path.open("rb") as f:
        response = client.post("/videos/", files={"file": ("video.mp4", f, "video/mp4")})
    assert response.status_code == 202
    return response.json()["video_id"]


def test_upload_and_list(client, tmp_path):
    vid = upload_sample_video(client, tmp_path)
    resp = client.get("/videos/")
    assert resp.status_code == 200
    data = resp.json()
    assert any(v["id"] == vid for v in data)


def test_metadata_and_thumbnails(client, tmp_path):
    vid = upload_sample_video(client, tmp_path)
    # metadata via listing
    listing = client.get("/videos/").json()
    meta = next(v for v in listing if v["id"] == vid)
    assert meta["metadata_uri"] == "ipfs://meta"

    resp = client.get(f"/videos/{vid}/thumbnails")
    assert resp.status_code == 200
    assert resp.json()["thumbnails"] == ["thumb1.jpg"]
