# decentralized_video/app/services/transcoder.py
"""
Transcoding and chunking service using FFmpeg for HLS/DASH streaming.
"""
import subprocess
import shutil
from pathlib import Path
from typing import List


def transcode_to_hls(
    input_path: str,
    output_dir: str,
    hls_time: int = 10
) -> List[Path]:
    """
    Transcode the input video into HLS format.

    Splits the video into segments of `hls_time` seconds and generates a .m3u8 playlist.
    Returns a list of Paths to the generated segment files (in order).
    """
    # Ensure output directory exists and is clean
    out_dir = Path(output_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    playlist_path = out_dir / "playlist.m3u8"
    
    # Build FFmpeg command
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-codec: copy",
        "-start_number", "0",
        "-hls_time", str(hls_time),
        "-hls_playlist_type", "vod",
        "-f", "hls",
        str(playlist_path)
    ]

    # Run FFmpeg
    subprocess.run(" ".join(cmd), shell=True, check=True)

    # Collect segment files (usually .ts files)
    segments = sorted(out_dir.glob("*.ts"), key=lambda p: p.name)
    return segments


def generate_chunk_bytes(
    segment_paths: List[Path]
) -> List[bytes]:
    """
    Read all segment files into memory as bytes.

    Returns a list of byte strings corresponding to each segment.
    """
    data_list: List[bytes] = []
    for seg in segment_paths:
        with seg.open("rb") as f:
            data_list.append(f.read())
    return data_list
