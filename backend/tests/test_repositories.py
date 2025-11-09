"""Tests for repository implementations."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import User, Recording, RecordingStatus
from app.repositories import MySQLUserRepository, MySQLRecordingRepository


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestUserRepository:
    """Test cases for UserRepository."""

    def test_create_user(self, db_session):
        """Test creating a new user."""
        repo = MySQLUserRepository(db_session)
        user = repo.create_user(
            google_id="test123",
            email="test@example.com",
            display_name="Test User",
            avatar_url="https://example.com/avatar.jpg"
        )

        assert user.id is not None
        assert user.google_id == "test123"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"

    def test_get_user_by_google_id(self, db_session):
        """Test retrieving user by Google ID."""
        repo = MySQLUserRepository(db_session)
        created_user = repo.create_user(
            google_id="test456",
            email="test2@example.com"
        )

        retrieved_user = repo.get_user_by_google_id("test456")
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id

    def test_update_user(self, db_session):
        """Test updating user information."""
        repo = MySQLUserRepository(db_session)
        user = repo.create_user(
            google_id="test789",
            email="test3@example.com"
        )

        updated_user = repo.update_user(
            user.id,
            display_name="Updated Name"
        )

        assert updated_user.display_name == "Updated Name"


class TestRecordingRepository:
    """Test cases for RecordingRepository."""

    def test_create_recording(self, db_session):
        """Test creating a new recording."""
        # Create a user first
        user_repo = MySQLUserRepository(db_session)
        user = user_repo.create_user(
            google_id="test_rec",
            email="rec@example.com"
        )

        # Create recording
        rec_repo = MySQLRecordingRepository(db_session)
        recording = rec_repo.create_recording(user.id)

        assert recording.id is not None
        assert recording.user_id == user.id
        assert recording.status == RecordingStatus.ACTIVE

    def test_add_chunk(self, db_session):
        """Test adding a chunk to a recording."""
        # Setup
        user_repo = MySQLUserRepository(db_session)
        user = user_repo.create_user(
            google_id="test_chunk",
            email="chunk@example.com"
        )

        rec_repo = MySQLRecordingRepository(db_session)
        recording = rec_repo.create_recording(user.id)

        # Add chunk
        chunk = rec_repo.add_chunk(
            recording.id,
            chunk_index=0,
            audio_blob_path="/path/to/chunk_0.webm",
            duration_seconds=10.5
        )

        assert chunk.id is not None
        assert chunk.recording_id == recording.id
        assert chunk.chunk_index == 0

    def test_mark_paused(self, db_session):
        """Test marking a recording as paused."""
        # Setup
        user_repo = MySQLUserRepository(db_session)
        user = user_repo.create_user(
            google_id="test_pause",
            email="pause@example.com"
        )

        rec_repo = MySQLRecordingRepository(db_session)
        recording = rec_repo.create_recording(user.id)

        # Pause recording
        paused_recording = rec_repo.mark_paused(recording.id)

        assert paused_recording.status == RecordingStatus.PAUSED

    def test_mark_ended(self, db_session):
        """Test marking a recording as ended."""
        # Setup
        user_repo = MySQLUserRepository(db_session)
        user = user_repo.create_user(
            google_id="test_end",
            email="end@example.com"
        )

        rec_repo = MySQLRecordingRepository(db_session)
        recording = rec_repo.create_recording(user.id)

        # End recording
        ended_recording = rec_repo.mark_ended(
            recording.id,
            full_audio_path="/path/to/full_audio.webm",
            transcription="Test transcription"
        )

        assert ended_recording.status == RecordingStatus.ENDED
        assert ended_recording.audio_file_path == "/path/to/full_audio.webm"
        assert ended_recording.transcription_text == "Test transcription"

    def test_list_recordings(self, db_session):
        """Test listing recordings for a user."""
        # Setup
        user_repo = MySQLUserRepository(db_session)
        user = user_repo.create_user(
            google_id="test_list",
            email="list@example.com"
        )

        rec_repo = MySQLRecordingRepository(db_session)
        rec1 = rec_repo.create_recording(user.id)
        rec2 = rec_repo.create_recording(user.id)

        # List recordings
        recordings = rec_repo.list_recordings(user.id)

        assert len(recordings) == 2
        assert recordings[0].id in [rec1.id, rec2.id]
