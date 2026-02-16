# Get Started with ABA Voice Agent

Welcome. This repository is a runnable FastAPI voice workflow for ABA insurance calls.

## What you have in this repo

- Real-time call handling routes for Twilio webhooks
- OpenAI Whisper + TTS integration
- Insurance rules and query services
- Test/demo utilities
- PostgreSQL-backed schema with call transcripts and audit tables

## First-time setup

```bash
make setup
make seed
make dev
```

Open the app:

- `http://localhost:8000/docs` (API docs)
- `http://localhost:8000/ui` (demo UI)

## Where to read what

- `README.md` – single source for current setup + endpoints
- `QUICKSTART.md` – shortest path to running locally
- `STRUCTURE.md` – file-level map
- `PROJECT_SUMMARY.md` – implementation overview
- `docs/ARCHITECTURE.md` – architecture details
- `docs/DEPLOYMENT.md` – deployment recommendations

## Current project shape (accurate to code)

- API routes are under `/api/v1` except root `/`, `/health`, and `/ui`.
- Outbound call endpoint is `POST /api/v1/outbound/call`.
- Database tables are created automatically at startup.
- Conversation state is currently kept in process memory in `active_conversations`.

## Quick checks before testing

```bash
make check-env
python scripts/seed_data.py
curl http://localhost:8000/health
```

## Helpful commands

```bash
make test     # run pytest with coverage
make lint     # run flake8 + mypy
make format   # run black
make clean    # remove temp files and caches
```

## Next steps

1. Configure real Twilio webhooks and phone numbers.
2. Replace sample prompts/models with your production-ready conversation logic.
3. Add authentication/rate limiting for production exposure.
4. Review `docs/DEPLOYMENT.md` for production checklist.

