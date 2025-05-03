# A) Generating your ABI JSONs

Go to your Hardhat project:

```bash
cd ~/Desktop/0block/dhardhat
```

Compile your contracts:

```bash
npx hardhat compile
```

Extract & wrap VideoRegistry ABI:

```bash
jq '{abi: .abi}' \
  artifacts/contracts/VideoRegistry.sol/VideoRegistry.json \
> ../decentralized_video/contracts/abis/VideoRegistry.json
```

Extract & wrap StorageStaking ABI:

```bash
jq '{abi: .abi}' \
  artifacts/contracts/StorageStaking.sol/StorageStaking.json \
> ../decentralized_video/contracts/abis/StorageStaking.json
```

Quick verify:

```bash
head -n5 ../decentralized_video/contracts/abis/VideoRegistry.json
```

You should see:

```text
{
  "abi": [
    { "inputs": … }
    …
  ]
}
```

---

# B) Fire up your four‐terminal dev stack

You need one terminal each for IPFS, Redis, Celery, and Uvicorn.

## 🖥️ Terminal 1 — IPFS daemon

```bash
# (only once ever)
ipfs init

# keep this running:
ipfs daemon
```

You’ll see “Daemon is ready”.

## 🖥️ Terminal 2 — Redis server

```bash
# (if not already installed)
sudo apt update && sudo apt install redis-server

sudo systemctl enable --now redis
redis-cli ping      # → PONG
```

## 🖥️ Terminal 3 — Celery worker

```bash
cd ~/Desktop/0block
source block/bin/activate

export DATABASE_URL="postgresql://blocksql:blocksqlpwd@localhost:5432/decentralized_video"
export WEB3_RPC_URL="http://127.0.0.1:8545"
export VIDEO_REGISTRY_ADDRESS="0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
export STORAGE_STAKING_ADDRESS="0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
export WEB3_PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

celery -A decentralized_video.worker.celery_app worker --loglevel=info
```

Wait until you see `celery@… ready.`

## 🖥️ Terminal 4 — FastAPI (Uvicorn)

```bash
cd ~/Desktop/0block/decentralized_video
source ../block/bin/activate

export DATABASE_URL="postgresql://blocksql:blocksqlpwd@localhost:5432/decentralized_video"
export WEB3_RPC_URL="http://127.0.0.1:8545"
export VIDEO_REGISTRY_ADDRESS="0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
export STORAGE_STAKING_ADDRESS="0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
export WEB3_PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see **Application startup complete.**

---

# Final sanity check

* **Terminal 1** → IPFS “Daemon is ready”
* **Terminal 2** → Redis “PONG”
* **Terminal 3** → Celery “ready.”
* **Terminal 4** → Uvicorn “startup complete.”

Now open [http://localhost:8000](http://localhost:8000) in your browser and you’re live!
