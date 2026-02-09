"""Прямой тест Ollama"""
import httpx
import json

print("=" * 60)
print("Тест подключения к Ollama")
print("=" * 60)

# Тест 1: Нативный API Ollama
print("\n1. Тест нативного API Ollama (/api/tags)...")
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
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
    print(f"   [ERROR] {e}")

# Тест 2: OpenAI-совместимый API
print("\n2. Тест OpenAI-совместимого API (/v1/models)...")
try:
    r = httpx.get('http://localhost:11434/v1/models', timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] OpenAI API доступен!")
        print(f"   Models: {data}")
    else:
        print(f"   [ERROR] Status: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Тест 3: Прямой запрос к /api/generate
print("\n3. Тест нативного API (/api/generate)...")
try:
    data = {
        'model': 'llama3.1:8b',
        'prompt': 'Hello',
        'stream': False
    }
    r = httpx.post('http://localhost:11434/api/generate', json=data, timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   [OK] Нативный API работает!")
        result = r.json()
        print(f"   Response: {result.get('response', '')[:100]}")
    else:
        print(f"   [ERROR] Status: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Тест 4: OpenAI-совместимый chat/completions
print("\n4. Тест OpenAI chat/completions (/v1/chat/completions)...")
try:
    data = {
        'model': 'llama3.1:8b',
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'stream': False
    }
    r = httpx.post('http://localhost:11434/v1/chat/completions', json=data, timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   [OK] OpenAI API работает!")
        result = r.json()
        print(f"   Response: {result.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]}")
    else:
        print(f"   [ERROR] Status: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 60)
print("Тест завершен")
print("=" * 60)

