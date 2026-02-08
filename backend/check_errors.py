"""
Quick check for common errors
"""
import sys
import os

print("Checking environment...")

# Check Python version
print(f"Python: {sys.version}")

# Check imports
try:
    from app.database.database import init_db, SessionLocal
    print("[OK] Database imports OK")
except Exception as e:
    print(f"[ERROR] Database import error: {e}")

try:
    from app.services.pageindex_service import PageIndexService
    print("[OK] PageIndexService import OK")
except Exception as e:
    print(f"[ERROR] PageIndexService import error: {e}")

try:
    from app.services.ollama_service import OllamaService
    print("[OK] OllamaService import OK")
except Exception as e:
    print(f"[ERROR] OllamaService import error: {e}")

# Check directories
from app.core.config import settings
print(f"\nUpload dir: {settings.UPLOAD_DIR}")
print(f"Index dir: {settings.INDEX_DIR}")

if not os.path.exists(settings.UPLOAD_DIR):
    print(f"[WARN] Creating upload directory: {settings.UPLOAD_DIR}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

if not os.path.exists(settings.INDEX_DIR):
    print(f"[WARN] Creating index directory: {settings.INDEX_DIR}")
    os.makedirs(settings.INDEX_DIR, exist_ok=True)

# Check database
try:
    init_db()
    print("[OK] Database initialized")
except Exception as e:
    print(f"[ERROR] Database init error: {e}")

print("\n[OK] Environment check complete!")

