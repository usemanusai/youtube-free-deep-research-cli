# 🎙️ YouTube Free Deep Research CLI

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/usemanusai/youtube-free-deep-research-cli)
[![JAEGIS](https://img.shields.io/badge/JAEGIS-AI%20Powered-purple.svg)](https://github.com/usemanusai)
[![Release](https://img.shields.io/badge/release-v2.0.1-brightgreen.svg)](https://github.com/usemanusai/youtube-free-deep-research-cli/releases)

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

## 📚 Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Getting Started](docs/getting-started/)** - Installation and setup guides
- **[Architecture](docs/architecture/)** - System design and modular structure
- **[API Reference](docs/api/)** - REST API documentation
- **[Guides](docs/guides/)** - User guides and tutorials
- **[Development](docs/development/)** - Contributing and deployment
- **[Integrations](docs/integrations/)** - N8N, Google Drive, MCP server

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

