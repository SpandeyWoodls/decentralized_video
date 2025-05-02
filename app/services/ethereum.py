# decentralized_video/app/services/ethereum.py
"""
Web3 wrapper for interacting with smart contracts: VideoRegistry, StorageStaking, and AccessControl.
"""
import json
import os
from web3 import Web3
from web3.exceptions import TransactionNotFound

# Module‐level Web3 instance and contract objects
_web3: Web3 = None
_video_registry = None
_storage_staking = None


def init_web3(
    rpc_url: str,
    private_key: str,
    registry_address: str,
    staking_address: str
):
    """
    Initialize Web3 client and contract instances.
    """
    global _web3, _video_registry, _storage_staking

    # ABI file paths (relative to project root)
    video_registry_abi_path = "./contracts/abis/VideoRegistry.json"
    storage_staking_abi_path = "./contracts/abis/StorageStaking.json"

    # Connect to RPC
    _web3 = Web3(Web3.HTTPProvider(rpc_url))

    # Load ABIs
    with open(video_registry_abi_path, "r") as f:
        video_registry_abi = json.load(f)['abi']
    with open(storage_staking_abi_path, "r") as f:
        storage_staking_abi = json.load(f)['abi']

    # Instantiate contract objects
    _video_registry = _web3.eth.contract(
        address=registry_address,
        abi=video_registry_abi
    )
    _storage_staking = _web3.eth.contract(
        address=staking_address,
        abi=storage_staking_abi
    )

    # Set default account so that build_transaction() picks it up
    account = _web3.eth.account.from_key(private_key)
    _web3.eth.default_account = account.address


def close_web3():
    """
    Cleanup Web3 instance if needed.
    """
    global _web3, _video_registry, _storage_staking
    _web3 = None
    _video_registry = None
    _storage_staking = None


def _send_transaction(tx):
    """
    Helper to sign and send a transaction, then wait for receipt.
    """
    # we already set default_account in init_web3
    signed = _web3.eth.account.sign_transaction(tx, _web3.eth.default_account)
    tx_hash = _web3.eth.send_raw_transaction(signed.rawTransaction)
    return _web3.eth.wait_for_transaction_receipt(tx_hash)


def register_video(video_hash: str, metadata_uri: str):
    """
    Call VideoRegistry.registerVideo on-chain.
    """
    tx = _video_registry.functions.registerVideo(video_hash, metadata_uri).build_transaction({
        "from": _web3.eth.default_account,
        "nonce": _web3.eth.get_transaction_count(_web3.eth.default_account),
        "gasPrice": _web3.eth.gas_price,
    })
    return _send_transaction(tx)


def stake_storage(node_address: str, capacity_gb: int):
    """
    Call StorageStaking.stakeStorage on-chain.
    """
    tx = _storage_staking.functions.stakeStorage(capacity_gb).build_transaction({
        "from": node_address,
        "nonce": _web3.eth.get_transaction_count(node_address),
        "gasPrice": _web3.eth.gas_price,
    })
    return _send_transaction(tx)


def submit_proof(node_address: str, cid: str, proof: str):
    """
    Call StorageStaking.submitProof on-chain.
    """
    tx = _storage_staking.functions.submitProof(cid, proof).build_transaction({
        "from": node_address,
        "nonce": _web3.eth.get_transaction_count(node_address),
        "gasPrice": _web3.eth.gas_price,
    })
    return _send_transaction(tx)
