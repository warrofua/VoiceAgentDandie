"""FastAPI routes for the voice agent API."""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
import json

from src.database.connection import get_db
from src.models.database_models import Call, Transcript
from src.voice.call_handler import CallHandler
from src.voice.twilio_service import TwilioService
from src.insurance.query_service import InsuranceQueryService
from src.insurance.conversation_agent import ConversationAgent

router = APIRouter()

# Global state for active conversations (in production, use Redis)
active_conversations = {}


@router.post("/voice/incoming")
async def handle_incoming_call(
    request: Request,
    From: str = Form(...),
    CallSid: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle incoming Twilio call.

    Args:
        From: Caller's phone number
        CallSid: Twilio call SID
        db: Database session

    Returns:
        TwiML response
    """
    # Create call record
    call = Call(
        call_sid=CallSid,
        phone_number=From,
        direction="inbound",
        status="in-progress"
    )
    db.add(call)
    db.commit()

    # Initialize conversation agent
    query_service = InsuranceQueryService(db)
    agent = ConversationAgent(query_service)
    welcome_message = await agent.start_conversation()

    # Store agent in active conversations
    active_conversations[CallSid] = {
        "agent": agent,
        "call_id": call.id,
        "context": {}
    }

    # Generate TwiML to start streaming
    twilio = TwilioService()
    twiml = twilio.generate_stream_response(
        websocket_url=f"wss://{request.url.hostname}/voice/stream"
    )

    return Response(content=twiml, media_type="application/xml")


@router.post("/voice/gather")
async def handle_gather(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle gathered user input from Twilio.

    Args:
        CallSid: Twilio call SID
        SpeechResult: Transcribed speech
        Digits: DTMF digits
        db: Database session

    Returns:
        TwiML response
    """
    conversation = active_conversations.get(CallSid)
    if not conversation:
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, your session has expired.</Say><Hangup/></Response>',
            media_type="application/xml"
        )

    user_input = SpeechResult or Digits

    # Save transcript
    transcript = Transcript(
        call_id=conversation["call_id"],
        speaker="caller",
        text=user_input,
        confidence=0.95
    )
    db.add(transcript)
    db.commit()

    # Process with conversation agent
    agent = conversation["agent"]
    response_data = await agent.process_user_input(
        user_input=user_input,
        context=conversation["context"]
    )

    response_text = response_data["response"]

    # Save agent response
    agent_transcript = Transcript(
        call_id=conversation["call_id"],
        speaker="agent",
        text=response_text,
        confidence=1.0
    )
    db.add(agent_transcript)
    db.commit()

    # Generate TwiML
    twilio = TwilioService()

    # Check if transfer requested
    if response_data["intent"] == "transfer_request":
        twiml = twilio.generate_hangup_response(
            "Transferring you now. Please hold."
        )
    else:
        # Continue gathering
        twiml = twilio.generate_gather_response(
            prompt=response_text,
            action_url=f"https://{request.url.hostname}/voice/gather",
            timeout=5
        )

    return Response(content=twiml, media_type="application/xml")


@router.post("/voice/status")
async def handle_call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    CallDuration: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle call status updates from Twilio.

    Args:
        CallSid: Twilio call SID
        CallStatus: Current call status
        CallDuration: Call duration in seconds
        db: Database session

    Returns:
        Success response
    """
    call = db.query(Call).filter(Call.call_sid == CallSid).first()

    if call:
        call.status = CallStatus
        if CallDuration:
            call.duration = CallDuration
        if CallStatus == "completed":
            from datetime import datetime
            call.ended_at = datetime.now()

        db.commit()

        # Clean up active conversation
        if CallSid in active_conversations:
            del active_conversations[CallSid]

    return {"status": "success"}


@router.post("/outbound/call")
async def initiate_outbound_call(
    phone_number: str,
    message: str,
    db: Session = Depends(get_db)
):
    """
    Initiate an outbound call.

    Args:
        phone_number: Number to call
        message: Message to deliver
        db: Database session

    Returns:
        Call information
    """
    try:
        call_handler = CallHandler()

        # Create call record
        call = Call(
            call_sid="pending",
            phone_number=phone_number,
            direction="outbound",
            status="initiated"
        )
        db.add(call)
        db.commit()

        # Make the call
        call_sid = call_handler.initiate_outbound_call(
            phone_number=phone_number,
            callback_url=f"https://your-domain.com/voice/outbound/callback"
        )

        # Update call record
        call.call_sid = call_sid
        db.commit()

        return {
            "success": True,
            "call_id": call.id,
            "call_sid": call_sid,
            "status": "initiated"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls/{call_id}/transcript")
async def get_call_transcript(
    call_id: int,
    db: Session = Depends(get_db)
):
    """
    Get transcript for a specific call.

    Args:
        call_id: Call ID
        db: Database session

    Returns:
        Call transcript
    """
    transcripts = db.query(Transcript).filter(
        Transcript.call_id == call_id
    ).order_by(Transcript.timestamp).all()

    return {
        "call_id": call_id,
        "transcript": [
            {
                "speaker": t.speaker,
                "text": t.text,
                "timestamp": t.timestamp.isoformat(),
                "confidence": t.confidence
            }
            for t in transcripts
        ]
    }


@router.get("/calls/{call_id}")
async def get_call_details(
    call_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details about a specific call.

    Args:
        call_id: Call ID
        db: Database session

    Returns:
        Call details
    """
    call = db.query(Call).filter(Call.id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "id": call.id,
        "call_sid": call.call_sid,
        "phone_number": call.phone_number,
        "direction": call.direction,
        "status": call.status,
        "duration": call.duration,
        "started_at": call.started_at.isoformat() if call.started_at else None,
        "ended_at": call.ended_at.isoformat() if call.ended_at else None
    }


@router.post("/test/speech-to-text")
async def test_speech_to_text(request: Request):
    """
    Test endpoint for Whisper speech-to-text.

    Args:
        request: Request with audio file

    Returns:
        Transcription result
    """
    from src.voice.whisper_service import WhisperService
    import tempfile
    import aiofiles

    # Get audio data from request
    audio_data = await request.body()

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_data)
        tmp_path = tmp.name

    # Transcribe
    whisper = WhisperService()
    result = await whisper.transcribe_audio(tmp_path)

    # Clean up
    import os
    os.unlink(tmp_path)

    return result


@router.post("/test/text-to-speech")
async def test_text_to_speech(text: str):
    """
    Test endpoint for TTS.

    Args:
        text: Text to convert to speech

    Returns:
        Audio file path
    """
    from src.voice.tts_service import TTSService
    import tempfile

    tts = TTSService()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        output_path = tmp.name

    await tts.generate_speech(text, output_path)

    return {"audio_path": output_path}
