# Настройка Ollama завершена

## Статус

### Ollama
- ✅ **Версия**: 0.15.6
- ✅ **Модели загружены**:
  - `phi3:3.8b` (2.2 GB)
  - `llama3.1:8b` (4.9 GB)
- ✅ **Процессы**: Запущены
- ✅ **Порт**: 11434 слушает

### Конфигурация
- ✅ **Создан файл `.env`** с настройками Ollama
- ✅ **Base URL**: `http://localhost:11434/v1`
- ✅ **Модель**: `llama3.1:8b`

## Настройки в .env

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b
```

## Проверка работы

### 1. Проверка через CLI
```bash
ollama list
ollama run llama3.1:8b "Hello"
```

### 2. Проверка через API
```bash
curl http://localhost:11434/api/tags
```

### 3. Проверка через приложение
- Backend использует настройки из `.env`
- Frontend готов: http://localhost:5173/

## Если Ollama не отвечает

### Перезапуск Ollama
```bash
# Остановить
taskkill /F /IM ollama.exe

# Запустить
ollama serve
```

### Проверка порта
```bash
netstat -ano | findstr ":11434"
```

### Проверка версии
```bash
ollama --version
```

## Готовность

✅ **Ollama настроен и готов к работе!**

Приложение должно теперь успешно подключаться к Ollama для индексации документов.

