# Статус серверов

## Проблема

- ❌ **Frontend не отвечает** (порт 5173 не слушает)
- ❌ **Backend возвращает 502** (порт 8000 не слушает правильно)

## Решение

### 1. Остановить все процессы
```bash
taskkill /F /IM node.exe /IM python.exe
```

### 2. Запустить Backend
```bash
cd backend
python run.py
```

### 3. Запустить Frontend (в другом терминале)
```bash
cd frontend
npm run dev
```

### 4. Проверить статус
```bash
# Проверка портов
netstat -ano | findstr ":5173 :8000"

# Проверка через браузер
# Backend: http://localhost:8000/api/health/
# Frontend: http://localhost:5173/
```

## Ожидаемый результат

- ✅ Backend слушает на порту 8000
- ✅ Frontend слушает на порту 5173
- ✅ Оба отвечают статусом 200

## Если не работает

1. Проверьте логи:
   - Backend: `backend/logs/backend.log`
   - Frontend: консоль терминала

2. Проверьте зависимости:
   - Backend: `pip install -r requirements.txt`
   - Frontend: `npm install`

3. Проверьте порты:
   - Убедитесь, что порты 8000 и 5173 свободны
   - Закройте другие приложения, использующие эти порты

