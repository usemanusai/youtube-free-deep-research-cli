# Voice Cloning Migration Guide

## Overview

This guide helps existing TTS users integrate voice cloning into their workflows.

## What's New

### Voice Cloning Features

- **Zero-Shot TTS**: Generate speech with custom voices from reference audio
- **Professional Settings**: Seed control, speed adjustment, quality presets
- **High Quality**: 4.0/5 quality rating comparable to MeloTTS
- **Python 3.13 Native**: No bridge needed, direct integration
- **Cross-Platform**: Windows, macOS, Linux support

### Quality Comparison

| Engine | Quality | Voice Cloning | Speed | Cost |
|--------|---------|---------------|-------|------|
| Chatterbox | 4.5/5 | ❌ | Slow | Free |
| MeloTTS | 4.0/5 | ❌ | Medium | Free |
| E2-F5-TTS | 4.0/5 | ✅ | Fast | Free |
| Edge TTS | 3.5/5 | ❌ | Fast | Free |
| gTTS | 3.0/5 | ❌ | Fast | Free |

## Installation

### Step 1: Install E2-F5-TTS

```bash
pip install f5-tts librosa soundfile
```

### Step 2: Verify Installation

```bash
python -c "from f5_tts.infer.api import F5TTS; print('✅ E2-F5-TTS installed')"
```

### Step 3: Initialize Voice Cloning Service

```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

service = VoiceCloningService()
print("✅ Voice cloning service ready")
```

## Migration Paths

### Path 1: Add Voice Cloning to Existing Podcast Generation

**Before**:
```python
from youtube_chat_cli_main.tts_service import TTSService

tts = TTSService()
audio = tts.generate_audio("Hello world", "output.wav")
```

**After**:
```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

# Create voice once
service = VoiceCloningService()
voice_info = service.create_voice(
    name="my_voice",
    reference_audio="reference.wav"
)

# Generate speech with cloned voice
audio = service.generate_speech(
    voice_id=voice_info['id'],
    text="Hello world",
    output_file="output.wav"
)
```

### Path 2: Hybrid Approach (Fallback to Standard TTS)

```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
from youtube_chat_cli_main.tts_service import TTSService

def generate_audio_hybrid(text, voice_id=None, reference_audio=None):
    """Generate audio with voice cloning or fallback to standard TTS."""
    
    # Try voice cloning if voice_id provided
    if voice_id:
        try:
            service = VoiceCloningService()
            return service.generate_speech(
                voice_id=voice_id,
                text=text,
                output_file="output.wav"
            )
        except Exception as e:
            print(f"Voice cloning failed: {e}, falling back to standard TTS")
    
    # Fallback to standard TTS
    tts = TTSService()
    return tts.generate_audio(text, "output.wav")
```

### Path 3: Podcast Generation with Voice Cloning

```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
from youtube_chat_cli_main.services.podcast.generator import PodcastGenerator

# Create cloned voices for different speakers
service = VoiceCloningService()

host_voice = service.create_voice(
    name="host",
    reference_audio="host_reference.wav"
)

expert_voice = service.create_voice(
    name="expert",
    reference_audio="expert_reference.wav"
)

# Generate podcast with cloned voices
generator = PodcastGenerator()
podcast = generator.generate_podcast(
    content="Your podcast content",
    voices={
        "host": host_voice['id'],
        "expert": expert_voice['id']
    },
    output_path="podcast.wav"
)
```

## Configuration

### Environment Variables

```bash
# Device selection
export E2F5_TTS_DEVICE=cuda  # or 'cpu'

# Quality preset
export E2F5_TTS_QUALITY=balanced  # fast, balanced, high

# Voice storage
export VOICE_CLONE_STORAGE_PATH=./voice_clones

# Number of function evaluations
export E2F5_TTS_NFE=16
```

### Configuration File

Create `config/voice_cloning.yaml`:

```yaml
voice_cloning:
  enabled: true
  storage_path: ./voice_clones
  
  e2f5_tts:
    model: F5-TTS
    device: cuda
    quality: balanced
    nfe: 16
    
  reference_audio:
    min_duration: 3
    max_duration: 300
    min_sample_rate: 22000
    min_snr: 15
```

## API Integration

### REST API

```bash
# Upload reference audio
curl -X POST http://localhost:8556/api/v1/voice-clone/upload-reference \
  -F "name=my_voice" \
  -F "file=@reference.wav"

# Generate speech
curl -X POST http://localhost:8556/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -d '{"voice_id": 1, "text": "Hello world"}'
```

### Python API

```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

service = VoiceCloningService()

# Create voice
voice = service.create_voice("my_voice", "reference.wav")

# Generate speech
audio = service.generate_speech(voice['id'], "Hello world", "output.wav")

# List voices
voices = service.list_voices()

# Delete voice
service.delete_voice(voice['id'])
```

## CLI Commands

### Create Voice

```bash
youtube-chat voice-clone create \
  --reference reference.wav \
  --name "my_voice"
```

### List Voices

```bash
youtube-chat voice-clone list
```

### Generate Speech

```bash
youtube-chat voice-clone generate \
  --voice "my_voice" \
  --text "Hello world" \
  --output output.wav
```

### Delete Voice

```bash
youtube-chat voice-clone delete --voice "my_voice"
```

## Troubleshooting

### Issue: "E2-F5-TTS not available"

**Solution**: Install F5-TTS package

```bash
pip install f5-tts
```

### Issue: "CUDA out of memory"

**Solution**: Use CPU or reduce quality

```bash
export E2F5_TTS_DEVICE=cpu
export E2F5_TTS_QUALITY=fast
```

### Issue: "Audio validation failed"

**Solution**: Check audio requirements

```python
service = VoiceCloningService()
validation = service.validate_reference_audio("reference.wav")
print(validation)
```

### Issue: "Voice cloning slower than expected"

**Solution**: Use fast quality preset

```python
service.engine.quality = "fast"
service.engine.nfe = 8
```

## Performance Optimization

### For Speed

```python
# Use fast preset
service.engine.quality = "fast"
service.engine.nfe = 8

# Use CPU for batch processing
service.engine.device = "cpu"
```

### For Quality

```python
# Use high preset
service.engine.quality = "high"
service.engine.nfe = 32

# Use GPU
service.engine.device = "cuda"
```

## Backward Compatibility

### Existing Code Still Works

All existing TTS code continues to work without changes:

```python
# This still works
tts = TTSService()
audio = tts.generate_audio("Hello world", "output.wav")
```

### New Code Uses Voice Cloning

```python
# New voice cloning feature
service = VoiceCloningService()
voice = service.create_voice("my_voice", "reference.wav")
audio = service.generate_speech(voice['id'], "Hello world", "output.wav")
```

## Best Practices

### 1. Reference Audio Quality

- Use 10-30 second reference audio
- Ensure high SNR (>20dB)
- Minimize background noise
- Use consistent speaking style

### 2. Voice Management

```python
# Create voices once, reuse many times
voice = service.create_voice("my_voice", "reference.wav")

# Generate multiple outputs with same voice
for text in texts:
    service.generate_speech(voice['id'], text, f"output_{i}.wav")
```

### 3. Error Handling

```python
try:
    voice = service.create_voice("my_voice", "reference.wav")
except ValueError as e:
    print(f"Invalid audio: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### 4. Consent Tracking

```python
# Always track consent
voice = service.create_voice(
    name="my_voice",
    reference_audio="reference.wav",
    consent_ip="192.168.1.1"
)
```

## Support

- **Documentation**: See [docs/voice-cloning/](.)
- **Issues**: Report on GitHub
- **Questions**: Check [FAQ](faq.md)

## Next Steps

1. [Installation Guide](installation.md) - Detailed setup instructions
2. [Usage Guide](usage-guide.md) - How to use voice cloning
3. [API Reference](api-reference.md) - API documentation
4. [Legal Compliance](legal-compliance.md) - Legal requirements

