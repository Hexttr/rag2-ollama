"""Проверка нового документа и индексации"""
import httpx
import json
from datetime import datetime

print("=" * 70)
print("ПРОВЕРКА НОВОГО ДОКУМЕНТА И ИНДЕКСАЦИИ")
print("=" * 70)

# 1. Проверка Ollama
print("\n1. OLLAMA:")
print("-" * 70)
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"[OK] Ollama работает")
        print(f"[MODELS] Модели: {[m['name'] for m in models]}")
        
        # Тестовый запрос
        test_r = httpx.post(
            'http://localhost:11434/v1/chat/completions',
            json={
                'model': 'llama3.1:8b',
                'messages': [{'role': 'user', 'content': 'test'}],
                'stream': False
            },
            timeout=15
        )
        if test_r.status_code == 200:
            print(f"[OK] Ollama отвечает на запросы")
        else:
            print(f"[WARNING] Ollama вернул статус: {test_r.status_code}")
    else:
        print(f"[ERROR] Ollama не отвечает (Status: {r.status_code})")
except Exception as e:
    print(f"[ERROR] Ошибка подключения к Ollama: {e}")

# 2. Проверка всех документов
print("\n2. ДОКУМЕНТЫ:")
print("-" * 70)
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/', timeout=5)
    if r.status_code == 200:
        docs = r.json()
        print(f"[TOTAL] Всего документов: {len(docs)}")
        
        for doc in docs:
            print(f"\n  Документ ID {doc['id']}:")
            print(f"    Файл: {doc.get('filename', 'N/A')}")
            print(f"    Статус: {doc.get('status', 'N/A')}")
            print(f"    Создан: {doc.get('created_at', 'N/A')}")
            print(f"    Обновлен: {doc.get('updated_at', 'N/A')}")
            
            if doc.get('status') == 'indexing':
                created_str = doc.get('created_at', '')
                updated_str = doc.get('updated_at', '')
                if created_str and updated_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                        updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                        now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
                        elapsed = (now - created).total_seconds()
                        time_since_update = (now - updated).total_seconds()
                        
                        print(f"    Время с начала: {elapsed/60:.1f} минут")
                        print(f"    Время с обновления: {time_since_update:.0f} секунд")
                        
                        if time_since_update < 60:
                            print(f"    [OK] Индексация активна (обновлено недавно)")
                        elif time_since_update < 300:
                            print(f"    [INFO] Индексация продолжается (обновлено {time_since_update:.0f} сек назад)")
                        else:
                            print(f"    [WARNING] Индексация может быть застряла")
                    except:
                        pass
            
            error_msg = doc.get('error_message')
            if error_msg:
                print(f"    [ERROR] Ошибка: {error_msg[:100]}")
    else:
        print(f"[ERROR] Не удалось получить документы (Status: {r.status_code})")
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")

# 3. Проверка активных соединений
print("\n3. АКТИВНЫЕ СОЕДИНЕНИЯ С OLLAMA:")
print("-" * 70)
import subprocess
try:
    result = subprocess.run(
        ['netstat', '-ano'],
        capture_output=True,
        text=True,
        timeout=5
    )
    ollama_connections = [line for line in result.stdout.split('\n') if '11434' in line and 'ESTABLISHED' in line]
    if ollama_connections:
        print(f"[OK] Найдено активных соединений: {len(ollama_connections)}")
        print("  (Это означает, что Ollama участвует в индексации)")
    else:
        print(f"[INFO] Нет активных соединений (может быть, индексация еще не началась)")
except Exception as e:
    print(f"[WARNING] Не удалось проверить соединения: {e}")

# 4. Вывод
print("\n" + "=" * 70)
print("ВЫВОД:")
print("=" * 70)
print("Проверяю статус всех компонентов...")
print("=" * 70)

