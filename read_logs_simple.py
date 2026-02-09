"""Simple script to read backend logs"""
import sys
from pathlib import Path

log_file = Path("backend/logs/backend.log")

if log_file.exists():
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"Total: {len(lines)} lines")
        print("\n" + "="*70)
        print("LAST 30 LINES:")
        print("="*70)
        for line in lines[-30:]:
            print(line.rstrip())
else:
    print("Log file not found:", log_file)





