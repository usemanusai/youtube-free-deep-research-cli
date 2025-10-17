# Google Drive Integration Guide

Complete guide to integrating YouTube Free Deep Research CLI with Google Drive.

## Overview

Access and process documents from Google Drive directly through the API.

## Setup

### 1. Create Google Cloud Project

1. Visit https://console.cloud.google.com
2. Create new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials as JSON

### 2. Configure Credentials

```bash
# Save credentials file
cp client_secret.json youtube_chat_cli_main/

# Set environment variable
export GOOGLE_DRIVE_CREDENTIALS_FILE=client_secret.json
export GOOGLE_DRIVE_TOKEN_FILE=token.pickle
```

### 3. Authenticate

```bash
# First run will prompt for authentication
youtube-chat gdrive auth

# Or via API
python -c "from youtube_chat_cli_main.services.integration import GDriveService; GDriveService().authenticate()"
```

## Configuration

### Environment Variables

```bash
# Credentials
GOOGLE_DRIVE_CREDENTIALS_FILE=client_secret.json
GOOGLE_DRIVE_TOKEN_FILE=token.pickle

# Settings
GOOGLE_DRIVE_TIMEOUT=30
GOOGLE_DRIVE_CACHE_ENABLED=true
GOOGLE_DRIVE_CACHE_TTL=3600
```

### Configuration File

```yaml
google_drive:
  credentials_file: client_secret.json
  token_file: token.pickle
  timeout: 30
  cache:
    enabled: true
    ttl: 3600
```

## Usage

### List Files

```bash
# List all files
youtube-chat gdrive list

# List with filter
youtube-chat gdrive list --query "name contains 'research'"

# List specific folder
youtube-chat gdrive list --folder-id FOLDER_ID
```

### Download File

```bash
# Download file
youtube-chat gdrive download FILE_ID --output document.pdf

# Download and process
youtube-chat gdrive download FILE_ID --process --extract-text
```

### Upload File

```bash
# Upload file
youtube-chat gdrive upload /path/to/file.pdf

# Upload to specific folder
youtube-chat gdrive upload /path/to/file.pdf --folder-id FOLDER_ID
```

### Search Files

```bash
# Search by name
youtube-chat gdrive search "research paper"

# Search by type
youtube-chat gdrive search --type "application/pdf"

# Search in folder
youtube-chat gdrive search "query" --folder-id FOLDER_ID
```

## Python API

### List Files

```python
from youtube_chat_cli_main.services.integration import GDriveService

gdrive = GDriveService()

# List all files
files = gdrive.list_files()
for file in files:
    print(f"{file['name']} ({file['id']})")

# List with query
files = gdrive.list_files(query="name contains 'research'")

# List in folder
files = gdrive.list_files(folder_id="FOLDER_ID")
```

### Download File

```python
# Download file
gdrive.download_file(file_id, output_path="document.pdf")

# Download and get content
content = gdrive.download_file_content(file_id)
```

### Upload File

```python
# Upload file
file_id = gdrive.upload_file(
    file_path="/path/to/file.pdf",
    folder_id="FOLDER_ID"
)

# Upload with metadata
file_id = gdrive.upload_file(
    file_path="/path/to/file.pdf",
    name="Custom Name",
    description="File description"
)
```

### Search Files

```python
# Search files
results = gdrive.search_files("research paper")

# Search with filters
results = gdrive.search_files(
    query="name contains 'research'",
    file_type="application/pdf"
)
```

## Integration with RAG

### Index Google Drive Documents

```bash
# Index all PDFs from Google Drive
youtube-chat gdrive index --file-type "application/pdf"

# Index specific folder
youtube-chat gdrive index --folder-id FOLDER_ID

# Index and search
youtube-chat gdrive index --folder-id FOLDER_ID
youtube-chat search vector "search query"
```

### Python Integration

```python
from youtube_chat_cli_main.services.integration import GDriveService
from youtube_chat_cli_main.services.rag import RAGEngine

gdrive = GDriveService()
rag = RAGEngine()

# Get files from Google Drive
files = gdrive.list_files(query="name contains 'research'")

# Download and index
for file in files:
    content = gdrive.download_file_content(file['id'])
    rag.add_document(content, metadata={"source": file['name']})

# Search
results = rag.search("search query")
```

## Sharing and Permissions

### Share File

```bash
# Share with email
youtube-chat gdrive share FILE_ID --email user@example.com --role reader

# Share with link
youtube-chat gdrive share FILE_ID --role reader --share-link
```

### Check Permissions

```bash
# List permissions
youtube-chat gdrive permissions FILE_ID

# Add permission
youtube-chat gdrive permissions FILE_ID --add user@example.com --role editor

# Remove permission
youtube-chat gdrive permissions FILE_ID --remove user@example.com
```

## Monitoring

### View Sync Status

```bash
# Check sync status
youtube-chat gdrive status

# View recent syncs
youtube-chat gdrive sync-history
```

### Enable Logging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# View logs
docker logs -f jaegis-api | grep gdrive
```

## Troubleshooting

### Authentication Error

**Error**: `Authentication failed`

**Solution**:
```bash
# Re-authenticate
youtube-chat gdrive auth

# Check credentials file
ls -la client_secret.json

# Check token file
ls -la token.pickle
```

### Connection Error

**Error**: `Connection error: Failed to connect to Google Drive`

**Solution**:
```bash
# Check internet connection
ping 8.8.8.8

# Check Google Drive API status
curl https://www.google.com/drive/

# Increase timeout
export GOOGLE_DRIVE_TIMEOUT=60
```

### File Not Found

**Error**: `File not found`

**Solution**:
```bash
# List files to find ID
youtube-chat gdrive list

# Check file permissions
youtube-chat gdrive permissions FILE_ID

# Verify file exists
youtube-chat gdrive search "filename"
```

### Quota Exceeded

**Error**: `Quota exceeded`

**Solution**:
```bash
# Wait for quota reset (usually 24 hours)

# Check quota usage
youtube-chat gdrive quota

# Reduce batch size
export GDRIVE_BATCH_SIZE=5
```

## Best Practices

1. **Organize Files** - Use folders for organization
2. **Set Permissions** - Restrict access appropriately
3. **Monitor Quota** - Track API quota usage
4. **Cache Results** - Enable caching for performance
5. **Error Handling** - Implement retry logic
6. **Logging** - Enable logging for debugging

## Advanced Usage

### Batch Operations

```python
# Batch download
files = gdrive.list_files(query="name contains 'research'")
for file in files:
    gdrive.download_file(file['id'], f"downloads/{file['name']}")
```

### Scheduled Sync

```bash
# Sync every hour
0 * * * * youtube-chat gdrive index --folder-id FOLDER_ID
```

### Custom Metadata

```python
# Add custom metadata
gdrive.upload_file(
    file_path="/path/to/file.pdf",
    properties={
        "category": "research",
        "author": "John Doe",
        "date": "2025-10-17"
    }
)
```

---

See [REST API](../api/rest-api.md) for API endpoints.

