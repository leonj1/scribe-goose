"""LLM provider interface definition."""
from typing import Protocol


class LLMProvider(Protocol):
    """Interface for LLM transcription providers."""

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file to transcribe

        Returns:
            Transcription text

        Raises:
            Exception: If transcription fails
        """
        ...
