# Quick Start Guide

## 1) Get the app running

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

make install
cp .env.example .env
```

Edit `.env` with your API keys:

- `OPENAI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `ENCRYPTION_KEY`

## 2) Create and seed the database

```bash
createdb aba_voice_agent
python scripts/seed_data.py
```

## 3) Start development server

```bash
make dev
```

The app should be reachable at:

- `http://localhost:8000`
- `http://localhost:8000/health`
- `http://localhost:8000/docs`
- `http://localhost:8000/ui`

## 4) Verify endpoints

```bash
curl http://localhost:8000/health

curl http://localhost:8000/api/v1/calls/1/transcript

curl -X POST "http://localhost:8000/api/v1/outbound/call" \
  --data "phone_number=+15555550123&message=Hello%20from%20ABA%20voice%20agent"
```

Note: `POST /api/v1/outbound/call` accepts query/form fields.

## 5) Configure Twilio for local testing

```bash
ngrok http 8000
```

Set these webhook URLs in Twilio:

- `https://<your-ngrok-host>/api/v1/voice/incoming`
- `https://<your-ngrok-host>/api/v1/voice/status`

## Troubleshooting

- Missing env vars:
  - `cat .env` and confirm required variables exist.
- PostgreSQL errors:
  - `pg_isready`
  - Restart PostgreSQL service if needed.
- App startup issues:
  - Ensure `venv` is active and all dependencies installed.

## Useful Make Targets

- `make install` – install dependencies
- `make setup` – installs deps, creates `.env`, creates runtime dirs
- `make check-env` – validates `.env` exists and OPENAI key is set
- `make seed` – seed sample data
- `make dev` – run the API
- `make test` – run tests
- `make lint` / `make format` – quality checks
- `make clean` – remove build artifacts and temp files
- `make docs` – open documentation

