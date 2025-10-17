"""
Test script for JAEGIS NexusSync API endpoints

This script tests all critical API endpoints to verify functionality.
Run this after starting the API server.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_test_header(test_name: str):
    """Print a formatted test header."""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)

def print_result(success: bool, message: str, data: Any = None):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")

def test_root_endpoint():
    """Test root endpoint."""
    print_test_header("Root Endpoint (/)")
    try:
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200 and "JAEGIS NexusSync" in response.text
        print_result(success, f"Status Code: {response.status_code}")
        if success:
            print("✓ HTML page returned successfully")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def test_health_check():
    """Test health check endpoint."""
    print_test_header("Health Check (/api/v1/health)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        data = response.json()
        success = response.status_code == 200 and data.get("status") == "healthy"
        print_result(success, f"Status Code: {response.status_code}", data)
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def test_system_status():
    """Test system status endpoint."""
    print_test_header("System Status (/api/v1/system/status)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/system/status")
        data = response.json()
        success = response.status_code == 200
        print_result(success, f"Status Code: {response.status_code}", data)
        
        if success and "services" in data:
            print("\nService Status:")
            for service, status in data["services"].items():
                status_icon = "✓" if status.get("status") == "ok" else "✗"
                print(f"  {status_icon} {service}: {status}")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def test_config_endpoint():
    """Test configuration endpoint."""
    print_test_header("Configuration (/api/v1/config)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/config")
        data = response.json()
        success = response.status_code == 200
        print_result(success, f"Status Code: {response.status_code}", data)
        
        if success:
            print("\nConfiguration Summary:")
            print(f"  Vector Store: {data.get('vector_store_type')} - {'✓ Configured' if data.get('vector_store_configured') else '✗ Not Configured'}")
            print(f"  LLM: {data.get('llm_model')} - {'✓ Configured' if data.get('llm_configured') else '✗ Not Configured'}")
            print(f"  Embedding: {data.get('embedding_provider')}")
            print(f"  Google Drive: {'✓ Configured' if data.get('google_drive_configured') else '✗ Not Configured'}")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def test_rag_chat():
    """Test RAG chat endpoint."""
    print_test_header("RAG Chat (/api/v1/chat/query)")
    try:
        payload = {
            "question": "What is JAEGIS NexusSync?",
            "session_id": "test-session-001"
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat/query", json=payload)
        data = response.json()
        success = response.status_code == 200
        print_result(success, f"Status Code: {response.status_code}", data)
        
        if success and "answer" in data:
            print(f"\nQuestion: {payload['question']}")
            print(f"Answer: {data['answer'][:200]}...")
            print(f"Sources: {len(data.get('sources', []))} documents")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def test_queue_status():
    """Test queue status endpoint."""
    print_test_header("Queue Status (/api/v1/queue/status)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/queue/status")
        data = response.json()
        success = response.status_code == 200
        print_result(success, f"Status Code: {response.status_code}", data)
        
        if success:
            print(f"\nQueue Summary:")
            print(f"  Total Items: {data.get('total', 0)}")
            print(f"  Pending: {data.get('pending', 0)}")
            print(f"  Processing: {data.get('processing', 0)}")
            print(f"  Completed: {data.get('completed', 0)}")
            print(f"  Failed: {data.get('failed', 0)}")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def test_vector_store_stats():
    """Test vector store stats endpoint."""
    print_test_header("Vector Store Stats (/api/v1/vector-store/stats)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/vector-store/stats")
        data = response.json()
        success = response.status_code == 200
        print_result(success, f"Status Code: {response.status_code}", data)
        
        if success:
            print(f"\nVector Store:")
            print(f"  Type: {data.get('type', 'unknown')}")
            print(f"  Document Count: {data.get('document_count', 0)}")
            print(f"  Collection: {data.get('collection_name', 'N/A')}")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def test_api_docs():
    """Test API documentation endpoint."""
    print_test_header("API Documentation (/docs)")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        success = response.status_code == 200 and "swagger" in response.text.lower()
        print_result(success, f"Status Code: {response.status_code}")
        if success:
            print("✓ Swagger UI is accessible")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("JAEGIS NexusSync API - Endpoint Testing")
    print("=" * 70)
    print(f"Testing API at: {BASE_URL}")
    print("=" * 70)
    
    # Run all tests
    test_root_endpoint()
    test_health_check()
    test_system_status()
    test_config_endpoint()
    test_vector_store_stats()
    test_queue_status()
    test_rag_chat()
    test_api_docs()
    
    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Review any failed tests above")
    print("2. Check server logs for detailed error messages")
    print("3. Visit http://localhost:8000/docs for interactive API testing")
    print("4. Start the dashboard: cd workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24 && npm run dev")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

