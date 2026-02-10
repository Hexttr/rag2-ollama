# 🚀 Инструкция по запуску серверов

## Запуск вручную

### 1. Backend (Терминал 1)

```powershell
cd C:\Users\User\Desktop\rag2\backend
python run.py
```

Или:
```powershell
cd C:\Users\User\Desktop\rag2\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Проверка:** http://localhost:8000/api/health

### 2. Frontend (Терминал 2)

```powershell
cd C:\Users\User\Desktop\rag2\frontend
npm run dev
```

**Проверка:** http://localhost:5173

### 3. Ollama (если не запущен)

```powershell
ollama serve
```

В другом терминале:
```powershell
ollama pull llama3.2
```

## Проверка портов

```powershell
# Проверить порты
netstat -ano | findstr ":8000 :5173"

# Убить процесс на порту (если нужно)
# taskkill /PID <PID> /F
```

## Ссылки

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

## Устранение проблем

### Frontend не запускается:
1. Проверьте, что вы в правильной директории: `C:\Users\User\Desktop\rag2\frontend`
2. Убедитесь, что `node_modules` существует: `npm install`
3. Проверьте порт 5173: `netstat -ano | findstr ":5173"`

### Backend не запускается:
1. Проверьте виртуальное окружение: `venv\Scripts\activate`
2. Убедитесь, что зависимости установлены: `pip install -r requirements.txt`
3. Проверьте порт 8000: `netstat -ano | findstr ":8000"`

---

*Используйте эти команды для запуска вручную*






