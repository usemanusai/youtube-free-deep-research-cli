# MeloTTS Implementation Plan

**Date:** September 30, 2025  
**Priority:** HIGH (Top recommendation from research document)  
**Status:** Ready to implement

---

## 🎯 Objective

Implement **MeloTTS** as the **primary TTS engine** based on the research document's top recommendation, while maintaining Kokoro as a fast alternative and creating a multi-tier fallback system.

---

## 📊 Why MeloTTS is the Top Recommendation

According to "Python TTS Library Research Mandate.md":

1. **Best Overall Balance**: Quality + CPU performance + permissive license
2. **Voice Quality**: 4/5 (vs. Kokoro's 3.5/5)
3. **CPU Optimized**: "Fast enough for CPU real-time inference"
4. **License**: MIT (fully permissive for commercial use)
5. **Multilingual**: English, Spanish, French, Chinese, Japanese, Korean
6. **Multiple Accents**: American, British, Indian, Australian English

**Research Quote:**
> "MeloTTS stands out as the most well-rounded and lowest-risk choice."

---

## 🔧 Implementation Steps

### Step 1: Install MeloTTS

```bash
pip install MeloTTS
```

**Expected Dependencies:**
- torch
- numpy
- librosa
- scipy

### Step 2: Test MeloTTS Installation

```bash
python -c "from melo.api import TTS; print('✅ MeloTTS installed successfully')"
```

### Step 3: Create Test Script

Create `test_melotts.py`:

```python
from melo.api import TTS
import os

# Initialize MeloTTS
print("Initializing MeloTTS...")
tts = TTS(language='EN', device='cpu')
speaker_ids = tts.hps.data.spk2id

print(f"Available speakers: {list(speaker_ids.keys())}")

# Test text
test_text = """
Host: Welcome to today's podcast! We're diving into an exciting topic.

Expert: Thanks for having me! I'm thrilled to share my insights on this subject.
"""

# Generate audio for Host (American English)
print("\nGenerating Host audio (EN-US)...")
tts.tts_to_file(
    text="Welcome to today's podcast! We're diving into an exciting topic.",
    speaker_id=speaker_ids['EN-US'],
    output_path='test_melotts_host.wav',
    speed=1.0
)
print("✅ Host audio generated: test_melotts_host.wav")

# Generate audio for Expert (British English)
print("\nGenerating Expert audio (EN-BR)...")
tts.tts_to_file(
    text="Thanks for having me! I'm thrilled to share my insights on this subject.",
    speaker_id=speaker_ids['EN-BR'],
    output_path='test_melotts_expert.wav',
    speed=1.0
)
print("✅ Expert audio generated: test_melotts_expert.wav")

# Get file sizes
host_size = os.path.getsize('test_melotts_host.wav')
expert_size = os.path.getsize('test_melotts_expert.wav')

print(f"\nHost audio: {host_size:,} bytes")
print(f"Expert audio: {expert_size:,} bytes")
print("\n✅ MeloTTS test complete!")
```

### Step 4: Modify TTS Service

Update `src/youtube_chat_cli/services/tts/service.py`:

**Add MeloTTS imports:**
```python
# MeloTTS integration (Top recommendation - best balance of quality + CPU performance)
MELOTTS_AVAILABLE = False
try:
    from melo.api import TTS as MeloTTS
    MELOTTS_AVAILABLE = True
    logger.info("✅ MeloTTS available - Top recommendation for quality + CPU performance")
except ImportError as e:
    logger.info(f"MeloTTS not available: {e}")
    MELOTTS_AVAILABLE = False
```

**Add to __init__ method:**
```python
self.melotts_available = MELOTTS_AVAILABLE

# MeloTTS initialization (lazy load)
if MELOTTS_AVAILABLE:
    self.melotts_model = None
    logger.info("MeloTTS initialized (model will be loaded on first use)")
```

**Add generate_audio_melotts method:**
```python
def generate_audio_melotts(self, text: str, output_file: str = "melotts_output.wav",
                          speaker: str = "EN-US", speed: float = 1.0) -> str:
    """Generate audio using MeloTTS (top recommendation for quality + CPU performance).
    
    Args:
        text: Text to convert to speech
        output_file: Output WAV file path
        speaker: Speaker ID (EN-US, EN-BR, EN-AU, EN-IN, etc.)
        speed: Speech speed (0.5-2.0, default 1.0)
    
    Returns:
        Path to generated audio file
    """
    if not self.melotts_available:
        raise APIError("MeloTTS not available")
    
    try:
        # Lazy load MeloTTS model
        if self.melotts_model is None:
            from melo.api import TTS as MeloTTS
            logger.info("Loading MeloTTS model (first use)...")
            self.melotts_model = MeloTTS(language='EN', device='cpu')
            logger.info("✅ MeloTTS model loaded successfully")
        
        # Get speaker IDs
        speaker_ids = self.melotts_model.hps.data.spk2id
        
        # Validate speaker
        if speaker not in speaker_ids:
            logger.warning(f"Speaker '{speaker}' not found, using EN-US")
            speaker = 'EN-US'
        
        # Generate audio
        logger.info(f"Generating MeloTTS audio (speaker: {speaker}, speed: {speed})")
        self.melotts_model.tts_to_file(
            text=text,
            speaker_id=speaker_ids[speaker],
            output_path=output_file,
            speed=speed
        )
        
        # Verify file was created
        if not os.path.exists(output_file):
            raise APIError(f"MeloTTS failed to create output file: {output_file}")
        
        file_size = os.path.getsize(output_file)
        logger.info(f"✅ MeloTTS audio generated: {output_file} ({file_size:,} bytes)")
        
        return output_file
    
    except Exception as e:
        logger.error(f"MeloTTS generation failed: {e}")
        raise APIError(f"MeloTTS generation failed: {e}")
```

**Update generate_audio method (prioritize MeloTTS):**
```python
def generate_audio(self, text: str, output_file: str = "overview.wav",
                  voice: str = "en-US-AriaNeural", audio_format: str = "wav", slow: bool = False) -> str:
    """Generate audio from text using MeloTTS (preferred), Kokoro, Edge TTS, or gTTS (fallback)."""
    
    # Try MeloTTS FIRST - Top recommendation from research
    if self.melotts_available:
        try:
            logger.info("✅ Using MeloTTS (top recommendation for quality + CPU performance)")
            
            # Map voice to MeloTTS speaker
            melotts_speaker = "EN-US"  # Default American English
            if voice and isinstance(voice, str):
                if "british" in voice.lower() or "br" in voice.lower():
                    melotts_speaker = "EN-BR"
                elif "australian" in voice.lower() or "au" in voice.lower():
                    melotts_speaker = "EN-AU"
                elif "indian" in voice.lower() or "in" in voice.lower():
                    melotts_speaker = "EN-IN"
                elif "male" in voice.lower() or "guy" in voice.lower():
                    melotts_speaker = "EN-BR"  # Use British for male voice
            
            speed = 0.85 if slow else 1.0
            return self.generate_audio_melotts(text, output_file, speaker=melotts_speaker, speed=speed)
        
        except Exception as e:
            logger.warning(f"MeloTTS failed, falling back to Kokoro: {e}")
    
    # Try Kokoro SECOND - Fast alternative
    if self.kokoro_available:
        try:
            logger.info("✅ Using Kokoro TTS (fast alternative)")
            # ... existing Kokoro code ...
        except Exception as e:
            logger.warning(f"Kokoro failed, falling back to Edge TTS: {e}")
    
    # Fallback to Edge TTS, gTTS, etc.
    # ... existing fallback code ...
```

### Step 5: Update Podcast Generator

Update `src/youtube_chat_cli/services/podcast/generator.py`:

**Add MeloTTS voice mapping:**
```python
def _generate_multi_speaker_audio(self, script: str, video_id: str, podcast_style: str, timestamp: str) -> Path:
    """Generate audio with multiple speakers for conversational podcasts.
    Uses MeloTTS (if available) for best quality, falls back to Kokoro, then Edge TTS."""
    
    # MeloTTS speakers: EN-US (American), EN-BR (British), EN-AU (Australian), EN-IN (Indian)
    melotts_voice_map = {
        "Host": "EN-US",        # American English (female-sounding)
        "Expert": "EN-BR",      # British English (male-sounding)
        "Moderator": "EN-AU",   # Australian English
        "Panelist1": "EN-US",
        "Panelist2": "EN-BR",
        "Panelist3": "EN-IN",   # Indian English
        "Advocate": "EN-US",
        "Critic": "EN-BR"
    }
    
    # Kokoro voices (fallback)
    kokoro_voice_map = {
        "Host": "af_sarah",
        "Expert": "am_adam",
        # ... existing mapping ...
    }
    
    # Edge TTS voices (fallback)
    edge_voice_map = {
        "Host": "en-US-JennyNeural",
        "Expert": "en-US-GuyNeural",
        # ... existing mapping ...
    }
```

**Update audio generation loop:**
```python
# Check which TTS engine is available (priority: MeloTTS > Kokoro > Edge)
use_melotts = hasattr(self.tts_service, 'melotts_available') and self.tts_service.melotts_available
use_kokoro = hasattr(self.tts_service, 'kokoro_available') and self.tts_service.kokoro_available

if use_melotts:
    logger.info("✅ Using MeloTTS for natural multi-speaker audio (top recommendation)")
elif use_kokoro:
    logger.info("✅ Using Kokoro TTS for fast multi-speaker audio")
else:
    logger.info("Using Edge TTS for multi-speaker audio")

for i, (speaker, text) in enumerate(segments):
    if use_melotts:
        speaker_id = melotts_voice_map.get(speaker, "EN-US")
        temp_file = self.output_dir / f"temp_{video_id}_{timestamp}_seg{i}.wav"
        cleaned_text = self._clean_text_for_speech(text.strip())
        self.tts_service.generate_audio_melotts(
            text=cleaned_text,
            output_file=str(temp_file),
            speaker=speaker_id,
            speed=1.0
        )
    elif use_kokoro:
        # ... existing Kokoro code ...
    else:
        # ... existing Edge TTS code ...
```

---

## 🧪 Testing Plan

### Test 1: Installation Verification
```bash
pip install MeloTTS
python -c "from melo.api import TTS; print('✅ MeloTTS installed')"
```

### Test 2: Standalone Test
```bash
python test_melotts.py
```

Expected output:
- ✅ Two WAV files generated
- ✅ Different voices (EN-US vs EN-BR)
- ✅ File sizes reasonable

### Test 3: Integration Test
```bash
python -m youtube_chat_cli.cli.main podcast "https://www.youtube.com/watch?v=i6JKEk4L_h8" --style interview --length short --tone conversational --no-rag
```

Expected behavior:
- ✅ Uses MeloTTS as primary engine
- ✅ Generates multi-speaker audio
- ✅ Falls back to Kokoro if MeloTTS fails

### Test 4: Quality Comparison

Generate same podcast with both engines:
1. MeloTTS version (new)
2. Kokoro version (current)

Compare:
- Audio quality (naturalness, expressiveness)
- Generation speed
- File size
- CPU usage

---

## 📊 Expected Results

### Audio Quality:
- **MeloTTS**: 4/5 (more natural, better prosody)
- **Kokoro**: 3.5/5 (fast, but slightly flat)

### Performance:
- **MeloTTS**: Real-time capable on CPU
- **Kokoro**: 3-5x real-time on CPU (faster)

### Model Size:
- **MeloTTS**: ~440 MB
- **Kokoro**: ~80-330 MB

### Use Cases:
- **MeloTTS**: Default choice (best balance)
- **Kokoro**: Speed-critical applications
- **Edge TTS**: Cloud fallback
- **pyttsx3**: Emergency fallback

---

## 🚀 Rollout Strategy

### Phase 1: Install and Test (Day 1)
- Install MeloTTS
- Run standalone test
- Verify audio quality

### Phase 2: Integration (Day 2)
- Add MeloTTS to TTS service
- Update podcast generator
- Test multi-speaker audio

### Phase 3: Comparison (Day 3)
- Generate comparison podcasts
- Measure performance metrics
- Document findings

### Phase 4: Production (Day 4)
- Set MeloTTS as default
- Update documentation
- Deploy to users

---

## ✅ Success Criteria

- [ ] MeloTTS successfully installed
- [ ] Standalone test generates audio
- [ ] Integration test works end-to-end
- [ ] Audio quality better than Kokoro
- [ ] CPU performance acceptable
- [ ] Multi-speaker audio working
- [ ] Fallback to Kokoro functional
- [ ] Documentation updated

---

## 🎯 Next Immediate Action

**Run this command to start:**
```bash
pip install MeloTTS && python test_melotts.py
```

Then compare the generated audio quality with the current Kokoro implementation.

---

**Generated by:** Augment Agent  
**Date:** September 30, 2025  
**Priority:** HIGH - Top recommendation from research document

