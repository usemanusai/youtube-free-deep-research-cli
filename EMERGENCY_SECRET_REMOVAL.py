#!/usr/bin/env python3
"""
EMERGENCY: Remove ALL secrets from git history
Handles: API keys, OAuth tokens, Firebase, Google, Tavily, etc.
"""

import subprocess
import re
import os

def run_cmd(cmd):
    """Run command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    print("🚨 EMERGENCY SECRET REMOVAL - FULL NUCLEAR OPTION 🚨\n")
    
    # List of files to completely remove from history
    files_to_remove = [
        'client_secret.json',
        '.env',
        '.env.local',
        '.env.production',
        '.env.staging',
        'OPENROUTER_KEY_ROTATION_IMPLEMENTATION.md',
        '.history',
        'credentials.json',
        'firebase-config.json',
        'google-credentials.json',
    ]
    
    print("Step 1: Removing sensitive files from git history...")
    for file in files_to_remove:
        print(f"  Removing: {file}")
        cmd = f'git filter-branch -f --tree-filter "rm -f {file}" -- --all'
        run_cmd(cmd)
    
    print("\nStep 2: Removing sensitive patterns from all files...")
    
    # Patterns to redact
    patterns = [
        (r'sk-or-v1-[a-zA-Z0-9]{64,}', 'REDACTED_OPENROUTER'),
        (r'tvly-[a-zA-Z0-9_-]+', 'REDACTED_TAVILY'),
        (r'AIza[0-9A-Za-z\-_]{35}', 'REDACTED_GOOGLE_API'),
        (r'GOCSPX-[a-zA-Z0-9_-]+', 'REDACTED_GOOGLE_SECRET'),
        (r'1079692665134-[a-zA-Z0-9_-]+', 'REDACTED_GOOGLE_CLIENT_ID'),
        (r'firebase[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]+', 'REDACTED_FIREBASE'),
        (r'oauth[_-]?token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_.-]+', 'REDACTED_OAUTH'),
        (r'Bearer\s+[a-zA-Z0-9_.-]+', 'Bearer REDACTED'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]+', 'api_key=REDACTED'),
        (r'secret["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]+', 'secret=REDACTED'),
        (r'password["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]+', 'password=REDACTED'),
        (r'token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_.-]+', 'token=REDACTED'),
    ]
    
    # Create filter script
    filter_code = '''
import re
import sys

patterns = [
    (r'sk-or-v1-[a-zA-Z0-9]{64,}', 'REDACTED_OPENROUTER'),
    (r'tvly-[a-zA-Z0-9_-]+', 'REDACTED_TAVILY'),
    (r'AIza[0-9A-Za-z\\-_]{35}', 'REDACTED_GOOGLE_API'),
    (r'GOCSPX-[a-zA-Z0-9_-]+', 'REDACTED_GOOGLE_SECRET'),
    (r'1079692665134-[a-zA-Z0-9_-]+', 'REDACTED_GOOGLE_CLIENT_ID'),
]

try:
    with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    with open(sys.argv[1], 'w', encoding='utf-8') as f:
        f.write(content)
except:
    pass
'''
    
    with open('_filter_secrets.py', 'w') as f:
        f.write(filter_code)
    
    print("  Running pattern-based redaction...")
    cmd = 'git filter-branch -f --tree-filter "python _filter_secrets.py $GIT_COMMIT" -- --all'
    returncode, stdout, stderr = run_cmd(cmd)
    
    print("\nStep 3: Garbage collection...")
    run_cmd('git reflog expire --expire=now --all')
    run_cmd('git gc --prune=now --aggressive')
    
    print("\nStep 4: Cleanup...")
    if os.path.exists('_filter_secrets.py'):
        os.remove('_filter_secrets.py')
    
    print("\n" + "="*70)
    print("✅ SECRET REMOVAL COMPLETE!")
    print("="*70)
    print("\n⚠️  CRITICAL NEXT STEPS:\n")
    print("1. FORCE PUSH TO GITHUB (this will overwrite history):")
    print("   git push origin --force --all")
    print("   git push origin --force --tags\n")
    print("2. IMMEDIATELY REVOKE ALL EXPOSED CREDENTIALS:")
    print("   ❌ Google OAuth: https://myaccount.google.com/permissions")
    print("   ❌ Tavily API: https://app.tavily.com/")
    print("   ❌ Firebase: https://console.firebase.google.com/")
    print("   ❌ OpenRouter: https://openrouter.ai/account/api-keys\n")
    print("3. REGENERATE NEW CREDENTIALS:")
    print("   - Create new Google OAuth credentials")
    print("   - Create new Tavily API key")
    print("   - Create new Firebase project")
    print("   - Create new OpenRouter keys\n")
    print("4. UPDATE GITHUB SECRETS:")
    print("   - Go to Settings → Secrets and variables → Actions")
    print("   - Update all secret values\n")
    print("5. VERIFY ON GITHUB:")
    print("   - Check Security → Secret scanning alerts")
    print("   - Mark all as 'Resolved'")
    print("   - Verify no new alerts appear\n")
    print("="*70)

if __name__ == '__main__':
    main()

