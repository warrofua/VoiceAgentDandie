"""Tests for voice services."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.voice.tts_service import TTSService


@pytest.mark.asyncio
async def test_tts_estimate_duration():
    """Test TTS duration estimation."""
    tts = TTSService()

    text = "This is a test sentence with exactly ten words here."
    duration = await tts.estimate_audio_duration(text)

    # 10 words at ~150 words/min = ~4 seconds
    assert 3 < duration < 6


def test_tts_get_available_voices():
    """Test getting available TTS voices."""
    tts = TTSService()

    voices = tts.get_available_voices()

    assert "alloy" in voices
    assert "echo" in voices
    assert len(voices) == 6


@pytest.mark.asyncio
@patch("src.voice.tts_service.AsyncOpenAI")
async def test_tts_generate_speech(mock_openai):
    """Test TTS speech generation."""
    # Mock the OpenAI client
    mock_client = AsyncMock()
    mock_response = AsyncMock()

    async def mock_iter():
        yield b"audio_chunk_1"
        yield b"audio_chunk_2"

    mock_response.iter_bytes = mock_iter
    mock_client.audio.speech.create.return_value = mock_response
    mock_openai.return_value = mock_client

    tts = TTSService()
    tts.client = mock_client

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        output_path = tmp.name

    result = await tts.generate_speech(
        text="Hello, this is a test",
        output_path=output_path
    )

    assert result == output_path
    mock_client.audio.speech.create.assert_called_once()


def test_twilio_service_generate_welcome():
    """Test Twilio welcome response generation."""
    from src.voice.twilio_service import TwilioService

    with patch("src.voice.twilio_service.Client"):
        twilio = TwilioService()
        twiml = twilio.generate_welcome_response("Welcome to our service")

        assert "Welcome to our service" in twiml
        assert "<Response>" in twiml
        assert "<Say>" in twiml


def test_twilio_service_generate_gather():
    """Test Twilio gather response generation."""
    from src.voice.twilio_service import TwilioService

    with patch("src.voice.twilio_service.Client"):
        twilio = TwilioService()
        twiml = twilio.generate_gather_response(
            prompt="Please enter your member ID",
            action_url="https://example.com/gather",
            timeout=5
        )

        assert "Please enter your member ID" in twiml
        assert "<Gather" in twiml
        assert "https://example.com/gather" in twiml


def test_twilio_service_generate_hangup():
    """Test Twilio hangup response generation."""
    from src.voice.twilio_service import TwilioService

    with patch("src.voice.twilio_service.Client"):
        twilio = TwilioService()
        twiml = twilio.generate_hangup_response("Thank you for calling")

        assert "Thank you for calling" in twiml
        assert "<Hangup/>" in twiml
