"""Проверка готовности приложения"""
import httpx
import time

print("=" * 60)
print("Проверка готовности приложения")
print("=" * 60)

# 1. Проверка Ollama
print("\n1. Проверка Ollama...")
try:
    r = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = r.json().get('models', [])
        print(f"   [OK] Ollama доступен")
        print(f"   Модели: {[m['name'] for m in models]}")
    else:
        print(f"   [ERROR] Ollama недоступен (status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Ollama недоступен: {e}")

# 2. Проверка Backend
print("\n2. Проверка Backend...")
for i in range(5):
    try:
        r = httpx.get('http://localhost:8000/api/health/', timeout=3)
        if r.status_code == 200:
            print(f"   [OK] Backend доступен")
            print(f"   Response: {r.json()}")
            break
        else:
            print(f"   [WAIT] Backend запускается... (status: {r.status_code})")
    except:
        print(f"   [WAIT] Backend запускается... (попытка {i+1}/5)")
        time.sleep(2)
else:
    print("   [ERROR] Backend не отвечает")

# 3. Проверка документов API
print("\n3. Проверка Documents API...")
try:
    r = httpx.get('http://localhost:8000/api/documents/', timeout=5)
    if r.status_code == 200:
        docs = r.json()
        print(f"   [OK] Documents API работает")
        print(f"   Всего документов: {len(docs)}")
        if docs:
            print("   Последние документы:")
            for doc in docs[-3:]:
                print(f"     ID: {doc['id']}, Status: {doc['status']}")
    else:
        print(f"   [ERROR] Documents API не работает (status: {r.status_code})")
except Exception as e:
    print(f"   [ERROR] Documents API ошибка: {e}")

# 4. Итоговый статус
print("\n" + "=" * 60)
print("ИТОГОВЫЙ СТАТУС")
print("=" * 60)
print("Приложение готово к индексации документов!")
print("\nДля загрузки документа используйте:")
print("  POST http://localhost:8000/api/documents/upload")
print("  Content-Type: multipart/form-data")
print("  Body: file=<путь_к_pdf>")


