"""
FastAPI main application
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.database import init_db
from app.api.routes import documents, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PageIndex Chat API",
    description="API for document indexing and chat with Ollama",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(documents.router)

# Chat routes
from app.api.routes import chat
app.include_router(chat.router)

# WebSocket routes
from app.api.routes import websocket
app.include_router(websocket.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        print("[OK] Database initialized")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"[ERROR] Database initialization failed: {e}")
        # Don't exit - allow server to start even if DB init fails

@app.get("/")
async def root():
    return {
        "message": "PageIndex Chat API",
        "version": "0.1.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.BACKEND_HOST, port=settings.BACKEND_PORT)

