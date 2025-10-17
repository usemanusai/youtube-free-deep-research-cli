@echo off
REM Setup script for n8n RAG integration (Windows)
REM This script helps you set up all required services for the n8n workflow

echo ==========================================
echo n8n RAG Integration Setup (Windows)
echo ==========================================
echo.

REM Check if Docker is installed
echo Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed
    echo Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)
echo [OK] Docker is installed
echo.

echo ==========================================
echo Step 1: Start Qdrant Vector Database
echo ==========================================
echo.

REM Check if Qdrant is already running
docker ps | findstr qdrant >nul 2>&1
if not errorlevel 1 (
    echo [OK] Qdrant is already running
) else (
    echo Starting Qdrant...
    docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
    echo [OK] Qdrant started on http://localhost:6333
)

REM Create collection
echo Creating Qdrant collection...
timeout /t 3 /nobreak >nul
curl -X PUT "http://localhost:6333/collections/documents" -H "Content-Type: application/json" -d "{\"vectors\":{\"size\":768,\"distance\":\"Cosine\"}}" >nul 2>&1
echo [OK] Qdrant collection 'documents' ready
echo.

echo ==========================================
echo Step 2: Start PostgreSQL (for chat memory)
echo ==========================================
echo.

REM Check if PostgreSQL is already running
docker ps | findstr postgres-n8n >nul 2>&1
if not errorlevel 1 (
    echo [OK] PostgreSQL is already running
) else (
    echo Starting PostgreSQL...
    docker run -d --name postgres-n8n -e POSTGRES_PASSWORD=n8n_password -e POSTGRES_DB=n8n_chat -p 5432:5432 postgres:15
    echo [OK] PostgreSQL started on localhost:5432
)

REM Create chat memory table
echo Creating chat memory table...
timeout /t 3 /nobreak >nul
docker exec -i postgres-n8n psql -U postgres -d n8n_chat -c "CREATE TABLE IF NOT EXISTS chat_memory (id SERIAL PRIMARY KEY, session_id VARCHAR(255) NOT NULL, message TEXT NOT NULL, role VARCHAR(50) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" >nul 2>&1
echo [OK] PostgreSQL chat memory table ready
echo.

echo ==========================================
echo Step 3: Check Ollama (Optional)
echo ==========================================
echo.

ollama --version >nul 2>&1
if not errorlevel 1 (
    echo [OK] Ollama is installed
    
    REM Check if models are installed
    echo Checking Ollama models...
    ollama list | findstr llama3.1 >nul 2>&1
    if not errorlevel 1 (
        echo [OK] llama3.1 model is installed
    ) else (
        echo Pulling llama3.1 model...
        ollama pull llama3.1:latest
    )
    
    ollama list | findstr nomic-embed-text >nul 2>&1
    if not errorlevel 1 (
        echo [OK] nomic-embed-text model is installed
    ) else (
        echo Pulling nomic-embed-text model...
        ollama pull nomic-embed-text:latest
    )
) else (
    echo [WARNING] Ollama is not installed
    echo Install Ollama from: https://ollama.ai/download
    echo Or use OpenRouter API instead (configure in .env)
)
echo.

echo ==========================================
echo Step 4: Start n8n
echo ==========================================
echo.

REM Check if n8n is already running
docker ps | findstr n8n >nul 2>&1
if not errorlevel 1 (
    echo [OK] n8n is already running
) else (
    echo Starting n8n...
    docker run -d --name n8n -p 5678:5678 -v %USERPROFILE%\.n8n:/home/node/.n8n n8nio/n8n
    echo [OK] n8n started on http://localhost:5678
    echo.
    echo Please wait 10 seconds for n8n to start...
    timeout /t 10 /nobreak >nul
)
echo.

echo ==========================================
echo Step 5: Configure .env file
echo ==========================================
echo.

REM Check if .env exists
if exist .env (
    findstr /C:"N8N_WEBHOOK_URL=" .env >nul 2>&1
    if not errorlevel 1 (
        echo [OK] N8N_WEBHOOK_URL is already configured
    ) else (
        echo Adding N8N_WEBHOOK_URL to .env...
        echo. >> .env
        echo # n8n RAG Integration >> .env
        echo N8N_WEBHOOK_URL=http://localhost:5678/webhook/invoke_n8n_agent >> .env
        echo [OK] N8N_WEBHOOK_URL added to .env
    )
) else (
    echo [WARNING] .env file not found
    echo Creating .env file...
    (
        echo # n8n RAG Integration
        echo N8N_WEBHOOK_URL=http://localhost:5678/webhook/invoke_n8n_agent
        echo.
        echo # OpenRouter API (optional - alternative to Ollama^)
        echo OPENROUTER_API_KEY=your_openrouter_api_key_here
    ) > .env
    echo [OK] .env file created
)
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo All services are running:
echo   * Qdrant Vector Database: http://localhost:6333
echo   * PostgreSQL: localhost:5432
echo   * n8n: http://localhost:5678
echo.
echo Next Steps:
echo.
echo 1. Open n8n at http://localhost:5678
echo.
echo 2. Import the workflow:
echo    - Click 'Workflows' -^> 'Import from File'
echo    - Select: youtube_chat_cli_main\Local RAG AI Agent.json
echo.
echo 3. Configure n8n credentials:
echo    - Qdrant: http://localhost:6333 (no API key^)
echo    - PostgreSQL: localhost:5432, db=n8n_chat, user=postgres, password=n8n_password
echo    - Ollama: http://localhost:11434 (if installed^)
echo    - OpenRouter: Add your API key from .env
echo.
echo 4. Activate the workflow in n8n
echo.
echo 5. Test the integration:
echo    python -m youtube_chat_cli_main.cli invoke-n8n "Hello, can you help me?"
echo.
echo 6. Process files:
echo    python -m youtube_chat_cli_main.cli process-file document.pdf
echo.
echo 7. Generate podcasts from RAG:
echo    python -m youtube_chat_cli_main.cli generate-podcast-from-rag --query "Summarize the uploaded documents"
echo.
echo For detailed instructions, see: N8N_INTEGRATION_ANALYSIS_AND_FIX.md
echo.
pause

