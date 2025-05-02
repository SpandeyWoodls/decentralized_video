# decentralized\_video

A FastAPI-based decentralized video platform that stores videos on IPFS, manages staking via Ethereum smart contracts, and processes uploads asynchronously with Celery.

---

## Table of Contents

* [Prerequisites](#prerequisites)
* [Project Structure](#project-structure)
* [Setup](#setup)

  * [1. Clone the repository](#1-clone-the-repository)
  * [2. Install system dependencies](#2-install-system-dependencies)
  * [3. Create & activate Python virtual environment](#3-create--activate-python-virtual-environment)
  * [4. Install Python dependencies](#4-install-python-dependencies)
  * [5. Hardhat: Compile & extract ABIs](#5-hardhat-compile--extract-abis)
* [Configuration](#configuration)

  * [Environment Variables](#environment-variables)
* [Running the application](#running-the-application)

  * [Terminal 1 – IPFS daemon](#terminal-1--ipfs-daemon)
  * [Terminal 2 – Redis server](#terminal-2--redis-server)
  * [Terminal 3 – Celery worker](#terminal-3--celery-worker)
  * [Terminal 4 – Uvicorn API server](#terminal-4--uvicorn-api-server)
* [Using the API](#using-the-api)

  * [Upload video example](#upload-video-example)
* [Project Structure](#project-structure-1)
* [Contributing](#contributing)
* [License](#license)

---

## Prerequisites

Make sure you have the following installed:

* **Git**
* **Node.js** & **npm** (for Hardhat)
* **Python 3.12+**
* **PostgreSQL**
* **Redis**
* **IPFS** (Kubo)
* **GitHub CLI** (optional, for repo creation)

## Project Structure

```
0block/
├── block/                 # Python virtualenv
├── dhardhat/              # Hardhat smart-contract project
│   ├── contracts/         # Solidity sources
│   └── artifacts/         # Compiled JSON outputs
├── decentralized_video/   # FastAPI app
│   ├── contracts/abis/    # Extracted ABIs JSON
│   ├── app/               # FastAPI code
│   ├── worker/            # Celery tasks
│   └── requirements.txt
└── README.md              # This file
```

## Setup

### 1️⃣ Clone the repository

```bash
cd ~/Desktop/0block
git clone git@github.com:SpandeyWoodls/decentralized_video.git
cd decentralized_video
```

### 2️⃣ Install system dependencies

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y redis-server ipfs
```

#### macOS (Homebrew)

```bash
brew update
brew install redis ipfs
```

### 3️⃣ Create & activate Python virtual environment

```bash
# from root of project
python3 -m venv ../block_env
source ../block_env/bin/activate
```

### 4️⃣ Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5️⃣ Hardhat: Compile & extract ABIs

```bash
# open a new terminal
cd ~/Desktop/0block/dhardhat
npm install
npx hardhat compile

# copy ABI JSON into FastAPI app
jq '{abi: .abi}' artifacts/contracts/VideoRegistry.sol/VideoRegistry.json \
  > ../decentralized_video/contracts/abis/VideoRegistry.json

jq '{abi: .abi}' artifacts/contracts/StorageStaking.sol/StorageStaking.json \
  > ../decentralized_video/contracts/abis/StorageStaking.json
```

## Configuration

### Environment Variables

Create a `.env` file in `decentralized_video/` or export these in your shell: (eg : d ~/Desktop/0block , source block/bin/activate) 

```bash
export DATABASE_URL="postgresql://blocksql:blocksqlpwd@localhost:5432/decentralized_video"
export WEB3_RPC_URL="http://127.0.0.1:8545"
export VIDEO_REGISTRY_ADDRESS="<deployed_address>"
export STORAGE_STAKING_ADDRESS="<deployed_address>"
export WEB3_PRIVATE_KEY="<your_eth_private_key>"
```

## Running the application

Open four separate terminals and run the following in each:

### Terminal 1 – IPFS daemon

```bash
# no need for virtualenv
# just start IPFS
ipfs init   # only once
ipfs daemon
```

### Terminal 2 – Redis server

```bash
# on Ubuntu/Debian
sudo systemctl enable --now redis-server
redis-cli ping   # should respond PONG
```

### Terminal 3 – Celery worker

```bash
cd ~/Desktop/0block/decentralized_video
source ../block_env/bin/activate
# ensure env vars are loaded (or put in .env)
celery -A decentralized_video.worker.celery_app worker --loglevel=info
```

### Terminal 4 – Uvicorn API server

```bash
cd ~/Desktop/0block/decentralized_video
source ../block_env/bin/activate
# ensure env vars loaded
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Now open your browser at [http://localhost:8000](http://localhost:8000).

## Using the API

### Upload video example

```bash
curl -X POST "http://localhost:8000/videos/" \
  -F "file=@/path/to/video.mp4" \
  -F "metadata='{"title":"My First Video","description":"..."}'"
```

The API will:

1. Pin the file to IPFS
2. Register the video hash on Ethereum
3. Enqueue a Celery job to generate thumbnails
4. Return a JSON response with `video_id`, `ipfs_hash`, and `status`.

Check the thumbnails endpoint:

```bash
GET http://localhost:8000/videos/{video_id}/thumbnails
```

## Contributing

1. Fork the repo
2. Create a feature branch
3. Submit a PR

## License

MIT © SpandeyWoodls
