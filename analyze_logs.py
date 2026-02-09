"""Анализ логов для документа 2"""
from pathlib import Path
import re

log_file = Path("backend/logs/backend.log")

if not log_file.exists():
    print(f"Лог файл не найден: {log_file}")
    exit(1)

print("=" * 70)
print("АНАЛИЗ ЛОГОВ ДЛЯ ДОКУМЕНТА ID 2")
print("=" * 70)

with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"\nВсего строк в логе: {len(lines)}")

# Ищем строки, связанные с документом 2
doc2_lines = []
for i, line in enumerate(lines):
    if 'документ 2' in line.lower() or 'document 2' in line.lower() or 'document_id=2' in line.lower():
        doc2_lines.append((i, line))

print(f"\nНайдено строк, связанных с документом 2: {len(doc2_lines)}")

if doc2_lines:
    print("\n" + "-" * 70)
    print("СТРОКИ, СВЯЗАННЫЕ С ДОКУМЕНТОМ 2:")
    print("-" * 70)
    for idx, line in doc2_lines:
        print(f"[{idx}] {line.rstrip()}")
        # Показываем контекст (2 строки до и после)
        start = max(0, idx - 2)
        end = min(len(lines), idx + 3)
        for i in range(start, end):
            if i != idx:
                print(f"  [{i}] {lines[i].rstrip()}")

# Ищем ошибки
error_lines = []
for i, line in enumerate(lines):
    if 'error' in line.lower() or 'exception' in line.lower() or 'traceback' in line.lower():
        error_lines.append((i, line))

print("\n" + "-" * 70)
print(f"НАЙДЕНО ОШИБОК: {len(error_lines)}")
print("-" * 70)

# Показываем последние 20 ошибок
for idx, line in error_lines[-20:]:
    print(f"[{idx}] {line.rstrip()}")

# Ищем строки с индексацией
indexing_lines = []
for i, line in enumerate(lines):
    if 'индекс' in line.lower() or 'index' in line.lower():
        indexing_lines.append((i, line))

print("\n" + "-" * 70)
print(f"НАЙДЕНО СТРОК С ИНДЕКСАЦИЕЙ: {len(indexing_lines)}")
print("-" * 70)

# Показываем последние 30 строк с индексацией
for idx, line in indexing_lines[-30:]:
    print(f"[{idx}] {line.rstrip()}")

# Ищем строки с Ollama
ollama_lines = []
for i, line in enumerate(lines):
    if 'ollama' in line.lower() or 'finish_reason' in line.lower():
        ollama_lines.append((i, line))

print("\n" + "-" * 70)
print(f"НАЙДЕНО СТРОК С OLLAMA: {len(ollama_lines)}")
print("-" * 70)

# Показываем последние 20 строк с Ollama
for idx, line in ollama_lines[-20:]:
    print(f"[{idx}] {line.rstrip()}")

print("\n" + "=" * 70)
print("АНАЛИЗ ЗАВЕРШЕН")
print("=" * 70)

