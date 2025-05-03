from setuptools import setup, find_packages

setup(
    name="decentralized_video",
    version="0.1.0",
    packages=find_packages(),          # will pick up decentralized_video, its subpackages, etc.
    install_requires=[
        "fastapi>=0.95.2",
        "uvicorn>=0.23.1",
        "SQLAlchemy>=2.0.20",
        "psycopg2-binary>=2.9.6",
        "alembic>=1.10.4",
        "celery>=5.3.0",
        "redis>=4.5.1",
        "ffmpeg-python>=0.2.0",
        "python-jose>=3.3.0",
        "web3>=5.31.3",
        "ipfshttpclient>=0.8.0a2",
    ],
    entry_points={
        "console_scripts": {
            "dv-server = decentralized_video.app.main:app",
        },
    },
)
