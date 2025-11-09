"""Recording service for business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories import MySQLRecordingRepository
from app.models import Recording, RecordingChunk
from app.llm import RequestYaiProvider
from app.services.audio_service import AudioService


class RecordingService:
    """Service for managing recording business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.recording_repo = MySQLRecordingRepository(db)
        self.audio_service = AudioService()
        self.llm_provider = RequestYaiProvider()

    def create_recording(self, user_id: str) -> Recording:
        """Create a new recording session."""
        return self.recording_repo.create_recording(user_id)

    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get a recording by ID."""
        return self.recording_repo.get_recording(recording_id)

    def list_user_recordings(self, user_id: str) -> List[Recording]:
        """List all recordings for a user."""
        return self.recording_repo.list_recordings(user_id)

    async def upload_chunk(
        self,
        recording_id: str,
        chunk_index: int,
        chunk_data: bytes,
        duration_seconds: Optional[float] = None
    ) -> RecordingChunk:
        """
        Upload and save an audio chunk.

        Args:
            recording_id: ID of the recording
            chunk_index: Index of the chunk
            chunk_data: Binary audio data
            duration_seconds: Duration of the chunk in seconds

        Returns:
            Created RecordingChunk
        """
        # Save chunk to disk
        chunk_path = await self.audio_service.save_chunk(recording_id, chunk_index, chunk_data)

        # Save chunk metadata to database
        return self.recording_repo.add_chunk(
            recording_id=recording_id,
            chunk_index=chunk_index,
            audio_blob_path=chunk_path,
            duration_seconds=duration_seconds
        )

    def pause_recording(self, recording_id: str) -> Optional[Recording]:
        """Pause a recording."""
        return self.recording_repo.mark_paused(recording_id)

    async def finish_recording(self, recording_id: str) -> Optional[Recording]:
        """
        Finish a recording, assemble chunks, and trigger transcription.

        Args:
            recording_id: ID of the recording

        Returns:
            Updated Recording with transcription
        """
        # Get all chunks for the recording
        chunks = self.recording_repo.get_chunks(recording_id)
        if not chunks:
            return None

        # Assemble chunks into a single audio file
        chunk_paths = [chunk.audio_blob_path for chunk in chunks]
        assembled_path = await self.audio_service.assemble_chunks(recording_id, chunk_paths)

        # Trigger transcription
        try:
            transcription = await self.llm_provider.transcribe_audio(assembled_path)
        except Exception as e:
            # If transcription fails, still mark as ended but without transcription
            print(f"Transcription failed: {e}")
            transcription = None

        # Mark recording as ended
        return self.recording_repo.mark_ended(
            recording_id=recording_id,
            full_audio_path=assembled_path,
            transcription=transcription
        )

    def add_notes(self, recording_id: str, notes: str) -> Optional[Recording]:
        """Add or update notes for a recording."""
        return self.recording_repo.add_notes(recording_id, notes)

    def delete_recording(self, recording_id: str) -> bool:
        """
        Delete a recording and all associated files.

        Args:
            recording_id: ID of the recording to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        # Delete files from disk
        self.audio_service.delete_recording_files(recording_id)

        # Delete from database
        return self.recording_repo.delete_recording(recording_id)
