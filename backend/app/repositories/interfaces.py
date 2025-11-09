"""Repository interface definitions using Protocol."""
from typing import Protocol, List, Optional
from app.models import User, Recording, RecordingChunk


class UserRepository(Protocol):
    """Interface for user repository operations."""

    def create_user(
        self,
        google_id: str,
        email: str,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Create a new user."""
        ...

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        ...

    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        ...

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        ...


class RecordingRepository(Protocol):
    """Interface for recording repository operations."""

    def create_recording(self, user_id: str) -> Recording:
        """Create a new recording session."""
        ...

    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get recording by ID."""
        ...

    def list_recordings(self, user_id: str) -> List[Recording]:
        """List all recordings for a user."""
        ...

    def add_chunk(
        self,
        recording_id: str,
        chunk_index: int,
        audio_blob_path: str,
        duration_seconds: Optional[float] = None
    ) -> RecordingChunk:
        """Add an audio chunk to a recording."""
        ...

    def get_chunks(self, recording_id: str) -> List[RecordingChunk]:
        """Get all chunks for a recording, ordered by chunk_index."""
        ...

    def mark_paused(self, recording_id: str) -> Optional[Recording]:
        """Mark a recording as paused."""
        ...

    def mark_ended(
        self,
        recording_id: str,
        full_audio_path: str,
        transcription: Optional[str] = None
    ) -> Optional[Recording]:
        """Mark a recording as ended and store the assembled audio path and transcription."""
        ...

    def update_transcription(self, recording_id: str, transcription: str) -> Optional[Recording]:
        """Update the transcription text for a recording."""
        ...

    def add_notes(self, recording_id: str, notes: str) -> Optional[Recording]:
        """Add or update notes for a recording."""
        ...

    def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording and its chunks."""
        ...
