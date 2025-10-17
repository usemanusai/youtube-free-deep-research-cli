# Documentation Index

Complete index of all documentation for YouTube Free Deep Research CLI v2.0.1.

## 📚 Main Documentation Structure

### Root Level
- **[README.md](README.md)** - Main project overview and quick start
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - This file
- **[LICENSE](LICENSE)** - MIT License
- **[pyproject.toml](pyproject.toml)** - Python package configuration
- **[setup.py](setup.py)** - Legacy setup script

### Documentation Directory (`/docs`)

## 🎯 Getting Started

**Location**: `/docs/getting-started/`

1. **[Quick Start](docs/getting-started/quick-start.md)** ⭐ START HERE
   - 5-minute setup guide
   - Basic commands
   - Health checks
   - Common troubleshooting

2. **[Installation Guide](docs/getting-started/installation.md)**
   - System requirements
   - Multiple installation methods
   - Docker setup
   - Verification steps

3. **[Configuration](docs/getting-started/configuration.md)**
   - Environment variables
   - Configuration files
   - Environment-specific setup
   - Secrets management

## 🏗️ Architecture

**Location**: `/docs/architecture/`

1. **[System Overview](docs/architecture/overview.md)**
   - High-level architecture diagram
   - Component breakdown
   - Data flow
   - Technology stack

2. **[Modular Structure](docs/architecture/modular-structure.md)**
   - 60+ file organization
   - Service modules (33 total)
   - API modules (13 total)
   - CLI modules (6 total)
   - Utility modules (4 total)

## 🔌 API Reference

**Location**: `/docs/api/`

1. **[REST API](docs/api/rest-api.md)**
   - Health endpoints
   - Chat endpoints
   - File endpoints
   - Search endpoints
   - Configuration endpoints
   - Background job endpoints
   - Error responses
   - Rate limiting

2. **[WebSocket API](docs/api/websocket-api.md)**
   - Connection management
   - Message format
   - Client/server messages
   - JavaScript client example
   - Python client example
   - Error handling

## 📖 User Guides

**Location**: `/docs/guides/`

1. **[CLI Usage](docs/guides/cli-usage.md)**
   - All CLI commands
   - Chat commands
   - File commands
   - Search commands
   - Configuration commands
   - Background job commands
   - RAG commands
   - Global options
   - Examples

2. **[RAG Engine](docs/guides/rag-engine.md)**
   - Architecture overview
   - Component breakdown
   - Setup instructions
   - Usage examples
   - Configuration options
   - Advanced usage
   - Performance optimization
   - Troubleshooting

3. **[TTS Configuration](docs/guides/tts-configuration.md)**
   - Engine overview
   - Setup for each engine
   - CLI usage
   - Advanced configuration
   - Troubleshooting
   - Performance tips

4. **[OpenRouter Integration](docs/guides/openrouter-integration.md)**
   - Setup instructions
   - Available models
   - Configuration options
   - Key rotation strategies
   - Usage examples
   - Error handling
   - Monitoring
   - Troubleshooting

## 👨‍💻 Development

**Location**: `/docs/development/`

1. **[Contributing](docs/development/contributing.md)**
   - Getting started
   - Development workflow
   - Code style
   - Type hints
   - Docstrings
   - Testing requirements
   - Commit guidelines
   - Pull request process
   - Adding new features
   - Code review checklist

2. **[Testing](docs/development/testing.md)**
   - Test structure
   - Running tests
   - Writing tests
   - Test fixtures
   - Test markers
   - Coverage
   - Integration tests
   - Performance testing
   - Debugging tests
   - CI/CD integration

3. **[Deployment](docs/development/deployment.md)**
   - Pre-deployment checklist
   - Docker deployment
   - Kubernetes deployment
   - Traditional server deployment
   - Cloud deployment (AWS, Heroku, GCP)
   - Monitoring
   - Backup and recovery
   - Rollback procedures
   - Performance tuning

4. **[Troubleshooting](docs/development/troubleshooting.md)**
   - Installation issues
   - Configuration issues
   - API server issues
   - LLM service issues
   - TTS service issues
   - RAG engine issues
   - Database issues
   - Testing issues
   - Performance issues
   - Logging and debugging

## 🔗 Integrations

**Location**: `/docs/integrations/`

1. **[N8N Workflows](docs/integrations/n8n.md)**
   - Setup instructions
   - Basic workflow
   - Advanced workflows
   - N8N nodes
   - Error handling
   - Examples
   - Testing
   - Monitoring
   - Best practices

2. **[Google Drive](docs/integrations/google-drive.md)**
   - Setup instructions
   - Configuration
   - CLI usage
   - Python API
   - RAG integration
   - Sharing and permissions
   - Monitoring
   - Troubleshooting
   - Best practices

3. **[MCP Server](docs/integrations/mcp-server.md)**
   - Installation
   - Configuration
   - Available tools
   - Usage examples
   - Troubleshooting
   - Development
   - Best practices

## 📊 Documentation Statistics

- **Total Documentation Files**: 20+
- **Total Sections**: 6 main categories
- **Code Examples**: 100+
- **Troubleshooting Entries**: 50+
- **API Endpoints Documented**: 20+
- **CLI Commands Documented**: 30+

## 🔍 Quick Navigation

### By Role

**For New Users**
1. [Quick Start](docs/getting-started/quick-start.md)
2. [Installation Guide](docs/getting-started/installation.md)
3. [Configuration](docs/getting-started/configuration.md)
4. [CLI Usage](docs/guides/cli-usage.md)

**For Developers**
1. [System Overview](docs/architecture/overview.md)
2. [Modular Structure](docs/architecture/modular-structure.md)
3. [REST API](docs/api/rest-api.md)
4. [Contributing](docs/development/contributing.md)
5. [Testing](docs/development/testing.md)

**For DevOps/Deployment**
1. [Configuration](docs/getting-started/configuration.md)
2. [Deployment](docs/development/deployment.md)
3. [Troubleshooting](docs/development/troubleshooting.md)

**For Integration**
1. [N8N Workflows](docs/integrations/n8n.md)
2. [Google Drive](docs/integrations/google-drive.md)
3. [MCP Server](docs/integrations/mcp-server.md)

### By Topic

**API & Integration**
- [REST API](docs/api/rest-api.md)
- [WebSocket API](docs/api/websocket-api.md)
- [N8N Workflows](docs/integrations/n8n.md)
- [MCP Server](docs/integrations/mcp-server.md)

**Configuration & Setup**
- [Installation Guide](docs/getting-started/installation.md)
- [Configuration](docs/getting-started/configuration.md)
- [TTS Configuration](docs/guides/tts-configuration.md)
- [OpenRouter Integration](docs/guides/openrouter-integration.md)

**Features & Usage**
- [CLI Usage](docs/guides/cli-usage.md)
- [RAG Engine](docs/guides/rag-engine.md)
- [Google Drive](docs/integrations/google-drive.md)

**Development & Deployment**
- [Contributing](docs/development/contributing.md)
- [Testing](docs/development/testing.md)
- [Deployment](docs/development/deployment.md)
- [Troubleshooting](docs/development/troubleshooting.md)

## 📝 Documentation Standards

All documentation follows these standards:

- **Markdown Format** - All files use standard Markdown
- **Code Examples** - Practical, runnable examples
- **Troubleshooting** - Common issues and solutions
- **Cross-References** - Links between related documents
- **Table of Contents** - Easy navigation
- **Clear Structure** - Logical organization
- **Professional Tone** - Clear and concise writing

## 🔄 Documentation Updates

Documentation is updated with each release:

- **v2.0.1** - Current version
- **Previous Versions** - See [CHANGELOG](CHANGELOG.md)

## 📞 Getting Help

- **Documentation**: Start with [Quick Start](docs/getting-started/quick-start.md)
- **Troubleshooting**: See [Troubleshooting Guide](docs/development/troubleshooting.md)
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: use.manus.ai@gmail.com

## 🎯 Next Steps

1. **New to the project?** → Start with [Quick Start](docs/getting-started/quick-start.md)
2. **Want to contribute?** → Read [Contributing](docs/development/contributing.md)
3. **Need to deploy?** → Check [Deployment](docs/development/deployment.md)
4. **Having issues?** → See [Troubleshooting](docs/development/troubleshooting.md)

---

**Last Updated**: 2025-10-17
**Version**: 2.0.1
**Status**: Complete and Production-Ready

