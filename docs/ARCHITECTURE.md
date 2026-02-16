# System Architecture

## Overview

The ABA Voice Agent is a conversational AI system that handles phone-based insurance inquiries for ABA therapy services using speech recognition, natural language processing, and text-to-speech technologies.

Current implementation notes:

- API routes are mounted at `/api/v1` plus root routes `/`, `/health`, and `/ui`.
- Conversation state is currently stored in-memory in `active_conversations` (not Redis-backed yet).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Caller                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Phone Call
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Twilio Voice API                          │
│  - Phone number routing                                      │
│  - Call management                                           │
│  - Audio streaming                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                        │
│                                                              │
│  ┌───────────────────────────────────────────────────┐      │
│  │           Call Handler Layer                      │      │
│  │  - Route incoming/outbound calls                  │      │
│  │  - Manage conversation state                      │      │
│  │  - Coordinate services                            │      │
│  └──────┬────────────────────────────────────────┬───┘      │
│         │                                        │          │
│         ▼                                        ▼          │
│  ┌─────────────┐                         ┌─────────────┐   │
│  │   Whisper   │                         │  OpenAI TTS │   │
│  │   Service   │                         │   Service   │   │
│  │  (STT)      │                         │  (Speech)   │   │
│  └──────┬──────┘                         └──────┬──────┘   │
│         │                                        │          │
│         └──────────────┬───────────────────────┘          │
│                        ▼                                   │
│              ┌──────────────────┐                         │
│              │ Conversation     │                         │
│              │ Agent (GPT-4)    │                         │
│              │ - Intent detect  │                         │
│              │ - NLU            │                         │
│              │ - Response gen   │                         │
│              └────────┬─────────┘                         │
│                       │                                    │
│                       ▼                                    │
│              ┌──────────────────┐                         │
│              │ Insurance Query  │                         │
│              │ Service          │                         │
│              │ - Eligibility    │                         │
│              │ - Authorization  │                         │
│              │ - Benefits       │                         │
│              └────────┬─────────┘                         │
│                       │                                    │
│                       ▼                                    │
│              ┌──────────────────┐                         │
│              │ Rules Engine     │                         │
│              │ - CPT validation │                         │
│              │ - Coverage rules │                         │
│              │ - Carrier logic  │                         │
│              └────────┬─────────┘                         │
│                       │                                    │
└───────────────────────┼────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │      Data Layer              │
         │                              │
         │  ┌─────────┐  ┌──────────┐  │
         │  │PostgreSQL│  │  Redis   │  │
         │  │  - Calls │  │ - Cache  │  │
         │  │  - Auth  │  │ - Session│  │
         │  │  - Rules │  │          │  │
         │  └─────────┘  └──────────┘  │
         └──────────────────────────────┘
```

## Component Details

### 1. Voice Processing Layer

#### Whisper Service (`src/voice/whisper_service.py`)
- **Purpose**: Convert speech to text
- **Technology**: OpenAI Whisper API
- **Functions**:
  - Transcribe audio files
  - Process audio streams
  - Return confidence scores
- **Latency**: ~500ms per request

#### TTS Service (`src/voice/tts_service.py`)
- **Purpose**: Convert text to natural speech
- **Technology**: OpenAI TTS API
- **Functions**:
  - Generate speech from text
  - Support multiple voices
  - Stream audio responses
- **Latency**: ~400ms per request

#### Twilio Service (`src/voice/twilio_service.py`)
- **Purpose**: Manage phone calls
- **Technology**: Twilio Voice API
- **Functions**:
  - Handle inbound calls
  - Make outbound calls
  - Generate TwiML responses
  - Manage call state

### 2. AI/NLP Layer

#### Conversation Agent (`src/insurance/conversation_agent.py`)
- **Purpose**: Orchestrate intelligent conversations
- **Technology**: GPT-4 Turbo
- **Functions**:
  - Detect caller intent
  - Extract entities (member ID, DOB, etc.)
  - Generate contextual responses
  - Maintain conversation state
  - Handle transfer requests

**Intent Types**:
- `eligibility_check` - Verify insurance coverage
- `authorization_status` - Check authorization details
- `benefits_inquiry` - Get coverage information
- `prior_auth_submission` - Submit new authorization
- `general_question` - Answer ABA therapy questions
- `transfer_request` - Escalate to human

### 3. Business Logic Layer

#### Insurance Query Service (`src/insurance/query_service.py`)
- **Purpose**: Handle insurance-specific queries
- **Functions**:
  - Verify patient eligibility
  - Check authorization status
  - Retrieve benefits information
  - Submit prior authorizations
  - Log all queries for audit

#### Rules Engine (`src/insurance/rules_engine.py`)
- **Purpose**: Enforce insurance rules and policies
- **Functions**:
  - Validate CPT codes (97151-97158)
  - Check diagnosis codes (F84.x)
  - Apply session limits
  - Verify provider credentials
  - Calculate reassessment dates
  - Carrier-specific rules

### 4. Data Layer

#### Database Models (`src/models/database_models.py`)

**Tables**:
- `calls` - Call records and metadata
- `transcripts` - Full conversation transcripts
- `patients` - Patient information (encrypted PHI)
- `authorizations` - ABA therapy authorizations
- `insurance_rules` - Carrier-specific rules
- `insurance_queries` - Query audit trail
- `audit_logs` - HIPAA compliance logging

#### Session Management
- In-memory conversation map for active sessions (`active_conversations`)
- Redis is defined in configuration and can be adopted as a production persistence layer
- 30-minute session timeout

### 5. API Layer

#### REST Endpoints (`src/api/routes.py`)

**Call Management**:
- `POST /voice/incoming` - Handle incoming calls
- `POST /voice/gather` - Process user input
- `POST /voice/status` - Call status updates
- `POST /outbound/call` - Initiate outbound call
- `GET /calls/{id}` - Get call details
- `GET /calls/{id}/transcript` - Get transcript

**Testing**:
- `POST /test/speech-to-text` - Test Whisper
- `POST /test/text-to-speech` - Test TTS

**Health**:
- `GET /health` - Health check
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe

## Data Flow

### Inbound Call Flow

```
1. Caller dials Twilio number
   │
   ▼
2. Twilio sends webhook to /voice/incoming
   │
   ▼
3. Create Call record in database
   │
   ▼
4. Initialize Conversation Agent
   │
   ▼
5. Return TwiML to start audio stream
   │
   ▼
6. Caller speaks → Whisper API → Text
   │
   ▼
7. Text → GPT-4 → Intent + Response
   │
   ▼
8. Check if query needed → Insurance Service
   │
   ▼
9. Apply rules → Rules Engine
   │
   ▼
10. Generate response → TTS → Audio
    │
    ▼
11. Play audio to caller
    │
    ▼
12. Save transcript to database
    │
    ▼
13. Repeat steps 6-12 until call ends
    │
    ▼
14. Call status webhook → Update Call record
```

### Authorization Check Flow

```
Caller: "Check authorization for member ID BCBS123456"
   │
   ▼
Intent Detection (GPT-4)
   │
   ├─ Intent: authorization_status
   ├─ Entity: member_id = "BCBS123456"
   └─ Requires: date_of_birth for verification
   │
   ▼
Agent: "May I have the date of birth to verify?"
   │
   ▼
Caller: "March 15, 2018"
   │
   ▼
Insurance Query Service
   │
   ├─ verify_eligibility(member_id, dob)
   │   └─ Query Patient table
   │       └─ Match found: patient_id=1
   │
   ├─ check_authorization_status(patient_id=1)
   │   └─ Query Authorization table
   │       └─ Find active authorization
   │
   └─ Apply Rules Engine checks
       ├─ Check expiration date
       ├─ Check reassessment due
       └─ Return status
   │
   ▼
Response Generation (GPT-4)
   │
   └─ Natural language summary of authorization
   │
   ▼
TTS → Audio → Play to caller
```

## Security Architecture

### HIPAA Compliance

**Data Protection**:
```
┌─────────────────────────────────────────┐
│   Sensitive Data (PHI)                  │
│                                         │
│   Encrypted at Rest:                   │
│   - Patient names                      │
│   - Date of birth                      │
│   - Member IDs                         │
│   - Call recordings (if enabled)       │
│                                         │
│   Using: AES-256 encryption            │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Encrypted in Transit                  │
│   - TLS 1.2+ for all connections       │
│   - HTTPS only                         │
│   - Encrypted WebSocket streams        │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Audit Logging                         │
│   - All PHI access logged              │
│   - User actions tracked               │
│   - Query history maintained           │
│   - Immutable audit trail              │
└─────────────────────────────────────────┘
```

### Authentication & Authorization (Planned)

```
Request → API application
   │
   ▼
Process Request
   │
   ▼
Log to Audit Trail
```

## Performance Considerations

### Latency Targets

| Component | Target | Typical |
|-----------|--------|---------|
| Whisper API | <1s | 500ms |
| GPT-4 Processing | <1.5s | 800ms |
| TTS Generation | <500ms | 400ms |
| Database Query | <100ms | 50ms |
| **Total Response** | **<2s** | **1.75s** |

### Optimization Strategies

1. **Caching**:
   - Redis cache for frequently accessed rules
   - Session state in memory
   - Pre-generated common responses

2. **Connection Pooling**:
   - Database connection pool (20 connections)
   - Redis connection pool
   - HTTP client connection reuse

3. **Async Processing**:
   - Parallel API calls where possible
   - Non-blocking I/O for all external calls
   - Background tasks for logging

4. **Audio Processing**:
   - Stream audio chunks (don't wait for full recording)
   - Use WebSocket for real-time streaming
   - Optimize audio format (MP3 vs WAV)

## Scalability

### Horizontal Scaling

```
         Load Balancer
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
  App-1    App-2    App-3
    │         │         │
    └─────────┼─────────┘
              │
         ┌────┴────┐
         ▼         ▼
    Database    Redis
   (Primary)   (Cluster)
         │
         ▼
    Read Replicas
```

### Capacity Planning

**Per Instance** (4 CPU, 8GB RAM):
- Concurrent calls: ~50
- API requests/sec: ~100
- Database connections: 20

**For 1000 concurrent calls**:
- App instances: 20
- Database: Primary + 3 read replicas
- Redis: 3-node cluster
- Estimated cost: ~$5000/month

## Monitoring & Observability

### Metrics Tracked

**System Metrics**:
- CPU/Memory usage
- Request latency (p50, p95, p99)
- Error rates
- Database connection pool

**Business Metrics**:
- Total calls processed
- Average call duration
- Intent distribution
- Authorization approval rate
- Transfer to human rate

**Voice Metrics**:
- Transcription accuracy
- TTS quality scores
- Audio latency
- Caller satisfaction

### Alerting

**Critical Alerts**:
- Error rate >5%
- Latency >3 seconds
- Database connection failures
- API quota exceeded

**Warning Alerts**:
- Error rate >2%
- High memory usage (>80%)
- Slow queries (>1 second)

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API Framework | FastAPI | REST endpoints |
| Language | Python 3.11+ | Application code |
| Database | PostgreSQL 14+ | Persistent storage |
| Cache | Redis 6+ | Session/caching |
| Speech-to-Text | Whisper API | Transcription |
| Text-to-Speech | OpenAI TTS | Voice synthesis |
| NLP | GPT-4 Turbo | Conversation AI |
| Phone | Twilio | Call infrastructure |
| ORM | SQLAlchemy | Database access |
| Testing | Pytest | Unit/integration tests |

## Future Enhancements

1. **Real-time Streaming**: WebSocket-based bidirectional audio
2. **Multi-language**: Spanish, French, Mandarin support
3. **Voice Biometrics**: Caller identification via voice
4. **Sentiment Analysis**: Detect caller frustration
5. **Predictive Analytics**: Anticipate caller needs
6. **Integration Hub**: Connect to carrier APIs directly
7. **Mobile App**: Provider companion app
8. **Dashboard**: Real-time analytics and monitoring
