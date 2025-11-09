"""Recording management routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core import get_db
from app.models import User, Recording
from app.services import RecordingService
from app.routers.dependencies import get_current_user

router = APIRouter(prefix="/recordings", tags=["recordings"])


# Pydantic models for request/response
class RecordingResponse(BaseModel):
    """Response model for recording."""
    id: str
    user_id: str
    status: str
    created_at: str
    updated_at: str
    audio_file_path: Optional[str] = None
    transcription_text: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class RecordingListResponse(BaseModel):
    """Response model for list of recordings."""
    recordings: List[RecordingResponse]


class NotesRequest(BaseModel):
    """Request model for adding notes."""
    notes: str


@router.post("/", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def create_recording(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new recording session.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Created recording
    """
    recording_service = RecordingService(db)
    recording = recording_service.create_recording(current_user.id)

    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat(),
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        notes=recording.notes
    )


@router.get("/", response_model=RecordingListResponse)
async def list_recordings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all recordings for the authenticated user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of user's recordings
    """
    recording_service = RecordingService(db)
    recordings = recording_service.list_user_recordings(current_user.id)

    return RecordingListResponse(
        recordings=[
            RecordingResponse(
                id=r.id,
                user_id=r.user_id,
                status=r.status.value,
                created_at=r.created_at.isoformat(),
                updated_at=r.updated_at.isoformat(),
                audio_file_path=r.audio_file_path,
                transcription_text=r.transcription_text,
                notes=r.notes
            )
            for r in recordings
        ]
    )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific recording.

    Args:
        recording_id: ID of the recording
        current_user: Authenticated user
        db: Database session

    Returns:
        Recording details

    Raises:
        HTTPException: If recording not found or access denied
    """
    recording_service = RecordingService(db)
    recording = recording_service.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    # Check if user owns the recording
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat(),
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        notes=recording.notes
    )


@router.post("/{recording_id}/chunks", status_code=status.HTTP_201_CREATED)
async def upload_chunk(
    recording_id: str,
    chunk_index: int = Form(...),
    audio_chunk: UploadFile = File(...),
    duration_seconds: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an audio chunk for a recording.

    Args:
        recording_id: ID of the recording
        chunk_index: Sequential index of the chunk
        audio_chunk: Audio file chunk
        duration_seconds: Optional duration of the chunk
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message with chunk info

    Raises:
        HTTPException: If recording not found or access denied
    """
    recording_service = RecordingService(db)
    recording = recording_service.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Read chunk data
    chunk_data = await audio_chunk.read()

    # Upload chunk
    chunk = await recording_service.upload_chunk(
        recording_id=recording_id,
        chunk_index=chunk_index,
        chunk_data=chunk_data,
        duration_seconds=duration_seconds
    )

    return {
        "message": "Chunk uploaded successfully",
        "chunk_id": chunk.id,
        "chunk_index": chunk.chunk_index
    }


@router.patch("/{recording_id}/pause", response_model=RecordingResponse)
async def pause_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pause a recording.

    Args:
        recording_id: ID of the recording
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated recording

    Raises:
        HTTPException: If recording not found or access denied
    """
    recording_service = RecordingService(db)
    recording = recording_service.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    recording = recording_service.pause_recording(recording_id)

    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat(),
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        notes=recording.notes
    )


@router.post("/{recording_id}/finish", response_model=RecordingResponse)
async def finish_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finish a recording, assemble chunks, and trigger transcription.

    Args:
        recording_id: ID of the recording
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated recording with transcription

    Raises:
        HTTPException: If recording not found or access denied
    """
    recording_service = RecordingService(db)
    recording = recording_service.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    recording = await recording_service.finish_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to finish recording"
        )

    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat(),
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        notes=recording.notes
    )


@router.patch("/{recording_id}/notes", response_model=RecordingResponse)
async def add_notes(
    recording_id: str,
    notes_request: NotesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add or update notes for a recording.

    Args:
        recording_id: ID of the recording
        notes_request: Notes content
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated recording

    Raises:
        HTTPException: If recording not found or access denied
    """
    recording_service = RecordingService(db)
    recording = recording_service.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    recording = recording_service.add_notes(recording_id, notes_request.notes)

    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat(),
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        notes=recording.notes
    )


@router.delete("/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a recording and all associated files.

    Args:
        recording_id: ID of the recording
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: If recording not found or access denied
    """
    recording_service = RecordingService(db)
    recording = recording_service.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    success = recording_service.delete_recording(recording_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recording"
        )

    return None
