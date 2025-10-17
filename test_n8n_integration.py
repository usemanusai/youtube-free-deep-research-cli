"""
Test script to diagnose n8n integration issues.
"""

import requests
import json
import sys

def test_n8n_health():
    """Test if n8n is running."""
    print("=" * 60)
    print("Test 1: n8n Health Check")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=5)
        print(f"✓ n8n is running (HTTP {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ n8n health check failed: {e}")
        return False

def test_qdrant():
    """Test if Qdrant is running."""
    print("\n" + "=" * 60)
    print("Test 2: Qdrant Vector Database")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:6333/collections", timeout=5)
        data = response.json()
        collections = [c['name'] for c in data['result']['collections']]
        print(f"✓ Qdrant is running")
        print(f"  Collections: {', '.join(collections)}")
        
        if 'documents' in collections:
            # Get collection info
            coll_response = requests.get("http://localhost:6333/collections/documents", timeout=5)
            coll_data = coll_response.json()
            vectors_count = coll_data['result'].get('vectors_count', 0)
            print(f"  'documents' collection: {vectors_count} vectors")
        return True
    except Exception as e:
        print(f"✗ Qdrant check failed: {e}")
        return False

def test_ollama():
    """Test if Ollama is running."""
    print("\n" + "=" * 60)
    print("Test 3: Ollama LLM")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = response.json()
        models = [m['name'] for m in data['models']]
        print(f"✓ Ollama is running")
        print(f"  Models: {', '.join(models)}")
        
        # Check for required models
        if 'llama3.1:latest' in models:
            print("  ✓ llama3.1:latest (chat model) is installed")
        else:
            print("  ✗ llama3.1:latest (chat model) is NOT installed")
            
        if 'nomic-embed-text:latest' in models:
            print("  ✓ nomic-embed-text:latest (embedding model) is installed")
        else:
            print("  ✗ nomic-embed-text:latest (embedding model) is NOT installed")
        
        return True
    except Exception as e:
        print(f"✗ Ollama check failed: {e}")
        return False

def test_postgres():
    """Test if PostgreSQL is running."""
    print("\n" + "=" * 60)
    print("Test 4: PostgreSQL Database")
    print("=" * 60)
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="n8n_prod_db",
            user="n8n_user",
            password="B6$tF8#kV9@zW2!sR5*dC1^mP4&jQ7%eN"
        )
        print("✓ PostgreSQL is running and accessible")
        
        # Check if chat_memory table exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'chat_memory'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM chat_memory;")
            count = cursor.fetchone()[0]
            print(f"  ✓ chat_memory table exists ({count} messages)")
        else:
            print("  ✗ chat_memory table does NOT exist")
        
        conn.close()
        return True
    except ImportError:
        print("  ⚠ psycopg2 not installed (pip install psycopg2-binary)")
        return True  # Don't fail the test
    except Exception as e:
        print(f"✗ PostgreSQL check failed: {e}")
        return False

def test_n8n_webhook():
    """Test the n8n webhook endpoint."""
    print("\n" + "=" * 60)
    print("Test 5: n8n Webhook Endpoint")
    print("=" * 60)
    
    webhook_url = "http://localhost:5678/webhook/invoke_n8n_agent"
    payload = {
        "chatInput": "Hello, this is a test message from the diagnostic script.",
        "sessionId": "test-diagnostic-session"
    }
    
    try:
        print(f"Sending POST request to: {webhook_url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"\nResponse Status: HTTP {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Response Length: {len(response.content)} bytes")
        
        if response.content:
            print(f"\nResponse Content:")
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
            except:
                print(response.text)
        else:
            print("\n⚠ Response is empty!")
            print("This suggests the n8n workflow might not be configured correctly.")
            print("Possible issues:")
            print("  1. Workflow is not active in n8n")
            print("  2. Credentials are not configured")
            print("  3. AI Agent node has errors")
            print("  4. Respond to Webhook node is not connected")
        
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Webhook test failed: {e}")
        return False

def test_python_client():
    """Test the Python n8n client."""
    print("\n" + "=" * 60)
    print("Test 6: Python n8n Client")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        import os
        
        # Load environment variables
        load_dotenv()
        
        webhook_url = os.getenv('N8N_WEBHOOK_URL')
        print(f"N8N_WEBHOOK_URL from .env: {webhook_url}")
        
        if not webhook_url:
            print("✗ N8N_WEBHOOK_URL is not set in .env file")
            return False
        
        # Import and test the client
        sys.path.insert(0, 'youtube_chat_cli_main')
        from n8n_client import get_n8n_client
        
        client = get_n8n_client()
        print(f"✓ n8n client initialized")
        print(f"  Webhook URL: {client.webhook_url}")
        
        # Test sending a message
        print("\nSending test message...")
        response = client.send_chat_message("Test from Python client", "test-python-session")
        print(f"✓ Response received: {response[:100]}..." if len(response) > 100 else f"✓ Response: {response}")
        
        return True
    except Exception as e:
        print(f"✗ Python client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("n8n RAG Integration Diagnostic Tests")
    print("=" * 60)
    
    results = {
        "n8n Health": test_n8n_health(),
        "Qdrant": test_qdrant(),
        "Ollama": test_ollama(),
        "PostgreSQL": test_postgres(),
        "n8n Webhook": test_n8n_webhook(),
        "Python Client": test_python_client()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nThe n8n integration should be working.")
        print("If you're still having issues, check the n8n UI for workflow errors:")
        print("  http://localhost:5678/workflow/vTN9y2dLXqTiDfPT")
    else:
        print("✗ Some tests failed!")
        print("\nPlease fix the failing tests before proceeding.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

