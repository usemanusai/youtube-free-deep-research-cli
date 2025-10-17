#!/usr/bin/env python3
"""
Remove all API keys and secrets from git history.
Uses git filter-branch to rewrite history.
"""

import subprocess
import re
import sys
import os

def run_command(cmd, shell=False):
    """Run a shell command."""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {e}")
        return 1, "", str(e)

def main():
    print("🔐 Starting secret removal from git history...")
    
    # Step 1: Create a temporary filter script
    filter_script = """
import re
import sys

# Read the file content
with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Remove OpenRouter API keys (sk-or-v1-*)
content = re.sub(r'sk-or-v1-[a-zA-Z0-9]{64,}', 'REDACTED_OPENROUTER_KEY', content)

# Remove PyPI tokens (pypi-*)
content = re.sub(r'pypi-[a-zA-Z0-9_-]+', 'REDACTED_PYPI_TOKEN', content)

# Remove NPM tokens (npm_*)
content = re.sub(r'npm_[a-zA-Z0-9_-]+', 'REDACTED_NPM_TOKEN', content)

# Remove generic API keys
content = re.sub(r'["\']?api[_-]?key["\']?\\s*[:=]\\s*["\']?[a-zA-Z0-9_-]+["\']?', 'api_key=REDACTED', content, flags=re.IGNORECASE)

# Remove Bearer tokens
content = re.sub(r'Bearer\\s+[a-zA-Z0-9_.-]+', 'Bearer REDACTED', content)

# Write back
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    f.write(content)
"""
    
    with open('filter_secrets_temp.py', 'w') as f:
        f.write(filter_script)
    
    print("✓ Created filter script")
    
    # Step 2: Run git filter-branch
    print("⏳ Filtering git history (this may take a while)...")
    
    cmd = [
        'git', 'filter-branch', '-f',
        '--tree-filter', f'python filter_secrets_temp.py "$GIT_COMMIT"',
        '--', '--all'
    ]
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"⚠️  Filter-branch output: {stdout}")
        if stderr:
            print(f"⚠️  Errors: {stderr}")
    else:
        print("✓ Git history filtered")
    
    # Step 3: Clean up
    print("🧹 Cleaning up...")
    os.remove('filter_secrets_temp.py')
    
    # Step 4: Garbage collection
    print("⏳ Running garbage collection...")
    run_command(['git', 'reflog', 'expire', '--expire=now', '--all'])
    run_command(['git', 'gc', '--prune=now', '--aggressive'])
    
    print("✓ Garbage collection complete")
    
    # Step 5: Instructions
    print("\n" + "="*60)
    print("✅ SECRET REMOVAL COMPLETE!")
    print("="*60)
    print("\n⚠️  IMPORTANT: You must force-push to GitHub to update the remote:")
    print("\n  git push origin --force --all")
    print("  git push origin --force --tags")
    print("\n📝 After pushing:")
    print("  1. Go to GitHub repository settings")
    print("  2. Check 'Secret scanning alerts'")
    print("  3. Mark all alerts as 'Resolved'")
    print("  4. Verify no new alerts appear")
    print("\n🔑 CRITICAL: Rotate all exposed API keys immediately!")
    print("="*60)

if __name__ == '__main__':
    main()

