# 🎨 Frontend - PageIndex Chat

## 🚀 Запуск

```bash
cd frontend
npm install
npm run dev
```

Приложение будет доступно по адресу: http://localhost:5173

## 📦 Структура проекта

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Header.tsx       ✅ Шапка приложения
│   │   │   └── Sidebar.tsx      ✅ Боковая панель
│   │   ├── Documents/
│   │   │   ├── DocumentList.tsx ✅ Список документов
│   │   │   └── DocumentUpload.tsx ✅ Загрузка документов
│   │   └── Chat/
│   │       ├── ChatWindow.tsx   ✅ Окно чата
│   │       ├── MessageList.tsx  ✅ Список сообщений
│   │       ├── MessageInput.tsx ✅ Ввод сообщений
│   │       └── SourceReferences.tsx ✅ Источники
│   ├── services/
│   │   └── api.ts               ✅ API клиент
│   ├── hooks/
│   │   └── useWebSocket.ts      ✅ WebSocket hook
│   ├── types/
│   │   └── index.ts             ✅ TypeScript типы
│   ├── App.tsx                  ✅ Главный компонент
│   └── main.tsx                 ✅ Точка входа
├── vite.config.ts               ✅ Конфигурация Vite
├── tailwind.config.js           ✅ Конфигурация Tailwind
└── package.json                 ✅ Зависимости
```

## 🎯 Функциональность

### ✅ Реализовано:

1. **Загрузка документов**
   - Drag & drop интерфейс
   - Выбор файла
   - Отображение статуса загрузки

2. **Список документов**
   - Отображение всех документов
   - Статусы (готов, индексация, ошибка)
   - Выбор документа

3. **Чат с документами**
   - Создание чатов
   - Отправка сообщений
   - Получение ответов
   - Отображение источников
   - Markdown рендеринг

4. **Real-time обновления**
   - WebSocket для статуса индексации
   - Polling для обновлений

## 🛠️ Технологии

- **React 18** - UI библиотека
- **TypeScript** - Типизация
- **Vite** - Build tool
- **TailwindCSS** - Стилизация
- **React Query** - Управление состоянием
- **Axios** - HTTP клиент
- **React Markdown** - Рендеринг Markdown

## 📝 API Интеграция

Все API вызовы через `services/api.ts`:

- `documentsApi` - Работа с документами
- `chatsApi` - Работа с чатами
- `healthApi` - Health checks

## 🔄 WebSocket

WebSocket hook для real-time обновлений статуса индексации:

```typescript
const { status, message } = useWebSocket(documentId)
```

## 🎨 UI Компоненты

### Layout
- **Header** - Шапка приложения
- **Sidebar** - Боковая панель с документами и чатами

### Documents
- **DocumentUpload** - Загрузка PDF файлов
- **DocumentList** - Список документов со статусами

### Chat
- **ChatWindow** - Главное окно чата
- **MessageList** - Список сообщений с Markdown
- **MessageInput** - Ввод сообщений
- **SourceReferences** - Отображение источников

## 🚧 Следующие шаги

- [ ] Улучшить WebSocket интеграцию
- [ ] Добавить обработку ошибок
- [ ] Добавить loading states
- [ ] Улучшить UI/UX
- [ ] Добавить темную тему (уже частично)

---

*Frontend готов к использованию!*



