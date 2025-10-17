#!/bin/bash
# Start JAEGIS NexusSync API Server (Linux/Mac)

echo "========================================"
echo "JAEGIS NexusSync API Server"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if FastAPI is installed
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "FastAPI not found. Installing API server dependencies..."
    pip install -r youtube_chat_cli_main/api_requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install dependencies!"
        exit 1
    fi
fi

# Change to project directory
cd youtube_chat_cli_main

# Start the API server
echo ""
echo "Starting API server on http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Use the launcher script to handle imports correctly
cd youtube_chat_cli_main
python run_api_server.py

