"""Audio processing service."""
import os
import shutil
from pathlib import Path
from typing import List
from app.core.config import settings


class AudioService:
    """Service for handling audio file operations."""

    def __init__(self):
        self.storage_path = Path(settings.AUDIO_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def get_chunk_directory(self, recording_id: str) -> Path:
        """Get the directory for storing chunks of a recording."""
        chunk_dir = self.storage_path / recording_id / "chunks"
        chunk_dir.mkdir(parents=True, exist_ok=True)
        return chunk_dir

    def get_recording_directory(self, recording_id: str) -> Path:
        """Get the directory for a recording."""
        recording_dir = self.storage_path / recording_id
        recording_dir.mkdir(parents=True, exist_ok=True)
        return recording_dir

    async def save_chunk(self, recording_id: str, chunk_index: int, chunk_data: bytes) -> str:
        """
        Save an audio chunk to disk.

        Args:
            recording_id: ID of the recording
            chunk_index: Index of the chunk
            chunk_data: Binary audio data

        Returns:
            Path to the saved chunk file
        """
        chunk_dir = self.get_chunk_directory(recording_id)
        chunk_path = chunk_dir / f"chunk_{chunk_index:05d}.webm"

        with open(chunk_path, "wb") as f:
            f.write(chunk_data)

        return str(chunk_path)

    async def assemble_chunks(self, recording_id: str, chunk_paths: List[str]) -> str:
        """
        Assemble audio chunks into a single file.

        Args:
            recording_id: ID of the recording
            chunk_paths: List of paths to chunk files in order

        Returns:
            Path to the assembled audio file
        """
        recording_dir = self.get_recording_directory(recording_id)
        output_path = recording_dir / "recording.webm"

        # Simple concatenation for WebM files
        # In production, you might want to use ffmpeg for proper merging
        with open(output_path, "wb") as output_file:
            for chunk_path in chunk_paths:
                with open(chunk_path, "rb") as chunk_file:
                    shutil.copyfileobj(chunk_file, output_file)

        return str(output_path)

    def delete_recording_files(self, recording_id: str) -> None:
        """
        Delete all files associated with a recording.

        Args:
            recording_id: ID of the recording
        """
        recording_dir = self.get_recording_directory(recording_id)
        if recording_dir.exists():
            shutil.rmtree(recording_dir)

    def get_file_size(self, file_path: str) -> int:
        """Get the size of a file in bytes."""
        return os.path.getsize(file_path)
