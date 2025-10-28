# Voice Cloning Installation Guide

## Prerequisites

- Python 3.13+ (native support, no bridge needed)
- 4-8GB VRAM (GPU recommended) or 2-4GB RAM (CPU)
- ~1GB disk space for models and voice storage

## Installation Steps

### 1. Install E2-F5-TTS

```bash
# Install F5-TTS package
pip install f5-tts

# For GPU support (NVIDIA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For AMD GPU (ROCm)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7

# For Apple Silicon
pip install torch torchvision torchaudio
```

### 2. Install Audio Processing Dependencies

```bash
# Audio processing
pip install librosa soundfile pydub

# For audio file format support
pip install scipy numpy

# Optional: For advanced audio processing
pip install julius resampy
```

### 3. Verify Installation

```bash
# Test E2-F5-TTS
python -c "from f5_tts.infer.api import F5TTS; print('✅ E2-F5-TTS installed')"

# Test audio libraries
python -c "import librosa; print('✅ librosa installed')"
```

### 4. Download Models

Models are automatically downloaded on first use to `~/.cache/huggingface/hub/`

```bash
# Pre-download models (optional)
python -c "from f5_tts.infer.api import F5TTS; F5TTS(model_name='F5-TTS')"
```

## Configuration

### Environment Variables

```bash
# Device selection
export E2F5_TTS_DEVICE=cuda  # or 'cpu'

# Model quality
export E2F5_TTS_QUALITY=balanced  # fast, balanced, high

# Voice storage
export VOICE_CLONE_STORAGE_PATH=./voice_clones

# Number of function evaluations (16-32)
export E2F5_TTS_NFE=16
```

### Configuration File

Create `config/voice_cloning.yaml`:

```yaml
voice_cloning:
  enabled: true
  storage_path: ./voice_clones
  
  e2f5_tts:
    model: F5-TTS  # or E2-TTS
    device: cuda   # auto-detect if null
    quality: balanced
    nfe: 16
    
  reference_audio:
    min_duration: 3      # seconds
    max_duration: 300    # seconds
    min_sample_rate: 22000  # Hz
    min_snr: 15          # dB
    
  generation:
    max_text_length: 5000
    default_speed: 1.0
    supported_speeds: [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
```

## Platform-Specific Setup

### Windows

```bash
# Install Visual C++ Build Tools (if needed)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### macOS

```bash
# Install with Homebrew (optional)
brew install ffmpeg

# Install PyTorch for Apple Silicon
pip install torch torchvision torchaudio

# Verify Metal acceleration
python -c "import torch; print(torch.backends.mps.is_available())"
```

### Linux

```bash
# Install system dependencies
sudo apt-get install -y ffmpeg libsndfile1

# Install PyTorch with CUDA (Ubuntu/Debian)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

## Troubleshooting

### CUDA Not Available

```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with correct CUDA version
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory (OOM)

```bash
# Use CPU instead
export E2F5_TTS_DEVICE=cpu

# Or reduce quality
export E2F5_TTS_QUALITY=fast
export E2F5_TTS_NFE=8
```

### Audio File Issues

```bash
# Convert audio to WAV 24kHz
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 24000 output.wav

# Check audio properties
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels,duration -of default=noprint_wrappers=1:nokey=1:noprint_wrappers=1 audio.wav
```

### Model Download Issues

```bash
# Manually set cache directory
export HF_HOME=/path/to/cache

# Clear cache and re-download
rm -rf ~/.cache/huggingface/hub/models--SWivid--F5-TTS
python -c "from f5_tts.infer.api import F5TTS; F5TTS()"
```

## Performance Optimization

### GPU Optimization

```bash
# Enable TensorRT for faster inference (optional)
pip install tensorrt

# Use mixed precision
export TORCH_DTYPE=float16
```

### CPU Optimization

```bash
# Use OpenMP for parallel processing
export OMP_NUM_THREADS=4

# Enable MKL optimization
pip install mkl
```

## Verification

```bash
# Test voice cloning service
python -c "
from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
service = VoiceCloningService()
print('✅ Voice cloning service initialized')
print(f'Storage: {service.storage_path}')
print(f'Device: {service.engine.device}')
"
```

## Next Steps

- [Usage Guide](usage-guide.md) - Learn how to use voice cloning
- [API Reference](api-reference.md) - API endpoint documentation
- [Legal Compliance](legal-compliance.md) - Legal requirements and best practices

