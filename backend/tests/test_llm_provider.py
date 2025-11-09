"""Tests for LLM provider implementations."""
import pytest
from unittest.mock import AsyncMock, patch, mock_open
from app.llm import RequestYaiProvider


class TestRequestYaiProvider:
    """Test cases for RequestYaiProvider."""

    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self):
        """Test successful audio transcription."""
        provider = RequestYaiProvider()

        # Mock the HTTP client
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "transcription": "This is a test transcription"
        }
        mock_response.raise_for_status = AsyncMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            with patch('builtins.open', mock_open(read_data=b'fake audio data')):
                result = await provider.transcribe_audio("/fake/path/audio.webm")

        assert result == "This is a test transcription"

    @pytest.mark.asyncio
    async def test_transcribe_audio_missing_field(self):
        """Test transcription with missing transcription field."""
        provider = RequestYaiProvider()

        # Mock the HTTP client with invalid response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"error": "Invalid response"}
        mock_response.raise_for_status = AsyncMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            with patch('builtins.open', mock_open(read_data=b'fake audio data')):
                with pytest.raises(ValueError, match="missing 'transcription' field"):
                    await provider.transcribe_audio("/fake/path/audio.webm")
