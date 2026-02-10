"""Проверка деталей ошибки индексации"""
import httpx
from pathlib import Path

print("=" * 70)
print("ПРОВЕРКА ОШИБКИ ИНДЕКСАЦИИ")
print("=" * 70)

# 1. Проверка документов
print("\n1. ДОКУМЕНТЫ:")
print("-" * 70)
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/', timeout=5)
    if r.status_code == 200:
        docs = r.json()
        print(f"Всего документов: {len(docs)}")
        
        for doc in docs:
            doc_id = doc['id']
            status = doc.get('status', 'unknown')
            filename = doc.get('filename', 'N/A')
            error_msg = doc.get('error_message', 'None')
            
            print(f"\n  Документ ID {doc_id}:")
            print(f"    Файл: {filename}")
            print(f"    Статус: {status}")
            if error_msg and error_msg != 'None':
                print(f"    [ERROR] Ошибка: {error_msg}")
    else:
        print(f"Ошибка получения документов: {r.status_code}")
except Exception as e:
    print(f"Ошибка: {e}")

# 2. Чтение последних логов
print("\n2. ПОСЛЕДНИЕ ЛОГИ (ошибки):")
print("-" * 70)
log_file = Path("backend/logs/backend.log")
if log_file.exists():
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Ищем ошибки, связанные с документом 1
        error_lines = []
        for i, line in enumerate(lines):
            if ('error' in line.lower() or 'exception' in line.lower() or 'traceback' in line.lower()) and ('документ 1' in line.lower() or 'document 1' in line.lower() or 'document_id=1' in line.lower()):
                error_lines.append((i, line))
        
        if error_lines:
            print(f"Найдено ошибок для документа 1: {len(error_lines)}")
            print("\nПоследние ошибки:")
            for idx, line in error_lines[-10:]:
                print(f"  [{idx}] {line.rstrip()}")
                # Показываем контекст
                start = max(0, idx - 2)
                end = min(len(lines), idx + 3)
                for i in range(start, end):
                    if i != idx:
                        print(f"      {lines[i].rstrip()}")
        else:
            print("Ошибок для документа 1 не найдено в логах")
            print("\nПоследние 20 строк лога:")
            for line in lines[-20:]:
                print(f"  {line.rstrip()}")
    except Exception as e:
        print(f"Ошибка чтения логов: {e}")
else:
    print(f"Лог файл не найден: {log_file}")

print("\n" + "=" * 70)


