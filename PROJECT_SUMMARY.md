# ABA Voice Agent - Current Summary

## Project Status

This repository contains a runnable FastAPI prototype for ABA insurance voice workflows.

## What is implemented

- FastAPI app startup and route registration in `src/main.py`
- Twilio webhook handling for inbound calls, inbound text/DTMF capture, and call status updates
- Outbound call kickoff (`/api/v1/outbound/call`)
- Whisper transcription, TTS response generation, and minimal call orchestration
- Insurance eligibility + authorization + benefits query services
- Rules engine for CPT/diagnosis/session limit checks
- Call/transcript/audit model layer and seed data utility
- Basic demo script and test scaffolding

## Current Source Inventory

- `src/main.py`
- `src/config.py`
- `src/api/routes.py`
- `src/database/connection.py`
- `src/models/database_models.py`
- `src/voice/whisper_service.py`
- `src/voice/tts_service.py`
- `src/voice/twilio_service.py`
- `src/voice/call_handler.py`
- `src/insurance/rules_engine.py`
- `src/insurance/query_service.py`
- `src/insurance/conversation_agent.py`

Total source files: **12**

## API Facts

All operational API routes are under `/api/v1`:

- `/voice/incoming`
- `/voice/gather`
- `/voice/status`
- `/outbound/call`
- `/calls/{id}`
- `/calls/{id}/transcript`
- `/test/speech-to-text`
- `/test/text-to-speech`

Root routes:

- `/`
- `/health`
- `/ui`

## Runtime Commands

```bash
make setup    # install + env + folders
make seed     # load sample patients and rules
make dev      # start development server
make test     # run pytest and report coverage
make lint     # run flake8 + mypy
make format   # format source files with black
make clean    # cleanup temp files
```

## Notes

- This is not yet a hardened production deployment.
- Redis is configured in settings, but active conversation state is currently in-memory (`active_conversations` in memory).
- Security, auth, and rate limiting are still candidates for hardening before production use.

