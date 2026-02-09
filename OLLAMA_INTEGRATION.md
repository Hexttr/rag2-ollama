# 🦙 Интеграция Ollama с PageIndex

## ✅ Да, можно подключить Ollama!

Ollama имеет **совместимый API с OpenAI**, поэтому можно использовать PageIndex **бесплатно** с локальными моделями.

---

## 🚀 Быстрая настройка

### 1. Установка Ollama

**Windows:**
```bash
# Скачать с https://ollama.com/download
# Или через winget
winget install Ollama.Ollama
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Загрузка модели

```bash
# Рекомендуемые модели для PageIndex:
ollama pull llama3.2          # Хороший баланс скорости и качества
ollama pull mistral           # Отличное качество
ollama pull qwen2.5:14b       # Очень хорошее качество (больше размер)
ollama pull gemma2:9b         # Быстрая и качественная

# Для тестирования (быстрая, но менее точная):
ollama pull llama3.2:1b
```

### 3. Запуск Ollama сервера

Ollama запускается автоматически, но можно проверить:
```bash
ollama serve
```

Проверка работы:
```bash
curl http://localhost:11434/api/tags
```

---

## 🔧 Модификация PageIndex для работы с Ollama

### Вариант 1: Простая модификация (рекомендуется)

Создайте файл `pageindex_ollama.py` с модифицированными функциями:

```python
# pageindex_ollama.py
import os
import openai
from pageindex.utils import *

# Настройка Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def ChatGPT_API_ollama(model=None, prompt=None, api_key="ollama", chat_history=None):
    """
    Замена ChatGPT_API для работы с Ollama
    """
    if model is None:
        model = OLLAMA_MODEL
    
    max_retries = 10
    client = openai.OpenAI(
        api_key=api_key,  # Ollama не требует ключ, но нужен для совместимости
        base_url=OLLAMA_BASE_URL
    )
    
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history
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
            print(f"Error: {e}")
            if i < max_retries - 1:
                import time
                time.sleep(1)
            else:
                return "Error"

async def ChatGPT_API_async_ollama(model=None, prompt=None, api_key="ollama"):
    """
    Асинхронная версия для Ollama
    """
    if model is None:
        model = OLLAMA_MODEL
    
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
            print(f"Error: {e}")
            if i < max_retries - 1:
                import asyncio
                await asyncio.sleep(1)
            else:
                return "Error"

def ChatGPT_API_with_finish_reason_ollama(model=None, prompt=None, api_key="ollama", chat_history=None):
    """
    Версия с finish_reason для Ollama
    """
    if model is None:
        model = OLLAMA_MODEL
    
    max_retries = 10
    client = openai.OpenAI(
        api_key=api_key,
        base_url=OLLAMA_BASE_URL
    )
    
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history
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
            print(f"Error: {e}")
            if i < max_retries - 1:
                import time
                time.sleep(1)
            else:
                return "Error", "error"
```

### Вариант 2: Модификация исходного кода (более сложный)

Можно напрямую изменить `PageIndex/pageindex/utils.py`, добавив поддержку Ollama через переменные окружения.

---

## 📝 Использование

### Способ 1: Монки-патчинг (простой)

Создайте файл `run_pageindex_ollama.py`:

```python
# run_pageindex_ollama.py
import os
import sys

# Добавляем путь к модифицированным функциям
sys.path.insert(0, os.path.dirname(__file__))

# Монки-патчинг функций
from pageindex import utils
from pageindex_ollama import (
    ChatGPT_API_ollama,
    ChatGPT_API_async_ollama,
    ChatGPT_API_with_finish_reason_ollama
)

# Заменяем функции
utils.ChatGPT_API = ChatGPT_API_ollama
utils.ChatGPT_API_async = ChatGPT_API_async_ollama
utils.ChatGPT_API_with_finish_reason = ChatGPT_API_with_finish_reason_ollama

# Теперь можно использовать обычный run_pageindex.py
from pageindex import page_index_main, config

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf_path', type=str, required=True)
    parser.add_argument('--model', type=str, default='llama3.2')
    args = parser.parse_args()
    
    opt = config(
        model=args.model,
        if_add_node_summary='yes',
        if_add_node_id='yes'
    )
    
    result = page_index_main(args.pdf_path, opt)
    
    import json
    output_file = f"{os.path.splitext(args.pdf_path)[0]}_structure.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Структура сохранена: {output_file}")
```

### Способ 2: Прямое использование

```python
# example_ollama.py
from pageindex_ollama import ChatGPT_API_ollama
from pageindex import page_index_main, config

# Настройка
opt = config(
    model='llama3.2',  # Модель Ollama
    if_add_node_summary='yes'
)

# Обработка документа
result = page_index_main('document.pdf', opt)
```

---

## ⚙️ Настройка через переменные окружения

Создайте `.env` файл:

```bash
# .env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2

# Или используйте OpenAI (если нужно переключиться)
USE_OLLAMA=true
```

---

## 🎯 Рекомендуемые модели Ollama для PageIndex

| Модель | Размер | Качество | Скорость | RAM |
|--------|--------|----------|----------|-----|
| **llama3.2** | 3B | ⭐⭐⭐ | ⚡⚡⚡ | 4GB |
| **mistral** | 7B | ⭐⭐⭐⭐ | ⚡⚡ | 8GB |
| **qwen2.5:14b** | 14B | ⭐⭐⭐⭐⭐ | ⚡ | 16GB |
| **gemma2:9b** | 9B | ⭐⭐⭐⭐ | ⚡⚡ | 10GB |
| **llama3.1:8b** | 8B | ⭐⭐⭐⭐ | ⚡⚡ | 10GB |

**Рекомендация:** Начните с `llama3.2` или `mistral` для баланса качества и скорости.

---

## ⚠️ Важные замечания

### 1. Качество результатов

- ✅ Локальные модели могут работать **хорошо** для простых задач
- ⚠️ Для сложных документов качество может быть **ниже**, чем у GPT-4o
- 💡 Рекомендуется использовать модели **7B+** для лучших результатов

### 2. Скорость

- 🐌 Локальные модели **медленнее**, чем облачные API
- ⏱️ Обработка документа 100 страниц может занять **10-30 минут** (vs 2-5 минут с GPT-4o)
- 💻 Зависит от вашего железа (CPU/GPU)

### 3. Память

- 💾 Модели требуют RAM/VRAM
- 📊 7B модель: ~8-10GB RAM
- 📊 14B модель: ~16-20GB RAM
- 💡 Используйте GPU для ускорения (CUDA)

### 4. JSON форматирование

Некоторые модели могут хуже следовать инструкциям JSON. Может потребоваться:
- Более детальные промпты
- Post-processing ответов
- Использование более мощных моделей

---

## 🧪 Тестирование

Проверьте работу Ollama:

```python
# test_ollama.py
from pageindex_ollama import ChatGPT_API_ollama

response = ChatGPT_API_ollama(
    model='llama3.2',
    prompt='Привет! Ответь коротко: работает ли Ollama?'
)

print(response)
```

---

## 📊 Сравнение: OpenAI vs Ollama

| Параметр | OpenAI GPT-4o | Ollama (локально) |
|----------|---------------|-------------------|
| **Стоимость** | 💰 Платно ($0.50-2/док) | ✅ Бесплатно |
| **Скорость** | ⚡ Быстро (2-5 мин) | 🐌 Медленнее (10-30 мин) |
| **Качество** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐-⭐⭐⭐⭐ |
| **Требования** | Интернет | Локальный компьютер |
| **Приватность** | ❌ Данные уходят в облако | ✅ Все локально |
| **Масштабирование** | ✅ Легко | ⚠️ Ограничено железом |

---

## 🚀 Готовое решение

Я создам готовый файл с интеграцией Ollama. См. `pageindex_ollama.py` и `run_pageindex_ollama.py`.

---

## 💡 Советы по оптимизации

1. **Используйте GPU** (если есть):
   ```bash
   # Ollama автоматически использует GPU, если доступен
   ```

2. **Кэшируйте индексы** - индексация делается один раз

3. **Начните с малых документов** для тестирования

4. **Используйте более мощные модели** для важных задач

5. **Комбинируйте подходы**:
   - Индексация: Ollama (бесплатно, можно подождать)
   - Поиск: OpenAI (быстро, качественно)

---

*Успешной интеграции! 🦙*




