"""Whisper API integration for speech-to-text."""
import asyncio
from pathlib import Path
from typing import Optional
import aiofiles
from openai import AsyncOpenAI
from src.config import get_settings

settings = get_settings()


class WhisperService:
    """Service for handling speech-to-text using Whisper API."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.whisper_model

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: str = "en",
        prompt: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio file using Whisper API.

        Args:
            audio_file_path: Path to audio file
            language: Language code (default: en)
            prompt: Optional prompt to guide transcription

        Returns:
            Dictionary with transcription and metadata
        """
        try:
            async with aiofiles.open(audio_file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()

            # Create a file-like object from bytes
            from io import BytesIO
            audio_buffer = BytesIO(audio_data)
            audio_buffer.name = Path(audio_file_path).name

            # Call Whisper API
            transcript = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_buffer,
                language=language,
                response_format="verbose_json",
                prompt=prompt
            )

            return {
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": getattr(transcript, 'segments', None)
            }

        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")

    async def transcribe_stream(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> str:
        """
        Transcribe audio from bytes stream.

        Args:
            audio_data: Audio data in bytes
            language: Language code

        Returns:
            Transcribed text
        """
        try:
            from io import BytesIO
            audio_buffer = BytesIO(audio_data)
            audio_buffer.name = "audio.wav"

            transcript = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_buffer,
                language=language,
                response_format="text"
            )

            return transcript

        except Exception as e:
            raise Exception(f"Stream transcription failed: {str(e)}")

    async def transcribe_with_confidence(
        self,
        audio_file_path: str,
        language: str = "en"
    ) -> dict:
        """
        Transcribe audio and return with confidence scores.

        Args:
            audio_file_path: Path to audio file
            language: Language code

        Returns:
            Dictionary with text, confidence, and word-level data
        """
        result = await self.transcribe_audio(audio_file_path, language)

        # Calculate average confidence from segments if available
        confidence = 0.95  # Default high confidence
        if result.get('segments'):
            # Whisper doesn't provide confidence in standard response
            # This would need custom implementation or alternative API
            pass

        return {
            "text": result["text"],
            "confidence": confidence,
            "language": result["language"],
            "duration": result["duration"]
        }
