"""Twilio integration for phone call handling."""
from typing import Optional
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from src.config import get_settings

settings = get_settings()


class TwilioService:
    """Service for handling phone calls via Twilio."""

    def __init__(self):
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.phone_number = settings.twilio_phone_number

    def make_outbound_call(
        self,
        to_number: str,
        callback_url: str,
        status_callback_url: Optional[str] = None
    ) -> str:
        """
        Initiate an outbound call.

        Args:
            to_number: Phone number to call
            callback_url: URL for handling call flow
            status_callback_url: URL for call status updates

        Returns:
            Call SID
        """
        call = self.client.calls.create(
            to=to_number,
            from_=self.phone_number,
            url=callback_url,
            status_callback=status_callback_url,
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        return call.sid

    def generate_welcome_response(self, message: str) -> str:
        """
        Generate TwiML for welcome message.

        Args:
            message: Welcome message to speak

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        response.say(message, voice='Polly.Joanna')
        response.pause(length=1)
        return str(response)

    def generate_gather_response(
        self,
        prompt: str,
        action_url: str,
        timeout: int = 5,
        num_digits: Optional[int] = None
    ) -> str:
        """
        Generate TwiML to gather user input.

        Args:
            prompt: Message to speak before gathering
            action_url: URL to send gathered data
            timeout: Seconds to wait for input
            num_digits: Expected number of digits

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        gather = Gather(
            action=action_url,
            timeout=timeout,
            num_digits=num_digits,
            input='speech dtmf'
        )
        gather.say(prompt, voice='Polly.Joanna')
        response.append(gather)

        # Fallback if no input
        response.say("I didn't receive any input. Please try again.")
        response.redirect(action_url)

        return str(response)

    def generate_stream_response(self, websocket_url: str) -> str:
        """
        Generate TwiML to start audio streaming.

        Args:
            websocket_url: WebSocket URL for audio stream

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        response.say("Please hold while I connect you.", voice='Polly.Joanna')

        # Start bidirectional audio stream
        start = response.start()
        start.stream(url=websocket_url)

        # Keep the call alive
        response.pause(length=3600)  # 1 hour max

        return str(response)

    def generate_hangup_response(self, message: Optional[str] = None) -> str:
        """
        Generate TwiML to end the call.

        Args:
            message: Optional goodbye message

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        if message:
            response.say(message, voice='Polly.Joanna')
        response.hangup()
        return str(response)

    def get_call_details(self, call_sid: str) -> dict:
        """
        Get details about a specific call.

        Args:
            call_sid: Twilio call SID

        Returns:
            Dictionary with call details
        """
        call = self.client.calls(call_sid).fetch()
        return {
            "sid": call.sid,
            "from": call.from_,
            "to": call.to,
            "status": call.status,
            "duration": call.duration,
            "start_time": call.start_time,
            "end_time": call.end_time
        }

    def generate_recording_response(
        self,
        message: str,
        action_url: str,
        max_length: int = 120
    ) -> str:
        """
        Generate TwiML to record caller's message.

        Args:
            message: Prompt before recording
            action_url: URL to handle recording
            max_length: Max recording length in seconds

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        response.say(message, voice='Polly.Joanna')
        response.record(
            action=action_url,
            max_length=max_length,
            play_beep=True,
            transcribe=False  # We'll use Whisper instead
        )
        return str(response)

    def update_call(self, call_sid: str, status: str) -> None:
        """
        Update an active call (e.g., to end it).

        Args:
            call_sid: Twilio call SID
            status: New status (e.g., 'completed')
        """
        self.client.calls(call_sid).update(status=status)
