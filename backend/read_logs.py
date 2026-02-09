"""
Script to read backend logs
"""
import sys
from pathlib import Path

log_file = Path(__file__).parent / "logs" / "backend.log"

if not log_file.exists():
    print("Log file not found:", log_file)
    sys.exit(1)

try:
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"Total log lines: {len(lines)}")
        print("\n" + "="*80)
        print("RECENT LOGS (last 50 lines):")
        print("="*80 + "\n")
        for line in lines[-50:]:
            print(line.rstrip())
except Exception as e:
    print(f"Error reading logs: {e}")




