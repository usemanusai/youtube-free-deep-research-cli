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

REM Use the proper launcher script
python run_api_server.py

pause

