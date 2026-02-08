# Проверка статуса документов

## Текущая ситуация

Документы 5 и 6 застряли в статусе `UPLOADING` - индексация не запустилась автоматически.

## Что было сделано

1. ✅ Создан скрипт `backend/fix_indexing.py` для ручного запуска индексации
2. ✅ Скрипт запущен в фоновом режиме
3. ✅ Исправлены ошибки в коде

## Как проверить статус

### 1. Через API
```bash
curl http://localhost:8000/api/documents/
```

### 2. Через базу данных
```bash
cd backend
python -c "import sqlite3; conn = sqlite3.connect('app.db'); cursor = conn.cursor(); cursor.execute('SELECT id, filename, status FROM documents ORDER BY id DESC LIMIT 5'); [print(f'ID: {r[0]}, File: {r[1]}, Status: {r[2]}') for r in cursor.fetchall()]; conn.close()"
```

### 3. Через логи
```bash
# Проверьте последние строки логов
tail -f backend/logs/backend.log
```

## Ожидаемые статусы

- `uploading` → `indexing` → `ready` (успех)
- `uploading` → `indexing` → `error` (ошибка)

## Если индексация все еще не запустилась

Запустите скрипт вручную:
```bash
cd backend
python fix_indexing.py
```

Скрипт:
- Найдет все документы со статусом `UPLOADING`
- Обновит статус на `INDEXING`
- Запустит индексацию
- Обновит статус на `READY` или `ERROR`

## Время индексации

Для файла 8 МБ индексация может занять:
- **10-30 минут** в зависимости от сложности документа
- Проверяйте статус через API, не ждите ответа

