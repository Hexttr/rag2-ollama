"""Проверка статуса серверов"""
import httpx
import time
import subprocess
import sys

print("=" * 60)
print("Проверка серверов")
print("=" * 60)

# Проверка портов
print("\n1. Проверка портов...")
try:
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    ports_8000 = [l for l in lines if ':8000' in l and 'LISTENING' in l]
    ports_5173 = [l for l in lines if ':5173' in l and 'LISTENING' in l]
    
    print(f"   Порт 8000 (Backend): {'[OK]' if ports_8000 else '[NOT LISTENING]'}")
    if ports_8000:
        print(f"   {ports_8000[0][:80]}")
    
    print(f"   Порт 5173 (Frontend): {'[OK]' if ports_5173 else '[NOT LISTENING]'}")
    if ports_5173:
        print(f"   {ports_5173[0][:80]}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Проверка Backend
print("\n2. Проверка Backend (http://localhost:8000/)...")
for i in range(3):
    try:
        r = httpx.get('http://localhost:8000/', timeout=3)
        print(f"   [OK] Backend отвечает: {r.status_code}")
        if r.status_code == 200:
            print(f"   Response: {r.json()}")
        break
    except Exception as e:
        if i < 2:
            print(f"   [WAIT] Попытка {i+1}/3...")
            time.sleep(2)
        else:
            print(f"   [ERROR] Backend не отвечает: {type(e).__name__}")

# Проверка Frontend
print("\n3. Проверка Frontend (http://localhost:5173/)...")
for i in range(3):
    try:
        r = httpx.get('http://localhost:5173/', timeout=3)
        print(f"   [OK] Frontend отвечает: {r.status_code}")
        break
    except Exception as e:
        if i < 2:
            print(f"   [WAIT] Попытка {i+1}/3...")
            time.sleep(2)
        else:
            print(f"   [ERROR] Frontend не отвечает: {type(e).__name__}")

# Проверка API
print("\n4. Проверка API (http://localhost:8000/api/health/)...")
try:
    r = httpx.get('http://localhost:8000/api/health/', timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   Response: {r.json()}")
    else:
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Проверка завершена")
print("=" * 60)


