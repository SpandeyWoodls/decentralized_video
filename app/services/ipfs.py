# decentralized_video/app/services/ipfs.py
"""
IPFS client wrapper for adding, fetching, and pinning chunks.
"""
import ipfshttpclient
from typing import Optional

# Module-level client instance
_client: Optional[ipfshttpclient.Client] = None


def init_client(address: str = "/ip4/127.0.0.1/tcp/5001"):  # default local API
    """
    Initialize and return the IPFS HTTP client.
    """
    global _client
    if _client is None:
        _client = ipfshttpclient.connect(addr=address)
    return _client


def close_client():
    """
    Close the IPFS client connection.
    """
    global _client
    if _client is not None:
        _client.close()
        _client = None


def add_chunk(data: bytes) -> str:
    """
    Add raw bytes to IPFS and return the CID.
    """
    client = init_client()
    cid = client.add_bytes(data)
    return cid


def fetch_chunk(cid: str) -> Optional[bytes]:
    """
    Retrieve raw bytes for a given CID. Returns None if not found.
    """
    client = init_client()
    try:
        return client.cat(cid)
    except ipfshttpclient.exceptions.ErrorResponse:
        return None


def pin(cid: str) -> None:
    """
    Pin a CID to ensure it's retained on the local node.
    """
    client = init_client()
    client.pin.add(cid)
