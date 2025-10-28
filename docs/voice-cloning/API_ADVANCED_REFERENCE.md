# Advanced Voice Cloning API Reference

Complete API reference for voice generation with advanced prosody control.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require API key in header:
```
Authorization: Bearer YOUR_API_KEY
```

## Generate Speech with Advanced Parameters

### Endpoint
```
POST /voice-clone/generate
```

### Request Body

```json
{
  "voice_id": 1,
  "text": "Hello world",
  "speed": 1.0,
  "pitch": 0,
  "exaggeration": 0.5,
  "cfg_weight": 0.5,
  "temperature": 0.9,
  "top_p": 0.95,
  "min_p": 0.1,
  "emotion": "neutral",
  "emphasis": ["important"],
  "pause_before": 0,
  "pause_after": 0,
  "breath_frequency": 0,
  "seed": null
}
```

### Parameter Details

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `voice_id` | integer | ID of cloned voice to use |
| `text` | string | Text to synthesize (max 5000 chars) |

#### Optional Voice Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `speed` | float | 0.5-2.0 | 1.0 | Speech rate multiplier |
| `pitch` | float | -12 to 12 | 0 | Pitch adjustment in semitones |
| `exaggeration` | float | 0.25-2.0 | 0.5 | Emotional exaggeration |
| `cfg_weight` | float | 0.0-1.0 | 0.5 | CFG weight for rhythm |
| `temperature` | float | 0.0-2.0 | 0.9 | Randomness/variation |
| `top_p` | float | 0.0-1.0 | 0.95 | Nucleus sampling |
| `min_p` | float | 0.0-1.0 | 0.1 | Min probability threshold |
| `emotion` | string | See below | "neutral" | Emotion type |
| `emphasis` | array | - | null | Words to emphasize |
| `pause_before` | integer | 0-5000 | 0 | Pause before (ms) |
| `pause_after` | integer | 0-5000 | 0 | Pause after (ms) |
| `breath_frequency` | integer | 0-20 | 0 | Breath every N words |
| `seed` | integer | 0-2^32-1 | null | Random seed |

#### Emotion Options
- `neutral` - Default, professional tone
- `happy` - Upbeat, positive delivery
- `sad` - Melancholic, sorrowful tone
- `angry` - Intense, forceful delivery
- `joyful` - Celebratory, enthusiastic tone
- `excited` - High energy, enthusiastic
- `surprised` - Shocked, astonished tone
- `curious` - Inquisitive, questioning tone
- `confident` - Assured, authoritative tone
- `empathetic` - Compassionate, understanding tone

### Response

#### Success (200 OK)
```json
{
  "success": true,
  "voice_id": 1,
  "output_path": "/tmp/output_abc123.wav",
  "duration": 2.5,
  "parameters": {
    "speed": 1.0,
    "pitch": 0,
    "emotion": "neutral"
  },
  "message": "Speech generated successfully"
}
```

#### Error (400 Bad Request)
```json
{
  "detail": "Speed must be between 0.5 and 2.0, got 3.0"
}
```

#### Error (404 Not Found)
```json
{
  "detail": "Voice with ID 1 not found"
}
```

### Examples

#### Basic Generation
```bash
curl -X POST http://localhost:8000/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "voice_id": 1,
    "text": "Hello world"
  }'
```

#### With Emotion and Pitch
```bash
curl -X POST http://localhost:8000/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "voice_id": 1,
    "text": "I am so happy!",
    "emotion": "happy",
    "pitch": 3,
    "exaggeration": 0.7
  }'
```

#### With Emphasis and Pauses
```bash
curl -X POST http://localhost:8000/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "voice_id": 1,
    "text": "This is very important",
    "emphasis": ["important", "very"],
    "pause_before": 500,
    "pause_after": 300
  }'
```

#### With All Parameters
```bash
curl -X POST http://localhost:8000/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "voice_id": 1,
    "text": "Welcome to our presentation",
    "speed": 1.0,
    "pitch": 1,
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 0.9,
    "top_p": 0.95,
    "min_p": 0.1,
    "emotion": "confident",
    "emphasis": ["welcome", "presentation"],
    "pause_before": 300,
    "pause_after": 200,
    "breath_frequency": 5,
    "seed": 42
  }'
```

## Get Parameter Presets

### Endpoint
```
GET /voice-clone/parameter-presets
```

### Response
```json
{
  "presets": {
    "neutral": {
      "speed": 1.0,
      "pitch": 0,
      "exaggeration": 0.5,
      "emotion": "neutral",
      "description": "Natural, balanced speech"
    },
    "happy": {
      "speed": 1.1,
      "pitch": 2,
      "exaggeration": 0.7,
      "emotion": "happy",
      "description": "Upbeat, cheerful speech"
    },
    ...
  }
}
```

### Example
```bash
curl -X GET http://localhost:8000/api/v1/voice-clone/parameter-presets \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## List Voices

### Endpoint
```
GET /voice-clone/voices
```

### Response
```json
{
  "voices": [
    {
      "id": 1,
      "name": "My Voice",
      "created_at": "2025-01-01T12:00:00Z",
      "usage_count": 42,
      "metadata": {}
    }
  ]
}
```

## Create Voice

### Endpoint
```
POST /voice-clone/create
```

### Request (multipart/form-data)
- `name`: Voice name (string)
- `reference_audio`: Audio file (WAV, MP3, FLAC)

### Response
```json
{
  "success": true,
  "voice_id": 1,
  "name": "My Voice",
  "message": "Voice created successfully"
}
```

## Delete Voice

### Endpoint
```
DELETE /voice-clone/voices/{voice_id}
```

### Response
```json
{
  "success": true,
  "message": "Voice deleted successfully"
}
```

## Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 400 | Parameter out of range | Check parameter ranges |
| 400 | Invalid emotion | Use valid emotion from list |
| 404 | Voice not found | Check voice ID |
| 422 | Validation error | Check request format |
| 500 | Generation failed | Try with simpler parameters |

## Rate Limiting

- 100 requests per minute per API key
- 10 concurrent requests maximum
- Response includes rate limit headers:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 99
  - `X-RateLimit-Reset`: 1234567890

## Best Practices

1. **Validate parameters** before sending requests
2. **Use presets** as starting points
3. **Cache results** with seed for reproducibility
4. **Handle errors** gracefully with retry logic
5. **Monitor rate limits** to avoid throttling
6. **Use appropriate quality** settings for your use case
7. **Test with short text** first before long passages
8. **Store successful parameters** for future use

## SDK Examples

### Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/voice-clone/generate',
    headers={'Authorization': 'Bearer YOUR_API_KEY'},
    json={
        'voice_id': 1,
        'text': 'Hello world',
        'emotion': 'happy',
        'pitch': 2
    }
)

result = response.json()
print(f"Output: {result['output_path']}")
```

### JavaScript
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/voice-clone/generate',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: JSON.stringify({
      voice_id: 1,
      text: 'Hello world',
      emotion: 'happy',
      pitch: 2
    })
  }
);

const result = await response.json();
console.log(`Output: ${result.output_path}`);
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "voice_id": 1,
    "text": "Hello world",
    "emotion": "happy",
    "pitch": 2
  }'
```

