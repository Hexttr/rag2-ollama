"""
Интеграция Ollama с PageIndex
Позволяет использовать локальные LLM модели вместо OpenAI API
"""

import os
import openai
import time
import asyncio
import logging

# Настройка Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Проверка доступности Ollama
def check_ollama_connection():
    """Проверяет, доступен ли Ollama сервер"""
    try:
        import requests
        base_url = OLLAMA_BASE_URL.replace('/v1', '')
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except ImportError:
        # requests не установлен, но это не критично
        # Попробуем через urllib
        try:
            import urllib.request
            base_url = OLLAMA_BASE_URL.replace('/v1', '')
            req = urllib.request.Request(f"{base_url}/api/tags")
            urllib.request.urlopen(req, timeout=5)
            return True
        except:
            return False
    except:
        return False

def ChatGPT_API_ollama(model=None, prompt=None, api_key="ollama", chat_history=None):
    """
    Замена ChatGPT_API для работы с Ollama
    
    Args:
        model: Название модели Ollama (по умолчанию из OLLAMA_MODEL)
        prompt: Текст запроса
        api_key: Не используется для Ollama, но нужен для совместимости
        chat_history: История чата (опционально)
    
    Returns:
        str: Ответ модели
    """
    if model is None:
        model = OLLAMA_MODEL
    
    if prompt is None:
        raise ValueError("Prompt is required")
    
    max_retries = 10
    client = openai.OpenAI(
        api_key=api_key,  # Ollama не требует ключ, но нужен для совместимости
        base_url=OLLAMA_BASE_URL
    )
    
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history.copy()
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f'************* Retrying ({i+1}/{max_retries}) *************')
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                time.sleep(2)  # Увеличено время ожидания для локальных моделей
            else:
                logging.error('Max retries reached for prompt: ' + prompt[:100])
                return "Error"

async def ChatGPT_API_async_ollama(model=None, prompt=None, api_key="ollama"):
    """
    Асинхронная версия для Ollama
    
    Args:
        model: Название модели Ollama
        prompt: Текст запроса
        api_key: Не используется для Ollama
    
    Returns:
        str: Ответ модели
    """
    if model is None:
        model = OLLAMA_MODEL
    
    if prompt is None:
        raise ValueError("Prompt is required")
    
    max_retries = 10
    messages = [{"role": "user", "content": prompt}]
    
    for i in range(max_retries):
        try:
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=OLLAMA_BASE_URL
            )
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f'************* Retrying ({i+1}/{max_retries}) *************')
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                await asyncio.sleep(2)  # Увеличено время ожидания
            else:
                logging.error('Max retries reached for prompt: ' + prompt[:100])
                return "Error"

def ChatGPT_API_with_finish_reason_ollama(model=None, prompt=None, api_key="ollama", chat_history=None):
    """
    Версия с finish_reason для Ollama
    
    Args:
        model: Название модели Ollama
        prompt: Текст запроса
        api_key: Не используется для Ollama
        chat_history: История чата (опционально)
    
    Returns:
        tuple: (ответ, finish_reason)
    """
    if model is None:
        model = OLLAMA_MODEL
    
    if prompt is None:
        raise ValueError("Prompt is required")
    
    max_retries = 10
    client = openai.OpenAI(
        api_key=api_key,
        base_url=OLLAMA_BASE_URL
    )
    
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history.copy()
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "length":
                return response.choices[0].message.content, "max_output_reached"
            else:
                return response.choices[0].message.content, "finished"
        except Exception as e:
            print(f'************* Retrying ({i+1}/{max_retries}) *************')
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                time.sleep(2)
            else:
                logging.error('Max retries reached for prompt: ' + prompt[:100])
                return "Error", "error"

# Функция для патчинга модуля pageindex.utils
def patch_pageindex_for_ollama():
    """
    Заменяет функции в pageindex.utils на версии для Ollama
    """
    try:
        from pageindex import utils
        
        utils.ChatGPT_API = ChatGPT_API_ollama
        utils.ChatGPT_API_async = ChatGPT_API_async_ollama
        utils.ChatGPT_API_with_finish_reason = ChatGPT_API_with_finish_reason_ollama
        
        print("[OK] PageIndex successfully configured for Ollama!")
        print(f"   Model: {OLLAMA_MODEL}")
        print(f"   URL: {OLLAMA_BASE_URL}")
        
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import pageindex: {e}")
        return False

if __name__ == "__main__":
    # Тестирование подключения
    print("Проверка подключения к Ollama...")
    if check_ollama_connection():
        print("✅ Ollama доступен!")
        
        # Тестовый запрос
        print("\nТестовый запрос...")
        response = ChatGPT_API_ollama(
            model=OLLAMA_MODEL,
            prompt="Привет! Ответь коротко: работает ли Ollama с PageIndex?"
        )
        print(f"Ответ: {response}")
    else:
        print("❌ Ollama недоступен!")
        print("   Убедитесь, что Ollama запущен: ollama serve")
        print("   Или установите: https://ollama.com")

