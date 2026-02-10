"""Тест для проверки работы Ollama с моделью phi3:3.8b"""
import openai
import json

client = openai.OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

print("Тестирую модель phi3:3.8b...")
try:
    response = client.chat.completions.create(
        model="phi3:3.8b",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
    print(f"✅ Успешно! Модель: {getattr(response, 'model', 'N/A')}")
    print(f"Ответ: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    error_str = str(e)
    if "46.9" in error_str or "memory" in error_str.lower():
        print("🚨 ПРОБЛЕМА: Ollama пытается загрузить большую модель!")
        print(f"Полная ошибка: {error_str}")

