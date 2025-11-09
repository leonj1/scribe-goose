"""MySQL implementation of RecordingRepository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Recording, RecordingChunk, RecordingStatus


class MySQLRecordingRepository:
    """MySQL implementation of the RecordingRepository interface."""

    def __init__(self, db: Session):
        self.db = db

    def create_recording(self, user_id: str) -> Recording:
        """Create a new recording session."""
        recording = Recording(user_id=user_id, status=RecordingStatus.ACTIVE)
        self.db.add(recording)
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get recording by ID."""
        return self.db.query(Recording).filter(Recording.id == recording_id).first()

    def list_recordings(self, user_id: str) -> List[Recording]:
        """List all recordings for a user."""
        return (
            self.db.query(Recording)
            .filter(Recording.user_id == user_id)
            .order_by(Recording.created_at.desc())
            .all()
        )

    def add_chunk(
        self,
        recording_id: str,
        chunk_index: int,
        audio_blob_path: str,
        duration_seconds: Optional[float] = None
    ) -> RecordingChunk:
        """Add an audio chunk to a recording."""
        chunk = RecordingChunk(
            recording_id=recording_id,
            chunk_index=chunk_index,
            audio_blob_path=audio_blob_path,
            duration_seconds=duration_seconds
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def get_chunks(self, recording_id: str) -> List[RecordingChunk]:
        """Get all chunks for a recording, ordered by chunk_index."""
        return (
            self.db.query(RecordingChunk)
            .filter(RecordingChunk.recording_id == recording_id)
            .order_by(RecordingChunk.chunk_index)
            .all()
        )

    def mark_paused(self, recording_id: str) -> Optional[Recording]:
        """Mark a recording as paused."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        recording.status = RecordingStatus.PAUSED
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def mark_ended(
        self,
        recording_id: str,
        full_audio_path: str,
        transcription: Optional[str] = None
    ) -> Optional[Recording]:
        """Mark a recording as ended and store the assembled audio path and transcription."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        recording.status = RecordingStatus.ENDED
        recording.audio_file_path = full_audio_path
        if transcription:
            recording.transcription_text = transcription
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def update_transcription(self, recording_id: str, transcription: str) -> Optional[Recording]:
        """Update the transcription text for a recording."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        recording.transcription_text = transcription
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def add_notes(self, recording_id: str, notes: str) -> Optional[Recording]:
        """Add or update notes for a recording."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        recording.notes = notes
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording and its chunks."""
        recording = self.get_recording(recording_id)
        if not recording:
            return False

        self.db.delete(recording)
        self.db.commit()
        return True
