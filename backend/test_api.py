"""
Тестовый скрипт для проверки API
"""
import httpx
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Проверка health endpoint"""
    print("Testing health endpoint...")
    try:
        response = httpx.get(f"{BASE_URL}/api/health/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_ollama_health():
    """Проверка Ollama health"""
    print("\nTesting Ollama health...")
    try:
        response = httpx.get(f"{BASE_URL}/api/health/ollama", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_documents_list():
    """Проверка списка документов"""
    print("\nTesting documents list...")
    try:
        response = httpx.get(f"{BASE_URL}/api/documents/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload_document(pdf_path):
    """Тест загрузки документа"""
    print(f"\nTesting document upload: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            response = httpx.post(
                f"{BASE_URL}/api/documents/upload",
                files=files,
                timeout=300
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return False, None

def test_document_status(document_id):
    """Проверка статуса документа"""
    print(f"\nTesting document status: {document_id}")
    try:
        response = httpx.get(f"{BASE_URL}/api/documents/{document_id}", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("API Test Script")
    print("=" * 50)
    
    # Ждем запуска сервера
    print("\nWaiting for server to start...")
    for i in range(10):
        try:
            response = httpx.get(f"{BASE_URL}/api/health/", timeout=2)
            if response.status_code == 200:
                print("Server is running!")
                break
        except:
            pass
        time.sleep(1)
        print(f"Attempt {i+1}/10...")
    else:
        print("Server is not responding. Make sure it's running on port 8000")
        exit(1)
    
    # Тесты
    print("\n" + "=" * 50)
    test_health()
    test_ollama_health()
    test_documents_list()
    
    # Тест загрузки документа (если есть файл)
    import os
    uploads_dir = "./uploads"
    if os.path.exists(uploads_dir):
        pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
        if pdf_files:
            pdf_path = os.path.join(uploads_dir, pdf_files[0])
            success, doc_data = test_upload_document(pdf_path)
            if success and doc_data:
                doc_id = doc_data.get('id')
                if doc_id:
                    print(f"\nDocument uploaded with ID: {doc_id}")
                    print("Checking indexing status...")
                    for i in range(30):  # Ждем до 30 секунд
                        test_document_status(doc_id)
                        time.sleep(2)
                        # Проверяем статус
                        response = httpx.get(f"{BASE_URL}/api/documents/{doc_id}", timeout=5)
                        if response.status_code == 200:
                            status = response.json().get('status')
                            print(f"Status: {status}")
                            if status in ['ready', 'error']:
                                break
    
    print("\n" + "=" * 50)
    print("Tests completed!")

