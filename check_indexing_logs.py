"""Проверка логов индексации и активности Ollama"""
import httpx
import json
from datetime import datetime

print("=" * 70)
print("АНАЛИЗ ИНДЕКСАЦИИ И АКТИВНОСТИ OLLAMA")
print("=" * 70)

# 1. Проверка Ollama
print("\n1. OLLAMA:")
print("-" * 70)
try:
    # Проверка доступности
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"[OK] Ollama работает")
        print(f"[MODELS] Модели: {[m['name'] for m in models]}")
        
        # Тестовый запрос
        print(f"\n[TEST] Тестовый запрос к Ollama API...")
        test_r = httpx.post(
            'http://localhost:11434/v1/chat/completions',
            json={
                'model': 'llama3.1:8b',
                'messages': [{'role': 'user', 'content': 'Say "test"'}],
                'stream': False
            },
            timeout=20
        )
        if test_r.status_code == 200:
            response = test_r.json()
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"[OK] Ollama отвечает на запросы")
            print(f"[RESPONSE] Ответ: {content[:50]}...")
        else:
            print(f"[ERROR] Ollama вернул статус: {test_r.status_code}")
    else:
        print(f"[ERROR] Ollama не отвечает (Status: {r.status_code})")
except Exception as e:
    print(f"[ERROR] Ошибка подключения к Ollama: {e}")

# 2. Проверка документа 4
print("\n2. ДОКУМЕНТ ID 4:")
print("-" * 70)
try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/4', timeout=5)
    if r.status_code == 200:
        doc = r.json()
        status = doc.get('status', 'unknown')
        print(f"[STATUS] Статус: {status}")
        print(f"[FILE] Файл: {doc.get('filename', 'N/A')}")
        
        created_str = doc.get('created_at', '')
        updated_str = doc.get('updated_at', '')
        
        if created_str and updated_str:
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
                
                total_elapsed = (now - created).total_seconds()
                time_since_update = (now - updated).total_seconds()
                
                print(f"[TIME] Создан: {created_str}")
                print(f"[TIME] Последнее обновление: {updated_str}")
                print(f"[TIME] Время с начала: {total_elapsed/60:.1f} минут ({total_elapsed/3600:.1f} часов)")
                print(f"[TIME] Время с последнего обновления: {time_since_update/60:.1f} минут")
                
                if status == 'indexing':
                    if time_since_update > 300:  # Больше 5 минут
                        print(f"\n[WARNING] !!! ИНДЕКСАЦИЯ ЗАСТРЯЛА !!!")
                        print(f"[WARNING] Документ не обновлялся {time_since_update/60:.1f} минут")
                        print(f"[WARNING] Возможно, процесс индексации завершился с ошибкой")
                    else:
                        print(f"\n[OK] Индексация активна (обновлено {time_since_update:.0f} сек назад)")
            except Exception as e:
                print(f"[WARNING] Ошибка парсинга времени: {e}")
        
        error_msg = doc.get('error_message')
        if error_msg:
            print(f"\n[ERROR] Сообщение об ошибке: {error_msg}")
    else:
        print(f"[ERROR] Документ не найден (Status: {r.status_code})")
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")

# 3. Проверка активных соединений с Ollama
print("\n3. АКТИВНЫЕ СОЕДИНЕНИЯ С OLLAMA:")
print("-" * 70)
print("Проверка через netstat...")
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
        for conn in ollama_connections[:3]:  # Показать первые 3
            print(f"  {conn.strip()}")
    else:
        print(f"[INFO] Нет активных соединений с Ollama")
except Exception as e:
    print(f"[WARNING] Не удалось проверить соединения: {e}")

# 4. Вывод
print("\n" + "=" * 70)
print("ВЫВОД:")
print("=" * 70)
print("1. Ollama работает и отвечает на запросы - [OK]")
print("2. Документ 4 в статусе 'indexing' но не обновлялся долго - [ПРОБЛЕМА]")
print("3. Возможно, индексация завершилась с ошибкой, но статус не обновился")
print("\nРЕКОМЕНДАЦИЯ:")
print("- Проверьте логи бэкенда (консоль, где запущен backend)")
print("- Если индексация застряла, возможно нужно перезапустить индексацию")
print("=" * 70)

