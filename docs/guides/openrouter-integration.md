# OpenRouter Integration Guide

Complete guide to OpenRouter LLM integration with 31-key rotation.

## Overview

OpenRouter provides access to multiple LLM models through a single API. The system implements intelligent key rotation to handle rate limits.

## Setup

### 1. Get API Keys

Visit https://openrouter.ai/keys to create API keys.

### 2. Configure Keys

```bash
# Add to .env file
OPENROUTER_API_KEYS=key1,key2,key3,...,key31

# Or set environment variable
export OPENROUTER_API_KEYS="key1,key2,key3,...,key31"
```

### 3. Verify Configuration

```bash
python -c "from youtube_chat_cli_main.services.llm import OpenRouterLLM; print('OK')"
```

## Available Models

### Popular Models

```
openrouter/auto                    # Auto-select best model
openrouter/gpt-4-turbo            # GPT-4 Turbo
openrouter/gpt-4                  # GPT-4
openrouter/gpt-3.5-turbo          # GPT-3.5 Turbo
openrouter/claude-3-opus          # Claude 3 Opus
openrouter/claude-3-sonnet        # Claude 3 Sonnet
openrouter/claude-3-haiku         # Claude 3 Haiku
openrouter/llama-2-70b            # Llama 2 70B
openrouter/mistral-7b             # Mistral 7B
openrouter/mixtral-8x7b           # Mixtral 8x7B
```

## Configuration

### Environment Variables

```bash
# API Keys (31 keys for rotation)
OPENROUTER_API_KEYS=key1,key2,...,key31

# Default Model
DEFAULT_LLM_MODEL=openrouter/auto

# LLM Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_TIMEOUT=30

# Key Rotation
LLM_KEY_ROTATION_ENABLED=true
LLM_KEY_ROTATION_STRATEGY=round_robin
LLM_KEY_ROTATION_RETRY_COUNT=3
```

### Configuration File

```yaml
llm:
  provider: openrouter
  model: openrouter/auto
  temperature: 0.7
  max_tokens: 2048
  timeout: 30
  
  openrouter:
    api_keys:
      - key1
      - key2
      - key31
    
    rotation:
      enabled: true
      strategy: round_robin  # or: least_used, random
      retry_count: 3
      retry_delay: 1
      
    models:
      - openrouter/auto
      - openrouter/gpt-4-turbo
      - openrouter/claude-3-opus
```

## Key Rotation Strategies

### Round Robin

Cycles through keys sequentially:

```bash
export LLM_KEY_ROTATION_STRATEGY=round_robin
```

### Least Used

Uses key with fewest requests:

```bash
export LLM_KEY_ROTATION_STRATEGY=least_used
```

### Random

Randomly selects key:

```bash
export LLM_KEY_ROTATION_STRATEGY=random
```

## Usage

### Basic Usage

```python
from youtube_chat_cli_main.services.llm import OpenRouterLLM

llm = OpenRouterLLM()
response = llm.generate("What is machine learning?")
print(response)
```

### With Options

```python
response = llm.generate(
    prompt="What is machine learning?",
    model="openrouter/gpt-4-turbo",
    temperature=0.7,
    max_tokens=2048
)
```

### Streaming

```python
for chunk in llm.generate_stream("Your question"):
    print(chunk, end="", flush=True)
```

### With System Prompt

```python
response = llm.generate(
    prompt="What is machine learning?",
    system_prompt="You are an expert in AI",
    model="openrouter/claude-3-opus"
)
```

## CLI Usage

### Generate Text

```bash
youtube-chat llm generate "What is machine learning?"
```

### Generate with Model

```bash
youtube-chat llm generate "What is machine learning?" --model openrouter/gpt-4-turbo
```

### Generate with Temperature

```bash
youtube-chat llm generate "What is machine learning?" --temperature 0.5
```

### List Available Models

```bash
youtube-chat llm models
```

## Error Handling

### Rate Limit (HTTP 429)

Automatically handled by key rotation:

```python
# Automatic retry with next key
response = llm.generate("Your question")
```

### Connection Error

```python
try:
    response = llm.generate("Your question")
except ConnectionError as e:
    print(f"Connection error: {e}")
```

### Invalid API Key

```python
try:
    response = llm.generate("Your question")
except ValueError as e:
    print(f"Invalid API key: {e}")
```

## Monitoring

### Key Usage Statistics

```python
stats = llm.get_key_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Requests per key: {stats['requests_per_key']}")
print(f"Failed requests: {stats['failed_requests']}")
```

### Key Health

```python
health = llm.get_key_health()
for key_id, status in health.items():
    print(f"Key {key_id}: {status}")
```

## Advanced Configuration

### Custom Retry Logic

```python
llm = OpenRouterLLM(
    retry_count=5,
    retry_delay=2,
    backoff_factor=1.5
)
```

### Custom Model Selection

```python
llm = OpenRouterLLM(
    model_selection_strategy="quality"  # or: speed, cost
)
```

### Request Timeout

```python
llm = OpenRouterLLM(
    timeout=60  # seconds
)
```

## Best Practices

1. **Use Multiple Keys** - Distribute load across 31 keys
2. **Monitor Usage** - Track key usage and health
3. **Set Appropriate Timeouts** - Avoid hanging requests
4. **Use Streaming** - For long responses
5. **Cache Results** - Avoid duplicate requests
6. **Test Fallback** - Ensure fallback models work

## Troubleshooting

### All Keys Rate Limited

```bash
# Wait for rate limit to reset (usually 1 hour)
# Or add more API keys

# Check key status
youtube-chat llm key-status
```

### Invalid API Key Error

```bash
# Verify keys in .env
cat .env | grep OPENROUTER_API_KEYS

# Test key manually
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openrouter/auto", "messages": [{"role": "user", "content": "test"}]}'
```

### Slow Response

```bash
# Check key health
youtube-chat llm key-status

# Try different model
youtube-chat llm generate "Your question" --model openrouter/gpt-3.5-turbo

# Increase timeout
export LLM_TIMEOUT=60
```

### Connection Timeout

```bash
# Check internet connection
ping 8.8.8.8

# Check OpenRouter status
curl https://openrouter.ai/api/v1/models

# Increase timeout
export LLM_TIMEOUT=60
```

## Performance Tips

1. **Use Auto Model** - Automatically selects best model
2. **Enable Streaming** - For faster response times
3. **Batch Requests** - Process multiple requests together
4. **Monitor Keys** - Track key health and usage
5. **Use Caching** - Avoid duplicate requests

---

See [System Overview](../architecture/overview.md) for architecture details.

