"""
Verify that all port references have been updated from 8000 to 8555
"""

import os
from pathlib import Path

def check_file_for_port(filepath, old_port="8000", new_port="8555"):
    """Check if a file contains references to the old port."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        old_count = content.count(old_port)
        new_count = content.count(new_port)
        
        return old_count, new_count
    except Exception as e:
        return None, None

def main():
    print("=" * 70)
    print("Port Change Verification (8000 → 8555)")
    print("=" * 70)
    print()
    
    # Files that should have been updated
    files_to_check = [
        "run_api_server.py",
        "youtube_chat_cli_main/test_api_endpoints.py",
        "youtube_chat_cli_main/FIXES_APPLIED.md",
        "youtube_chat_cli_main/VERIFICATION_STEPS.md",
        "youtube_chat_cli_main/STATUS_REPORT.md",
        "youtube_chat_cli_main/QUICK_REFERENCE.md",
        "youtube_chat_cli_main/START_HERE.md",
        "youtube_chat_cli_main/start_api_server.bat",
        "youtube_chat_cli_main/start_api_server.sh",
        "youtube_chat_cli_main/workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24/.env.local.example",
        "youtube_chat_cli_main/workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24/src/lib/api-client.ts",
    ]
    
    all_good = True
    
    for filepath in files_to_check:
        old_count, new_count = check_file_for_port(filepath)
        
        if old_count is None:
            print(f"⚠️  {filepath}")
            print(f"   File not found or error reading")
            all_good = False
        elif old_count > 0:
            print(f"❌ {filepath}")
            print(f"   Still contains {old_count} reference(s) to port 8000")
            all_good = False
        elif new_count > 0:
            print(f"✅ {filepath}")
            print(f"   Updated correctly ({new_count} reference(s) to port 8555)")
        else:
            print(f"ℹ️  {filepath}")
            print(f"   No port references found")
    
    print()
    print("=" * 70)
    
    if all_good:
        print("✅ All files have been updated correctly!")
        print()
        print("Next steps:")
        print("1. Restart the API server: python run_api_server.py")
        print("2. Verify it starts on port 8555")
        print("3. Test the endpoints: python youtube_chat_cli_main/test_api_endpoints.py")
    else:
        print("❌ Some files still contain references to port 8000")
        print()
        print("Please review the files marked with ❌ above")
    
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()

