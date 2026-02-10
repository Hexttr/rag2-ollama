"""Детальная проверка статуса индексации"""
import httpx
import json
from datetime import datetime

print("=" * 70)
print("ПРОВЕРКА СТАТУСА ИНДЕКСАЦИИ")
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
            created_str = doc.get('created_at', '')
            updated_str = doc.get('updated_at', '')
            
            print(f"\n  Документ ID {doc_id}:")
            print(f"    Файл: {filename}")
            print(f"    Статус: {status}")
            
            if created_str and updated_str:
                try:
                    created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                    now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
                    
                    total_elapsed = (now - created).total_seconds()
                    time_since_update = (now - updated).total_seconds()
                    
                    print(f"    Создан: {created_str}")
                    print(f"    Обновлен: {updated_str}")
                    print(f"    Время с начала: {total_elapsed/60:.1f} минут ({total_elapsed/3600:.2f} часов)")
                    print(f"    Время с обновления: {time_since_update/60:.1f} минут")
                    
                    if status == 'indexing':
                        if time_since_update < 60:
                            print(f"    [OK] Индексация активна (обновлено недавно)")
                        elif time_since_update < 300:
                            print(f"    [INFO] Индексация продолжается (обновлено {time_since_update:.0f} сек назад)")
                        elif time_since_update < 1800:  # 30 минут
                            print(f"    [WARNING] Индексация может быть медленной (не обновлялось {time_since_update/60:.1f} мин)")
                        else:
                            print(f"    [ERROR] Индексация застряла! (не обновлялось {time_since_update/60:.1f} мин)")
                    elif status == 'error':
                        error_msg = doc.get('error_message', 'N/A')
                        print(f"    [ERROR] Ошибка: {error_msg[:200]}")
                except Exception as e:
                    print(f"    [WARNING] Ошибка парсинга времени: {e}")
    else:
        print(f"[ERROR] Не удалось получить документы (Status: {r.status_code})")
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")

# 2. Проверка Ollama
print("\n2. OLLAMA:")
print("-" * 70)
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"[OK] Ollama работает")
        print(f"[MODELS] Модели: {[m['name'] for m in models]}")
    else:
        print(f"[ERROR] Ollama не отвечает (Status: {r.status_code})")
except Exception as e:
    print(f"[ERROR] Ошибка подключения к Ollama: {e}")

# 3. Проверка активных соединений
print("\n3. АКТИВНЫЕ СОЕДИНЕНИЯ:")
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
        print(f"[OK] Найдено активных соединений с Ollama: {len(ollama_connections)}")
        print("  (Это означает, что Ollama участвует в индексации)")
    else:
        print(f"[INFO] Нет активных соединений с Ollama")
        print("  (Возможно, индексация завершилась или еще не началась)")
except Exception as e:
    print(f"[WARNING] Не удалось проверить соединения: {e}")

# 4. Вывод
print("\n" + "=" * 70)
print("ВЫВОД:")
print("=" * 70)
print("Проверьте статус документов выше.")
print("Если индексация идет долго (>30 минут без обновлений) - возможно застряла.")
print("Если есть ошибки - проверьте логи backend.")
print("=" * 70)


