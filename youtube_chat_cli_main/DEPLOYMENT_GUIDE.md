# 🚀 JAEGIS NexusSync - Deployment Guide

Complete guide to deploying JAEGIS NexusSync in various environments.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

### System Requirements

**Minimum:**
- Python 3.13+
- 4GB RAM
- 10GB disk space
- Windows/macOS/Linux

**Recommended:**
- Python 3.13+
- 8GB+ RAM
- 20GB+ disk space
- SSD storage

### Required Services

**Local (Free):**
- Ollama (LLM & Embeddings)
- Qdrant (Vector Store)
- Tesseract OCR

**Optional (Free Tier):**
- OpenRouter (Alternative LLM)
- Tavily (Web Search)
- Google Drive (Document Storage)

---

## 💻 Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd youtube-chat-cli-main/youtube_chat_cli_main
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Local Services

**Ollama:**
```bash
# Windows/macOS/Linux
# Download from https://ollama.ai
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

**Qdrant:**
```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or download from https://qdrant.tech
```

**Tesseract OCR:**
```bash
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

### 5. Configure Environment

```bash
# Copy example .env
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Minimum Configuration:**
```env
# LLM Settings
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434

# Embedding Settings
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text

# Vector Store Settings
VECTOR_STORE_TYPE=qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=jaegis_nexus

# OCR Settings
OCR_PROVIDER=tesseract
```

### 6. Initialize Database

```bash
python -c "from youtube_chat_cli_main.core.database import get_database; get_database()"
```

### 7. Verify Installation

```bash
python cli/main.py verify-connections
```

---

## 🏭 Production Deployment

### 1. System Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.13
sudo apt-get install python3.13 python3.13-venv python3.13-dev

# Install system dependencies
sudo apt-get install tesseract-ocr poppler-utils
```

### 2. Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/jaegis-nexus
sudo chown $USER:$USER /opt/jaegis-nexus
cd /opt/jaegis-nexus

# Clone and setup
git clone <repository-url> .
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Services

**Ollama (Systemd Service):**
```bash
# /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ollama
ExecStart=/usr/local/bin/ollama serve
Restart=always

[Install]
WantedBy=multi-user.target
```

**Qdrant (Docker):**
```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v /opt/jaegis-nexus/qdrant_data:/qdrant/storage \
  --restart unless-stopped \
  qdrant/qdrant
```

### 4. Background Service

**Systemd Service:**
```bash
# /etc/systemd/system/jaegis-nexus-bg.service
[Unit]
Description=JAEGIS NexusSync Background Service
After=network.target ollama.service docker.service

[Service]
Type=simple
User=jaegis
WorkingDirectory=/opt/jaegis-nexus
Environment="PATH=/opt/jaegis-nexus/venv/bin"
ExecStart=/opt/jaegis-nexus/venv/bin/python cli/main.py background start
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable jaegis-nexus-bg
sudo systemctl start jaegis-nexus-bg
sudo systemctl status jaegis-nexus-bg
```

### 5. MCP Server

**Systemd Service:**
```bash
# /etc/systemd/system/jaegis-nexus-mcp.service
[Unit]
Description=JAEGIS NexusSync MCP Server
After=network.target

[Service]
Type=simple
User=jaegis
WorkingDirectory=/opt/jaegis-nexus
Environment="PATH=/opt/jaegis-nexus/venv/bin"
ExecStart=/opt/jaegis-nexus/venv/bin/uvicorn youtube_chat_cli_main.mcp.server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable jaegis-nexus-mcp
sudo systemctl start jaegis-nexus-mcp
sudo systemctl status jaegis-nexus-mcp
```

### 6. Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/jaegis-nexus
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable:**
```bash
sudo ln -s /etc/nginx/sites-available/jaegis-nexus /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🐳 Docker Deployment

### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8000

# Run application
CMD ["uvicorn", "youtube_chat_cli_main.mcp.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  jaegis-nexus:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    depends_on:
      - ollama
      - qdrant
    restart: unless-stopped
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - QDRANT_URL=http://qdrant:6333

volumes:
  ollama_data:
  qdrant_data:
```

### 3. Deploy

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## ☁️ Cloud Deployment

### AWS Deployment

**1. EC2 Instance:**
- Instance Type: t3.medium (2 vCPU, 4GB RAM)
- Storage: 20GB SSD
- Security Group: Allow ports 22, 80, 443, 8000

**2. Setup:**
```bash
# SSH into instance
ssh -i key.pem ubuntu@<instance-ip>

# Follow production deployment steps
```

**3. S3 for Document Storage:**
```python
# Configure in .env
DOCUMENT_STORAGE=s3
S3_BUCKET_NAME=jaegis-nexus-docs
AWS_REGION=us-east-1
```

### Google Cloud Deployment

**1. Compute Engine:**
- Machine Type: e2-medium
- Boot Disk: 20GB SSD
- Firewall: Allow HTTP, HTTPS

**2. Cloud Run (Serverless):**
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/jaegis-nexus

# Deploy
gcloud run deploy jaegis-nexus \
  --image gcr.io/PROJECT_ID/jaegis-nexus \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check services
python cli/main.py verify-connections

# Check queue status
python cli/main.py queue-status

# Check background service
python cli/main.py background status
```

### Logs

```bash
# Application logs
tail -f /var/log/jaegis-nexus/app.log

# Systemd logs
sudo journalctl -u jaegis-nexus-bg -f
sudo journalctl -u jaegis-nexus-mcp -f
```

### Backups

```bash
# Backup database
cp data/jaegis_nexus.db backups/jaegis_nexus_$(date +%Y%m%d).db

# Backup vector store
docker exec qdrant tar czf - /qdrant/storage > backups/qdrant_$(date +%Y%m%d).tar.gz
```

### Updates

```bash
# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl restart jaegis-nexus-bg
sudo systemctl restart jaegis-nexus-mcp
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Ollama Connection Failed:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama
```

**2. Qdrant Connection Failed:**
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Restart Qdrant
docker restart qdrant
```

**3. Out of Memory:**
```bash
# Check memory usage
free -h

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**4. Permission Errors:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/jaegis-nexus

# Fix permissions
chmod +x cli/main.py
```

---

## 🎉 Success!

Your JAEGIS NexusSync deployment is complete!

**Next Steps:**
1. Configure Google Drive integration
2. Set up monitoring and alerts
3. Configure backups
4. Test the system end-to-end

For support, see:
- [API Documentation](API_DOCUMENTATION.md)
- [Testing Guide](TESTING_GUIDE.md)
- [CLI Usage Guide](CLI_USAGE_GUIDE.md)

