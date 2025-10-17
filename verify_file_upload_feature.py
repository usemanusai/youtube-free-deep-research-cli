"""
Verification script for file upload feature implementation
"""
import os
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}")
        print(f"   Path: {path}")
        return True
    else:
        print(f"❌ {description}")
        print(f"   Path: {path}")
        return False

def check_file_contains(path, search_text, description):
    """Check if a file contains specific text"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description}")
                return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    print("=" * 70)
    print("JAEGIS NexusSync - File Upload Feature Verification")
    print("=" * 70)
    print()
    
    base_path = Path(".")
    dashboard_path = base_path / "youtube_chat_cli_main" / "workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24"
    
    # Check API Server endpoints
    print("📡 API Server Endpoints")
    print("-" * 70)
    api_server_path = base_path / "youtube_chat_cli_main" / "api_server.py"
    check_file_contains(
        api_server_path,
        '@app.get("/api/v1/gdrive/list")',
        "Google Drive list endpoint exists"
    )
    check_file_contains(
        api_server_path,
        '@app.post("/api/v1/gdrive/download")',
        "Google Drive download endpoint exists"
    )
    check_file_contains(
        api_server_path,
        '@app.post("/api/v1/files/upload")',
        "File upload endpoint exists"
    )
    print()
    
    # Check Frontend Components
    print("🎨 Frontend Components")
    print("-" * 70)
    file_upload_dialog = dashboard_path / "src" / "components" / "file-upload-dialog.tsx"
    check_file_exists(
        file_upload_dialog,
        "File upload dialog component exists"
    )
    check_file_contains(
        file_upload_dialog,
        "FileUploadDialog",
        "FileUploadDialog component defined"
    )
    check_file_contains(
        file_upload_dialog,
        "Local Files",
        "Local Files tab exists"
    )
    check_file_contains(
        file_upload_dialog,
        "Google Drive",
        "Google Drive tab exists"
    )
    print()
    
    # Check Chat Interface Integration
    print("💬 Chat Interface Integration")
    print("-" * 70)
    chat_interface = dashboard_path / "src" / "components" / "chat-interface.tsx"
    check_file_contains(
        chat_interface,
        "import { FileUploadDialog }",
        "FileUploadDialog imported in chat interface"
    )
    check_file_contains(
        chat_interface,
        "Paperclip",
        "Paperclip icon imported"
    )
    check_file_contains(
        chat_interface,
        "uploadDialogOpen",
        "Upload dialog state exists"
    )
    check_file_contains(
        chat_interface,
        "handleFileUploaded",
        "File upload handler exists"
    )
    check_file_contains(
        chat_interface,
        "<FileUploadDialog",
        "FileUploadDialog component rendered"
    )
    print()
    
    # Check Environment Configuration
    print("⚙️  Environment Configuration")
    print("-" * 70)
    env_local = dashboard_path / ".env.local"
    check_file_exists(
        env_local,
        ".env.local file exists"
    )
    check_file_contains(
        env_local,
        "NEXT_PUBLIC_API_URL=http://localhost:8555",
        "API URL configured correctly"
    )
    print()
    
    # Check UI Components
    print("🧩 UI Components (shadcn/ui)")
    print("-" * 70)
    ui_path = dashboard_path / "src" / "components" / "ui"
    required_components = [
        "dialog.tsx",
        "tabs.tsx",
        "progress.tsx",
        "badge.tsx",
        "scroll-area.tsx",
        "button.tsx",
        "input.tsx"
    ]
    
    for component in required_components:
        check_file_exists(
            ui_path / component,
            f"{component} component exists"
        )
    print()
    
    # Check Google Drive Configuration
    print("🔐 Google Drive Configuration")
    print("-" * 70)
    check_file_exists(
        base_path / "client_secret.json",
        "Google Drive OAuth credentials exist"
    )
    check_file_exists(
        base_path / "token.pickle",
        "Google Drive token cache exists"
    )
    print()
    
    # Summary
    print("=" * 70)
    print("Verification Complete!")
    print("=" * 70)
    print()
    print("📋 Next Steps:")
    print("1. Restart the API server: restart_api_server.bat")
    print("2. Restart the dashboard: cd youtube_chat_cli_main\\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24 && npm run dev")
    print("3. Open browser to http://localhost:3000")
    print("4. Click the paperclip icon to test file upload")
    print()

if __name__ == "__main__":
    main()

