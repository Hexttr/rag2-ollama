# Статус серверов для тестирования

## Серверы запущены

### Backend
- **Порт**: 8000
- **Команда запуска**: `cd backend && python run.py`
- **URL**: http://localhost:8000
- **API Health**: http://localhost:8000/api/health/

### Frontend  
- **Порт**: 5173
- **Команда запуска**: `cd frontend && npm run dev`
- **URL**: http://localhost:5173/

## Проверка статуса

### Через браузер
1. Откройте: **http://localhost:5173/**
2. Если фронтенд не загружается, проверьте консоль браузера

### Через API
```bash
# Проверка бэкенда
curl http://localhost:8000/api/health/

# Список документов
curl http://localhost:8000/api/documents/
```

## Тест индексации

### 1. Откройте фронтенд
```
http://localhost:5173/
```

### 2. Загрузите PDF
- Используйте интерфейс загрузки
- Или через curl:
  ```bash
  curl -X POST http://localhost:8000/api/documents/upload \
    -F "file=@путь/к/файлу.pdf"
  ```

### 3. Мониторинг
- Проверяйте статус через API
- Смотрите логи: `backend/logs/backend.log`

## Готовность

✅ **Серверы запущены и готовы к тестированию!**

Откройте http://localhost:5173/ в браузере для начала теста.

