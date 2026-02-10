"""Проверка активности Ollama во время индексации"""
import httpx
import json
import time
from datetime import datetime

print("=" * 70)
print("Проверка активности Ollama и индексации")
print("=" * 70)

# 1. Проверка Ollama
print("\n1. Проверка Ollama:")
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"   [OK] Ollama работает")
        print(f"   [MODELS] Доступные модели: {[m['name'] for m in models]}")
        
        # Тестовый запрос к Ollama
        print("\n   [TEST] Тестовый запрос к Ollama...")
        try:
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
                print(f"   [OK] Ollama отвечает на запросы (Status: {test_r.status_code})")
            else:
                print(f"   [WARNING] Ollama вернул статус: {test_r.status_code}")
        except Exception as e:
            print(f"   [WARNING] Тестовый запрос не прошел: {e}")
    else:
        print(f"   [ERROR] Ollama не отвечает (Status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Ошибка подключения к Ollama: {e}")

# 2. Проверка документа 4
print("\n2. Проверка документа ID 4:")
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/4', timeout=5)
    if r.status_code == 200:
        doc = r.json()
        status = doc.get('status', 'unknown')
        print(f"   [STATUS] Статус: {status}")
        print(f"   [FILE] Файл: {doc.get('filename', 'N/A')}")
        
        created_str = doc.get('created_at', '')
        updated_str = doc.get('updated_at', '')
        
        if created_str and updated_str:
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                elapsed = (updated - created).total_seconds()
                now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
                total_elapsed = (now - created).total_seconds()
                
                print(f"   [TIME] Создан: {created_str}")
                print(f"   [TIME] Последнее обновление: {updated_str}")
                print(f"   [TIME] Время с начала: {total_elapsed:.0f} секунд ({total_elapsed/60:.1f} минут)")
                
                if status == 'indexing':
                    # Проверяем, обновлялся ли статус недавно
                    time_since_update = (now - updated).total_seconds()
                    if time_since_update < 300:  # Меньше 5 минут
                        print(f"   [ACTIVE] Индексация активна (обновлено {time_since_update:.0f} сек назад)")
                    else:
                        print(f"   [WARNING] Индексация может быть застряла (не обновлялось {time_since_update:.0f} сек)")
            except Exception as e:
                print(f"   [WARNING] Ошибка парсинга времени: {e}")
        
        error_msg = doc.get('error_message')
        if error_msg:
            print(f"   [ERROR] Ошибка: {error_msg[:200]}")
    else:
        print(f"   [ERROR] Документ не найден (Status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Ошибка: {e}")

# 3. Проверка всех документов
print("\n3. Статус всех документов:")
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/', timeout=5)
    if r.status_code == 200:
        docs = r.json()
        statuses = {}
        for doc in docs:
            status = doc.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"   [TOTAL] Всего документов: {len(docs)}")
        for status, count in statuses.items():
            print(f"   [STATUS] {status}: {count}")
    else:
        print(f"   [ERROR] Не удалось получить документы (Status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Ошибка: {e}")

print("\n" + "=" * 70)
print("Проверка завершена")
print("=" * 70)
print("\nВывод:")
print("- Если статус 'indexing' и время обновления недавнее - индексация идет")
print("- Если Ollama отвечает на тестовый запрос - он работает")
print("- Если время обновления > 5 минут - возможно индексация застряла")


