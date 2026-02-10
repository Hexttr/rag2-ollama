"""
Test script for document upload
"""
import requests
import sys

def test_upload():
    url = "http://localhost:8000/api/documents/upload"
    
    # Create a dummy PDF file for testing
    test_file_path = "test.pdf"
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test.pdf', f, 'application/pdf')}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
        else:
            print(f"❌ Upload failed: {response.text}")
    except FileNotFoundError:
        print(f"❌ Test file not found: {test_file_path}")
        print("Create a test PDF file first")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload()






