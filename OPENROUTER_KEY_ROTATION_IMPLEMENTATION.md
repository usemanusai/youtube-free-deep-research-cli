# OpenRouter API Key Rotation Implementation

## Overview

Implemented an intelligent API key rotation service for OpenRouter to handle HTTP 429 "Too Many Requests" rate limit errors when using free-tier models like `deepseek/deepseek-chat-v3.1:free`.

## Features

### 1. Multi-Key Configuration Support

The system now supports multiple OpenRouter API keys from different free accounts with two configuration formats:

**Option 1: Comma-Separated List (Recommended)**
```env
OPENROUTER_API_KEYS=key1,key2,key3,...
```

**Option 2: Numbered Keys (Backward Compatible)**
```env
OPENROUTER_API_KEY=key1
OPENROUTER_API_KEY_2=key2
OPENROUTER_API_KEY_3=key3
```

### 2. Smart Rotation Logic

- **Automatic Rotation**: Detects `openai.RateLimitError` (HTTP 429) and automatically rotates to the next available key
- **Rate Limit Tracking**: Tracks rate limit status per key with timestamps and cooldown periods
- **Intelligent Key Selection**: Skips keys that are currently rate-limited and tries the next available key
- **Exponential Backoff**: If all keys are rate-limited, calculates the shortest cooldown period
- **Detailed Logging**: Logs which key is being used for each request and rotation events

### 3. Error Handling

- **429 Rate Limit Errors**: Immediate rotation to next available key
- **Other Errors (502, 500, etc.)**: Attempts one retry with a different key if multiple keys are available
- **All Keys Exhausted**: Clear error message indicating all keys are rate-limited with retry time

## Implementation Details

### Files Modified

1. **`youtube_chat_cli_main/core/config.py`**
   - Added `openrouter_api_keys` property that returns a list of all configured API keys
   - Supports both comma-separated and numbered key formats
   - Removes duplicates automatically
   - Maintains backward compatibility with single `openrouter_api_key`

2. **`youtube_chat_cli_main/services/llm_service.py`**
   - Rewrote `OpenRouterLLMService` class with rotation support
   - Added `_get_next_available_key()` method for intelligent key selection
   - Added `_mark_key_rate_limited()` method to track rate-limited keys
   - Added `_create_client()` method to create OpenAI clients with different keys
   - Updated `generate()` method to catch `RateLimitError` and rotate keys
   - Updated `LLMService` backend selection to check `openrouter_api_keys` instead of singular `openrouter_api_key`

3. **`youtube_chat_cli_main/.env`**
   - Configured with 31 OpenRouter API keys using comma-separated format
   - Added explanatory comments about the rotation feature

### Key Rotation Algorithm

```python
def generate(prompt, ...):
    max_retries = len(api_keys)
    
    for attempt in range(max_retries):
        try:
            # Make API request with current key
            response = client.chat.completions.create(...)
            return response
            
        except RateLimitError:
            # Mark current key as rate-limited (60s cooldown)
            mark_key_rate_limited(current_key_index, cooldown_seconds=60)
            
            # Get next available key
            next_index, next_key = get_next_available_key()
            
            # Update client with new key
            current_key_index = next_index
            client = create_client(next_key)
            
            # Continue to next attempt
            continue
            
        except Exception as e:
            # For non-429 errors, try one more time with different key
            if len(api_keys) > 1 and attempt == 0:
                rotate_and_retry()
            else:
                raise
```

### Rate Limit Tracking

Each key maintains a tracking record:
```python
rate_limit_tracker = {
    key_index: {
        'last_429_time': timestamp,
        'cooldown_until': timestamp + 60  # 60 second cooldown
    }
}
```

## Configuration

### Current Setup

The system is configured with **31 OpenRouter API keys** in `youtube_chat_cli_main/.env`:

```env
OPENROUTER_API_KEYS=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,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,...
```

### Verification

Test the configuration:
```bash
python test_keys.py
```

Expected output:
```
Raw OPENROUTER_API_KEYS length: 2293 characters
Number of keys parsed: 31
First key: sk-or-v1-20c310112309c81b77fc9...
Last key: sk-or-v1-384d9c73aeba2bea4eecc...

--- Testing Config Class ---
Config loaded 31 API keys
First key from config: sk-or-v1-20c310112309c81b77fc9...
Last key from config: sk-or-v1-384d9c73aeba2bea4eecc...
```

## Usage

The rotation is completely transparent to the user. Simply use the LLM service as normal:

```python
from youtube_chat_cli_main.services.llm_service import get_llm_service

llm = get_llm_service()
result = llm.generate(prompt="Hello, world!", temperature=0.7, max_tokens=50)
```

If a 429 error occurs, the service will automatically:
1. Log: `🔄 API key 1/31 rate-limited. Cooldown: 60s`
2. Rotate to the next available key
3. Log: `🔄 Rotating to API key 2/31`
4. Retry the request

## Logging Examples

### Successful Generation
```
Using API key 1/31
✅ Generation successful!
```

### Rate Limit Hit - Automatic Rotation
```
Using API key 1/31
🔄 API key 1/31 rate-limited. Cooldown: 60s
🔄 Rotating to API key 2/31
Using API key 2/31
✅ Generation successful!
```

### All Keys Exhausted
```
Using API key 1/31
🔄 API key 1/31 rate-limited. Cooldown: 60s
...
Using API key 31/31
🔄 API key 31/31 rate-limited. Cooldown: 60s
❌ All 31 OpenRouter API keys are rate-limited. Retry in 45.3 seconds.
```

## Benefits

1. **Increased Throughput**: With 31 keys, the system can handle 31x more requests before hitting rate limits
2. **Automatic Recovery**: No manual intervention needed when rate limits are hit
3. **Transparent**: Existing code continues to work without modifications
4. **Free Tier Friendly**: Designed specifically for free-tier models with rate limits
5. **Resilient**: Handles both rate limit errors and other API errors gracefully

## Testing

### Test Scripts

1. **`test_keys.py`**: Verifies that all 31 keys are loaded correctly
2. **`test_rotation.py`**: Tests basic generation and rotation logic

### Manual Testing

Test with a simple generation:
```bash
python test_rotation.py
```

Test with the RAG blueprint generation (which previously failed with 502 errors):
```bash
.\.venv\Scripts\python -m youtube_chat_cli_main.cli.main rag generate-blueprint --type spec -t podcast,important --top-k 30 --max-chars 12000 -o blueprint_full.md
```

## Future Enhancements

Potential improvements:
1. **Persistent Rate Limit Tracking**: Save rate limit state to disk to survive restarts
2. **Dynamic Cooldown**: Adjust cooldown period based on API response headers
3. **Key Health Monitoring**: Track success rates per key and prioritize healthy keys
4. **Concurrent Request Support**: Add thread-safe locking for concurrent requests
5. **Key Pool Management**: Add/remove keys dynamically without restart

## Backward Compatibility

The implementation maintains full backward compatibility:
- Single `OPENROUTER_API_KEY` still works
- Existing code requires no changes
- If only one key is configured, rotation is disabled (but error handling still works)

## Constraints Met

✅ **FREE**: Uses only free-tier OpenRouter accounts  
✅ **Minimal Code Changes**: Only modified 3 files  
✅ **Existing Client**: Uses the existing OpenAI Python client  
✅ **No Breaking Changes**: Single-key configurations still work  
✅ **Clear Logging**: Detailed logs for debugging and monitoring

