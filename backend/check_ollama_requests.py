"""
Скрипт для проверки запросов к Ollama
"""
import httpx
import time
import json

def check_ollama_status():
    """Проверка статуса Ollama"""
    print("=" * 60)
    print("Проверка Ollama")
    print("=" * 60)
    
    try:
        # Проверка доступности
        r = httpx.get('http://localhost:11434/api/tags', timeout=5)
        print(f"[OK] Ollama доступен (статус: {r.status_code})")
        
        models = r.json().get('models', [])
        print(f"[MODELS] Доступные модели: {[m['name'] for m in models]}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Ollama недоступен: {e}")
        return False

def test_ollama_request():
    """Тестовый запрос к Ollama"""
    print("\n" + "=" * 60)
    print("Тестовый запрос к Ollama")
    print("=" * 60)
    
    try:
        # Используем OpenAI-совместимый API
        import openai
        client = openai.OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )
        
        print("Отправка запроса...")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": "Скажи 'привет' одним словом"}],
            temperature=0
        )
        
        elapsed = time.time() - start_time
        result = response.choices[0].message.content
        
        print(f"[OK] Запрос выполнен за {elapsed:.2f} секунд")
        print(f"[RESPONSE] Ответ: {result}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка запроса: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_backend_logs():
    """Проверка логов backend на запросы к Ollama"""
    print("\n" + "=" * 60)
    print("Проверка логов backend")
    print("=" * 60)
    
    log_file = "logs/backend.log"
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Ищем последние упоминания Ollama
        ollama_lines = [l for l in lines[-100:] if 'ollama' in l.lower() or '11434' in l]
        
        if ollama_lines:
            print(f"[OK] Найдено {len(ollama_lines)} упоминаний Ollama в последних 100 строках:")
            for line in ollama_lines[-5:]:  # Последние 5
                print(f"  {line.strip()}")
        else:
            print("[WARNING] Нет упоминаний Ollama в последних 100 строках логов")
            print("   Это может означать, что запросы не идут")
        
    except Exception as e:
        print(f"[ERROR] Ошибка чтения логов: {e}")

def check_documents_status():
    """Проверка статуса документов"""
    print("\n" + "=" * 60)
    print("Статус документов")
    print("=" * 60)
    
    try:
        r = httpx.get('http://localhost:8000/api/documents/', timeout=5)
        docs = r.json()
        
        print(f"Всего документов: {len(docs)}")
        
        statuses = {}
        for doc in docs:
            status = doc['status']
            statuses[status] = statuses.get(status, 0) + 1
        
        print("\nСтатусы:")
        for status, count in statuses.items():
            print(f"  {status}: {count}")
        
        # Показываем последние документы
        print("\nПоследние 3 документа:")
        for doc in docs[-3:]:
            print(f"  ID: {doc['id']}, File: {doc['filename']}, Status: {doc['status']}")
            if doc['status'] == 'indexing':
                print(f"    [INDEXING] Индексация в процессе...")
            elif doc['status'] == 'error':
                print(f"    [ERROR] Ошибка: {doc.get('error_message', 'Unknown')[:100]}")
        
    except Exception as e:
        print(f"[ERROR] Ошибка проверки документов: {e}")

if __name__ == "__main__":
    check_ollama_status()
    test_ollama_request()
    check_backend_logs()
    check_documents_status()
    
    print("\n" + "=" * 60)
    print("Проверка завершена")
    print("=" * 60)

