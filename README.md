# ABA Voice Agent

A FastAPI application that handles ABA therapy insurance calls using OpenAI and Twilio.

## Features

- 🎙️ **Speech-to-Text**: Whisper API transcription
- 🔊 **Text-to-Speech**: OpenAI TTS generation
- 📞 **Phone integration**: Twilio inbound/outbound call handling
- 🏥 **Insurance rules engine**: CPT code and diagnosis validation
- 🤖 **Conversation flow**: GPT-4 powered insurance agent
- 📊 **Audit + transcripts**: Recorded call and query history

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Voice**: OpenAI Whisper API, OpenAI TTS
- **Telephony**: Twilio Voice
- **AI**: GPT-4
- **Caching**: Redis (configured for future session scaling)

## Project Structure

```text
VoiceAgentDandie/
├── src/
│   ├── api/              # FastAPI routes and endpoints
│   ├── voice/            # Whisper, TTS, Twilio service, call orchestration
│   ├── insurance/        # Rules engine, query service, conversation agent
│   ├── database/         # Connection/session management
│   ├── models/           # SQLAlchemy schema models
│   ├── config.py         # Environment settings
│   └── main.py           # App startup
├── examples/             # Demo conversation script
├── docs/                 # Architecture + deployment docs
├── tests/                # Unit tests
├── scripts/              # Seed, dev runner, test runner
├── static/               # Optional UI at /ui
├── requirements.txt
├── pyproject.toml
├── Makefile
└── .env.example
```

## Quick Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- OpenAI API key
- Twilio account

### 2. Install and configure

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

make install
# or: pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
OPENAI_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
DATABASE_URL=postgresql://user:pass@localhost:5432/aba_voice_agent
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Initialize data

```bash
createdb aba_voice_agent
python scripts/seed_data.py
```

### 4. Start server

```bash
make dev
# or: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Surface

Most API routes are prefixed with `/api/v1`.

- `GET /` – health and version metadata
- `GET /health` – lightweight health check
- `GET /ui` – static demo UI

### API v1 routes

- `POST /api/v1/voice/incoming` – Twilio inbound call webhook
- `POST /api/v1/voice/gather` – Gathered user input handler
- `POST /api/v1/voice/status` – Twilio call-status callback
- `POST /api/v1/outbound/call` – Trigger outbound calls
- `GET /api/v1/calls/{call_id}` – Call metadata
- `GET /api/v1/calls/{call_id}/transcript` – Call transcript
- `POST /api/v1/test/speech-to-text` – Test Whisper integration
- `POST /api/v1/test/text-to-speech` – Test TTS integration

Swagger UI is at `http://localhost:8000/docs` and ReDoc is at `http://localhost:8000/redoc`.

## Usage Examples

### Make an outbound call

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/outbound/call",
    params={
        "phone_number": "+15555550123",
        "message": "Your appointment is coming up tomorrow."
    },
)
print(response.json())
```

### Fetch a transcript

```python
call_id = 1
resp = requests.get(f"http://localhost:8000/api/v1/calls/{call_id}/transcript")
print(resp.json())
```

## Twilio Setup

Point Twilio to:

- `https://your-domain.com/api/v1/voice/incoming`
- `https://your-domain.com/api/v1/voice/status`

Use `ngrok http 8000` for local testing.

## Testing

```bash
make test
./scripts/test.sh
pytest tests/test_insurance_rules.py -v
```

You can also run lint and format steps from the Makefile:

```bash
make lint
make format
```

## Security Notes

- Keep API keys and signing secrets in `.env` only.
- `/.env` must never be committed.
- Rotate secrets for staging/production.

HIPAA-relevant controls are implemented at a project level through:

- Encryption-sensitive data fields
- Session status tracking
- Call and query audit trail in the database

This project is a **development-focused implementation** and should be hardened before production use.

