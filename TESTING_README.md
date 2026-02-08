# Инструкция по тестированию приложения

## Статус
✅ **Приложение готово к тестированию!**

## Что было исправлено

1. ✅ Реализован патчинг PageIndex для работы с Ollama
2. ✅ Создан `pageindex_service.py` для индексации документов
3. ✅ Создан API для загрузки и индексации документов
4. ✅ Исправлены все импорты и зависимости

## Запуск приложения

### 1. Убедитесь, что Ollama запущен

```bash
# Проверка Ollama
curl http://localhost:11434/api/tags

# Или запустите Ollama если не запущен
ollama serve
```

### 2. Запуск Backend сервера

**Вариант 1: Через run.py**
```bash
cd backend
python run.py
```

**Вариант 2: Через start_server.bat (Windows)**
```bash
cd backend
start_server.bat
```

**Вариант 3: Через uvicorn напрямую**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер запустится на: `http://localhost:8000`

## Тестирование API

### 1. Проверка здоровья сервера

```bash
# Health check
curl http://localhost:8000/api/health/

# Ollama health check
curl http://localhost:8000/api/health/ollama
```

### 2. Список документов

```bash
curl http://localhost:8000/api/documents/
```

### 3. Загрузка документа

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@путь/к/файлу.pdf"
```

**Пример:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@uploads/Haval F7 instruction.pdf"
```

### 4. Проверка статуса документа

```bash
curl http://localhost:8000/api/documents/{document_id}
```

### 5. Автоматическое тестирование

Используйте готовый тестовый скрипт:

```bash
cd backend
python test_api.py
```

## Тестирование через Python

```python
import httpx

# Health check
response = httpx.get("http://localhost:8000/api/health/")
print(response.json())

# Загрузка документа
with open("path/to/document.pdf", "rb") as f:
    files = {"file": ("document.pdf", f, "application/pdf")}
    response = httpx.post(
        "http://localhost:8000/api/documents/upload",
        files=files,
        timeout=300
    )
    print(response.json())
    document_id = response.json()["id"]

# Проверка статуса
response = httpx.get(f"http://localhost:8000/api/documents/{document_id}")
print(response.json())
```

## Ожидаемое поведение

1. **Загрузка документа:**
   - Статус: `uploading` → `indexing` → `ready` (или `error`)
   - Индексация происходит в фоновом режиме
   - Время индексации зависит от размера документа

2. **Успешная индексация:**
   - Статус: `ready`
   - `index_path` содержит путь к файлу индекса
   - `error_message`: `null`

3. **Ошибка индексации:**
   - Статус: `error`
   - `error_message` содержит описание ошибки

## Проверка логов

Логи сохраняются в: `backend/logs/backend.log`

```bash
# Просмотр последних логов
tail -f backend/logs/backend.log
```

## Возможные проблемы

### 1. Ollama недоступен
```
Error: Connection refused
```
**Решение:** Убедитесь, что Ollama запущен: `ollama serve`

### 2. Модель не найдена
```
Error: model not found
```
**Решение:** Установите модель: `ollama pull llama3.2` или измените `OLLAMA_MODEL` в конфиге

### 3. Порт занят
```
Error: Address already in use
```
**Решение:** Измените порт в `backend/app/core/config.py` или остановите другой процесс на порту 8000

### 4. Ошибка импорта PageIndex
```
Error: ModuleNotFoundError: No module named 'PageIndex'
```
**Решение:** Убедитесь, что папка `PageIndex` находится в корне проекта `rag2/`

## Структура проекта

```
rag2/
├── PageIndex/          # Оригинальный PageIndex
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── documents.py  # ✅ Новый API для документов
│   │   └── services/
│   │       └── pageindex_service.py  # ✅ Сервис индексации
│   └── run.py
├── pageindex_ollama.py  # ✅ Патчинг для Ollama
└── run_pageindex_ollama.py
```

## Следующие шаги

После успешной индексации документа можно:
1. Использовать API чата для вопросов по документу
2. Реализовать tree search для более точного поиска
3. Добавить WebSocket для real-time обновлений статуса

## Контакты и поддержка

Если возникли проблемы:
1. Проверьте логи: `backend/logs/backend.log`
2. Проверьте подключение к Ollama
3. Убедитесь, что все зависимости установлены: `pip install -r backend/requirements.txt`

