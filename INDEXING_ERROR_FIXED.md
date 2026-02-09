# ✅ Ошибка индексации исправлена

## Проблема

**Ошибка**: `finish reason: error`

Ollama возвращал `finish_reason == "error"` в ответе, но код не обрабатывал этот случай правильно.

## Исправления

### 1. Обработка `finish_reason == "error"`

Добавлена обработка случая, когда Ollama возвращает `finish_reason == "error"`:

**В `pageindex_ollama.py`:**
- Функция `patched_ChatGPT_API_with_finish_reason` теперь проверяет `finish_reason == "error"`
- При ошибке делается повторная попытка (до 10 раз)
- Если все попытки исчерпаны, возвращается "Error", "error"

**В `backend/app/services/pageindex_service.py`:**
- Та же логика применена к локальной версии функции

### 2. Добавлен timeout во все запросы к Ollama

Добавлен `timeout=300` (5 минут) во все вызовы:
- `ollama_client.chat.completions.create()`
- `ollama_async_client.chat.completions.create()`

Это предотвращает зависания при долгих запросах.

## Измененные файлы

1. `pageindex_ollama.py`:
   - Добавлена обработка `finish_reason == "error"`
   - Добавлен timeout во все запросы

2. `backend/app/services/pageindex_service.py`:
   - Добавлена обработка `finish_reason == "error"`
   - Добавлен timeout во все запросы

## Готовность

✅ **Ошибка исправлена**
✅ **Код обрабатывает `finish_reason == "error"`**
✅ **Добавлен timeout для предотвращения зависаний**

Теперь индексация должна работать корректно даже при ошибках Ollama.
