# 🚀 Инструкции по разработке

## Запуск Backend

```bash
cd backend
python run.py
```

Или через uvicorn напрямую:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Проверка работы

1. Health check: http://localhost:8000/api/health
2. Ollama check: http://localhost:8000/api/health/ollama
3. Documents list: http://localhost:8000/api/documents

## Структура проекта

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── documents.py
│   │       └── health.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── database/
│   │   └── database.py
│   ├── models/
│   │   ├── document.py
│   │   └── chat.py
│   ├── services/
│   │   ├── document_service.py
│   │   ├── ollama_service.py
│   │   └── pageindex_service.py
│   └── main.py
├── requirements.txt
└── run.py
```

## Следующие шаги

1. Исправить импорты PageIndex
2. Протестировать загрузку документов
3. Протестировать индексацию
4. Создать frontend





