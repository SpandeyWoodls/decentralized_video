# decentralized_video/app/main.py

import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .db import get_db, engine
from .models import Base
from .services import ipfs
from .services.ethereum import init_web3, close_web3
from .routers import videos, storage

app = FastAPI(
    title="Decentralized Video Streaming",
    description="API for uploading, viewing and staking storage for videos via blockchain + IPFS",
    version="0.1.0",
)

# Allow CORS (for a browser frontend); tighten allow_origins in prod!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount your routers; use Depends(get_db) if you need DB in every endpoint
app.include_router(
    videos.router,
    prefix="/videos",
    tags=["videos"],
    dependencies=[Depends(get_db)],
)
app.include_router(
    storage.router,
    prefix="/nodes",
    tags=["storage"],
    dependencies=[Depends(get_db)],
)


@app.on_event("startup")
def on_startup():
    # 1) Ensure your database schema is present (for dev; Alembic handles prod)
    Base.metadata.create_all(bind=engine)

    # 2) Start your IPFS client
    ipfs.init_client()

    # 3) Read & validate on-chain env vars, then initialize web3 + contracts
    rpc     = os.getenv("WEB3_RPC_URL")
    pk      = os.getenv("WEB3_PRIVATE_KEY")
    vr_addr = os.getenv("VIDEO_REGISTRY_ADDRESS")
    ss_addr = os.getenv("STORAGE_STAKING_ADDRESS")

    if not all([rpc, pk, vr_addr, ss_addr]):
        raise RuntimeError(
            "Missing one or more WEB3_* environment variables; "
            "check WEB3_RPC_URL, WEB3_PRIVATE_KEY, VIDEO_REGISTRY_ADDRESS, STORAGE_STAKING_ADDRESS"
        )

    init_web3(
        rpc_url=rpc,
        private_key=pk,
        registry_address=vr_addr,
        staking_address=ss_addr,
    )


@app.on_event("shutdown")
def on_shutdown():
    # Clean up IPFS & web3 connections if necessary
    ipfs.close_client()
    close_web3()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Decentralized Video Streaming platform"}
