@echo off
echo ============================================================
echo JAEGIS NexusSync - Restarting API Server
echo ============================================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting API server on port 8555...
echo Press Ctrl+C to stop the server
echo.

python youtube_chat_cli_main\api_server.py

pause

