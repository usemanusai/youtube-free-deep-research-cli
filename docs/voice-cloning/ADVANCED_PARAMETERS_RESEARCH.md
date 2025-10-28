# Advanced Voice Cloning CLI Parameters - Research Findings
**Date:** October 28, 2025  
**Research Scope:** 20+ in-depth web searches on F5-TTS, voice cloning, TTS parameters, and CLI implementation patterns

---

## 1. Chatterbox TTS Advanced Parameters

### Core Voice Control Parameters
- **`exaggeration`** (Range: 0.25 - 2.0, Default: 0.5)
  - Controls emotional and intonational exaggeration
  - 0.1-0.3: Flat, monotone delivery
  - 0.4-0.6: Natural speech (0.5 default)
  - 0.7-0.9: More expressive delivery
  - 1.0+: Highly dramatic, theatrical speech
  - Higher values increase speech speed

- **`cfg_weight`** (Range: 0.0 - 1.0, Default: 0.5)
  - Controls classifier-free guidance and speech rhythm
  - Low (0.2-0.5): Strict text adherence, slower measured speech
  - Mid (0.6-1.0): Balanced approach
  - High (1.2-2.0): More interpretive, creative delivery
  - For fast-paced reference audio, lower to ~0.3

- **`temperature`** (Range: 0 - 2, Default: 0.9)
  - Governs randomness and variation
  - 0.2-0.5: Consistent, predictable output
  - 0.8-1.2: Moderate variation
  - 1.5-2.0: Highly varied, unpredictable

- **`top_p`** (Default: 0.95)
  - Nucleus sampling parameter for diversity

- **`min_p`** (Default: 0.1)
  - Minimum probability threshold

---

## 2. SSML (Speech Synthesis Markup Language) Control

### Pause and Break Control
```xml
<break time="500ms"/>  <!-- 500ms pause -->
<break time="1s"/>     <!-- 1 second pause -->
```

### Prosody Control
```xml
<prosody rate="slow" pitch="+2st">Text here</prosody>
<prosody volume="50%">Quieter text</prosody>
<prosody pitch="+12st">Higher pitch</prosody>
```

### Pitch Control
- Range: -20 to +20 semitones (typical)
- Semitone = 100 cents
- Example: `<prosody pitch="+5st">` = 5 semitones higher

### Speaking Rate
- Range: 0.25x to 4.0x multiplier
- Example: `<prosody rate="1.5">` = 1.5x speed

### Emphasis and Stress
```xml
<emphasis level="strong">Important word</emphasis>
<emphasis level="moderate">Somewhat important</emphasis>
```

---

## 3. Voice Cloning Reference Audio Requirements

### Minimum Duration
- **Minimum:** 3-5 seconds of clear audio
- **Recommended:** 10-30 seconds for high-quality clones
- **Optimal:** 15-30 seconds captures subtle characteristics

### Audio Quality Metrics
- **Signal-to-Noise Ratio (SNR):** ≥20 dB recommended
  - SNR = 10 × log₁₀(P_signal / P_noise)
  - Higher SNR = cleaner audio
  - Typical range: 20-40 dB for quality voice cloning

- **Sample Rate:** 16 kHz minimum, 44.1 kHz or 48 kHz preferred
- **Bit Depth:** 16-bit minimum
- **Format:** WAV, MP3, or OGG

### Audio Preprocessing
- Remove background noise and silence
- Normalize loudness to -18 LUFS (EBU R128 standard)
- Trim disfluencies (fillers, long pauses)
- Ensure clear pronunciation
- Mono or stereo acceptable

---

## 4. Advanced Prosody Control Features

### Global Prosody Control
- **Valence-Arousal-Dominance (VAD) Space:**
  - Valence: Positive/Negative emotion
  - Arousal: Energy level (calm to excited)
  - Dominance: Confidence/authority level

### Local Prosody Control
- **Pitch Contour:** Dynamic pitch changes across utterance
- **Energy/Loudness:** RMS (Root Mean Square) amplitude
- **Duration:** Phoneme and word-level timing
- **Spectral Centroid:** Perceived brightness/timbre (1500-2500 Hz typical)

### Emotion Exaggeration
- Dial up/down emotional expressiveness
- Affects intonation, rhythm, and energy
- First open-source TTS feature (Chatterbox)

---

## 5. Voice Characteristics Adjustable Parameters

### Timbre/Brightness Control
- **Spectral Centroid:** Frequency distribution
  - Lower values = warmer, darker voice
  - Higher values = brighter, sharper voice

### Rhythm and Pacing
- **Breath Insertion:** Natural breathing patterns
- **Pause Frequency:** Insert pauses every N words
- **Stress Patterns:** Word-level emphasis

### Tone and Emotion
- **Sarcasm, Whispering, Shouting, Thoughtful, Formal**
- **Laughter, Sighs, Gasps, Ahem**
- **Joyful, Sad, Excited, Surprised, Curious, Confident, Empathetic**

---

## 6. CLI Implementation Patterns (Click Framework)

### Option Types and Validation
```python
@click.option('--pitch', type=float, default=0.0, 
              help='Pitch adjustment (-12 to +12 semitones)')
@click.option('--speed', type=float, default=1.0,
              help='Speed multiplier (0.5 to 2.0)')
@click.option('--emotion', type=click.Choice(['neutral', 'happy', 'sad']),
              default='neutral')
@click.option('--emphasis', multiple=True,
              help='Words to emphasize')
```

### Configuration Management
- **Precedence:** Defaults → Config file → Environment → CLI flags
- **Config Formats:** TOML (recommended), JSON, YAML
- **Frozen Config Objects:** Pass immutable config through functions

### Best Practices
- Use option groups for related parameters
- Provide sensible defaults
- Include validation and type conversion
- Support config files for complex setups
- Use environment variables for sensitive data

---

## 7. FastAPI Request Body Validation

### Pydantic Model Pattern
```python
from pydantic import BaseModel, Field

class VoiceGenerateRequest(BaseModel):
    text: str
    voice_id: int
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=0.0, ge=-12, le=12)
    exaggeration: float = Field(default=0.5, ge=0.25, le=2.0)
    cfg_weight: float = Field(default=0.5, ge=0.0, le=1.0)
```

### Validation Features
- Type checking and conversion
- Range validation (ge, le, gt, lt)
- Custom validators
- Automatic OpenAPI documentation
- Error messages with field details

---

## 8. Implementation Recommendations

### Parameter Ranges (Validated)
| Parameter | Min | Default | Max | Unit |
|-----------|-----|---------|-----|------|
| Speed | 0.5 | 1.0 | 2.0 | multiplier |
| Pitch | -12 | 0 | +12 | semitones |
| Exaggeration | 0.25 | 0.5 | 2.0 | factor |
| CFG Weight | 0.0 | 0.5 | 1.0 | factor |
| Pause Duration | 0 | 0 | 5000 | milliseconds |
| Breath Frequency | 0 | 0 | 20 | words |

### Batch Processing
- Support multiple voice generation requests
- Implement queue-based processing
- Add progress tracking
- Enable concurrent generation with rate limiting

### Seed Parameter
- Use for reproducibility
- Fixed seed = identical output
- Random seed = variation in output
- Range: 0 to 2^32-1

---

## 9. Key Findings Summary

✅ **Chatterbox TTS** offers emotion exaggeration control (first in open-source)  
✅ **SSML** provides fine-grained control via XML markup  
✅ **Voice cloning** requires minimal audio (3-30 seconds)  
✅ **Prosody control** includes pitch, energy, duration, timbre  
✅ **CLI patterns** use Click with config file support  
✅ **FastAPI** with Pydantic for robust validation  
✅ **SNR ≥20 dB** recommended for quality audio  
✅ **Parameter ranges** well-defined and validated  

---

## 10. References & Sources

- Chatterbox TTS Documentation (2025)
- SSML W3C Specification
- Azure Speech Service Documentation
- Google Cloud Text-to-Speech API
- Amazon Polly SSML Support
- BatonVoice Prosody Control Research
- StressTransfer Speech-to-Speech Translation
- Click Framework Best Practices
- FastAPI Pydantic Validation
- Voice Cloning Quality Requirements (2025)

