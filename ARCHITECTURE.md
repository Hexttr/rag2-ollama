# 🏗️ Архитектура приложения: PageIndex Chat с Ollama

## 📋 Обзор системы

**Цель:** Создать веб-приложение с чат-интерфейсом для работы с документами через PageIndex, используя локальный Ollama.

---

## 🎯 Требования

### Функциональные:
- ✅ Загрузка PDF документов
- ✅ Индексация документов через PageIndex (CLI)
- ✅ Веб-интерфейс с чатом
- ✅ Вопрос-ответ по документам
- ✅ Показ источников (разделы, страницы)
- ✅ История чатов
- ✅ Управление документами

### Нефункциональные:
- ✅ Использование Ollama (локально)
- ✅ Быстрая индексация
- ✅ Асинхронная обработка
- ✅ Масштабируемость
- ✅ Безопасность

---

## 🏛️ Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Chat UI    │  │  Documents   │  │   Settings   │  │
│  │   Component  │  │   Manager    │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                    HTTP/REST API
                          │
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   API Routes  │  │  Document    │  │   Chat       │  │
│  │   /api/*      │  │  Service     │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  PageIndex   │  │  Ollama       │  │   Storage    │  │
│  │  Wrapper     │  │  Client       │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│   Ollama     │  │   File       │  │   Database   │
│   Server     │  │   Storage    │  │   (SQLite)   │
│  localhost   │  │   /uploads   │  │              │
│  :11434      │  │   /indices   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 📦 Компоненты системы

### 1. Frontend (React + TypeScript)

**Технологии:**
- React 18+
- TypeScript
- Vite (build tool)
- TailwindCSS (стилизация)
- React Query (управление состоянием)
- Axios (HTTP клиент)

**Структура:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── SourceReferences.tsx
│   │   ├── Documents/
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── DocumentCard.tsx
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── hooks/
│   │   ├── useChat.ts
│   │   └── useDocuments.ts
│   ├── types/
│   │   └── index.ts
│   └── App.tsx
└── package.json
```

### 2. Backend (FastAPI + Python)

**Технологии:**
- FastAPI
- Python 3.10+
- SQLAlchemy (ORM)
- SQLite (БД)
- Celery (фоновые задачи)
- WebSockets (real-time обновления)

**Структура:**
```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── documents.py
│   │   │   ├── chat.py
│   │   │   └── health.py
│   │   └── dependencies.py
│   ├── services/
│   │   ├── pageindex_service.py
│   │   ├── ollama_service.py
│   │   ├── document_service.py
│   │   └── chat_service.py
│   ├── models/
│   │   ├── document.py
│   │   ├── chat.py
│   │   └── message.py
│   ├── database/
│   │   ├── database.py
│   │   └── migrations/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   └── main.py
├── requirements.txt
└── Dockerfile
```

### 3. Интеграции

**PageIndex:**
- Использование модифицированного `pageindex_ollama.py`
- Асинхронная индексация документов
- Кэширование индексов

**Ollama:**
- HTTP клиент для Ollama API
- Поддержка разных моделей
- Обработка ошибок и retry логика

---

## 🔄 Потоки данных

### 1. Загрузка и индексация документа

```
User → Frontend → Backend API → Document Service
                                    ↓
                            PageIndex Service
                                    ↓
                            Ollama (индексация)
                                    ↓
                            Сохранение индекса
                                    ↓
                            WebSocket → Frontend
```

### 2. Чат с документом

```
User → Frontend → Backend API → Chat Service
                                    ↓
                            Document Service (получение индекса)
                                    ↓
                            Tree Search (PageIndex)
                                    ↓
                            Ollama (reasoning + ответ)
                                    ↓
                            Форматирование ответа
                                    ↓
                            Frontend (отображение)
```

---

## 🗄️ База данных

### Схема (SQLite):

```sql
-- Документы
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    index_path TEXT,
    status TEXT, -- 'uploading', 'indexing', 'ready', 'error'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Чаты
CREATE TABLE chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Сообщения
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    role TEXT, -- 'user' or 'assistant'
    content TEXT,
    sources JSON, -- источники из документа
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);
```

---

## 🔐 Безопасность

1. **Валидация файлов:**
   - Проверка типа (только PDF)
   - Ограничение размера (max 100MB)
   - Сканирование на вирусы (опционально)

2. **API Security:**
   - Rate limiting
   - CORS настройки
   - Валидация входных данных

3. **Хранение файлов:**
   - Изолированная директория
   - Уникальные имена файлов
   - Очистка старых файлов

---

## ⚡ Производительность

1. **Асинхронная обработка:**
   - Индексация в фоне (Celery)
   - WebSocket для обновлений
   - Кэширование индексов

2. **Оптимизация:**
   - Ленивая загрузка индексов
   - Пагинация сообщений
   - Сжатие ответов

3. **Масштабирование:**
   - Горизонтальное масштабирование backend
   - Redis для кэша (опционально)
   - Load balancing (для продакшена)

---

## 🚀 Деплой

### Development:
- Frontend: Vite dev server (localhost:5173)
- Backend: FastAPI dev server (localhost:8000)
- Ollama: локально (localhost:11434)

### Production:
- Frontend: Nginx + статические файлы
- Backend: Gunicorn + Uvicorn
- Database: PostgreSQL (вместо SQLite)
- Ollama: отдельный сервер или контейнер

---

## 📊 Мониторинг

1. **Логирование:**
   - Структурированные логи
   - Уровни логирования
   - Ротация логов

2. **Метрики:**
   - Время индексации
   - Время ответа API
   - Использование Ollama

3. **Ошибки:**
   - Обработка исключений
   - Уведомления об ошибках
   - Retry механизмы

---

## 🔧 Конфигурация

### Environment Variables:

```bash
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./app.db
UPLOAD_DIR=./uploads
INDEX_DIR=./indices

# Ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=300

# PageIndex
PAGEINDEX_MAX_PAGES_PER_NODE=10
PAGEINDEX_MAX_TOKENS_PER_NODE=20000

# Security
MAX_FILE_SIZE=104857600  # 100MB
ALLOWED_EXTENSIONS=pdf
```

---

## 📝 API Endpoints

### Documents:
- `POST /api/documents/upload` - Загрузка документа
- `GET /api/documents` - Список документов
- `GET /api/documents/{id}` - Информация о документе
- `DELETE /api/documents/{id}` - Удаление документа
- `GET /api/documents/{id}/status` - Статус индексации

### Chat:
- `POST /api/chats` - Создать чат
- `GET /api/chats` - Список чатов
- `GET /api/chats/{id}` - Получить чат
- `POST /api/chats/{id}/messages` - Отправить сообщение
- `GET /api/chats/{id}/messages` - История сообщений
- `DELETE /api/chats/{id}` - Удалить чат

### Health:
- `GET /api/health` - Проверка здоровья
- `GET /api/health/ollama` - Проверка Ollama

---

## 🎨 UI/UX Дизайн

### Главная страница:
- Список документов слева
- Чат по центру
- Настройки справа

### Компоненты:
- Drag & drop загрузка
- Real-time статус индексации
- Markdown рендеринг ответов
- Подсветка источников
- История чатов

---

## 🧪 Тестирование

1. **Unit тесты:**
   - Сервисы
   - Утилиты
   - Компоненты

2. **Integration тесты:**
   - API endpoints
   - Интеграция с Ollama
   - Интеграция с PageIndex

3. **E2E тесты:**
   - Полный flow загрузки и чата
   - Обработка ошибок

---

*Архитектура готова к реализации!*



