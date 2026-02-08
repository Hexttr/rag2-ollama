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

@router.get("/logs")
async def get_logs(lines: int = 100):
    """Get recent backend logs"""
    from pathlib import Path
    import os
    
    log_file = Path(__file__).parent.parent.parent / "logs" / "backend.log"
    
    if not log_file.exists():
        return {"logs": [], "message": "Log file not found"}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return {
                "logs": recent_lines,
                "total_lines": len(all_lines),
                "returned_lines": len(recent_lines)
            }
    except Exception as e:
        return {"error": str(e), "logs": []}

