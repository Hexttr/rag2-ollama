"""Тест подключения к Ollama"""
import httpx
import json
import time

print("=" * 60)
print("Тест подключения к Ollama")
print("=" * 60)

base_url = "http://localhost:11434"
model = "llama3.1:8b"

# Тест 1: Проверка базового API
print(f"\n1. Проверка базового API: {base_url}/api/tags")
try:
    r = httpx.get(f"{base_url}/api/tags", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        models = data.get('models', [])
        print(f"   [OK] Ollama доступен!")
        print(f"   Модели: {[m['name'] for m in models]}")
    else:
        print(f"   [ERROR] Status: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")

# Тест 2: Нативный API generate
print(f"\n2. Тест нативного API: {base_url}/api/generate")
try:
    data = {
        'model': model,
        'prompt': 'Say hello',
        'stream': False
    }
    print(f"   Отправка запроса...")
    r = httpx.post(f"{base_url}/api/generate", json=data, timeout=30)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   [OK] Нативный API работает!")
        print(f"   Response: {result.get('response', '')[:100]}")
    else:
        print(f"   [ERROR] Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")

# Тест 3: OpenAI-совместимый API
print(f"\n3. Тест OpenAI API: {base_url}/v1/chat/completions")
try:
    data = {
        'model': model,
        'messages': [{'role': 'user', 'content': 'Say hello'}],
        'stream': False
    }
    print(f"   Отправка запроса...")
    r = httpx.post(f"{base_url}/v1/chat/completions", json=data, timeout=30)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   [OK] OpenAI API работает!")
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f"   Response: {content[:100]}")
    else:
        print(f"   [ERROR] Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Тест завершен")
print("=" * 60)

