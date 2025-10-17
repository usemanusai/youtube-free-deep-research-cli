@echo off
REM Start JAEGIS NexusSync API Server (Windows)

echo ========================================
echo JAEGIS NexusSync API Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if FastAPI is installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo.
    echo FastAPI not found. Installing API server dependencies...
    pip install -r youtube_chat_cli_main\api_requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM Start the API server
echo.
echo Starting API server on http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Use the launcher script to handle imports correctly
cd youtube_chat_cli_main
python run_api_server.py

pause

