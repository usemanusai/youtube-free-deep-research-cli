# Configuration Guide

Complete configuration instructions for YouTube Free Deep Research CLI.

## Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.template .env
```

### API Configuration

```bash
# API Server
API_HOST=0.0.0.0
API_PORT=8556
API_WORKERS=4
API_RELOAD=true  # Development only

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### LLM Configuration

```bash
# OpenRouter API Keys (31 keys for rotation)
OPENROUTER_API_KEYS=key1,key2,key3,...,key31

# Default Model
DEFAULT_LLM_MODEL=openrouter/auto

# LLM Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_TIMEOUT=30
```

### Database Configuration

```bash
# SQLite Database
DATABASE_URL=sqlite:///./data.db

# Or PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

### RAG Configuration

```bash
# Vector Store
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key

# Or Chroma
# VECTOR_STORE_TYPE=chroma
# CHROMA_PERSIST_DIR=./chroma_data

# Embeddings
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### TTS Configuration

```bash
# Default TTS Engine
DEFAULT_TTS_ENGINE=edge-tts
DEFAULT_TTS_VOICE=en-US-AriaNeural

# TTS Settings
TTS_SAMPLE_RATE=22050
TTS_TIMEOUT=30
```

### Search Configuration

```bash
# Web Search
TAVILY_API_KEY=your_tavily_key
BRAVE_SEARCH_API_KEY=your_brave_key

# Search Settings
SEARCH_TIMEOUT=10
SEARCH_MAX_RESULTS=10
```

### Google Drive Configuration

```bash
# Google Drive OAuth
GOOGLE_DRIVE_CREDENTIALS_FILE=client_secret.json
GOOGLE_DRIVE_TOKEN_FILE=token.pickle

# Google Drive Settings
GOOGLE_DRIVE_TIMEOUT=30
```

### N8N Integration

```bash
# N8N Webhook
N8N_WEBHOOK_URL=http://localhost:5678/webhook/your-webhook-id
N8N_API_KEY=your_n8n_api_key

# N8N Settings
N8N_TIMEOUT=30
N8N_RETRY_COUNT=3
```

### Background Jobs

```bash
# APScheduler
SCHEDULER_TIMEZONE=UTC
SCHEDULER_POOL_SIZE=10

# Job Settings
JOB_TIMEOUT=3600
JOB_MAX_RETRIES=3
```

## Configuration Files

### .env.template

Template file with all available configuration options:

```bash
# Copy to .env and fill in your values
cp .env.template .env
```

### config/default_config.yaml

Default configuration in YAML format:

```yaml
api:
  host: 0.0.0.0
  port: 8556
  workers: 4

llm:
  model: openrouter/auto
  temperature: 0.7
  max_tokens: 2048

rag:
  vector_store: qdrant
  embeddings_model: sentence-transformers/all-MiniLM-L6-v2

tts:
  engine: edge-tts
  voice: en-US-AriaNeural
```

## Environment-Specific Configuration

### Development

```bash
# .env.development
API_RELOAD=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./dev.db
```

### Production

```bash
# .env.production
API_RELOAD=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@prod-db/dbname
API_WORKERS=8
```

### Testing

```bash
# .env.test
DATABASE_URL=sqlite:///:memory:
LOG_LEVEL=WARNING
OPENROUTER_API_KEYS=test-key
```

## Configuration Validation

```bash
# Validate configuration
python -c "from youtube_chat_cli_main.core.config import Config; Config.validate()"

# Check configuration
python -c "from youtube_chat_cli_main.core.config import Config; print(Config.get_all())"
```

## Secrets Management

### Using Environment Variables

```bash
# Set in shell
export OPENROUTER_API_KEYS="key1,key2,key3"

# Or in .env file
OPENROUTER_API_KEYS=key1,key2,key3
```

### Using Secrets Manager

```bash
# AWS Secrets Manager
export OPENROUTER_API_KEYS=$(aws secretsmanager get-secret-value --secret-id openrouter-keys --query SecretString --output text)

# HashiCorp Vault
export OPENROUTER_API_KEYS=$(vault kv get -field=keys secret/openrouter)
```

## Docker Configuration

### Environment File

```bash
# Create .env.docker
API_HOST=0.0.0.0
API_PORT=8556
DATABASE_URL=postgresql://user:password@db:5432/dbname

# Run with environment file
docker run --rm -p 8556:8556 --env-file .env.docker jaegis-api
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    image: jaegis-api
    ports:
      - "8556:8556"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8556
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
```

## Troubleshooting Configuration

### Missing Environment Variables

```bash
# Check if .env file exists
ls -la .env

# Check if variables are loaded
python -c "import os; print(os.getenv('OPENROUTER_API_KEYS'))"
```

### Invalid Configuration

```bash
# Validate configuration
python -m youtube_chat_cli_main.core.config --validate

# Show current configuration
python -m youtube_chat_cli_main.core.config --show
```

## Next Steps

1. **Quick Start** - See [Quick Start Guide](quick-start.md)
2. **CLI Usage** - See [CLI Usage Guide](../guides/cli-usage.md)
3. **API Reference** - See [REST API](../api/rest-api.md)

---

**Configuration complete?** Continue with [Quick Start Guide](quick-start.md).

