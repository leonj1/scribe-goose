"""Recording models."""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class RecordingStatus(str, Enum):
    """Enum for recording status."""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class Recording(Base):
    """Recording model for storing audio recording sessions."""

    __tablename__ = "recordings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(SQLEnum(RecordingStatus), default=RecordingStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    audio_file_path = Column(String(512), nullable=True)
    transcription_text = Column(Text, nullable=True)
    llm_provider = Column(String(50), default="requestyai", nullable=False)
    notes = Column(Text, nullable=True)  # For user notes on the recording session

    # Relationships
    user = relationship("User", back_populates="recordings")
    chunks = relationship("RecordingChunk", back_populates="recording", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recording(id={self.id}, user_id={self.user_id}, status={self.status})>"


class RecordingChunk(Base):
    """RecordingChunk model for storing individual audio chunks."""

    __tablename__ = "recording_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id = Column(String(36), ForeignKey("recordings.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    audio_blob_path = Column(String(512), nullable=False)
    duration_seconds = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recording = relationship("Recording", back_populates="chunks")

    def __repr__(self):
        return f"<RecordingChunk(id={self.id}, recording_id={self.recording_id}, chunk_index={self.chunk_index})>"
