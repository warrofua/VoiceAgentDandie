# Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] Security audit completed
- [ ] HIPAA compliance review completed
- [ ] BAA signed with all third-party vendors (OpenAI, Twilio)
- [ ] Encryption keys generated and secured
- [ ] SSL certificates obtained
- [ ] Environment variables configured
- [ ] Database backup strategy implemented
- [ ] Monitoring and alerting configured

### Infrastructure Setup

#### Option 1: AWS Deployment

**Services Required:**
- EC2 or ECS for application hosting
- RDS PostgreSQL for database
- ElastiCache Redis for caching
- S3 for audio file storage (encrypted)
- CloudWatch for monitoring
- AWS WAF for security

**Steps:**

```bash
# 1. Create RDS PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier aba-voice-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --master-username admin \
    --master-user-password <secure-password> \
    --allocated-storage 100 \
    --storage-encrypted

# 2. Create ElastiCache Redis cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id aba-voice-cache \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1

# 3. Deploy application to ECS or EC2
# (Use Docker container or direct deployment)
```

#### Option 2: Azure Deployment

**Services Required:**
- Azure App Service or AKS
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Storage (encrypted)
- Azure Monitor

#### Option 3: Google Cloud Platform

**Services Required:**
- Cloud Run or GKE
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Storage
- Cloud Monitoring

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create directories
RUN mkdir -p temp_audio logs

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/aba_voice
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      - db
      - redis
    volumes:
      - ./temp_audio:/app/temp_audio

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=aba_voice
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Deploy with Docker:

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f app

# Run migrations
docker-compose exec app python scripts/seed_data.py
```

### Environment Configuration

Production `.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-prod-...

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Database (use connection pooling)
DATABASE_URL=postgresql://user:password@prod-db.example.com:5432/aba_voice?pool_size=20&max_overflow=40
REDIS_URL=redis://prod-redis.example.com:6379/0

# Security
SECRET_KEY=<64-char-random-string>
ENCRYPTION_KEY=<32-char-random-string>

# Production settings
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_AUDIT_LOG=true

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Security Hardening

1. **Encryption Keys**

```bash
# Generate strong keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Database Encryption**

Enable encryption at rest in your database:

```sql
-- PostgreSQL: Use encrypted tablespaces
CREATE TABLESPACE encrypted_space
  LOCATION '/path/to/encrypted/storage'
  ENCRYPTION='AES256';
```

3. **Network Security**

- Use VPC/Private networks
- Configure security groups to allow only necessary traffic
- Enable SSL/TLS for all connections
- Use AWS WAF or equivalent for DDoS protection

4. **Application Security**

```python
# Add to main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

### SSL/TLS Configuration

Using Let's Encrypt with Nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoring & Logging

1. **Application Monitoring**

```python
# Add to main.py
from prometheus_client import Counter, Histogram
import time

call_counter = Counter('calls_total', 'Total calls processed')
call_duration = Histogram('call_duration_seconds', 'Call duration')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    call_duration.observe(duration)
    call_counter.inc()

    return response
```

2. **Log Aggregation**

Use CloudWatch, Datadog, or ELK stack:

```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Database Migrations

Using Alembic:

```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Backup Strategy

```bash
# Automated PostgreSQL backup
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | \
    gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz \
    s3://your-backup-bucket/postgres/

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

### Health Checks

```python
# Add to routes.py
@router.get("/health/live")
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe."""
    try:
        # Check database
        db.execute("SELECT 1")

        # Check Redis
        # redis_client.ping()

        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Not ready")
```

### Twilio Production Configuration

1. **Buy Production Phone Number**
2. **Configure Webhooks**:
   - Voice URL: `https://api.yourdomain.com/api/v1/voice/incoming`
   - Status Callback: `https://api.yourdomain.com/api/v1/voice/status`
3. **Enable Geographic Permissions**
4. **Set up Call Recording** (with consent)

### Performance Optimization

1. **Database Connection Pooling**

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

2. **Redis Caching**

```python
import redis
from functools import wraps

redis_client = redis.from_url(settings.redis_url)

def cache_result(expire=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)

            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire, json.dumps(result))

            return result
        return wrapper
    return decorator
```

3. **Load Balancing**

Use multiple application instances behind a load balancer.

### Post-Deployment

- [ ] Verify all endpoints are accessible
- [ ] Test call flow end-to-end
- [ ] Monitor error rates and latency
- [ ] Review audit logs
- [ ] Set up alerts for critical failures
- [ ] Document runbook for common issues
- [ ] Train support team

### Scaling Considerations

- Horizontal scaling: Add more application instances
- Database read replicas for query load
- CDN for static assets
- Queue system (Celery/RabbitMQ) for async tasks
- WebSocket server for real-time features

### Cost Optimization

- Use reserved instances for predictable workload
- Auto-scaling for variable load
- Monitor API usage to optimize calls
- Archive old call data to cheaper storage
- Use spot instances for non-critical workloads
