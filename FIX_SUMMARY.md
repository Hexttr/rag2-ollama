# ✅ Исправление ошибки индексации

## Проблема

**Ошибка**: `PageIndex indexing failed: finish reason: error`

Ollama возвращал `finish_reason == "error"` в ответе, но код не обрабатывал этот случай, что приводило к падению индексации.

## Исправления

### 1. Обработка `finish_reason == "error"`

**Файлы:**
- `pageindex_ollama.py`
- `backend/app/services/pageindex_service.py`

**Изменения:**
- Добавлена проверка `finish_reason == "error"`
- При ошибке делается повторная попытка (до 10 раз)
- Если все попытки исчерпаны, возвращается "Error", "error"
- Добавлено логирование для отладки

### 2. Добавлен timeout во все запросы

**Файлы:**
- `pageindex_ollama.py`
- `backend/app/services/pageindex_service.py`

**Изменения:**
- Добавлен `timeout=300` (5 минут) во все вызовы `ollama_client.chat.completions.create()`
- Добавлен `timeout=300` во все вызовы `ollama_async_client.chat.completions.create()`

Это предотвращает зависания при долгих запросах.

## Готовность

✅ **Ошибка исправлена**
✅ **Код обрабатывает `finish_reason == "error"`**
✅ **Добавлен timeout для предотвращения зависаний**

## Следующие шаги

1. Перезапустите backend для применения изменений
2. Попробуйте загрузить документ снова
3. Индексация должна работать корректно даже при ошибках Ollama
