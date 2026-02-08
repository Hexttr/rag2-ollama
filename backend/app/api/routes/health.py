"""
Health check routes
"""
from fastapi import APIRouter
from app.services.ollama_service import OllamaService

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "PageIndex Chat API"
    }

@router.get("/ollama")
async def ollama_health_check():
    """Check Ollama connection"""
    service = OllamaService()
    is_available = await service.check_connection()
    
    return {
        "status": "healthy" if is_available else "unavailable",
        "ollama_available": is_available,
        "model": service.model
    }

