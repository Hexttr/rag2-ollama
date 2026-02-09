"""Проверка статуса документов"""
import httpx
import json

try:
    r = httpx.get('http://localhost:8000/api/documents/', timeout=10)
    print(f'Status: {r.status_code}')
    if r.text:
        docs = json.loads(r.text)
        print(f'Documents: {len(docs)}')
        for d in docs[-3:]:
            print(f'  ID: {d.get("id")}, Status: {d.get("status")}, File: {d.get("filename", "N/A")}')
    else:
        print('Empty response')
except Exception as e:
    print(f'Error: {e}')

