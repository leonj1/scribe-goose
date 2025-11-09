"""RequestYai LLM provider implementation."""
import httpx
from app.core.config import settings


class RequestYaiProvider:
    """RequestYai implementation of the LLMProvider interface."""

    def __init__(self):
        self.api_url = settings.LLM_API_URL
        self.api_key = settings.LLM_API_KEY

    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe an audio file using RequestYai API.

        Args:
            audio_path: Path to the audio file to transcribe

        Returns:
            Transcription text

        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If the response is invalid
        """
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Read the audio file
            with open(audio_path, "rb") as audio_file:
                files = {"audio": audio_file}
                headers = {"Authorization": f"Bearer {self.api_key}"}

                # Make the API request
                response = await client.post(
                    self.api_url,
                    files=files,
                    headers=headers
                )

                # Check for errors
                response.raise_for_status()

                # Parse the response
                data = response.json()
                if "transcription" not in data:
                    raise ValueError("Invalid response from RequestYai API: missing 'transcription' field")

                return data["transcription"]
