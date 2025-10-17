# TTS Configuration Guide

Complete guide to configuring Text-to-Speech (TTS) engines.

## Overview

The system supports multiple TTS engines with automatic fallback:

1. **MeloTTS** - High-quality, local (Python 3.11 bridge)
2. **Chatterbox** - Alternative high-quality (Python 3.11 bridge)
3. **Edge TTS** - Cloud-based, free
4. **Google TTS (gTTS)** - Cloud-based, free
5. **pyttsx3** - Offline, system-based

## Configuration

### Environment Variables

```bash
# Default TTS Engine
DEFAULT_TTS_ENGINE=edge-tts

# Default Voice
DEFAULT_TTS_VOICE=en-US-AriaNeural

# TTS Settings
TTS_SAMPLE_RATE=22050
TTS_TIMEOUT=30
TTS_ENABLE_CACHE=true
```

### Configuration File

```yaml
tts:
  engine: edge-tts
  voice: en-US-AriaNeural
  sample_rate: 22050
  timeout: 30
  cache_enabled: true
  engines:
    melotts:
      enabled: true
      quality: high
    chatterbox:
      enabled: true
      quality: high
    edge_tts:
      enabled: true
      quality: medium
    gtts:
      enabled: true
      quality: medium
    pyttsx3:
      enabled: true
      quality: low
```

## Engine Setup

### 1. MeloTTS (Recommended for Quality)

**Requirements:**
- Python 3.11 (via bridge)
- CUDA/GPU (optional, for faster processing)

**Setup:**

```bash
# Install MeloTTS bridge
pip install melo-tts

# Download models
python -c "from melo.api import TTS; TTS(language='EN')"
```

**Configuration:**

```bash
export DEFAULT_TTS_ENGINE=melotts
export MELOTTS_VOICE=EN-US
export MELOTTS_SPEED=1.0
```

**Usage:**

```python
from youtube_chat_cli_main.services.tts import TTSOrchestrator

tts = TTSOrchestrator()
audio = tts.synthesize("Hello, world!", engine="melotts")
```

### 2. Chatterbox (Alternative Quality)

**Requirements:**
- Python 3.11 (via bridge)

**Setup:**

```bash
# Install Chatterbox
pip install chatterbox-tts

# Download models
python -c "from chatterbox import Chatterbox; Chatterbox()"
```

**Configuration:**

```bash
export DEFAULT_TTS_ENGINE=chatterbox
export CHATTERBOX_VOICE=en-US
```

**Usage:**

```python
tts = TTSOrchestrator()
audio = tts.synthesize("Hello, world!", engine="chatterbox")
```

### 3. Edge TTS (Cloud-Based, Free)

**Requirements:**
- Internet connection
- No API key needed

**Setup:**

```bash
# Install Edge TTS
pip install edge-tts
```

**Configuration:**

```bash
export DEFAULT_TTS_ENGINE=edge-tts
export EDGE_TTS_VOICE=en-US-AriaNeural
```

**Available Voices:**

```
en-US-AriaNeural (Female)
en-US-GuyNeural (Male)
en-US-AmberNeural (Female)
en-US-AshleyNeural (Female)
en-US-CoraNeural (Female)
en-US-ElizabethNeural (Female)
en-US-JennyNeural (Female)
en-US-MichelleNeural (Female)
en-US-MonicaNeural (Female)
en-US-SaraNeural (Female)
en-US-AvaNeural (Female)
en-US-BrianNeural (Male)
en-US-ChristopherNeural (Male)
en-US-EricNeural (Male)
en-US-JacobNeural (Male)
en-US-JasonNeural (Male)
en-US-RyanNeural (Male)
en-US-TonyNeural (Male)
```

**Usage:**

```python
tts = TTSOrchestrator()
audio = tts.synthesize(
    "Hello, world!",
    engine="edge-tts",
    voice="en-US-AriaNeural"
)
```

### 4. Google TTS (gTTS)

**Requirements:**
- Internet connection
- No API key needed

**Setup:**

```bash
# Install gTTS
pip install gtts
```

**Configuration:**

```bash
export DEFAULT_TTS_ENGINE=gtts
export GTTS_LANGUAGE=en
```

**Usage:**

```python
tts = TTSOrchestrator()
audio = tts.synthesize("Hello, world!", engine="gtts")
```

### 5. pyttsx3 (Offline)

**Requirements:**
- System TTS engine (Windows: SAPI5, macOS: NSSpeechSynthesizer, Linux: espeak)

**Setup:**

```bash
# Install pyttsx3
pip install pyttsx3

# Linux: Install espeak
sudo apt-get install espeak
```

**Configuration:**

```bash
export DEFAULT_TTS_ENGINE=pyttsx3
export PYTTSX3_VOICE=default
export PYTTSX3_RATE=150
```

**Usage:**

```python
tts = TTSOrchestrator()
audio = tts.synthesize("Hello, world!", engine="pyttsx3")
```

## CLI Usage

### Synthesize Text

```bash
youtube-chat tts synthesize "Hello, world!"
```

### Synthesize with Engine

```bash
youtube-chat tts synthesize "Hello, world!" --engine melotts
```

### Synthesize with Voice

```bash
youtube-chat tts synthesize "Hello, world!" --engine edge-tts --voice en-US-AriaNeural
```

### Save to File

```bash
youtube-chat tts synthesize "Hello, world!" --output audio.mp3
```

### List Available Voices

```bash
youtube-chat tts voices --engine edge-tts
```

## Advanced Configuration

### Engine Priority

```bash
# Set fallback order
export TTS_ENGINE_PRIORITY=melotts,chatterbox,edge-tts,gtts,pyttsx3
```

### Caching

```bash
# Enable caching
export TTS_CACHE_ENABLED=true
export TTS_CACHE_DIR=./tts_cache

# Clear cache
youtube-chat tts cache clear
```

### Performance

```bash
# Parallel processing
export TTS_WORKERS=4

# Batch processing
export TTS_BATCH_SIZE=10
```

## Troubleshooting

### MeloTTS Not Working

```bash
# Check Python 3.11 bridge
python -c "from melo.api import TTS; print('OK')"

# Reinstall
pip install --upgrade melo-tts
```

### Edge TTS Connection Error

```bash
# Check internet connection
ping 8.8.8.8

# Try different voice
youtube-chat tts synthesize "Hello" --voice en-US-GuyNeural
```

### pyttsx3 No Audio

```bash
# Linux: Install espeak
sudo apt-get install espeak

# macOS: Check NSSpeechSynthesizer
system_profiler SPAudioDataType

# Windows: Check SAPI5
```

### Low Audio Quality

```bash
# Increase sample rate
export TTS_SAMPLE_RATE=44100

# Use MeloTTS for better quality
export DEFAULT_TTS_ENGINE=melotts
```

## Performance Tips

1. **Use MeloTTS** - Best quality, local processing
2. **Enable Caching** - Avoid re-synthesizing same text
3. **Batch Processing** - Process multiple texts together
4. **Parallel Workers** - Use multiple workers for throughput
5. **Monitor Latency** - Track synthesis time

## Best Practices

1. **Choose Engine Based on Use Case**
   - Quality: MeloTTS > Chatterbox > Edge TTS > gTTS > pyttsx3
   - Speed: pyttsx3 > gTTS > Edge TTS > Chatterbox > MeloTTS
   - Offline: pyttsx3 > MeloTTS > Chatterbox

2. **Set Appropriate Voices** - Match voice to content

3. **Cache Results** - Avoid re-synthesizing

4. **Monitor Performance** - Track latency and quality

5. **Test Fallback** - Ensure fallback engines work

---

See [System Overview](../architecture/overview.md) for architecture details.

