"""Финальная проверка статуса индексации"""
import httpx
import sqlite3
import os
from pathlib import Path

print("=" * 60)
print("ФИНАЛЬНЫЙ ОТЧЕТ О ПРОВЕРКЕ ИНДЕКСАЦИИ")
print("=" * 60)

# 1. Проверка статуса документов через API
print("\n1. Статус документов через API:")
try:
    r = httpx.get('http://localhost:8000/api/documents/', timeout=5)
    docs = r.json()
    for doc in docs:
        if doc['id'] in [5, 6]:
            print(f"  Document {doc['id']}:")
            print(f"    Status: {doc['status']}")
            print(f"    File: {doc['filename']}")
            if doc.get('error_message'):
                print(f"    Error: {doc['error_message'][:100]}")
            if doc.get('index_path'):
                print(f"    Index: {doc['index_path']}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Проверка статуса через БД
print("\n2. Статус документов в БД:")
try:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, status, error_message FROM documents WHERE id IN (5, 6)')
    rows = cursor.fetchall()
    for row in rows:
        print(f"  Document {row[0]}: Status={row[1]}, Error={row[2][:50] if row[2] else 'None'}")
    conn.close()
except Exception as e:
    print(f"  Error: {e}")

# 3. Проверка размера лог-файла
print("\n3. Логи:")
try:
    log_file = Path('logs/backend.log')
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"  Log file size: {size} bytes ({size/1024:.2f} KB)")
        
        # Читаем последние строки
        with open(log_file, 'rb') as f:
            f.seek(max(0, size - 10000))
            content = f.read().decode('utf-8', errors='ignore')
            lines = content.split('\n')
            print(f"  Last 10 lines:")
            for line in lines[-10:]:
                if line.strip():
                    print(f"    {line.strip()[:100]}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Проверка процессов Python
print("\n4. Активные процессы Python:")
try:
    import subprocess
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    python_count = result.stdout.count('python.exe')
    print(f"  Active Python processes: {python_count}")
except Exception as e:
    print(f"  Error: {e}")

# 5. Проверка Ollama
print("\n5. Проверка Ollama:")
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        print("  Ollama доступен")
        models = r.json().get('models', [])
        print(f"  Модели: {[m['name'] for m in models]}")
    else:
        print(f"  Ollama недоступен (status: {r.status_code})")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("Проверка завершена")
print("=" * 60)

