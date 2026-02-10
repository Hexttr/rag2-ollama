"""Проверка статуса индексации"""
import httpx
import json

try:
    r = httpx.get('http://127.0.0.1:8000/api/documents/', timeout=10)
    if r.status_code == 200:
        docs = json.loads(r.text)
        print(f'Всего документов: {len(docs)}')
        print('\nПоследние документы:')
        for d in docs[-5:]:
            print(f'  ID: {d.get("id")}, Status: {d.get("status")}, File: {d.get("filename", "N/A")}')
    else:
        print(f'Status: {r.status_code}')
        print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')


