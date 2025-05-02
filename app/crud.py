# decentralized_video/app/crud.py

from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from .models import Video, Chunk, Node, Proof


def create_video(
    db: Session,
    uploader: str,
    video_hash: str,
    metadata_uri: str
) -> Video:
    """
    Create a new Video record.
    """
    video = Video(
        uploader=uploader,
        video_hash=video_hash,
        metadata_uri=metadata_uri
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def get_video(
    db: Session,
    video_id: uuid.UUID
) -> Optional[Video]:
    """
    Retrieve a Video by its ID.
    """
    return db.query(Video).filter(Video.id == video_id).first()


def list_chunks(
    db: Session,
    video_id: uuid.UUID
) -> List[Chunk]:
    """
    List all chunks for a given video, ordered by their index.
    """
    return (
        db.query(Chunk)
        .filter(Chunk.video_id == video_id)
        .order_by(Chunk.index)
        .all()
    )


def create_chunk(
    db: Session,
    video_id: uuid.UUID,
    cid: str,
    index: int
) -> Chunk:
    """
    Create a new Chunk record.
    """
    chunk = Chunk(
        video_id=video_id,
        cid=cid,
        index=index
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def register_node(
    db: Session,
    node_id: str,
    capacity_gb: int
) -> Node:
    """
    Register a new storage node.
    """
    node = Node(
        id=node_id,
        capacity_gb=capacity_gb
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def get_node(
    db: Session,
    node_id: str
) -> Optional[Node]:
    """
    Retrieve a Node by its ID.
    """
    return db.query(Node).filter(Node.id == node_id).first()


def record_proof(
    db: Session,
    node_id: str,
    cid: str,
    proof: str
) -> Proof:
    """
    Record a storage proof for a node.
    """
    proof_obj = Proof(
        node_id=node_id,
        cid=cid,
        proof=proof
    )
    db.add(proof_obj)
    db.commit()
    db.refresh(proof_obj)
    return proof_obj


def list_proofs(
    db: Session,
    node_id: str
) -> List[Proof]:
    """
    List all proofs submitted by a given node.
    """
    return db.query(Proof).filter(Proof.node_id == node_id).all()
