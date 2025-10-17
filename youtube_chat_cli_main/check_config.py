"""
Quick configuration checker for JAEGIS NexusSync

Run this to verify your configuration is correct.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def print_status(label, status, details=""):
    icon = "✅" if status else "❌"
    print(f"{icon} {label}: {details}")

def main():
    print_header("JAEGIS NexusSync Configuration Check")
    
    # Load environment variables
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    print(f"\n📁 Environment file: {env_path}")
    print(f"   Exists: {'✅ Yes' if env_path.exists() else '❌ No'}")
    
    # Check vector store configuration
    print_header("Vector Store Configuration")
    vector_store_type = os.getenv('VECTOR_STORE_TYPE', 'not set')
    print_status("Vector Store Type", True, vector_store_type)
    
    if vector_store_type == 'chroma':
        chroma_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
        chroma_collection = os.getenv('CHROMA_COLLECTION_NAME', 'documents')
        print_status("ChromaDB Directory", True, chroma_dir)
        print_status("Collection Name", True, chroma_collection)
        print("\n✅ ChromaDB is configured correctly (no Docker required)")
    elif vector_store_type == 'qdrant':
        qdrant_url = os.getenv('QDRANT_URL', 'not set')
        qdrant_key = os.getenv('QDRANT_API_KEY', '')
        print_status("Qdrant URL", bool(qdrant_url), qdrant_url)
        print_status("Qdrant API Key", bool(qdrant_key), "Set" if qdrant_key else "Not set")
        if not qdrant_key:
            print("\n⚠️  WARNING: Qdrant requires an API key or you need to switch to ChromaDB")
            print("   To fix: Edit .env and set VECTOR_STORE_TYPE=chroma")
    else:
        print_status("Vector Store", False, f"Unknown type: {vector_store_type}")
    
    # Check LLM configuration
    print_header("LLM Configuration")
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'not set')
    ollama_model = os.getenv('OLLAMA_MODEL', 'not set')
    print_status("Ollama URL", True, ollama_url)
    print_status("Ollama Model", True, ollama_model)
    
    # Check embedding configuration
    print_header("Embedding Configuration")
    embedding_provider = os.getenv('EMBEDDING_PROVIDER', 'not set')
    embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL', 'not set')
    print_status("Provider", True, embedding_provider)
    print_status("Model", True, embedding_model)
    
    # Check database configuration
    print_header("Database Configuration")
    db_path = os.getenv('DATABASE_PATH', './jaegis_nexus_sync.db')
    print_status("Database Path", True, db_path)
    
    # Check Google Drive configuration
    print_header("Google Drive Configuration (Optional)")
    gdrive_folder = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'client_secret.json')
    client_secret_path = Path(__file__).parent / client_secret
    print_status("Folder ID", bool(gdrive_folder), gdrive_folder if gdrive_folder else "Not set")
    print_status("Client Secret File", client_secret_path.exists(), str(client_secret_path))
    
    if not gdrive_folder:
        print("\nℹ️  Google Drive is not configured (this is optional)")
        print("   You can still upload files manually")
    
    # Summary
    print_header("Summary")
    
    issues = []
    if vector_store_type == 'qdrant' and not os.getenv('QDRANT_API_KEY'):
        issues.append("Qdrant API key not set - switch to ChromaDB or set API key")
    
    if issues:
        print("\n❌ Issues Found:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n📝 To fix: Edit youtube_chat_cli_main/.env file")
    else:
        print("\n✅ All critical configuration is correct!")
        print("\n🚀 You can start the server with:")
        print("   python run_api_server.py")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error checking configuration: {e}")
        print("\nMake sure you're running this from the youtube_chat_cli_main directory")
        sys.exit(1)

