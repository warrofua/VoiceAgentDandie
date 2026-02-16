"""Call handling orchestration combining voice services."""
import asyncio
from typing import Optional
from pathlib import Path
import tempfile
from src.voice.whisper_service import WhisperService
from src.voice.tts_service import TTSService
from src.voice.twilio_service import TwilioService


class CallHandler:
    """Orchestrates call handling with voice services."""

    def __init__(self):
        self.whisper = WhisperService()
        self.tts = TTSService()
        self.twilio = TwilioService()

    async def process_caller_audio(
        self,
        audio_file_path: str,
        language: str = "en"
    ) -> dict:
        """
        Process caller's audio input.

        Args:
            audio_file_path: Path to audio file
            language: Language code

        Returns:
            Transcription result with text and metadata
        """
        try:
            result = await self.whisper.transcribe_with_confidence(
                audio_file_path,
                language
            )
            return {
                "success": True,
                "text": result["text"],
                "confidence": result["confidence"],
                "duration": result["duration"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_agent_response(
        self,
        response_text: str,
        voice: Optional[str] = None
    ) -> str:
        """
        Generate agent's audio response.

        Args:
            response_text: Text to convert to speech
            voice: Voice to use

        Returns:
            Path to generated audio file
        """
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3",
                dir="temp_audio"
            ) as tmp_file:
                output_path = tmp_file.name

            # Ensure temp directory exists
            Path("temp_audio").mkdir(exist_ok=True)

            await self.tts.generate_speech(
                text=response_text,
                output_path=output_path,
                voice=voice
            )

            return output_path

        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    async def handle_call_turn(
        self,
        caller_audio_path: str,
        agent_response_text: str
    ) -> dict:
        """
        Handle one turn of conversation (listen + respond).

        Args:
            caller_audio_path: Path to caller's audio
            agent_response_text: Agent's response text

        Returns:
            Dictionary with transcription and response paths
        """
        # Process caller input and generate response in parallel
        transcription_task = self.process_caller_audio(caller_audio_path)
        response_task = self.generate_agent_response(agent_response_text)

        transcription, response_path = await asyncio.gather(
            transcription_task,
            response_task
        )

        return {
            "caller_text": transcription.get("text"),
            "caller_confidence": transcription.get("confidence"),
            "agent_audio_path": response_path
        }

    def initiate_outbound_call(
        self,
        phone_number: str,
        callback_url: str
    ) -> str:
        """
        Start an outbound call.

        Args:
            phone_number: Number to call
            callback_url: URL for call handling

        Returns:
            Call SID
        """
        return self.twilio.make_outbound_call(
            to_number=phone_number,
            callback_url=callback_url
        )

    async def handle_streaming_conversation(
        self,
        audio_stream: bytes,
        conversation_context: dict
    ) -> str:
        """
        Handle real-time streaming conversation.

        Args:
            audio_stream: Audio data bytes
            conversation_context: Current conversation state

        Returns:
            Agent's response text
        """
        # Transcribe incoming audio
        caller_text = await self.whisper.transcribe_stream(audio_stream)

        # This would integrate with the AI agent to generate response
        # (implemented in conversation_agent.py)
        agent_response = f"I heard you say: {caller_text}"

        return agent_response
