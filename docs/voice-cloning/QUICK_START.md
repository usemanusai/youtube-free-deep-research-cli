# Voice Cloning - Quick Start Guide

## 5-Minute Setup

### 1. Install (1 minute)

```bash
pip install f5-tts librosa soundfile
```

### 2. Create Voice (2 minutes)

```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

# Initialize service
service = VoiceCloningService()

# Create voice from reference audio (10-30 seconds recommended)
voice = service.create_voice(
    name="my_voice",
    reference_audio="reference.wav"
)

print(f"✅ Voice created: {voice['id']}")
```

### 3. Generate Speech (2 minutes)

```python
# Generate speech with cloned voice
audio = service.generate_speech(
    voice_id=voice['id'],
    text="Hello, this is my cloned voice!",
    output_file="output.wav"
)

print(f"✅ Audio generated: {audio}")
```

## Common Tasks

### List All Voices

```python
voices = service.list_voices()
for v in voices:
    print(f"- {v['name']} (ID: {v['id']}, Usage: {v['usage_count']})")
```

### Generate Multiple Outputs

```python
texts = [
    "First sentence",
    "Second sentence",
    "Third sentence"
]

for i, text in enumerate(texts):
    service.generate_speech(
        voice_id=voice['id'],
        text=text,
        output_file=f"output_{i}.wav"
    )
```

### Adjust Speed

```python
# Slow speech (0.5x)
service.generate_speech(voice['id'], "Slow text", "slow.wav", speed=0.5)

# Fast speech (1.5x)
service.generate_speech(voice['id'], "Fast text", "fast.wav", speed=1.5)
```

### Delete Voice

```python
service.delete_voice(voice['id'])
print("✅ Voice deleted")
```

### Validate Audio Before Creating Voice

```python
validation = service.validate_reference_audio("reference.wav")

if validation['valid']:
    print("✅ Audio is valid")
else:
    print("❌ Audio issues:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

## API Usage

### Upload Voice

```bash
curl -X POST http://localhost:8556/api/v1/voice-clone/upload-reference \
  -F "name=my_voice" \
  -F "file=@reference.wav"
```

### Generate Speech

```bash
curl -X POST http://localhost:8556/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": 1,
    "text": "Hello world!",
    "speed": 1.0
  }'
```

### List Voices

```bash
curl http://localhost:8556/api/v1/voice-clone/voices
```

### Delete Voice

```bash
curl -X DELETE http://localhost:8556/api/v1/voice-clone/voices/1
```

## Quality Settings

### Fast (Recommended for Real-Time)

```python
service.engine.quality = "fast"
service.engine.nfe = 8
# ~1-2 seconds for 100 words
```

### Balanced (Recommended for Most Use Cases)

```python
service.engine.quality = "balanced"
service.engine.nfe = 16
# ~2-3 seconds for 100 words
```

### High (Recommended for Studio Quality)

```python
service.engine.quality = "high"
service.engine.nfe = 32
# ~4-5 seconds for 100 words
```

## Device Selection

### Auto-Detect (Recommended)

```python
service = VoiceCloningService()  # Auto-detects GPU/CPU
```

### Force GPU

```python
service = VoiceCloningService(device="cuda")
```

### Force CPU

```python
service = VoiceCloningService(device="cpu")
```

## Troubleshooting

### "E2-F5-TTS not available"

```bash
pip install f5-tts
```

### "CUDA out of memory"

```python
service.engine.device = "cpu"
service.engine.quality = "fast"
```

### "Audio validation failed"

```python
validation = service.validate_reference_audio("reference.wav")
print(validation)  # See what's wrong
```

### "Generation is slow"

```python
# Use fast preset
service.engine.quality = "fast"

# Or use CPU for batch processing
service.engine.device = "cpu"
```

## Reference Audio Tips

### ✅ Good Reference Audio

- 10-30 seconds duration
- Clear, natural speech
- Minimal background noise
- Consistent volume
- Varied intonation

### ❌ Bad Reference Audio

- Too short (<3 seconds)
- Too long (>300 seconds)
- Lots of background noise
- Inconsistent volume
- Monotone speech

### Record Reference Audio

```bash
# Using ffmpeg
ffmpeg -f dshow -i audio="Microphone" -t 20 reference.wav

# Using sox
rec -r 24000 -c 1 reference.wav trim 0 20
```

## Integration Examples

### With Podcast Generation

```python
from youtube_chat_cli_main.services.podcast.generator import PodcastGenerator

# Create voice
voice = service.create_voice("host", "host_reference.wav")

# Generate podcast
generator = PodcastGenerator()
podcast = generator.generate_podcast(
    content="Your podcast content",
    voice_id=voice['id'],
    output_path="podcast.wav"
)
```

### With Existing TTS Service

```python
from youtube_chat_cli_main.tts_service import TTSService

tts = TTSService()

# Use E2-F5-TTS for voice cloning
audio = tts.generate_audio_e2f5(
    text="Hello world",
    reference_audio="reference.wav",
    output_file="output.wav"
)
```

## Performance Metrics

| Operation | Time | Memory |
|-----------|------|--------|
| Create voice | <1s | 100MB |
| Generate (fast) | 1-2s | 2GB GPU |
| Generate (balanced) | 2-3s | 3GB GPU |
| Generate (high) | 4-5s | 4GB GPU |
| List voices | <100ms | 50MB |
| Delete voice | <500ms | 50MB |

## Next Steps

1. **Read Full Docs**: [Installation Guide](installation.md)
2. **Learn API**: [API Reference](api-reference.md)
3. **Understand Legal**: [Legal Compliance](legal-compliance.md)
4. **Migrate Existing Code**: [Migration Guide](migration-guide.md)
5. **Run Tests**: `pytest tests/test_voice_cloning.py -v`

## Support

- **Issues**: Check [troubleshooting.md](troubleshooting.md)
- **Legal Questions**: See [legal-compliance.md](legal-compliance.md)
- **API Questions**: See [api-reference.md](api-reference.md)
- **Usage Questions**: See [usage-guide.md](usage-guide.md)

---

**Ready to start?** Run this:

```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

service = VoiceCloningService()
voice = service.create_voice("my_voice", "reference.wav")
audio = service.generate_speech(voice['id'], "Hello world!", "output.wav")
print("✅ Done!")
```

