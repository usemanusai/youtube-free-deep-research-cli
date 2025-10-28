# 🎙️ YouTube Free Deep Research CLI

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/usemanusai/youtube-free-deep-research-cli)
[![JAEGIS](https://img.shields.io/badge/JAEGIS-AI%20Powered-purple.svg)](https://github.com/usemanusai)
[![Release](https://img.shields.io/badge/release-v2.0.1-brightgreen.svg)](https://github.com/usemanusai/youtube-free-deep-research-cli/releases)
[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/usemanusai-youtube-free-deep-research-cli-badge.png)](https://mseep.ai/app/usemanusai-youtube-free-deep-research-cli)

**Production-ready Python 3.13+ CLI/API system with Adaptive RAG, multi-engine TTS, OpenRouter key rotation, FastAPI backend, and Next.js dashboard.**

A comprehensive, modular platform for deep research, content analysis, and intelligent workflow automation. Features adaptive RAG engine (LangGraph-based), multi-engine TTS (MeloTTS/Chatterbox via Python 3.11 bridge), 31-key OpenRouter rotation with intelligent failover, FastAPI backend with REST API and WebSocket support, Next.js dashboard, MCP server for Claude Desktop integration, and comprehensive testing suite.

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🏗️ Architecture](#️-architecture)
- [📚 Documentation](#-documentation)
- [🧪 Testing](#-testing)
- [🐳 Docker](#-docker)
- [🔄 CI/CD](#-cicd)
- [📝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

### Core Capabilities
- **Adaptive RAG Engine** - LangGraph-based retrieval-augmented generation
- **Multi-Engine TTS** - MeloTTS, Chatterbox, Edge TTS, gTTS, pyttsx3
- **OpenRouter Integration** - 31-key rotation with intelligent failover
- **FastAPI Backend** - REST API with WebSocket support
- **Next.js Dashboard** - Professional web interface
- **MCP Server** - Claude Desktop integration
- **Comprehensive Testing** - Unit and integration tests

### Advanced Features
- **Python 3.13 Compatibility** - Modern Python support with TTS bridge
- **Modular Architecture** - 60+ files organized into services, API, CLI, utils
- **100% Backward Compatible** - Zero breaking changes
- **Production-Ready** - Comprehensive error handling and logging
- **Advanced Voice Cloning** - 13 prosody parameters for complete voice control
- **Voice Cloning Parameters** - Speed, pitch, emotion, emphasis, pauses, breath patterns, and more

### 🎙️ **Advanced Podcast Generation (NEW in v2.1.0)**
- **14 Professional Podcast Styles**: Interview, Debate, News Report, Educational, Storytelling, Panel Discussion, Documentary, Quick Tips, Deep Dive, Roundup, and more
- **Multi-Voice Support**: Different speakers for different roles (host, expert, moderator, panelists)
- **Customizable Length & Tone**: Short (2-8 min) to Extended (30+ min) with 8 different tone options
- **Intelligent Content Synthesis**: AI-powered script generation with n8n RAG integration

### 📁 **Multi-Source Content Processing (NEW in v2.1.0)**
- **20+ File Types**: PDF, DOCX, TXT, MD, CSV, XLSX, MP3, WAV, MP4, AVI, URLs, YouTube videos/playlists/channels, PPTX, code files, images (OCR)
- **Advanced Filtering**: Date range, file type, size, tags, location-based filtering
- **Batch Processing**: Handle hundreds of sources efficiently with parallel processing
- **Smart Content Prioritization**: AI selects most relevant content automatically

### 📋 **Blueprint Generation (NEW in v2.1.0)**
- **5 Blueprint Styles**: Comprehensive, Executive, Technical, Educational, Reference
- **Multiple Output Formats**: Markdown, PDF, HTML, DOCX, JSON
- **Intelligent Documentation**: AI-powered synthesis from multiple sources
- **Structured Output**: Table of contents, citations, metadata, and professional formatting

### 💬 **Interactive Chat Interface (NEW in v2.1.0)**
- **Rich Terminal UI**: Beautiful formatting with syntax highlighting, tables, and markdown rendering
- **Session Management**: Save, load, resume conversations with full history
- **Real-time Streaming**: Live responses from n8n RAG workflows
- **Export Capabilities**: JSON and Markdown export of chat sessions

### 🔄 **Workflow Management (NEW in v2.1.0)**
- **Multiple n8n Workflows**: Manage different RAG workflows for various use cases
- **Connection Testing**: Automated workflow health checks
- **Default Workflow**: Set preferred workflows for different tasks
- **Import/Export**: Backup and share workflow configurations

### YouTube Integration
- **Interactive chat** with YouTube video transcripts using advanced AI models
- **Automated channel monitoring** with configurable intervals (daily, weekly, custom)
- **Bulk import** from channels, playlists, and URL files with comprehensive filtering
- **Advanced filtering** by duration, keywords, view count, exclude shorts/live streams
- **Video metadata extraction** and persistent storage with SQLite database
- **Intelligent transcript processing** with punctuation restoration and formatting

### Text-to-Speech (TTS)
- **Support for 6 TTS libraries**: Kokoro, OpenVoice v2, MeloTTS, Chatterbox, Edge TTS, Google TTS
- **Automated installer** with CPU-only support for compatibility
- **Configurable voice selection** and audio settings per library
- **Retry logic and timeout handling** for robust audio generation
- **Podcast-style audio overviews** with natural speech patterns

### Intelligent Rate Limiting
- **Smart queue system** to prevent YouTube IP blocking and API quota exhaustion
- **Maximum 5 videos per day** processing limit (configurable)
- **1-2 hour delays** between video processing attempts with smart distribution
- **Exponential backoff** on rate limit detection (2+ hour delays)
- **Distributed processing** throughout the day instead of bulk operations
- **Automatic rescheduling** of failed videos with intelligent retry logic

### Background Service
- **Automated channel monitoring** with APScheduler for cross-platform scheduling
- **Daily video discovery scans** at configurable times (default: 8 AM)
- **Continuous queue processing** every 2 hours respecting rate limits
- **Health checks and stuck job detection** every 30 minutes

## 🚀 Quick Start Options

### 📦 **Python Package (PyPI)**
```bash
pip install youtube-chat-cli
youtube-chat --help
```

### 🤖 **MCP Server for AI Assistants (npm)**
```bash
npx jaegis-youtube-chat-mcp
```

### 🔌 **MCP Client Configuration**
```json
{
  "mcpServers": {
    "jaegis-youtube-chat": {
      "command": "npx",
      "args": ["jaegis-youtube-chat-mcp"]
    }
  }
}
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn youtube_chat_cli_main.api_server:app --reload --port 8556
```

### Health Endpoints

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe

## 📦 Installation

### From Source

```bash
# Install with development dependencies
pip install -e .
pip install -r requirements.txt -r youtube_chat_cli_main/api_requirements.txt

# Run tests
pytest -q
```

### Using uv (Recommended)

```bash
# Install uv
python -m pip install -U uv

# Lock dependencies
uv lock

# Run tests
uv run --with dev pytest -q
```

### Docker

```bash
docker build -t jaegis-api .
docker run --rm -p 8556:8556 jaegis-api
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8556

# LLM Configuration
OPENROUTER_API_KEYS=key1,key2,key3,...  # 31 keys for rotation

# Database
DATABASE_URL=sqlite:///./data.db

# Logging
LOG_LEVEL=INFO
```

## 🏗️ Architecture

### System Overview

```
youtube_chat_cli_main/
├── services/          # 33 service modules
│   ├── llm/          # LLM implementations
│   ├── tts/          # TTS orchestrator & engines
│   ├── rag/          # RAG engine
│   ├── content/      # Content processing
│   ├── search/       # Search services
│   ├── storage/      # Vector store & sessions
│   ├── integration/  # Google Drive, n8n, embeddings
│   └── background/   # Background tasks
├── api/              # 13 API modules
│   ├── routes/       # API endpoints
│   ├── models/       # Request/response models
│   ├── middleware/   # CORS, error handling
│   └── server.py     # FastAPI factory
├── cli/              # 6 CLI modules
│   └── commands/     # Command implementations
├── utils/            # 4 utility modules
└── tests/            # 4 test packages
```

## 🎙️ Advanced Voice Cloning Parameters (v2.0.0)

Generate natural-sounding speech with complete prosody control using 13 advanced parameters:

### CLI Usage
```bash
# Basic generation
youtube-chat voice-clone generate --voice-id 1 --text "Hello world" --output output.wav

# With emotion and pitch
youtube-chat voice-clone generate --voice-id 1 --text "I'm so happy!" \
  --emotion happy --pitch 3 --exaggeration 0.7 --output happy.wav

# Professional presentation
youtube-chat voice-clone generate --voice-id 1 --text "Welcome to our report" \
  --speed 1.0 --pitch 1 --emotion confident --emphasis "earnings" "report" \
  --output presentation.wav

# View available presets
youtube-chat voice-clone presets
```

### Available Parameters
- **Speed** (0.5-2.0) - Speech rate multiplier
- **Pitch** (-12 to +12) - Pitch adjustment in semitones
- **Exaggeration** (0.25-2.0) - Emotional intensity
- **Emotion** (10 types) - neutral, happy, sad, angry, joyful, excited, surprised, curious, confident, empathetic
- **Emphasis** - Words to emphasize in speech
- **Pauses** - Silence before/after speech (0-5000ms)
- **Breath Frequency** - Insert breath every N words
- **CFG Weight, Temperature, Top P, Min P** - Advanced generation parameters
- **Seed** - For reproducible results

### Documentation
- **[Parameter Tuning Guide](docs/voice-cloning/PARAMETER_TUNING_GUIDE.md)** - Complete parameter reference
- **[CLI Usage Guide](docs/voice-cloning/CLI_ADVANCED_USAGE.md)** - CLI examples and patterns
- **[API Reference](docs/voice-cloning/API_ADVANCED_REFERENCE.md)** - REST API documentation

## 📚 Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Getting Started](docs/getting-started/)** - Installation and setup guides
- **[Architecture](docs/architecture/)** - System design and modular structure
- **[API Reference](docs/api/)** - REST API documentation
- **[Guides](docs/guides/)** - User guides and tutorials
- **[Development](docs/development/)** - Contributing and deployment
- **[Integrations](docs/integrations/)** - N8N, Google Drive, MCP server
- **[Voice Cloning](docs/voice-cloning/)** - Advanced voice cloning with prosody control

## 🧪 Testing

```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=youtube_chat_cli_main

# Run specific test file
pytest tests/test_api_endpoints.py

# Run with verbose output
pytest -v
```

## 🐳 Docker

```bash
# Build image
docker build -t jaegis-api .

# Run container
docker run --rm -p 8556:8556 jaegis-api

# Run with environment file
docker run --rm -p 8556:8556 --env-file .env jaegis-api
```

## 🔄 CI/CD

GitHub Actions workflows:

- **Quality Assurance** - `.github/workflows/quality-assurance.yml`
  - Lint, test, and coverage on Ubuntu, Windows, macOS
- **Security Audit** - `.github/workflows/security-audit.yml`
  - Semgrep, Bandit, Gitleaks, ESLint

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for researchers and content creators**

Transform your research into actionable insights with AI-powered intelligence! 🚀✨

