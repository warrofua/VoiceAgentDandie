# Project Structure

```
ChristineDemo/
│
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # 10-minute setup guide
├── 📄 PROJECT_PLAN.md              # Original planning document
├── 📄 PROJECT_SUMMARY.md           # Project summary
├── 📄 STRUCTURE.md                 # This file
├── 📄 Makefile                     # Command shortcuts
│
├── 📁 docs/                        # Documentation
│   ├── ARCHITECTURE.md             # System architecture
│   └── DEPLOYMENT.md               # Production deployment guide
│
├── 📁 src/                         # Source code
│   ├── main.py                     # FastAPI application
│   ├── config.py                   # Configuration management
│   │
│   ├── 📁 api/                     # API layer
│   │   └── routes.py               # FastAPI endpoints
│   │
│   ├── 📁 voice/                   # Voice processing
│   │   ├── whisper_service.py      # Speech-to-text (Whisper API)
│   │   ├── tts_service.py          # Text-to-speech (OpenAI TTS)
│   │   ├── twilio_service.py       # Phone integration (Twilio)
│   │   └── call_handler.py         # Call orchestration
│   │
│   ├── 📁 insurance/               # Insurance logic
│   │   ├── rules_engine.py         # ABA therapy rules & validation
│   │   ├── query_service.py        # Insurance queries
│   │   └── conversation_agent.py   # GPT-4 conversation AI
│   │
│   ├── 📁 database/                # Database layer
│   │   └── connection.py           # Database connection & sessions
│   │
│   └── 📁 models/                  # Data models
│       └── database_models.py      # SQLAlchemy models
│
├── 📁 tests/                       # Test suite
│   ├── test_insurance_rules.py     # Rules engine tests
│   └── test_voice_services.py      # Voice service tests
│
├── 📁 scripts/                     # Utility scripts
│   ├── seed_data.py                # Database seeding
│   ├── run_dev.sh                  # Development startup
│   └── test.sh                     # Test runner
│
├── 📁 examples/                    # Example code
│   └── demo_conversation.py        # Interactive demo
│
├── 📁 config/                      # Configuration files
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 pyproject.toml               # Project metadata
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
│
└── 📁 temp_audio/                  # Temporary audio files (created at runtime)
```

## File Descriptions

### Documentation
- **README.md**: Complete project documentation with setup, usage, and examples
- **QUICKSTART.md**: Get started in 10 minutes
- **PROJECT_PLAN.md**: Original 26-week implementation plan
- **PROJECT_SUMMARY.md**: Overview of what was built
- **docs/ARCHITECTURE.md**: System architecture and data flows
- **docs/DEPLOYMENT.md**: Production deployment guide with Docker, AWS, security

### Source Code (src/)

#### API Layer
- **main.py**: FastAPI application setup, middleware, startup/shutdown
- **api/routes.py**: REST endpoints for calls, voice, testing

#### Voice Processing
- **voice/whisper_service.py**: Whisper API integration for speech-to-text
- **voice/tts_service.py**: OpenAI TTS for text-to-speech
- **voice/twilio_service.py**: Twilio integration for phone calls
- **voice/call_handler.py**: Orchestrates voice services (STT → AI → TTS)

#### Insurance Logic
- **insurance/rules_engine.py**: ABA therapy CPT/diagnosis validation, session limits
- **insurance/query_service.py**: Eligibility, authorization, benefits queries
- **insurance/conversation_agent.py**: GPT-4 powered conversational AI

#### Data Layer
- **database/connection.py**: SQLAlchemy engine and session management
- **models/database_models.py**: Database models (Calls, Patients, Authorizations, etc.)
- **config.py**: Environment configuration using Pydantic

### Testing & Scripts
- **tests/**: Pytest test suite with coverage
- **scripts/seed_data.py**: Populate database with sample data
- **scripts/run_dev.sh**: Start development server
- **scripts/test.sh**: Run tests with coverage
- **examples/demo_conversation.py**: Interactive demo showing system capabilities

### Configuration
- **requirements.txt**: Python package dependencies
- **pyproject.toml**: Poetry/build configuration
- **.env.example**: Template for environment variables
- **.gitignore**: Git ignore patterns
- **Makefile**: Common command shortcuts

## Key Concepts by File

### Call Flow
1. **twilio_service.py** receives incoming call
2. **routes.py** creates Call record, initializes agent
3. **call_handler.py** orchestrates the conversation
4. **whisper_service.py** transcribes caller speech
5. **conversation_agent.py** understands intent, generates response
6. **query_service.py** fetches insurance data if needed
7. **rules_engine.py** validates against ABA rules
8. **tts_service.py** converts response to speech
9. **routes.py** saves transcript to database

### Database Schema
**database_models.py** defines:
- `Call`: Call metadata (SID, phone, duration, status)
- `Transcript`: Conversation history (speaker, text, timestamp)
- `Patient`: Patient info (member ID, DOB, carrier) - encrypted
- `Authorization`: ABA authorizations (codes, dates, services)
- `InsuranceRule`: Carrier-specific rules (limits, requirements)
- `InsuranceQuery`: Query audit trail
- `AuditLog`: HIPAA compliance logging

### AI Pipeline
1. **Whisper** (whisper_service.py): Audio → Text
2. **GPT-4** (conversation_agent.py): Text → Intent + Entities
3. **Rules Engine** (rules_engine.py): Validate insurance rules
4. **Query Service** (query_service.py): Fetch data
5. **GPT-4** (conversation_agent.py): Generate natural response
6. **TTS** (tts_service.py): Text → Audio

## Lines of Code

| Component | Files | LoC |
|-----------|-------|-----|
| Voice Processing | 4 | ~600 |
| Insurance Logic | 3 | ~800 |
| API & Models | 3 | ~700 |
| Tests | 2 | ~300 |
| Scripts | 3 | ~200 |
| **Total** | **15** | **~2,600** |

Plus ~900 lines of documentation!

## Quick Commands

```bash
# Setup
make install        # Install dependencies
make setup          # Full setup (creates .env, directories)

# Development
make dev            # Start development server
make seed           # Populate database with sample data
make demo           # Run interactive demo

# Testing
make test           # Run test suite with coverage
make lint           # Run linters
make format         # Format code with black

# Cleanup
make clean          # Remove temporary files
```

## Technology by File

| File | Technologies |
|------|-------------|
| whisper_service.py | OpenAI Whisper API |
| tts_service.py | OpenAI TTS API |
| twilio_service.py | Twilio Voice API |
| conversation_agent.py | GPT-4 Turbo, LangChain |
| database_models.py | SQLAlchemy ORM |
| routes.py | FastAPI |
| main.py | FastAPI, Uvicorn |

## Getting Started

1. Read **QUICKSTART.md** for setup
2. Run `make setup` to initialize
3. Edit `.env` with your API keys
4. Run `make seed` to add sample data
5. Run `make dev` to start server
6. Visit http://localhost:8000/docs

## Learn More

- Architecture details: **docs/ARCHITECTURE.md**
- Production deployment: **docs/DEPLOYMENT.md**
- Full documentation: **README.md**
