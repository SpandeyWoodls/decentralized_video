# decentralized_video/app/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Read your DATABASE_URL env var (exported earlier)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI to yield a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
