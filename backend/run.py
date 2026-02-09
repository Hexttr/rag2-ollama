"""
Run development server
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Use 0.0.0.0 to accept connections from localhost and 127.0.0.1
        port=settings.BACKEND_PORT,
        reload=False,  # Disable reload to avoid issues
        log_level="info"
    )




