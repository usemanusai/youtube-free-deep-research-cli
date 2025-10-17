"""
Test script for file upload and Google Drive endpoints
"""
import requests
import json

API_URL = "http://localhost:8555"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/v1/health")
        print(f"✅ Health: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health failed: {e}")

def test_gdrive_status():
    """Test Google Drive status endpoint"""
    print("\nTesting Google Drive status endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/v1/gdrive/status")
        print(f"✅ GDrive Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ GDrive Status failed: {e}")

def test_gdrive_list():
    """Test Google Drive list endpoint"""
    print("\nTesting Google Drive list endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/v1/gdrive/list?page_size=10")
        print(f"✅ GDrive List: {response.status_code}")
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   File count: {data.get('count')}")
        if data.get('files'):
            print(f"   First file: {data['files'][0].get('name')}")
    except Exception as e:
        print(f"❌ GDrive List failed: {e}")

def test_file_upload():
    """Test file upload endpoint"""
    print("\nTesting file upload endpoint...")
    try:
        # Create a test file
        test_content = "This is a test file for the knowledge base."
        files = {'file': ('test.txt', test_content, 'text/plain')}
        
        response = requests.post(f"{API_URL}/api/v1/files/upload", files=files)
        print(f"✅ File Upload: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ File Upload failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("JAEGIS NexusSync - File Endpoints Test")
    print("=" * 60)
    
    test_health()
    test_gdrive_status()
    test_gdrive_list()
    test_file_upload()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

