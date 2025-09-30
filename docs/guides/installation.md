# Installation Guide

This guide provides detailed installation instructions for YouTube Chat CLI.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 4GB RAM recommended (2GB minimum)
- **Storage**: 2GB free space (for TTS libraries and database)
- **Network**: Stable internet connection for API calls

## Prerequisites

### 1. Python Installation

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
# Using Homebrew
brew install python3

# Or download from python.org
```

**Windows:**
- Download Python from [python.org](https://python.org)
- Ensure "Add Python to PATH" is checked during installation

### 2. API Keys

**YouTube Data API v3 Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Restrict the key to YouTube Data API v3 (recommended)

**OpenRouter API Key (Optional):**
1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Generate an API key from the dashboard

## Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Run the installation script
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

The script will:
- Check Python version compatibility
- Create a virtual environment
- Install the package and dependencies
- Optionally install TTS libraries
- Create configuration files

### Method 2: Manual Installation

```bash
# 1. Clone the repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install the package
pip install -e .

# 6. Install additional dependencies
pip install -r requirements.txt
```

### Method 3: Development Installation

For contributors and developers:

```bash
# Clone and enter directory
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install with all dependencies
pip install -e ".[dev,tts,all]"
```

## Configuration

### 1. Environment Variables

```bash
# Copy the sample configuration
cp examples/sample_config.env .env

# Edit the configuration file
nano .env  # or your preferred editor
```

**Required Configuration:**
```bash
# YouTube Data API v3 key (required)
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**Optional Configuration:**
```bash
# OpenRouter API key (for AI features)
OPENROUTER_API_KEY=your_openrouter_key_here

# n8n webhook URL (for RAG integration)
N8N_WEBHOOK_URL=http://localhost:5678/workflow/your_workflow_id

# MaryTTS server URL (for advanced TTS)
MARYTTS_SERVER_URL=http://localhost:59125

# Rate limiting settings
MAX_VIDEOS_PER_DAY=5
MIN_DELAY_HOURS=1
MAX_DELAY_HOURS=2
BACKOFF_HOURS=2
```

### 2. TTS Libraries (Optional)

Install text-to-speech libraries for audio generation:

```bash
# Install all TTS libraries (CPU-only for compatibility)
youtube-chat tts install-all --cpu-only

# Or install specific libraries
youtube-chat tts install edge-tts --cpu-only
youtube-chat tts install gtts --cpu-only
```

**Available TTS Libraries:**
- **edge-tts**: Microsoft Edge TTS (recommended)
- **gtts**: Google Text-to-Speech
- **kokoro**: High-quality neural TTS
- **openvoice**: Advanced voice cloning
- **melotts**: Multilingual TTS
- **chatterbox**: Conversational TTS

## Verification

### 1. Test Installation

```bash
# Test CLI access
youtube-chat --help

# Test backward compatibility
python cli.py --help

# Check version
youtube-chat --version
```

### 2. Test Core Functionality

```bash
# Test database initialization
youtube-chat stats

# Test TTS libraries
youtube-chat tts list

# Test API connections (requires API keys)
youtube-chat verify-connections
```

### 3. Test Channel Operations

```bash
# List channels (should be empty initially)
youtube-chat channel list

# Test service status
youtube-chat service status
```

## Troubleshooting Installation

### Common Issues

**Issue: Python version too old**
```
Error: Python 3.8+ is required
```
**Solution:** Upgrade Python or use a newer version

**Issue: Permission denied**
```
Error: Permission denied when installing packages
```
**Solution:** Use virtual environment or `--user` flag:
```bash
pip install --user -e .
```

**Issue: TTS installation fails**
```
Error: Failed to install TTS library
```
**Solution:** Use CPU-only installation:
```bash
youtube-chat tts install-all --cpu-only
```

**Issue: Import errors**
```
ModuleNotFoundError: No module named 'youtube_chat_cli'
```
**Solution:** Ensure package is installed correctly:
```bash
pip install -e .
```

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../README.md#troubleshooting)
2. Review installation logs
3. Ensure all prerequisites are met
4. Try the automated installation script
5. Open an issue on GitHub with error details

## Next Steps

After successful installation:

1. **Configure API keys** in the `.env` file
2. **Add your first channel**: `youtube-chat channel add <channel_url>`
3. **Start the background service**: `youtube-chat service start --daemon`
4. **Monitor progress**: `youtube-chat stats`

See the [Usage Guide](../README.md#usage) for detailed usage instructions.
