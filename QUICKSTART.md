# Quick Start Guide

Get your ABA Voice Agent up and running in 10 minutes!

## Prerequisites

Before you begin, make sure you have:

- ✅ Python 3.11+ installed
- ✅ PostgreSQL 14+ running
- ✅ Redis 6+ running (optional for local dev)
- ✅ OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- ✅ Twilio account ([sign up here](https://www.twilio.com/try-twilio))

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

**Minimum required variables:**

```bash
OPENAI_API_KEY=sk-your-key-here
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
DATABASE_URL=postgresql://user:pass@localhost:5432/aba_voice_agent
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

## Step 3: Setup Database

```bash
# Create database
createdb aba_voice_agent

# Or using psql
psql -U postgres -c "CREATE DATABASE aba_voice_agent;"

# Seed with sample data
python scripts/seed_data.py
```

You should see:

```
Seeding insurance rules...
Added 7 insurance rules
Seeding sample patients...
Added 3 sample patients
Seeding sample authorizations...
Added 3 sample authorizations

✅ Database seeding completed successfully!
```

## Step 4: Start the Server

```bash
# Using the dev script
./scripts/run_dev.sh

# Or manually
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 5: Test the API

Open your browser and visit:

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use curl:

```bash
# Health check
curl http://localhost:8000/health

# Get call details (using sample data)
curl http://localhost:8000/api/v1/calls/1
```

## Step 6: Configure Twilio for Local Testing

For local development, use ngrok to expose your local server:

```bash
# Install ngrok (if not already installed)
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start ngrok
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) and configure in Twilio:

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to Phone Numbers → Your phone number
3. Under "Voice Configuration":
   - **A CALL COMES IN**: `https://abc123.ngrok.io/api/v1/voice/incoming`
   - **STATUS CALLBACK**: `https://abc123.ngrok.io/api/v1/voice/status`
4. Save

## Step 7: Test a Live Call

Call your Twilio phone number! You should hear:

> "Hello, thank you for calling ABA Therapy Insurance Services. I'm here to help you with insurance verification, authorizations, and benefit inquiries. How may I assist you today?"

## Testing Without a Phone Call

You can test individual components:

### Test Speech-to-Text

```bash
curl -X POST http://localhost:8000/api/v1/test/speech-to-text \
  -H "Content-Type: audio/wav" \
  --data-binary @sample_audio.wav
```

### Test Text-to-Speech

```bash
curl -X POST "http://localhost:8000/api/v1/test/text-to-speech?text=Hello%20world"
```

### Test Insurance Query

```python
import requests

# Verify eligibility
response = requests.post(
    "http://localhost:8000/api/v1/insurance/verify",
    json={
        "member_id": "BCBS123456",
        "date_of_birth": "2018-03-15"
    }
)
print(response.json())
```

## Sample Data Available

After seeding, you have access to:

### Sample Patients

| Member ID | Name | Carrier | Status |
|-----------|------|---------|--------|
| BCBS123456 | John Doe | Blue Cross Blue Shield | Active auth |
| AETNA789012 | Jane Smith | Aetna | Expiring soon |
| UHC345678 | Michael Johnson | UnitedHealthcare | Pending |

### Sample Authorizations

- **AUTH-2024-001234**: Active, 120 days remaining
- **AUTH-2024-005678**: Expiring in 20 days
- **AUTH-2024-009012**: Pending approval

## Common Issues & Solutions

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# If not running (macOS)
brew services start postgresql

# If not running (Linux)
sudo systemctl start postgresql
```

### Import Errors

```bash
# Make sure you're in the virtual environment
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Twilio Webhook Not Working

```bash
# Check ngrok is running
curl http://localhost:4040/api/tunnels

# Verify webhook URL in Twilio console
# Check server logs for incoming requests
```

### OpenAI API Errors

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API access
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Next Steps

Now that your system is running:

1. **Customize Conversation Flow**: Edit `src/insurance/conversation_agent.py`
2. **Add Insurance Carriers**: Update `scripts/seed_data.py` with your carriers
3. **Configure Voice**: Change TTS voice in `.env` (alloy, echo, fable, onyx, nova, shimmer)
4. **Add Custom Rules**: Create new insurance rules in the database
5. **Build Tests**: Add tests in `tests/` directory

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
./scripts/test.sh

# Run specific test
pytest tests/test_insurance_rules.py -v
```

## Development Workflow

```bash
# 1. Create a new branch
git checkout -b feature/new-feature

# 2. Make changes

# 3. Run tests
pytest

# 4. Format code
black src/

# 5. Commit changes
git add .
git commit -m "Add new feature"

# 6. Push and create PR
git push origin feature/new-feature
```

## Getting Help

- 📖 Full documentation: See `README.md`
- 🚀 Deployment guide: See `docs/DEPLOYMENT.md`
- 🐛 Found a bug? Open an issue
- 💡 Have questions? Check the docs or ask the team

## What's Next?

Explore these advanced features:

- **Real-time Streaming**: Implement WebSocket for live conversations
- **Analytics Dashboard**: Build call analytics and reporting
- **Multi-language Support**: Add Spanish, French, etc.
- **Insurance API Integration**: Connect to real insurance carrier APIs
- **Provider Portal**: Create web interface for providers

Happy coding! 🎉
