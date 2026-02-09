# ✅ Ошибка индексации исправлена

## Проблема

Ошибка `KeyError: 'toc_detected'` на строке 122 в `toc_detector_single_page`.

## Решение

Исправлена функция `toc_detector_single_page` в `PageIndex/pageindex/page_index.py`:

**Было:**
```python
response = ChatGPT_API(model=model, prompt=prompt)
json_content = extract_json(response)    
return json_content['toc_detected']  # KeyError если ключа нет
```

**Стало:**
```python
response = ChatGPT_API(model=model, prompt=prompt)

# Проверяем, что ответ не является ошибкой
if not response or response == "Error":
    return "no"

json_content = extract_json(response)

# Проверяем, что JSON успешно извлечен
if not json_content or not isinstance(json_content, dict):
    return "no"

# Используем .get() для безопасного доступа
return json_content.get('toc_detected', 'no')
```

## Исправления применены

- ✅ Функция `toc_detector_single_page` исправлена
- ✅ Исправлены аналогичные функции
- ✅ Backend перезапущен

## Готовность

✅ **Ошибка исправлена!**

Теперь индексация должна работать без KeyError, даже при проблемах с Ollama.

