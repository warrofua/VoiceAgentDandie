# ABA Voice Agent

A voice-enabled AI agent system for handling ABA (Applied Behavior Analysis) therapy insurance inquiries, authorizations, and claims processing using OpenAI's Whisper API and GPT-4.

## Features

- 🎙️ **Speech-to-Text**: Whisper API for accurate voice transcription
- 🔊 **Text-to-Speech**: OpenAI TTS for natural voice responses
- 📞 **Phone Integration**: Twilio for inbound/outbound calls
- 🏥 **Insurance Rules Engine**: ABA therapy-specific CPT code validation
- 🤖 **AI Conversation Agent**: GPT-4 powered natural language understanding
- 🔒 **HIPAA Compliant**: Secure handling of protected health information
- 📊 **Call Analytics**: Complete transcripts and audit logging

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Voice Processing**: OpenAI Whisper API, OpenAI TTS
- **Phone System**: Twilio
- **AI**: GPT-4 Turbo, LangChain
- **Caching**: Redis

## Project Structure

```
ChristineDemo/
├── src/
│   ├── api/              # FastAPI routes and endpoints
│   ├── voice/            # Voice processing services
│   │   ├── whisper_service.py
│   │   ├── tts_service.py
│   │   ├── twilio_service.py
│   │   └── call_handler.py
│   ├── insurance/        # Insurance logic
│   │   ├── rules_engine.py
│   │   ├── query_service.py
│   │   └── conversation_agent.py
│   ├── database/         # Database connection
│   ├── models/           # SQLAlchemy models
│   ├── config.py         # Configuration management
│   └── main.py           # FastAPI application
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+
- Redis 6+
- Twilio account
- OpenAI API key

### 2. Clone and Install

```bash
# Clone the repository
cd ChristineDemo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required environment variables:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aba_voice_agent
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# Environment
ENVIRONMENT=development
```

### 4. Setup Database

```bash
# Create database
createdb aba_voice_agent

# Run migrations (if using Alembic)
alembic upgrade head

# Seed sample data
python scripts/seed_data.py
```

### 5. Run the Application

```bash
# Development mode
python src/main.py

# Or using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 6. Configure Twilio Webhooks

In your Twilio console, configure the following webhooks:

- **Voice URL**: `https://your-domain.com/api/v1/voice/incoming`
- **Status Callback**: `https://your-domain.com/api/v1/voice/status`

For local development, use ngrok:

```bash
ngrok http 8000
# Use the ngrok URL for Twilio webhooks
```

## Usage Examples

### Making an Outbound Call

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/outbound/call",
    json={
        "phone_number": "+1234567890",
        "message": "This is a reminder about your upcoming appointment"
    }
)
```

### Getting Call Transcript

```python
import requests

call_id = 123
response = requests.get(f"http://localhost:8000/api/v1/calls/{call_id}/transcript")
transcript = response.json()
```

## ABA Therapy CPT Codes

The system handles the following ABA therapy CPT codes:

- **97151**: Behavior identification assessment
- **97152**: Behavior identification supporting assessment
- **97153**: Adaptive behavior treatment by technician
- **97154**: Group adaptive behavior treatment by technician
- **97155**: Adaptive behavior treatment with protocol modification (BCBA)
- **97156**: Family adaptive behavior treatment guidance
- **97157**: Multiple family group adaptive behavior treatment
- **97158**: Group adaptive behavior treatment

## Insurance Carriers Supported

- Blue Cross Blue Shield
- Aetna
- UnitedHealthcare
- Cigna
- Anthem
- Medicaid (state-specific)
- Tricare

## Sample Conversation Flow

```
Agent: "Hello, thank you for calling ABA Therapy Insurance Services.
        How may I assist you today?"

Caller: "I need to check on an authorization for my son."

Agent: "I'd be happy to help you check on that authorization.
        May I have the member ID and date of birth to verify the account?"

Caller: "Member ID is BCBS123456, date of birth is March 15, 2018."

Agent: "Thank you. I see an active authorization for John Doe covering
        ABA therapy services. The authorization is valid through June 30, 2024,
        and covers up to 160 hours per month of technician services under code 97153,
        and 8 hours per month of BCBA supervision under code 97155."
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_insurance_rules.py

# Run specific test
pytest tests/test_insurance_rules.py::test_validate_cpt_code
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Security & HIPAA Compliance

This application implements several security measures:

- ✅ Encrypted data at rest and in transit
- ✅ Audit logging for all PHI access
- ✅ Session management and timeouts
- ✅ Secure API authentication
- ✅ Role-based access control
- ✅ PHI data encryption

**Important**: Before production deployment:

1. Sign Business Associate Agreements (BAA) with all vendors
2. Conduct security audit and penetration testing
3. Implement proper encryption for PHI fields
4. Set up secure backup procedures
5. Configure proper access controls
6. Enable monitoring and alerting

## Development Roadmap

- [x] Core voice processing (Whisper + TTS)
- [x] Twilio phone integration
- [x] Insurance rules engine
- [x] GPT-4 conversation agent
- [x] Basic API endpoints
- [ ] Real-time WebSocket streaming
- [ ] Advanced NLP for intent detection
- [ ] Multi-language support
- [ ] Call analytics dashboard
- [ ] Integration with insurance carrier APIs
- [ ] Mobile app for providers

## Cost Estimates

For 1000 hours of monthly usage:

- OpenAI Whisper: ~$360
- OpenAI GPT-4: ~$1,500
- OpenAI TTS: ~$300
- Twilio Voice: ~$780
- Infrastructure: ~$500-1000

**Total**: ~$3,500-4,000/month

## Troubleshooting

### Audio Issues

```bash
# Ensure temp_audio directory exists
mkdir -p temp_audio

# Check file permissions
chmod 755 temp_audio
```

### Database Connection

```bash
# Test PostgreSQL connection
psql -U your_user -d aba_voice_agent -c "SELECT 1;"

# Reset database
dropdb aba_voice_agent
createdb aba_voice_agent
python scripts/seed_data.py
```

### Twilio Webhook Issues

```bash
# Check ngrok is running
ngrok http 8000

# Verify webhook URL in Twilio console
# Check application logs for incoming requests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is proprietary and confidential.

## Support

For issues or questions, please contact the development team.

## Acknowledgments

- OpenAI for Whisper and GPT-4 APIs
- Twilio for voice infrastructure
- FastAPI framework
- SQLAlchemy ORM
