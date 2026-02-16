"""OpenAI TTS integration for text-to-speech."""
from pathlib import Path
from typing import Literal, Optional
import aiofiles
from openai import AsyncOpenAI
from src.config import get_settings

settings = get_settings()


class TTSService:
    """Service for text-to-speech using OpenAI TTS."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.tts_model
        self.voice = settings.tts_voice

    async def generate_speech(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> str:
        """
        Generate speech from text and save to file.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speed of speech (0.25 to 4.0)

        Returns:
            Path to generated audio file
        """
        try:
            voice = voice or self.voice

            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            # Save audio to file
            async with aiofiles.open(output_path, 'wb') as audio_file:
                async for chunk in response.iter_bytes():
                    await audio_file.write(chunk)

            return output_path

        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")

    async def generate_speech_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ):
        """
        Generate speech and stream audio bytes.

        Args:
            text: Text to convert to speech
            voice: Voice to use
            speed: Speed of speech

        Yields:
            Audio data chunks
        """
        try:
            voice = voice or self.voice

            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            async for chunk in response.iter_bytes():
                yield chunk

        except Exception as e:
            raise Exception(f"TTS streaming failed: {str(e)}")

    async def generate_multiple_responses(
        self,
        texts: list[str],
        output_dir: str,
        voice: Optional[str] = None
    ) -> list[str]:
        """
        Generate multiple speech files concurrently.

        Args:
            texts: List of texts to convert
            output_dir: Directory to save audio files
            voice: Voice to use

        Returns:
            List of paths to generated audio files
        """
        import asyncio

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        tasks = []
        for idx, text in enumerate(texts):
            output_path = f"{output_dir}/response_{idx}.mp3"
            tasks.append(self.generate_speech(text, output_path, voice))

        return await asyncio.gather(*tasks)

    def get_available_voices(self) -> list[str]:
        """Get list of available TTS voices."""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    async def estimate_audio_duration(self, text: str) -> float:
        """
        Estimate audio duration based on text length.

        Args:
            text: Text to estimate

        Returns:
            Estimated duration in seconds
        """
        # Rough estimate: ~150 words per minute
        words = len(text.split())
        duration = (words / 150) * 60
        return duration
