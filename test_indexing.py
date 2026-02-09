"""Тестирование индексации после исправлений"""
import httpx
import json
from datetime import datetime

print("=" * 70)
print("ТЕСТИРОВАНИЕ СИСТЕМЫ ПОСЛЕ ИСПРАВЛЕНИЙ")
print("=" * 70)

# 1. Проверка компонентов
print("\n1. ПРОВЕРКА КОМПОНЕНТОВ:")
print("-" * 70)

# Backend
try:
    r = httpx.get('http://127.0.0.1:8000/api/health/', timeout=5)
    if r.status_code == 200:
        print("[OK] Backend работает")
    else:
        print(f"[ERROR] Backend вернул статус: {r.status_code}")
except Exception as e:
    print(f"[ERROR] Backend не отвечает: {e}")

# Ollama
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"[OK] Ollama работает")
        print(f"[MODELS] Модели: {[m['name'] for m in models]}")
    else:
        print(f"[ERROR] Ollama вернул статус: {r.status_code}")
except Exception as e:
    print(f"[ERROR] Ollama не отвечает: {e}")

# Frontend
try:
    r = httpx.get('http://localhost:5173', timeout=5)
    if r.status_code == 200:
        print("[OK] Frontend работает")
    else:
        print(f"[WARNING] Frontend вернул статус: {r.status_code}")
except Exception as e:
    print(f"[WARNING] Frontend не отвечает: {e}")

# 2. Проверка документов
print("\n2. ПРОВЕРКА ДОКУМЕНТОВ:")
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
            
            if doc.get('status') == 'error':
                error_msg = doc.get('error_message', 'N/A')
                print(f"    [ERROR] Ошибка: {error_msg[:150]}")
            elif doc.get('status') == 'indexing':
                created_str = doc.get('created_at', '')
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                        now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
                        elapsed = (now - created).total_seconds()
                        print(f"    [INDEXING] В процессе ({elapsed/60:.1f} минут)")
                    except:
                        pass
    else:
        print(f"[ERROR] Не удалось получить документы (Status: {r.status_code})")
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")

# 3. Тест Ollama API
print("\n3. ТЕСТ OLLAMA API:")
print("-" * 70)
try:
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
        finish_reason = response.get('choices', [{}])[0].get('finish_reason', 'unknown')
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f"[OK] Ollama API работает")
        print(f"[FINISH_REASON] finish_reason: {finish_reason}")
        print(f"[RESPONSE] Ответ: {content[:50]}...")
        
        if finish_reason == "error":
            print(f"[WARNING] Ollama вернул finish_reason='error' - это должно обрабатываться")
        else:
            print(f"[OK] finish_reason корректный: {finish_reason}")
    else:
        print(f"[ERROR] Ollama API вернул статус: {test_r.status_code}")
except Exception as e:
    print(f"[ERROR] Ошибка теста Ollama API: {e}")

print("\n" + "=" * 70)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 70)
print("\nРЕКОМЕНДАЦИИ:")
print("- Если все компоненты работают - можно загружать документ")
print("- Если есть ошибки - проверьте логи backend")
print("=" * 70)

