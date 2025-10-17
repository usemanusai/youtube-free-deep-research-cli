# Troubleshooting Guide

Common issues and solutions for YouTube Free Deep Research CLI.

## Installation Issues

### Python Version Error

**Error**: `Python 3.13+ required`

**Solution**:
```bash
# Check version
python --version

# Use python3.13 if available
python3.13 -m venv venv

# Or install Python 3.13
# Windows: Download from python.org
# macOS: brew install python@3.13
# Linux: sudo apt-get install python3.13
```

### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'youtube_chat_cli_main'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt -r youtube_chat_cli_main/api_requirements.txt

# Or use development install
pip install -e .
```

### Virtual Environment Issues

**Error**: `Command not found: youtube-chat`

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall package
pip install -e .
```

## Configuration Issues

### Missing Environment Variables

**Error**: `KeyError: 'OPENROUTER_API_KEYS'`

**Solution**:
```bash
# Create .env file
cp .env.template .env

# Edit .env and add required variables
# Check which variables are required
python -c "from youtube_chat_cli_main.core.config import Config; Config.validate()"
```

### Invalid Configuration

**Error**: `ValueError: Invalid configuration`

**Solution**:
```bash
# Validate configuration
python -m youtube_chat_cli_main.core.config --validate

# Show current configuration
python -m youtube_chat_cli_main.core.config --show

# Reset to defaults
youtube-chat config reset
```

## API Server Issues

### Port Already in Use

**Error**: `Address already in use: ('0.0.0.0', 8556)`

**Solution**:
```bash
# Use different port
uvicorn youtube_chat_cli_main.api_server:app --port 8557

# Or kill process using port
# Linux/macOS
lsof -i :8556
kill -9 <PID>

# Windows
netstat -ano | findstr :8556
taskkill /PID <PID> /F
```

### Connection Refused

**Error**: `Connection refused`

**Solution**:
```bash
# Check if server is running
curl http://localhost:8556/health/live

# Start server
uvicorn youtube_chat_cli_main.api_server:app --reload

# Check firewall
# Windows: Check Windows Defender Firewall
# Linux: sudo ufw allow 8556
```

### Timeout Error

**Error**: `TimeoutError: Request timed out`

**Solution**:
```bash
# Increase timeout
export LLM_TIMEOUT=60

# Check server logs
docker logs jaegis-api

# Check network connectivity
ping 8.8.8.8
```

## LLM Service Issues

### API Key Error

**Error**: `Invalid API key`

**Solution**:
```bash
# Verify API keys
echo $OPENROUTER_API_KEYS

# Test key manually
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openrouter/auto", "messages": [{"role": "user", "content": "test"}]}'

# Check key status
youtube-chat llm key-status
```

### Rate Limit Error

**Error**: `HTTP 429: Too Many Requests`

**Solution**:
```bash
# Check key rotation
youtube-chat llm key-status

# Wait for rate limit to reset (usually 1 hour)

# Add more API keys
export OPENROUTER_API_KEYS="key1,key2,...,key31"

# Use different model
youtube-chat llm generate "test" --model openrouter/gpt-3.5-turbo
```

### Connection Error

**Error**: `Connection error: Failed to connect to OpenRouter`

**Solution**:
```bash
# Check internet connection
ping 8.8.8.8

# Check OpenRouter status
curl https://openrouter.ai/api/v1/models

# Increase timeout
export LLM_TIMEOUT=60

# Check firewall
# Ensure port 443 is open
```

## TTS Service Issues

### MeloTTS Not Working

**Error**: `ModuleNotFoundError: No module named 'melo'`

**Solution**:
```bash
# Install MeloTTS
pip install melo-tts

# Download models
python -c "from melo.api import TTS; TTS(language='EN')"

# Check Python 3.11 bridge
python -c "from melo.api import TTS; print('OK')"
```

### Edge TTS Connection Error

**Error**: `Connection error: Failed to connect to Edge TTS`

**Solution**:
```bash
# Check internet connection
ping 8.8.8.8

# Try different voice
youtube-chat tts synthesize "Hello" --voice en-US-GuyNeural

# Check Edge TTS service
curl https://edge.microsoft.com/
```

### pyttsx3 No Audio

**Error**: `No audio output from pyttsx3`

**Solution**:
```bash
# Linux: Install espeak
sudo apt-get install espeak

# macOS: Check NSSpeechSynthesizer
system_profiler SPAudioDataType

# Windows: Check SAPI5
# Ensure audio device is connected

# Test pyttsx3
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"
```

## RAG Engine Issues

### Vector Store Connection Error

**Error**: `Connection error: Failed to connect to Qdrant`

**Solution**:
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Start Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant

# Check configuration
echo $QDRANT_URL
echo $VECTOR_STORE_TYPE
```

### No Results Found

**Error**: `No documents found`

**Solution**:
```bash
# Check if documents are indexed
youtube-chat rag stats

# Re-index documents
youtube-chat rag clear
youtube-chat rag index /path/to/documents

# Check document format
# Supported: PDF, DOCX, TXT, MD, HTML, JSON
```

### Low Quality Results

**Error**: `Results are not relevant`

**Solution**:
```bash
# Adjust threshold
youtube-chat config set rag.threshold 0.5

# Increase top_k
youtube-chat config set rag.top_k 10

# Use different embeddings model
youtube-chat config set embeddings.model sentence-transformers/all-mpnet-base-v2

# Re-index documents
youtube-chat rag clear
youtube-chat rag index /path/to/documents
```

## Database Issues

### Database Connection Error

**Error**: `Connection error: Failed to connect to database`

**Solution**:
```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python -c "from youtube_chat_cli_main.core.database import Database; Database.test_connection()"

# Check if database is running
# PostgreSQL: psql -U user -d dbname
# SQLite: sqlite3 data.db

# Restart database
docker restart postgres
```

### Migration Error

**Error**: `Migration failed`

**Solution**:
```bash
# Check migration status
alembic current

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing Issues

### Tests Fail Locally

**Error**: `Tests fail locally but pass in CI`

**Solution**:
```bash
# Run in isolated environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
pytest

# Check environment variables
env | grep -E "(OPENROUTER|DATABASE|VECTOR)"

# Run with verbose output
pytest -v -s
```

### Flaky Tests

**Error**: `Tests pass sometimes, fail sometimes`

**Solution**:
```bash
# Run test multiple times
pytest --count=10 tests/unit/test_flaky.py

# Run with different random seed
pytest --randomly-seed=12345

# Check for timing issues
pytest --durations=10
```

## Performance Issues

### Slow Response

**Error**: `API response is slow`

**Solution**:
```bash
# Check server logs
docker logs -f jaegis-api

# Monitor resource usage
docker stats jaegis-api

# Increase workers
uvicorn youtube_chat_cli_main.api_server:app --workers 8

# Check database performance
# Add indexes if needed
```

### High Memory Usage

**Error**: `Out of memory`

**Solution**:
```bash
# Check memory usage
docker stats jaegis-api

# Reduce cache size
export CACHE_MAX_SIZE=100

# Reduce batch size
export BATCH_SIZE=10

# Restart service
docker restart jaegis-api
```

## Logging and Debugging

### Enable Debug Logging

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with verbose output
youtube-chat --verbose chat --message "test"

# View logs
docker logs -f jaegis-api
```

### Get Help

- Check [Documentation](../README.md)
- Review [Configuration](../getting-started/configuration.md)
- Open an issue on GitHub
- Ask in GitHub Discussions

---

**Still having issues?** Open an issue on GitHub with:
- Error message
- Steps to reproduce
- Environment details (OS, Python version, etc.)
- Relevant logs

