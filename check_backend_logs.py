"""Проверка логов и статуса индексации"""
import httpx
import json
import subprocess
from datetime import datetime

print("=" * 70)
print("ДЕТАЛЬНАЯ ПРОВЕРКА ЛОГОВ И ИНДЕКСАЦИИ")
print("=" * 70)

# 1. Проверка документа 2
print("\n1. ДОКУМЕНТ ID 2:")
print("-" * 70)
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/2', timeout=5)
    if r.status_code == 200:
        doc = r.json()
        print(f"Статус: {doc.get('status')}")
        print(f"Файл: {doc.get('filename')}")
        print(f"Создан: {doc.get('created_at')}")
        print(f"Обновлен: {doc.get('updated_at')}")
        print(f"Ошибка: {doc.get('error_message', 'None')}")
        
        created_str = doc.get('created_at', '')
        updated_str = doc.get('updated_at', '')
        if created_str and updated_str:
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
                elapsed = (now - created).total_seconds()
                time_since_update = (now - updated).total_seconds()
                print(f"\nВремя с начала: {elapsed/60:.1f} минут ({elapsed/3600:.2f} часов)")
                print(f"Время с обновления: {time_since_update/60:.1f} минут")
            except:
                pass
    else:
        print(f"Ошибка получения документа: {r.status_code}")
except Exception as e:
    print(f"Ошибка: {e}")

# 2. Проверка процессов Python
print("\n2. ПРОЦЕССЫ PYTHON:")
print("-" * 70)
try:
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
        capture_output=True,
        text=True,
        timeout=5
    )
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        print(f"Найдено процессов Python: {len(lines) - 1}")
        for line in lines[1:]:  # Пропускаем заголовок
            parts = line.split(',')
            if len(parts) >= 2:
                pid = parts[1].strip('"')
                mem = parts[4].strip('"') if len(parts) > 4 else 'N/A'
                print(f"  PID: {pid}, Память: {mem}")
    else:
        print("Процессы Python не найдены")
except Exception as e:
    print(f"Ошибка проверки процессов: {e}")

# 3. Проверка активных соединений с Ollama
print("\n3. СОЕДИНЕНИЯ С OLLAMA:")
print("-" * 70)
try:
    result = subprocess.run(
        ['netstat', '-ano'],
        capture_output=True,
        text=True,
        timeout=5
    )
    ollama_connections = [line for line in result.stdout.split('\n') if '11434' in line and 'ESTABLISHED' in line]
    if ollama_connections:
        print(f"Активных соединений с Ollama: {len(ollama_connections)}")
        for conn in ollama_connections[:5]:
            print(f"  {conn.strip()}")
    else:
        print("Нет активных соединений с Ollama")
except Exception as e:
    print(f"Ошибка: {e}")

# 4. Проверка файлов индексации
print("\n4. ФАЙЛЫ ИНДЕКСАЦИИ:")
print("-" * 70)
import os
from pathlib import Path

index_dir = Path("backend/indices") if Path("backend/indices").exists() else Path("indices")
if index_dir.exists():
    index_files = list(index_dir.glob("*.json"))
    print(f"Найдено файлов индексов: {len(index_files)}")
    for idx_file in index_files[:5]:
        size = idx_file.stat().st_size / 1024  # KB
        mtime = datetime.fromtimestamp(idx_file.stat().st_mtime)
        print(f"  {idx_file.name}: {size:.1f} KB, изменен: {mtime}")
else:
    print(f"Директория индексов не найдена: {index_dir}")

# 5. Проверка загруженных файлов
print("\n5. ЗАГРУЖЕННЫЕ ФАЙЛЫ:")
print("-" * 70)
upload_dir = Path("backend/uploads") if Path("backend/uploads").exists() else Path("uploads")
if upload_dir.exists():
    pdf_files = list(upload_dir.glob("*.pdf"))
    print(f"Найдено PDF файлов: {len(pdf_files)}")
    for pdf_file in pdf_files:
        size = pdf_file.stat().st_size / (1024 * 1024)  # MB
        mtime = datetime.fromtimestamp(pdf_file.stat().st_mtime)
        print(f"  {pdf_file.name}: {size:.2f} MB, изменен: {mtime}")
else:
    print(f"Директория загрузок не найдена: {upload_dir}")

# 6. Тест Ollama
print("\n6. ТЕСТ OLLAMA:")
print("-" * 70)
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        print("[OK] Ollama работает")
    else:
        print(f"[ERROR] Ollama вернул статус: {r.status_code}")
except Exception as e:
    print(f"[ERROR] Ollama не отвечает: {e}")

print("\n" + "=" * 70)
print("РЕКОМЕНДАЦИИ:")
print("=" * 70)
print("1. Проверьте консоль, где запущен backend - там должны быть логи")
print("2. Ищите сообщения об ошибках или 'Ошибка при индексации'")
print("3. Проверьте, не завис ли процесс индексации")
print("4. Если процесс завис - перезапустите backend")
print("=" * 70)

