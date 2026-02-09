"""
Run development server
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Use 127.0.0.1 instead of 0.0.0.0 for better compatibility
        port=settings.BACKEND_PORT,
        reload=False,  # Disable reload to avoid issues
        log_level="info"
    )




