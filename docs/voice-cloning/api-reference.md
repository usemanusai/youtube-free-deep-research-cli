# Voice Cloning API Reference

## Base URL

```
http://localhost:8556/api/v1/voice-clone
```

## Authentication

Currently, no authentication is required. For production, implement API key authentication.

## Endpoints

### 1. Upload Reference Audio

**Endpoint**: `POST /upload-reference`

**Description**: Upload reference audio for voice cloning

**Parameters**:
- `name` (string, required): Name for the cloned voice
- `file` (file, required): Audio file (WAV, MP3, FLAC)
- `consent_ip` (string, optional): IP address for consent tracking

**Request**:
```bash
curl -X POST http://localhost:8556/api/v1/voice-clone/upload-reference \
  -F "name=my_voice" \
  -F "file=@reference.wav" \
  -F "consent_ip=192.168.1.1"
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "my_voice",
  "reference_audio_path": "/path/to/voice_clones/my_voice_abc12345.wav",
  "audio_hash": "abc123456789...",
  "metadata": {
    "seed": 42,
    "quality": "balanced",
    "validation": {
      "valid": true,
      "duration": 15.5,
      "sample_rate": 24000,
      "snr_db": 25.3,
      "issues": []
    }
  },
  "created_at": "2025-10-27T10:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid audio file
- `500 Internal Server Error`: Server error

---

### 2. List Voices

**Endpoint**: `GET /voices`

**Description**: List all cloned voices

**Parameters**: None

**Request**:
```bash
curl http://localhost:8556/api/v1/voice-clone/voices
```

**Response** (200 OK):
```json
{
  "voices": [
    {
      "id": 1,
      "name": "my_voice",
      "reference_audio_path": "/path/to/voice_clones/my_voice_abc12345.wav",
      "created_at": "2025-10-27T10:30:00Z",
      "usage_count": 5,
      "metadata": {
        "seed": 42,
        "quality": "balanced"
      }
    }
  ],
  "total": 1
}
```

---

### 3. Generate Speech

**Endpoint**: `POST /generate`

**Description**: Generate speech with cloned voice

**Parameters**:
- `voice_id` (integer, required): ID of cloned voice
- `text` (string, required): Text to synthesize (max 5000 characters)
- `speed` (float, optional): Speech rate (0.5-2.0, default: 1.0)

**Request**:
```bash
curl -X POST http://localhost:8556/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": 1,
    "text": "Hello, this is my cloned voice!",
    "speed": 1.0
  }'
```

**Response** (200 OK):
```json
{
  "success": true,
  "output_path": "/tmp/voice_output_1_abc123.wav",
  "text_length": 33,
  "voice_id": 1
}
```

**Error Responses**:
- `400 Bad Request`: Invalid voice ID or text
- `500 Internal Server Error`: Generation failed

---

### 4. Delete Voice

**Endpoint**: `DELETE /voices/{voice_id}`

**Description**: Delete a cloned voice

**Parameters**:
- `voice_id` (integer, required): ID of voice to delete

**Request**:
```bash
curl -X DELETE http://localhost:8556/api/v1/voice-clone/voices/1
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Voice 1 deleted"
}
```

**Error Responses**:
- `404 Not Found`: Voice not found
- `500 Internal Server Error`: Deletion failed

---

### 5. Get Settings

**Endpoint**: `GET /settings`

**Description**: Get voice cloning settings

**Parameters**: None

**Request**:
```bash
curl http://localhost:8556/api/v1/voice-clone/settings
```

**Response** (200 OK):
```json
{
  "device": "cuda",
  "model": "F5-TTS",
  "quality": "balanced",
  "nfe": 16,
  "cuda_available": true,
  "storage_path": "./voice_clones"
}
```

---

### 6. Validate Audio

**Endpoint**: `POST /validate-audio`

**Description**: Validate reference audio file

**Parameters**:
- `file` (file, required): Audio file to validate

**Request**:
```bash
curl -X POST http://localhost:8556/api/v1/voice-clone/validate-audio \
  -F "file=@reference.wav"
```

**Response** (200 OK):
```json
{
  "valid": true,
  "duration": 15.5,
  "sample_rate": 24000,
  "snr_db": 25.3,
  "issues": [],
  "file_size": 1536000
}
```

**Error Response** (400 Bad Request):
```json
{
  "valid": false,
  "duration": 2.5,
  "sample_rate": 22000,
  "snr_db": 12.1,
  "issues": [
    "Audio too short: 2.5s (minimum: 3s)",
    "Low SNR: 12.1dB (recommended: >20dB)"
  ],
  "file_size": 110000
}
```

---

## Error Handling

### Common Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Bad Request | Invalid parameters or audio file |
| 404 | Not Found | Voice ID not found |
| 500 | Internal Server Error | Server error or service unavailable |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, implement:
- 100 requests per minute per IP
- 10 concurrent generation requests per user
- 1GB storage per user

---

## Pagination

List endpoints support pagination:

```bash
curl "http://localhost:8556/api/v1/voice-clone/voices?limit=10&offset=0"
```

---

## Webhooks (Future)

Planned webhook support for async operations:

```json
{
  "event": "voice.generated",
  "voice_id": 1,
  "output_path": "/tmp/voice_output_1_abc123.wav",
  "timestamp": "2025-10-27T10:30:00Z"
}
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8556/api/v1/voice-clone"

# Upload reference audio
with open("reference.wav", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/upload-reference",
        params={"name": "my_voice"},
        files={"file": f}
    )
    voice_info = response.json()
    voice_id = voice_info["id"]

# Generate speech
response = requests.post(
    f"{BASE_URL}/generate",
    json={
        "voice_id": voice_id,
        "text": "Hello world!",
        "speed": 1.0
    }
)
output = response.json()
print(f"Generated: {output['output_path']}")

# List voices
response = requests.get(f"{BASE_URL}/voices")
voices = response.json()
print(f"Total voices: {voices['total']}")

# Delete voice
response = requests.delete(f"{BASE_URL}/voices/{voice_id}")
print(response.json())
```

---

## JavaScript/TypeScript Client Example

```typescript
const BASE_URL = "http://localhost:8556/api/v1/voice-clone";

// Upload reference audio
async function uploadVoice(name: string, file: File) {
  const formData = new FormData();
  formData.append("name", name);
  formData.append("file", file);
  
  const response = await fetch(`${BASE_URL}/upload-reference`, {
    method: "POST",
    body: formData
  });
  
  return response.json();
}

// Generate speech
async function generateSpeech(voiceId: number, text: string, speed: number = 1.0) {
  const response = await fetch(`${BASE_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ voice_id: voiceId, text, speed })
  });
  
  return response.json();
}

// List voices
async function listVoices() {
  const response = await fetch(`${BASE_URL}/voices`);
  return response.json();
}

// Delete voice
async function deleteVoice(voiceId: number) {
  const response = await fetch(`${BASE_URL}/voices/${voiceId}`, {
    method: "DELETE"
  });
  
  return response.json();
}
```

---

## Performance Metrics

### Generation Speed

- **Fast Quality**: ~1-2 seconds for 100 words
- **Balanced Quality**: ~2-3 seconds for 100 words
- **High Quality**: ~4-5 seconds for 100 words

### Memory Usage

- **GPU (CUDA)**: ~2-4GB VRAM
- **CPU**: ~1-2GB RAM

### Supported Audio Formats

- WAV (recommended)
- MP3
- FLAC
- OGG

---

## Changelog

### v1.0.0 (2025-10-27)

- Initial release
- E2-F5-TTS integration
- Voice cloning with zero-shot TTS
- REST API endpoints
- Audio validation
- Consent tracking

