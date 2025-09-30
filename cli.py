#!/usr/bin/env python3
"""
Backward compatibility wrapper for YouTube Chat CLI.

This file maintains backward compatibility with the old CLI entry point.
The actual implementation has been moved to src/youtube_chat_cli/cli/main.py
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from youtube_chat_cli.cli.main import main
except ImportError as e:
    print(f"Error importing YouTube Chat CLI: {e}")
    print("Please ensure the package is properly installed:")
    print("  pip install -e .")
    sys.exit(1)

if __name__ == '__main__':
    main()
