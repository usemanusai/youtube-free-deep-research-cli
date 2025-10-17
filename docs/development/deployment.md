# Deployment Guide

Production deployment guide for YouTube Free Deep Research CLI.

## Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Changelog updated
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Backups created

## Deployment Methods

## 1. Docker Deployment

### Build Image

```bash
# Build image
docker build -t jaegis-api:2.0.1 .

# Build with build args
docker build -t jaegis-api:2.0.1 \
  --build-arg PYTHON_VERSION=3.13 \
  .
```

### Run Container

```bash
# Run with environment file
docker run -d \
  --name jaegis-api \
  -p 8556:8556 \
  --env-file .env.production \
  jaegis-api:2.0.1

# Run with volume mounts
docker run -d \
  --name jaegis-api \
  -p 8556:8556 \
  -v /data/db:/app/data \
  -v /data/cache:/app/cache \
  --env-file .env.production \
  jaegis-api:2.0.1
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    image: jaegis-api:2.0.1
    ports:
      - "8556:8556"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8556
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
    depends_on:
      - db
      - vector_store
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  vector_store:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage
    restart: unless-stopped
```

### Deploy with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## 2. Kubernetes Deployment

### Create Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaegis-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jaegis-api
  template:
    metadata:
      labels:
        app: jaegis-api
    spec:
      containers:
      - name: api
        image: jaegis-api:2.0.1
        ports:
        - containerPort: 8556
        env:
        - name: API_HOST
          value: "0.0.0.0"
        - name: API_PORT
          value: "8556"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8556
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8556
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace jaegis

# Create secrets
kubectl create secret generic db-secret \
  --from-literal=url=postgresql://user:password@db:5432/dbname \
  -n jaegis

# Deploy
kubectl apply -f k8s/deployment.yaml -n jaegis

# Check status
kubectl get pods -n jaegis
kubectl logs -f deployment/jaegis-api -n jaegis
```

## 3. Traditional Server Deployment

### Install Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.13
sudo apt-get install -y python3.13 python3.13-venv python3.13-dev

# Install system dependencies
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y redis-server
```

### Setup Application

```bash
# Clone repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.template .env
# Edit .env with production values
```

### Setup Systemd Service

```bash
# Create service file
sudo tee /etc/systemd/system/jaegis-api.service > /dev/null <<EOF
[Unit]
Description=JAEGIS API Server
After=network.target

[Service]
Type=notify
User=jaegis
WorkingDirectory=/home/jaegis/youtube-free-deep-research-cli
Environment="PATH=/home/jaegis/youtube-free-deep-research-cli/venv/bin"
ExecStart=/home/jaegis/youtube-free-deep-research-cli/venv/bin/uvicorn \
  youtube_chat_cli_main.api_server:app \
  --host 0.0.0.0 \
  --port 8556 \
  --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable jaegis-api
sudo systemctl start jaegis-api

# Check status
sudo systemctl status jaegis-api
```

### Setup Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/jaegis-api
upstream jaegis_api {
    server 127.0.0.1:8556;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://jaegis_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://jaegis_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Enable Nginx Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/jaegis-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 4. Cloud Deployment

### AWS EC2

```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name my-key \
  --security-groups jaegis-api

# SSH into instance
ssh -i my-key.pem ec2-user@instance-ip

# Follow traditional server deployment steps
```

### Heroku

```bash
# Create Procfile
echo "web: uvicorn youtube_chat_cli_main.api_server:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create jaegis-api
git push heroku main

# View logs
heroku logs -f
```

### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/jaegis-api

# Deploy
gcloud run deploy jaegis-api \
  --image gcr.io/PROJECT_ID/jaegis-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...
```

## Monitoring

### Health Checks

```bash
# Liveness probe
curl http://localhost:8556/health/live

# Readiness probe
curl http://localhost:8556/health/ready
```

### Logging

```bash
# View logs
docker logs jaegis-api

# Follow logs
docker logs -f jaegis-api

# Systemd logs
sudo journalctl -u jaegis-api -f
```

### Metrics

```bash
# Prometheus metrics
curl http://localhost:8556/metrics
```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump dbname > backup.sql

# Restore
psql dbname < backup.sql
```

### Vector Store Backup

```bash
# Qdrant backup
docker exec qdrant qdrant-cli backup create

# Restore
docker exec qdrant qdrant-cli backup restore
```

## Rollback

### Docker Rollback

```bash
# Stop current version
docker stop jaegis-api

# Run previous version
docker run -d --name jaegis-api jaegis-api:2.0.0
```

### Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/jaegis-api

# Rollback to previous version
kubectl rollout undo deployment/jaegis-api
```

## Performance Tuning

### API Workers

```bash
# Increase workers
uvicorn youtube_chat_cli_main.api_server:app --workers 8
```

### Database Connection Pool

```bash
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=40
```

### Caching

```bash
export CACHE_ENABLED=true
export CACHE_TTL=3600
```

---

See [Configuration](../getting-started/configuration.md) for environment setup.

