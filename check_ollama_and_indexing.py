"""Проверка Ollama и статуса индексации"""
import httpx
import json
import time

print("=" * 60)
print("Проверка Ollama и индексации")
print("=" * 60)

# 1. Проверка Ollama
print("\n1. Проверка Ollama:")
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"   [OK] Ollama работает (Status: {r.status_code})")
        print(f"   [MODELS] Доступные модели: {[m['name'] for m in models]}")
    else:
        print(f"   [ERROR] Ollama не отвечает (Status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Ошибка подключения к Ollama: {e}")

# 2. Проверка Backend
print("\n2. Проверка Backend:")
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/', timeout=5)
    if r.status_code == 200:
        docs = r.json()
        print(f"   [OK] Backend работает (Status: {r.status_code})")
        print(f"   [DOCS] Всего документов: {len(docs)}")
        
        # Статусы документов
        statuses = {}
        for doc in docs:
            status = doc.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"   [STATUS] Статусы:")
        for status, count in statuses.items():
            print(f"      - {status}: {count}")
        
        # Документы в процессе индексации
        indexing_docs = [d for d in docs if d.get('status') == 'indexing']
        if indexing_docs:
            print(f"\n   [INDEXING] Документы в процессе индексации:")
            for doc in indexing_docs:
                created = doc.get('created_at', 'N/A')
                updated = doc.get('updated_at', 'N/A')
                print(f"      - ID {doc['id']}: {doc.get('filename', 'N/A')}")
                print(f"        Создан: {created}")
                print(f"        Обновлен: {updated}")
        
        # Документы с ошибками
        error_docs = [d for d in docs if d.get('status') == 'error']
        if error_docs:
            print(f"\n   [ERROR] Документы с ошибками:")
            for doc in error_docs:
                error_msg = doc.get('error_message', 'N/A')
                print(f"      - ID {doc['id']}: {doc.get('filename', 'N/A')}")
                if error_msg and error_msg != 'N/A':
                    print(f"        Ошибка: {error_msg[:100]}")
    else:
        print(f"   [ERROR] Backend не отвечает (Status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Ошибка подключения к Backend: {e}")

# 3. Проверка конкретного документа 4
print("\n3. Проверка документа ID 4:")
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/4', timeout=5)
    if r.status_code == 200:
        doc = r.json()
        print(f"   [OK] Документ найден")
        print(f"   [FILE] Файл: {doc.get('filename', 'N/A')}")
        print(f"   [STATUS] Статус: {doc.get('status', 'N/A')}")
        print(f"   [TIME] Создан: {doc.get('created_at', 'N/A')}")
        print(f"   [TIME] Обновлен: {doc.get('updated_at', 'N/A')}")
        
        if doc.get('status') == 'indexing':
            # Вычисляем время индексации
            try:
                from datetime import datetime
                created_str = doc.get('created_at', '')
                updated_str = doc.get('updated_at', '')
                if created_str and updated_str:
                    created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                    elapsed = (updated - created).total_seconds()
                    print(f"   [TIME] Время индексации: {elapsed:.0f} секунд ({elapsed/60:.1f} минут)")
            except:
                pass
    else:
        print(f"   [ERROR] Документ не найден (Status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Ошибка: {e}")

print("\n" + "=" * 60)
print("Проверка завершена")
print("=" * 60)

