"""
Ollama service for LLM interactions
"""
import openai
from typing import Optional, List, Dict
from app.core.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with Ollama"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        
        # Create OpenAI-compatible client
        self.client = openai.OpenAI(
            api_key="ollama",  # Not used, but required for compatibility
            base_url=self.base_url
        )
    
    async def check_connection(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url.replace('/v1', '')}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False
    
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response from Ollama"""
        try:
            model = model or self.model
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def generate_with_context(
        self,
        context: str,
        question: str,
        model: Optional[str] = None
    ) -> str:
        """Generate response with context"""
        prompt = f"""На основе следующего контекста из документа ответьте на вопрос пользователя.

Контекст:
{context}

Вопрос: {question}

Дайте точный и полный ответ, используя информацию из предоставленного контекста.
Если информации недостаточно, укажите это."""
        
        return await self.generate_response(prompt, model=model)
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        # This would require additional API call to Ollama
        # For now, return default model
        return [self.model]



