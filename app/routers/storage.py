# decentralized_video/app/routers/storage.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List

from ..main import get_db
from ..crud import register_node, get_node, record_proof, list_proofs
from ..services.ethereum import stake_storage as ethereum_stake_storage, submit_proof as ethereum_submit_proof

router = APIRouter()

# --- Pydantic schemas ---
class StakeRequest(BaseModel):
    capacity_gb: int

class StakeResponse(BaseModel):
    node_id: str

class ProofRequest(BaseModel):
    cid: str
    proof: str

class ProofResponse(BaseModel):
    proof_id: int

class ProofInfo(BaseModel):
    cid: str
    proof: str
    created_at: datetime

class NodeStatusResponse(BaseModel):
    node_id: str
    capacity_gb: int
    proofs: List[ProofInfo]


# --- Stake storage endpoint ---
@router.post(
    "/nodes/{node_id}/stake",
    response_model=StakeResponse,
    status_code=status.HTTP_201_CREATED,
)
def stake_node(
    node_id: str,
    request: StakeRequest,
    db: Session = Depends(get_db),
):
    # Blockchain: stake storage on-chain
    tx_receipt = ethereum_stake_storage(node_id, request.capacity_gb)

    # Database: register the node
    node = register_node(db, node_id=node_id, capacity_gb=request.capacity_gb)
    return {"node_id": node.id}


# --- Submit storage proof endpoint ---
@router.post(
    "/nodes/{node_id}/proofs",
    response_model=ProofResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_storage_proof(
    node_id: str,
    request: ProofRequest,
    db: Session = Depends(get_db),
):
    # Ensure node exists
    node = get_node(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Blockchain: submit proof on-chain
    tx_receipt = ethereum_submit_proof(node_id, request.cid, request.proof)

    # Database: record proof
    proof_obj = record_proof(db, node_id=node_id, cid=request.cid, proof=request.proof)
    return {"proof_id": proof_obj.id}


# --- Get node status & proofs ---
@router.get(
    "/nodes/{node_id}",
    response_model=NodeStatusResponse,
)
def get_node_status(
    node_id: str,
    db: Session = Depends(get_db),
):
    node = get_node(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    proofs = list_proofs(db, node_id)
    proof_list = [
        ProofInfo(
            cid=p.cid,
            proof=p.proof,
            created_at=p.created_at
        )
        for p in proofs
    ]

    return {
        "node_id": node.id,
        "capacity_gb": node.capacity_gb,
        "proofs": proof_list,
    }
