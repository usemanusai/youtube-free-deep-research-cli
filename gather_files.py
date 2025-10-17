#!/usr/bin/env python3
"""Gather all files for GitHub upload, respecting .gitignore patterns."""

import os
import json
from pathlib import Path

# Directories to exclude (matching .gitignore)
EXCLUDE_DIRS = {
    'venv', 'tts-bridge-py310', 'node_modules', '__pycache__', '.git', 
    '.next', '.vscode', '.idea', 'chroma_db', 'outputs', 'tmp_ingest',
    '.egg-info', '.pytest_cache', 'dist', 'build', 'logs'
}

# File extensions to exclude
EXCLUDE_EXTS = {'.pyc', '.pyo', '.pyd', '.log', '.db', '.sqlite3', '.pickle', '.wav', '.tar'}

# Patterns to exclude
EXCLUDE_PATTERNS = {
    'workspace-', 'vscode-app-', '.history', '__pycache__', 'node_modules'
}

def should_exclude(path_str):
    """Check if a path should be excluded."""
    parts = Path(path_str).parts
    
    # Check directory names
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
        for pattern in EXCLUDE_PATTERNS:
            if pattern in part:
                return True
    
    # Check file extension
    if Path(path_str).suffix in EXCLUDE_EXTS:
        return True
    
    return False

def gather_files():
    """Gather all files to upload."""
    files = {}
    root = Path('.')
    
    for file_path in sorted(root.rglob('*')):
        if not file_path.is_file():
            continue
        
        if should_exclude(str(file_path)):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            rel_path = str(file_path.relative_to('.')).replace('\\', '/')
            files[rel_path] = content
        except Exception as e:
            print(f"Skipped {file_path}: {e}")
    
    return files

if __name__ == '__main__':
    files = gather_files()
    print(f"Total files to upload: {len(files)}")
    
    # Save to JSON for inspection
    with open('files_to_upload.json', 'w') as f:
        json.dump({
            'count': len(files),
            'files': list(files.keys())[:50]  # First 50 for preview
        }, f, indent=2)
    
    print("File list saved to files_to_upload.json")
    print("\nSample files:")
    for path in sorted(files.keys())[:20]:
        print(f"  {path}")

