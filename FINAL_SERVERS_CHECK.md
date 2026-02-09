# Итоговая проверка серверов

## ✅ Серверы запущены в фоновом режиме

### Backend
- **Команда**: `cd backend && python run.py`
- **Порт**: 8000
- **URL**: http://localhost:8000/

### Frontend
- **Команда**: `cd frontend && npm run dev`
- **Порт**: 5173
- **URL**: http://localhost:5173/

## Проверка статуса

### 1. Проверьте порты
```bash
netstat -ano | findstr ":5173 :8000"
```

Должны быть строки с `LISTENING` для обоих портов.

### 2. Проверьте процессы
```bash
tasklist | findstr "node python"
```

Должны быть процессы `node.exe` и `python.exe`.

### 3. Откройте в браузере
- **Frontend**: http://localhost:5173/
- **Backend API**: http://localhost:8000/api/health/

## Если фронтенд не отвечает

### Вариант 1: Запустить вручную
Откройте два терминала:

**Терминал 1 (Backend):**
```bash
cd C:\Users\User\Desktop\rag2\backend
python run.py
```

**Терминал 2 (Frontend):**
```bash
cd C:\Users\User\Desktop\rag2\frontend
npm run dev
```

### Вариант 2: Проверить зависимости
```bash
# Frontend
cd frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

### Вариант 3: Проверить порты
```bash
# Проверить, не заняты ли порты
netstat -ano | findstr ":5173 :8000"

# Если заняты, остановите процессы
taskkill /F /PID <PID>
```

## Ожидаемый результат

- ✅ Backend отвечает на http://localhost:8000/api/health/ (статус 200)
- ✅ Frontend отвечает на http://localhost:5173/ (статус 200)
- ✅ Оба порта слушают (LISTENING)

## Готовность

✅ **Серверы должны быть запущены!**

Проверьте в браузере: http://localhost:5173/

