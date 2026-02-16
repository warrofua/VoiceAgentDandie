# Project Structure

```text
VoiceAgentDandie/
├── README.md
├── QUICKSTART.md
├── START_HERE.md
├── PROJECT_PLAN.md
├── PROJECT_SUMMARY.md
├── STRUCTURE.md
├── Makefile
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── src/
│   ├── main.py
│   ├── config.py
│   ├── api/routes.py
│   ├── database/connection.py
│   ├── models/database_models.py
│   ├── voice/
│   │   ├── whisper_service.py
│   │   ├── tts_service.py
│   │   ├── twilio_service.py
│   │   └── call_handler.py
│   └── insurance/
│       ├── rules_engine.py
│       ├── query_service.py
│       └── conversation_agent.py
├── tests/
│   ├── test_insurance_rules.py
│   └── test_voice_services.py
├── scripts/
│   ├── run_dev.sh
│   ├── seed_data.py
│   └── test.sh
├── examples/
│   └── demo_conversation.py
├── static/
│   └── index.html
├── config/
├── logs/
├── temp_audio/
├── requirements.txt
├── pyproject.toml
├── .env.example
└── .gitignore
```

## File Roles

- **src/main.py** – app creation and startup/shutdown hooks
- **src/api/routes.py** – HTTP routes
- **src/voice/\*** – speech and telephony services
- **src/insurance/\*** – rules, query logic, conversation agent
- **src/database/connection.py** – SQLAlchemy engine/session
- **src/models/database_models.py** – DB schema
- **scripts/seed_data.py** – sample data bootstrap
- **scripts/run_dev.sh** – dependency install, env check, start server
- **scripts/test.sh** – test runner
- **static/index.html** – demo UI mounted at `/ui`

## Runtime Notes

- App listens at `http://localhost:8000` (configurable via `API_HOST`/`API_PORT`).
- API routes are mounted at `/api/v1`.
- Root endpoints:
  - `GET /`
  - `GET /health`
  - `GET /ui`

