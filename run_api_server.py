"""
JAEGIS NexusSync API Server Launcher

This script properly sets up the Python path and launches the API server.
Run this from the repository root directory (youtube-chat-cli-main).
"""

import sys
import os
from pathlib import Path

# Ensure we're running from the correct directory
current_dir = Path(__file__).parent.resolve()
os.chdir(current_dir)

# Add current directory to Python path
sys.path.insert(0, str(current_dir))

# Now import and run the API server
if __name__ == "__main__":
    # Import uvicorn
    import uvicorn

    # Run the server
    print("=" * 60)
    print("JAEGIS NexusSync API Server")
    print("=" * 60)
    print()
    print("Starting API server on http://localhost:8555")
    print("API documentation: http://localhost:8555/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print()

    # Use import string for reload to work properly
    uvicorn.run(
        "youtube_chat_cli_main.api_server:app",
        host="0.0.0.0",
        port=8555,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

