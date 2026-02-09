"""
Проверка статуса документов и индексации
"""
import httpx
import json
from datetime import datetime

print("=" * 80)
print("ПРОВЕРКА СТАТУСА ДОКУМЕНТОВ И ИНДЕКСАЦИИ")
print("=" * 80)

# 1. Проверка документов
print("\n1. Список документов:")
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents', timeout=5)
    if r.status_code == 200:
        docs = r.json()
        if docs:
            for doc in docs:
                print(f"\n  Документ ID: {doc['id']}")
                print(f"  Файл: {doc['filename']}")
                print(f"  Статус: {doc['status']}")
                if doc.get('error_message'):
                    print(f"  Ошибка: {doc['error_message']}")
                print(f"  Создан: {doc.get('created_at', 'unknown')}")
                print(f"  Обновлен: {doc.get('updated_at', 'unknown')}")
        else:
            print("  Документов нет")
    else:
        print(f"  [ERROR] Не удалось получить документы (Status: {r.status_code})")
except Exception as e:
    print(f"  [ERROR] Ошибка при получении документов: {e}")

# 2. Проверка логов
print("\n2. Последние логи индексации:")
try:
    r = httpx.get('http://127.0.0.1:8000/api/health/logs?lines=100', timeout=5)
    if r.status_code == 200:
        logs_data = r.json()
        logs = logs_data.get('logs', [])
        if logs:
            # Фильтруем логи, связанные с индексацией
            indexing_logs = [line for line in logs if 'индекс' in line.lower() or 'index' in line.lower() or 'документ' in line.lower()]
            if indexing_logs:
                print("  Последние логи индексации:")
                for line in indexing_logs[-20:]:
                    print(f"    {line.rstrip()}")
            else:
                print("  Логи индексации не найдены")
                print("  Последние 10 строк логов:")
                for line in logs[-10:]:
                    print(f"    {line.rstrip()}")
        else:
            print("  Логи пусты")
    else:
        print(f"  [ERROR] Не удалось получить логи (Status: {r.status_code})")
except Exception as e:
    print(f"  [ERROR] Ошибка при получении логов: {e}")

# 3. Проверка Ollama
print("\n3. Статус Ollama:")
try:
    r = httpx.get('http://127.0.0.1:8000/api/health/ollama', timeout=5)
    if r.status_code == 200:
        health = r.json()
        print(f"  Статус: {health.get('status', 'unknown')}")
        print(f"  Доступен: {health.get('ollama_available', False)}")
        print(f"  Модель: {health.get('model', 'unknown')}")
    else:
        print(f"  [ERROR] Не удалось проверить Ollama (Status: {r.status_code})")
except Exception as e:
    print(f"  [ERROR] Ошибка при проверке Ollama: {e}")

print("\n" + "=" * 80)

