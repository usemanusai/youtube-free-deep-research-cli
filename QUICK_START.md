# TTS Bridge - Quick Start Guide

**Get MeloTTS (4/5) and Chatterbox (4.5/5) working in 3 steps!**

---

## ⚡ 3-Step Setup

### Step 1: Setup Python 3.11 Environment (5 min)

**Windows:**
```bash
setup_python311_env.bat
```

**Linux/Mac:**
```bash
chmod +x setup_python311_env.sh
./setup_python311_env.sh
```

---

### Step 2: Test Installation (2 min)

```bash
python test_tts_bridge.py
```

**Expected:** `5/5 tests passed ✅`

---

### Step 3: Generate Podcast (Same as before!)

```bash
python -m youtube_chat_cli_main.cli <video_url>
```

**That's it!** Audio quality automatically upgraded to 4.5/5!

---

## 🎯 What You Get

| Engine | Quality | Status |
|--------|---------|--------|
| **Chatterbox** | 4.5/5 ⭐⭐⭐⭐⭐ | ✅ NEW |
| **MeloTTS** | 4/5 ⭐⭐⭐⭐ | ✅ NEW |
| Kokoro | 3.5/5 ⭐⭐⭐ | ✅ Existing |
| Edge TTS | 3/5 ⭐⭐⭐ | ✅ Existing |
| gTTS | 2.5/5 ⭐⭐ | ✅ Existing |
| pyttsx3 | 1.5/5 ⭐ | ✅ Existing |

**Quality Range:** 1.5/5 → 4.5/5 (FULL RANGE!)

---

## 🐛 Troubleshooting

**Setup script fails?**
```bash
# Manual setup
conda create -n tts-bridge-py311 python=3.11
conda activate tts-bridge-py311
pip install MeloTTS chatterbox-tts
which python > .python311_path
```

**Tests fail?**
```bash
# Check Python 3.11 path
cat .python311_path  # Linux/Mac
type .python311_path  # Windows
```

**Slow generation?**
- First run downloads models (~700MB) - normal
- Subsequent runs: 2-8 seconds per segment

---

## 📚 Full Documentation

- **Setup Guide:** `TTS_BRIDGE_SETUP.md`
- **Implementation Details:** `TTS_BRIDGE_IMPLEMENTATION_COMPLETE.md`
- **Technical Analysis:** `PYTHON_313_COMPATIBILITY_SOLUTION.md`

---

## ✅ Success Checklist

- [ ] Run `setup_python311_env.bat` or `.sh`
- [ ] Run `python test_tts_bridge.py` → 5/5 tests pass
- [ ] Generate podcast → Check logs for "🎯 Attempting Chatterbox"
- [ ] Listen to audio → Notice improved quality!

---

**Questions?** Check `TTS_BRIDGE_SETUP.md` for detailed troubleshooting!

