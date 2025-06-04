# decentralized_video/app/models.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    uploader = Column(String, nullable=False)
    video_hash = Column(String, unique=True, nullable=False)
    metadata_uri = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to chunks
    chunks = relationship("Chunk", back_populates="video", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    cid = Column(String, nullable=False, index=True)
    index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="chunks")

class Node(Base):
    __tablename__ = "nodes"
    id = Column(String, primary_key=True)  # e.g. node’s wallet address or UUID
    capacity_gb = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    proofs = relationship("Proof", back_populates="node", cascade="all, delete-orphan")

class Proof(Base):
    __tablename__ = "proofs"
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    cid = Column(String, nullable=False)       # chunk CID being proved
    proof = Column(String, nullable=False)     # Merkle proof or similar
    created_at = Column(DateTime, default=datetime.utcnow)

    node = relationship("Node", back_populates="proofs")
