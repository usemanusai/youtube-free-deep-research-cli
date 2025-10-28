# Voice Cloning Integration - Research Findings

## E2-F5-TTS Technical Analysis

### Installation & Compatibility
- **Python Version**: Requires Python ≥3.10 (supports 3.10, 3.11, 3.12, 3.13)
- **Installation Methods**:
  - Pip package: `pip install f5-tts` (inference only)
  - Local editable: Clone repo for training/finetuning
  - Docker: Pre-built images available
- **PyTorch Support**: NVIDIA GPU, AMD GPU (ROCm), Intel GPU (XPU), Apple Silicon
- **Python 3.13 Compatibility**: ✅ Fully supported (no bridge needed)

### Performance Characteristics
- **Inference Speed**: 
  - F5-TTS Base: 253ms latency (RTF: 0.0394) on L20 GPU
  - RTF (Real-Time Factor): 0.0394-0.1467 depending on mode
  - CPU inference: Slower but functional
- **Reference Audio Requirements**:
  - Minimum: 3-5 seconds of clear audio
  - Recommended: 10-30 seconds for quality cloning
  - Format: WAV, MP3, FLAC
  - Sample rate: ≥22kHz (24kHz optimal)
  - Quality: Clear speech, minimal background noise
- **Memory Requirements**:
  - GPU: ~4-8GB VRAM (L20 benchmark)
  - CPU: ~2-4GB RAM
  - Model size: ~300MB-1GB

### Voice Cloning Capabilities
- **Zero-Shot TTS**: Generate speech in any language without training
- **In-Context Learning**: Adapts to new voices with 3-second samples
- **Quality Metrics**:
  - WER (Word Error Rate): 1.42-1.73%
  - Speaker Similarity: 0.67-0.68
  - CMOS (Comparative Mean Opinion Score): 0.31-0.33
  - UTMOS (Utterance-level MOS): 3.35-3.70
- **Multi-Speaker Support**: Can generate multiple voices in single session
- **Emotion Preservation**: Retains speaker emotion and acoustic characteristics

### Architecture
- **Model Type**: Diffusion Transformer with ConvNeXt V2
- **Inference Method**: Flow Matching with ODE solver
- **Vocoder**: Vocos or BigVGAN
- **Phoneme Alignment**: Not required (simplified pipeline)
- **Duration Modeling**: Implicit (no explicit duration model needed)

---

## Voice Cloning Legal & Compliance Framework

### Regulatory Landscape
- **GDPR (EU)**: Biometric data classification, explicit consent required
- **CCPA/CPRA (California)**: Biometric information privacy, opt-in model
- **BIPA (Illinois)**: Biometric Information Privacy Act, strict consent
- **State Laws**: 20+ US states have comprehensive privacy laws (2025)

### Consent Requirements
- **Opt-In Model**: Explicit consent before voice cloning
- **Minimum Information**:
  - Clear disclosure of voice cloning purpose
  - Explanation of how voice will be used
  - Duration of consent (time-limited recommended)
  - Right to revoke consent
- **Documentation**: Store consent timestamp, IP address, user ID
- **Verification**: Require explicit checkbox acceptance

### Fraud Prevention
- **CEO Voice Fraud**: Attackers clone executive voices for wire transfer requests
- **Vishing Attacks**: Real-time voice cloning for social engineering
- **Detection Methods**:
  - Multi-channel verification for high-value transactions
  - Callback verification to known numbers
  - Video call confirmation via separate channels
  - Email verification to known addresses
- **Minimum Audio Duration**: 3 seconds (attackers need ~10 words)

### Impersonation & Misuse Prevention
- **Usage Restrictions**:
  - Prohibit impersonation, deception, fraud, harassment
  - Prohibit creating clones of non-consenting individuals
  - Prohibit commercial use without explicit permission
- **Watermarking**: Mark all AI-generated audio with metadata
- **Usage Logging**: Track all voice cloning operations
- **Disclaimer**: "For educational and authorized use only"

### Platform Policies
- **YouTube**: AI/Impersonation policy prohibits:
  - Impersonating real people without consent
  - Misleading viewers about content authenticity
  - Deepfakes of real people without disclosure
- **Disclosure Requirements**: Mark AI-generated content clearly
- **Takedown Rights**: Platforms can remove non-compliant content

---

## Integration Architecture

### Bridge Pattern (Python 3.13 Compatibility)
- **Status**: NOT NEEDED - F5-TTS supports Python 3.13 natively
- **Benefit**: Simpler implementation, no subprocess overhead
- **Direct Integration**: Can import F5-TTS directly in Python 3.13

### Service Layer Integration
- **Location**: `youtube_chat_cli_main/services/tts/engines/e2f5_tts_engine.py`
- **Pattern**: Follows existing engine architecture (MeloTTS, Chatterbox)
- **Priority**: Insert after Chatterbox (quality: 4.0/5)
- **Fallback**: Automatic fallback to Edge TTS if E2-F5-TTS fails

### Database Schema
```sql
CREATE TABLE cloned_voices (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    reference_audio_path TEXT NOT NULL,
    reference_audio_hash TEXT,  -- SHA256 for deduplication
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    metadata JSON,  -- seed, settings, quality metrics
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    user_id TEXT,  -- For multi-user support
    consent_timestamp TIMESTAMP,
    consent_ip_address TEXT,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE voice_cloning_logs (
    id INTEGER PRIMARY KEY,
    voice_id INTEGER,
    operation TEXT,  -- 'create', 'generate', 'delete'
    text_length INTEGER,
    output_path TEXT,
    duration_seconds FLOAT,
    quality_score FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voice_id) REFERENCES cloned_voices(id)
);
```

### Configuration
```python
# Environment variables
E2F5_TTS_MODEL_PATH = "~/.cache/huggingface/hub/models--SWivid--F5-TTS"
E2F5_TTS_DEVICE = "cuda"  # or "cpu"
E2F5_TTS_QUALITY = "balanced"  # fast, balanced, high
E2F5_TTS_NFE = 16  # Number of function evaluations (16-32)
VOICE_CLONE_STORAGE_PATH = "./voice_clones"
VOICE_CLONE_MAX_DURATION = 300  # seconds
VOICE_CLONE_MIN_DURATION = 3  # seconds
```

---

## Reference Audio Processing Pipeline

### Preprocessing Steps
1. **Format Conversion**: Convert to WAV 24kHz mono
2. **Noise Reduction**: Optional denoising (VoiceFixer recommended)
3. **Normalization**: Normalize to -20dB LUFS
4. **Silence Trimming**: Remove leading/trailing silence (>0.5s)
5. **Quality Validation**:
   - Check sample rate ≥22kHz
   - Verify bit depth ≥16-bit
   - Ensure speech clarity (SNR >20dB)
   - Validate duration 3-300 seconds

### Quality Metrics
- **Signal-to-Noise Ratio (SNR)**: >20dB recommended
- **Spectral Centroid**: 1000-4000 Hz (speech range)
- **Zero Crossing Rate**: Detect speech vs silence
- **MFCC Coefficients**: Verify voice characteristics

---

## Performance Benchmarks

### Inference Speed (F5-TTS Base)
| Scenario | Latency | RTF | Device |
|----------|---------|-----|--------|
| Single inference | 253ms | 0.0394 | L20 GPU |
| Batch (size 2) | 253ms | 0.0394 | L20 GPU |
| CPU inference | 2-5s | 0.1467 | CPU |
| Streaming (32 NFE) | 500-1000ms | Variable | GPU |

### Quality Comparison
| Metric | F5-TTS | E2-TTS | Chatterbox |
|--------|--------|--------|-----------|
| WER (%) | 1.42 | 1.97 | N/A |
| Speaker Similarity | 0.68 | 0.67 | 0.85+ |
| UTMOS | 3.70 | 3.59 | 4.0+ |
| Inference Speed | Fast | Fast | Medium |

---

## Implementation Roadmap

### Phase 1: Core Engine (Week 1)
- [ ] Create E2FTTSEngine class
- [ ] Implement reference audio preprocessing
- [ ] Add voice cloning inference
- [ ] Integrate with TTS service

### Phase 2: Storage & Database (Week 1-2)
- [ ] Extend database schema
- [ ] Implement voice storage
- [ ] Add metadata management

### Phase 3: API Endpoints (Week 2)
- [ ] Upload reference audio
- [ ] Record from microphone
- [ ] Generate speech with cloned voice
- [ ] List/delete voices

### Phase 4: CLI Commands (Week 2)
- [ ] Voice creation command
- [ ] Voice listing command
- [ ] Voice testing command
- [ ] Voice deletion command

### Phase 5: Dashboard UI (Week 3)
- [ ] Voice cloning tab
- [ ] Upload/recording interface
- [ ] Voice library management
- [ ] Settings panel

### Phase 6: Legal Compliance (Week 3)
- [ ] Consent tracking
- [ ] Usage logging
- [ ] Disclaimer display
- [ ] Watermarking

### Phase 7: Testing & Docs (Week 4)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] Documentation
- [ ] Cross-platform validation

---

## Success Criteria
✅ Python 3.13 native support (no bridge needed)
✅ <500ms inference for 100 words on GPU
✅ Studio-quality output (UTMOS >3.5)
✅ Full legal compliance framework
✅ Cross-platform support (Windows/Mac/Linux)
✅ 80%+ test coverage
✅ Comprehensive documentation

