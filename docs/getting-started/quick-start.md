# Quick Start Guide

Get up and running with YouTube Free Deep Research CLI in 5 minutes.

## Prerequisites

- Python 3.13+
- Git
- pip or uv package manager

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using uv (recommended):

```bash
python -m pip install -U uv
uv lock
uv pip sync
```

### 4. Configure Environment

Create a `.env` file:

```bash
cp .env.template .env
# Edit .env and add your API keys
```

### 5. Run the API Server

```bash
uvicorn youtube_chat_cli_main.api_server:app --reload --port 8556
```

Visit http://localhost:8556/docs for interactive API documentation.

## Health Checks

```bash
# Check if server is alive
curl http://localhost:8556/health/live

# Check if server is ready
curl http://localhost:8556/health/ready
```

## Running Tests

```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=youtube_chat_cli_main

# Run specific test
pytest tests/test_api_endpoints.py -v
```

## Next Steps

- Read [Installation Guide](installation.md) for detailed setup
- Check [Configuration](configuration.md) for environment variables
- Review [CLI Usage](../guides/cli-usage.md) for command-line interface
- See [REST API](../api/rest-api.md) for API endpoints

## Troubleshooting

### Import Errors

```bash
pip install -r requirements.txt -r youtube_chat_cli_main/api_requirements.txt
```

### Port Already in Use

```bash
uvicorn youtube_chat_cli_main.api_server:app --port 8557
```

### Python Version Issues

Ensure you're using Python 3.13+:

```bash
python --version
```

## Common Commands

```bash
# Start development server
uvicorn youtube_chat_cli_main.api_server:app --reload

# Run tests
pytest -q

# Run with coverage
pytest --cov=youtube_chat_cli_main

# Format code
black youtube_chat_cli_main

# Lint code
flake8 youtube_chat_cli_main

# Type check
mypy youtube_chat_cli_main
```

## Docker Quick Start

```bash
# Build image
docker build -t jaegis-api .

# Run container
docker run --rm -p 8556:8556 jaegis-api

# Run with environment file
docker run --rm -p 8556:8556 --env-file .env jaegis-api
```

## Getting Help

- Check [Troubleshooting](../development/troubleshooting.md)
- Review [Configuration](configuration.md)
- See [Installation Guide](installation.md)
- Open an issue on GitHub

---

**Ready to dive deeper?** Check out the [full documentation](../README.md).

