#!/usr/bin/env python3
"""
NUCLEAR OPTION: Remove ALL secrets from git history using git-filter-repo
This is the most aggressive approach - removes secrets from EVERY commit
"""

import subprocess
import os
import sys
import tempfile

def run_cmd(cmd, check=True):
    """Run command and return output."""
    print(f"  Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    return True

def main():
    print("🔥 NUCLEAR SECRET REMOVAL - USING GIT-FILTER-REPO 🔥\n")
    
    # Step 1: Create a list of files to completely remove
    print("Step 1: Creating file removal list...")
    files_to_remove = [
        'client_secret.json',
        '.env',
        '.env.local',
        '.env.production',
        '.env.staging',
        'OPENROUTER_KEY_ROTATION_IMPLEMENTATION.md',
        'credentials.json',
        'firebase-config.json',
        'google-credentials.json',
    ]
    
    # Create a temporary file with the list
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for file in files_to_remove:
            f.write(f"{file}\n")
        remove_list = f.name
    
    print(f"  Files to remove: {len(files_to_remove)}")
    
    # Step 2: Remove files using git-filter-repo
    print("\nStep 2: Removing files from git history...")
    cmd = f'git filter-repo --use-mailmap --force --paths-from-file "{remove_list}"'
    run_cmd(cmd)
    
    # Step 3: Create a Python script to redact secrets in all files
    print("\nStep 3: Creating secret redaction script...")
    redact_script = '''
import re
import sys

# Patterns to redact
patterns = [
    (r'sk-or-v1-[a-zA-Z0-9]{64,}', 'REDACTED_OPENROUTER_KEY'),
    (r'tvly-[a-zA-Z0-9_-]{20,}', 'REDACTED_TAVILY_KEY'),
    (r'AIza[0-9A-Za-z\\-_]{35}', 'REDACTED_GOOGLE_API_KEY'),
    (r'GOCSPX-[a-zA-Z0-9_-]{20,}', 'REDACTED_GOOGLE_SECRET'),
    (r'1079692665134-[a-zA-Z0-9_-]{20,}', 'REDACTED_GOOGLE_CLIENT_ID'),
    (r'ya29\\.[a-zA-Z0-9_-]{100,}', 'REDACTED_GOOGLE_OAUTH_TOKEN'),
    (r'[a-zA-Z0-9_-]{20,}@[a-zA-Z0-9_-]{20,}\\.iam\\.gserviceaccount\\.com', 'REDACTED_SERVICE_ACCOUNT'),
    (r'Bearer [a-zA-Z0-9_.-]{50,}', 'Bearer REDACTED_TOKEN'),
    (r'api[_-]?key["\\'\\s]*[:=]["\\'\\s]*[a-zA-Z0-9_-]{20,}', 'api_key=REDACTED'),
    (r'secret["\\'\\s]*[:=]["\\'\\s]*[a-zA-Z0-9_-]{20,}', 'secret=REDACTED'),
    (r'password["\\'\\s]*[:=]["\\'\\s]*[a-zA-Z0-9_-]{20,}', 'password=REDACTED'),
    (r'token["\\'\\s]*[:=]["\\'\\s]*[a-zA-Z0-9_.-]{20,}', 'token=REDACTED'),
]

try:
    with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    modified = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            modified = True
            content = new_content
    
    if modified:
        with open(sys.argv[1], 'w', encoding='utf-8') as f:
            f.write(content)
except Exception as e:
    pass
'''
    
    with open('_redact_secrets.py', 'w') as f:
        f.write(redact_script)
    
    # Step 4: Apply redaction to all files
    print("\nStep 4: Redacting secrets from all files...")
    cmd = 'git filter-repo --use-mailmap --force --tree-filter "python _redact_secrets.py $file_path"'
    run_cmd(cmd)
    
    # Step 5: Remove .history directory
    print("\nStep 5: Removing .history directory...")
    cmd = 'git filter-repo --use-mailmap --force --invert-paths --path .history'
    run_cmd(cmd)
    
    # Step 6: Garbage collection
    print("\nStep 6: Running garbage collection...")
    run_cmd('git reflog expire --expire=now --all')
    run_cmd('git gc --prune=now --aggressive')
    
    # Step 7: Cleanup
    print("\nStep 7: Cleaning up...")
    if os.path.exists('_redact_secrets.py'):
        os.remove('_redact_secrets.py')
    if os.path.exists(remove_list):
        os.remove(remove_list)
    
    print("\n" + "="*80)
    print("✅ NUCLEAR SECRET REMOVAL COMPLETE!")
    print("="*80)
    print("\n⚠️  CRITICAL NEXT STEPS:\n")
    print("1. FORCE PUSH TO GITHUB (this will completely rewrite history):")
    print("   git push origin --force --all")
    print("   git push origin --force --tags\n")
    print("2. VERIFY ON GITHUB:")
    print("   - Go to: https://github.com/usemanusai/youtube-free-deep-research-cli/security/secret-scanning")
    print("   - Wait for GitHub to re-scan (may take 5-10 minutes)")
    print("   - All alerts should disappear\n")
    print("3. IF ALERTS STILL APPEAR:")
    print("   - Run this script again")
    print("   - Check for additional secret patterns")
    print("   - Contact GitHub support\n")
    print("="*80)

if __name__ == '__main__':
    main()

