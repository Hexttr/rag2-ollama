"""Тест производительности Ollama"""
import httpx
import time

print("=" * 70)
print("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ OLLAMA")
print("=" * 70)

# Тест 1: Простой запрос
print("\n1. ПРОСТОЙ ЗАПРОС:")
print("-" * 70)
try:
    start = time.time()
    r = httpx.post(
        'http://localhost:11434/v1/chat/completions',
        json={
            'model': 'llama3.1:8b',
            'messages': [{'role': 'user', 'content': 'Say "hello"'}],
            'stream': False
        },
        timeout=60
    )
    elapsed = time.time() - start
    print(f"Время ответа: {elapsed:.2f} секунд")
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        response = r.json()
        finish_reason = response.get('choices', [{}])[0].get('finish_reason', 'unknown')
        print(f"Finish reason: {finish_reason}")
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 2: Запрос с большим промптом (имитация индексации)
print("\n2. ЗАПРОС С БОЛЬШИМ ПРОМПТОМ:")
print("-" * 70)
large_prompt = """
Your job is to detect if there is a table of content provided in the given text.
Given text: This is a test document with multiple sections. Section 1: Introduction. Section 2: Methods. Section 3: Results. Section 4: Conclusion.
return the following JSON format:
{
    "thinking": "why do you think there is a table of content in the given text",
    "toc_detected": "yes or no",
}
Directly return the final JSON structure. Do not output anything else.
Please note: abstract,summary, notation list, figure list, table list, etc. are not table of contents.
"""
try:
    start = time.time()
    r = httpx.post(
        'http://localhost:11434/v1/chat/completions',
        json={
            'model': 'llama3.1:8b',
            'messages': [{'role': 'user', 'content': large_prompt}],
            'stream': False
        },
        timeout=120
    )
    elapsed = time.time() - start
    print(f"Время ответа: {elapsed:.2f} секунд ({elapsed/60:.1f} минут)")
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        response = r.json()
        finish_reason = response.get('choices', [{}])[0].get('finish_reason', 'unknown')
        print(f"Finish reason: {finish_reason}")
        if finish_reason == "error":
            print("[WARNING] Ollama вернул finish_reason='error'")
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 3: Проверка доступности Ollama
print("\n3. ПРОВЕРКА OLLAMA:")
print("-" * 70)
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"[OK] Ollama работает")
        print(f"Модели: {[m['name'] for m in models]}")
        
        # Проверка размера моделей
        for model in models:
            size = model.get('size', 0)
            size_gb = size / (1024**3) if size > 0 else 0
            print(f"  {model['name']}: {size_gb:.2f} GB")
    else:
        print(f"[ERROR] Ollama вернул статус: {r.status_code}")
except Exception as e:
    print(f"[ERROR] Ошибка подключения: {e}")

print("\n" + "=" * 70)
print("ВЫВОД:")
print("=" * 70)
print("Если время ответа > 5 минут - Ollama работает медленно")
print("Если finish_reason='error' - возможна проблема с моделью")
print("=" * 70)

