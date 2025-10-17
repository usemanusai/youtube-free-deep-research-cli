# Installation Guide

Comprehensive installation instructions for YouTube Free Deep Research CLI.

## System Requirements

- **Python**: 3.13 or higher
- **OS**: Linux, macOS, Windows
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB minimum for dependencies
- **Network**: Stable internet connection

## Installation Methods

### Method 1: From Source (Recommended)

```bash
# Clone repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r youtube_chat_cli_main/api_requirements.txt

# Verify installation
python -m pytest -q
```

### Method 2: Using uv (Recommended)

```bash
# Install uv
python -m pip install -U uv

# Clone repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Lock dependencies
uv lock

# Sync environment
uv pip sync

# Run tests
uv run pytest -q
```

### Method 3: Development Installation

```bash
# Clone repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### Method 4: Docker

```bash
# Build image
docker build -t jaegis-api .

# Run container
docker run --rm -p 8556:8556 jaegis-api

# Run with environment file
docker run --rm -p 8556:8556 --env-file .env jaegis-api

# Run with volume mount
docker run --rm -p 8556:8556 -v $(pwd):/app jaegis-api
```

## Verification

### Check Python Version

```bash
python --version
# Should output: Python 3.13.x
```

### Verify Installation

```bash
# Test imports
python -c "import youtube_chat_cli_main; print('✓ Installation successful')"

# Run tests
pytest -q

# Check API server
uvicorn youtube_chat_cli_main.api_server:app --help
```

### Health Check

```bash
# Start server
uvicorn youtube_chat_cli_main.api_server:app --port 8556 &

# Check health
curl http://localhost:8556/health/live
curl http://localhost:8556/health/ready
```

## Troubleshooting

### Python Version Error

```bash
# Check version
python --version

# If wrong version, use python3.13
python3.13 -m venv venv
```

### Missing Dependencies

```bash
# Reinstall all dependencies
pip install --upgrade pip
pip install -r requirements.txt -r youtube_chat_cli_main/api_requirements.txt
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall package
pip install -e .
```

### Port Already in Use

```bash
# Use different port
uvicorn youtube_chat_cli_main.api_server:app --port 8557
```

### Permission Denied (Linux/macOS)

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run with python
python scripts/install_dependencies.sh
```

## Next Steps

1. **Configure Environment** - See [Configuration](configuration.md)
2. **Quick Start** - See [Quick Start Guide](quick-start.md)
3. **Run Tests** - `pytest -q`
4. **Start Server** - `uvicorn youtube_chat_cli_main.api_server:app --reload`

## Getting Help

- Check [Troubleshooting](../development/troubleshooting.md)
- Review [Configuration](configuration.md)
- Open an issue on GitHub

---

**Installation complete?** Continue with [Configuration](configuration.md).

