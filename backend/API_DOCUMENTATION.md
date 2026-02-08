# 📚 API Документация

## Базовый URL
```
http://localhost:8000
```

## Health Endpoints

### GET /api/health
Проверка здоровья сервиса

**Response:**
```json
{
  "status": "healthy",
  "service": "PageIndex Chat API"
}
```

### GET /api/health/ollama
Проверка подключения к Ollama

**Response:**
```json
{
  "status": "healthy",
  "ollama_available": true,
  "model": "llama3.2"
}
```

## Document Endpoints

### GET /api/documents
Получить список всех документов

**Response:**
```json
[
  {
    "id": 1,
    "filename": "document.pdf",
    "status": "ready",
    "created_at": "2025-01-20T10:00:00",
    "index_path": "./indices/document_structure.json"
  }
]
```

### GET /api/documents/{document_id}
Получить документ по ID

### POST /api/documents/upload
Загрузить и проиндексировать документ

**Request:**
- `file`: PDF файл (multipart/form-data)

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "status": "indexing",
  "message": "Document uploaded, indexing started"
}
```

### GET /api/documents/{document_id}/status
Получить статус индексации документа

**Response:**
```json
{
  "id": 1,
  "status": "ready",
  "error_message": null
}
```

**Статусы:**
- `uploading` - Загрузка
- `indexing` - Индексация
- `ready` - Готов
- `error` - Ошибка

### DELETE /api/documents/{document_id}
Удалить документ

## Chat Endpoints

### POST /api/chats
Создать новый чат

**Request:**
```json
{
  "document_id": 1,
  "title": "Chat about document"
}
```

**Response:**
```json
{
  "id": 1,
  "document_id": 1,
  "title": "Chat about document",
  "created_at": "2025-01-20T10:00:00"
}
```

### GET /api/chats
Получить список чатов

**Query Parameters:**
- `document_id` (optional) - Фильтр по документу

### GET /api/chats/{chat_id}
Получить чат по ID

### GET /api/chats/{chat_id}/messages
Получить историю сообщений чата

**Response:**
```json
[
  {
    "id": 1,
    "chat_id": 1,
    "role": "user",
    "content": "Каковы основные риски?",
    "sources": null,
    "created_at": "2025-01-20T10:00:00"
  },
  {
    "id": 2,
    "chat_id": 1,
    "role": "assistant",
    "content": "Основные риски включают...",
    "sources": [
      {
        "title": "Risk Factors",
        "node_id": "0003",
        "pages": "15-22"
      }
    ],
    "created_at": "2025-01-20T10:00:05"
  }
]
```

### POST /api/chats/{chat_id}/query
Отправить запрос и получить ответ

**Request:**
```json
{
  "query": "Каковы основные риски компании?",
  "document_id": 1
}
```

**Response:**
```json
{
  "id": 2,
  "chat_id": 1,
  "role": "assistant",
  "content": "Основные риски включают...",
  "sources": [...],
  "created_at": "2025-01-20T10:00:05"
}
```

### DELETE /api/chats/{chat_id}
Удалить чат

## WebSocket

### WS /ws/document/{document_id}
Real-time обновления статуса индексации

**Подключение:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/document/1');
```

**Сообщения от сервера:**
```json
{
  "type": "status_update",
  "status": "indexing",
  "message": "Обработка документа..."
}
```

**Статусы:**
- `indexing` - Индексация в процессе
- `ready` - Индексация завершена
- `error` - Ошибка индексации

**Отправка сообщений клиенту:**
```json
{
  "type": "ping"
}
```

**Ответ сервера:**
```json
{
  "type": "pong"
}
```

## Примеры использования

### Загрузка документа
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.pdf"
```

### Создание чата
```bash
curl -X POST http://localhost:8000/api/chats \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1, "title": "My Chat"}'
```

### Отправка запроса
```bash
curl -X POST http://localhost:8000/api/chats/1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Каковы основные риски?", "document_id": 1}'
```

---

*Документация обновлена после завершения Этапов 3-4*

