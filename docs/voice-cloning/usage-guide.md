# Voice Cloning Usage Guide

## Quick Start

### 1. Create a Cloned Voice

```python
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService

# Initialize service
service = VoiceCloningService()

# Create voice from reference audio
voice_info = service.create_voice(
    name="my_voice",
    reference_audio="path/to/reference.wav",
    consent_ip="192.168.1.1"
)

print(f"Voice created: {voice_info['id']}")
```

### 2. Generate Speech

```python
# Generate speech with cloned voice
output = service.generate_speech(
    voice_id=voice_info['id'],
    text="Hello, this is my cloned voice!",
    output_file="output.wav",
    speed=1.0
)

print(f"Audio generated: {output}")
```

### 3. List Voices

```python
# List all cloned voices
voices = service.list_voices()

for voice in voices:
    print(f"- {voice['name']} (ID: {voice['id']}, Usage: {voice['usage_count']})")
```

## Reference Audio Requirements

### Optimal Specifications
- **Duration**: 10-30 seconds (minimum 3s, maximum 300s)
- **Sample Rate**: 24kHz (minimum 22kHz)
- **Format**: WAV, MP3, FLAC
- **Bit Depth**: 16-bit or higher
- **Channels**: Mono or stereo
- **SNR**: >20dB (signal-to-noise ratio)

### Recording Tips

1. **Quiet Environment**: Minimize background noise
2. **Clear Speech**: Speak naturally and clearly
3. **Varied Intonation**: Use different tones and emotions
4. **Consistent Volume**: Maintain steady volume throughout
5. **No Silence**: Minimize long pauses

### Audio Preprocessing

```bash
# Convert to optimal format
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 24000 -ac 1 output.wav

# Normalize audio
ffmpeg-normalize input.wav -o normalized.wav

# Remove silence
ffmpeg -i input.wav -af "silenceremove=1=1D=1:2=0.1D=1" output.wav
```

## CLI Usage

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

## API Usage

### Upload Reference Audio

```bash
curl -X POST http://localhost:8556/api/v1/voice-clone/upload-reference \
  -F "name=my_voice" \
  -F "file=@reference.wav" \
  -F "consent_ip=192.168.1.1"
```

### Generate Speech

```bash
curl -X POST http://localhost:8556/api/v1/voice-clone/generate \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": 1,
    "text": "Hello, this is my cloned voice!",
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

## Advanced Features

### Batch Generation

```python
texts = [
    "First sentence",
    "Second sentence",
    "Third sentence"
]

output_files = service.engine.generate_audio_batch(
    texts=texts,
    reference_audio="reference.wav",
    output_dir="./batch_output"
)

print(f"Generated {len(output_files)} files")
```

### Reproducible Generation

```python
# Use seed for reproducible results
output1 = service.generate_speech(
    voice_id=1,
    text="Same text",
    output_file="output1.wav",
    seed=42
)

output2 = service.generate_speech(
    voice_id=1,
    text="Same text",
    output_file="output2.wav",
    seed=42
)

# output1 and output2 will be identical
```

### Speed Control

```python
# Slow speech (0.5x speed)
service.generate_speech(
    voice_id=1,
    text="Slow speech",
    output_file="slow.wav",
    speed=0.5
)

# Fast speech (1.5x speed)
service.generate_speech(
    voice_id=1,
    text="Fast speech",
    output_file="fast.wav",
    speed=1.5
)
```

### Audio Validation

```python
# Validate reference audio before creating voice
validation = service.validate_reference_audio("reference.wav")

if validation['valid']:
    print("✅ Audio is valid")
else:
    print("❌ Audio issues:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

## Integration with Podcast Generation

```python
from youtube_chat_cli_main.services.podcast.generator import PodcastGenerator

# Generate podcast with cloned voice
generator = PodcastGenerator()

podcast = generator.generate_podcast(
    content="Your podcast content",
    voice_id=1,  # Use cloned voice
    style="detailed",
    output_path="podcast.wav"
)
```

## Performance Tips

### Optimize for Speed

```python
# Use fast quality preset
service.engine.quality = "fast"
service.engine.nfe = 8

# Generate on CPU for faster batch processing
service.engine.device = "cpu"
```

### Optimize for Quality

```python
# Use high quality preset
service.engine.quality = "high"
service.engine.nfe = 32

# Use GPU for better quality
service.engine.device = "cuda"
```

## Troubleshooting

### Audio Quality Issues

- Ensure reference audio has high SNR (>20dB)
- Use 10-30 second reference for best results
- Avoid background noise and music
- Use consistent speaking style

### Generation Failures

- Check reference audio validity: `service.validate_reference_audio()`
- Verify text length (<5000 characters)
- Ensure sufficient disk space
- Check GPU memory availability

### Performance Issues

- Use CPU for batch processing
- Reduce quality preset for faster generation
- Increase NFE for better quality (slower)
- Monitor GPU memory usage

## Next Steps

- [API Reference](api-reference.md) - Detailed API documentation
- [Legal Compliance](legal-compliance.md) - Legal requirements
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

