"""
Chat service for managing chats and messages
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.models.chat import Chat, Message, MessageRole
from app.models.document import Document
from app.services.ollama_service import OllamaService
from app.services.pageindex_service import PageIndexService
import logging

logger = logging.getLogger(__name__)

class ChatService:
    """Service for chat management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ollama_service = OllamaService()
        self.pageindex_service = PageIndexService()
    
    def create_chat(self, document_id: Optional[int] = None, title: Optional[str] = None) -> Chat:
        """Create a new chat"""
        chat = Chat(
            document_id=document_id,
            title=title or "New Chat"
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get chat by ID"""
        return self.db.query(Chat).filter(Chat.id == chat_id).first()
    
    def get_chats_by_document(self, document_id: int) -> List[Chat]:
        """Get all chats for a document"""
        return self.db.query(Chat).filter(Chat.document_id == document_id).all()
    
    def get_all_chats(self) -> List[Chat]:
        """Get all chats"""
        return self.db.query(Chat).order_by(Chat.updated_at.desc()).all()
    
    def add_message(
        self,
        chat_id: int,
        role: MessageRole,
        content: str,
        sources: Optional[Dict] = None
    ) -> Message:
        """Add a message to chat"""
        message = Message(
            chat_id=chat_id,
            role=role.value,
            content=content,
            sources=sources
        )
        self.db.add(message)
        
        # Update chat updated_at
        chat = self.get_chat(chat_id)
        if chat:
            from datetime import datetime
            chat.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_messages(self, chat_id: int) -> List[Message]:
        """Get all messages for a chat"""
        return self.db.query(Message).filter(
            Message.chat_id == chat_id
        ).order_by(Message.created_at.asc()).all()
    
    async def process_query(
        self,
        chat_id: int,
        query: str,
        document_id: Optional[int] = None
    ) -> Message:
        """
        Process a user query and generate response
        
        Args:
            chat_id: Chat ID
            query: User query
            document_id: Optional document ID for context
        
        Returns:
            Assistant message with response
        """
        # Add user message
        user_message = self.add_message(chat_id, MessageRole.USER, query)
        
        # If document is provided, search in document
        context = ""
        sources = None
        
        if document_id:
            try:
                # Get document
                document = self.db.query(Document).filter(Document.id == document_id).first()
                if document and document.index_path and document.status.value == "ready":
                    # Search in document tree
                    search_result = await self.pageindex_service.search_tree(
                        document.index_path,
                        query
                    )
                    
                    # Extract context from search result
                    # This is simplified - will be improved with actual tree search
                    if "index" in search_result and "structure" in search_result["index"]:
                        # Get relevant sections
                        structure = search_result["index"]["structure"]
                        context = self._extract_context_from_structure(structure, query)
                        sources = self._extract_sources(structure)
            except Exception as e:
                logger.error(f"Error searching document: {e}")
        
        # Generate response using Ollama
        try:
            if context:
                response_content = await self.ollama_service.generate_with_context(
                    context=context,
                    question=query
                )
            else:
                response_content = await self.ollama_service.generate_response(
                    prompt=f"Ответь на вопрос: {query}"
                )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response_content = f"Извините, произошла ошибка при генерации ответа: {str(e)}"
        
        # Add assistant message
        assistant_message = self.add_message(
            chat_id,
            MessageRole.ASSISTANT,
            response_content,
            sources=sources
        )
        
        return assistant_message
    
    def _extract_context_from_structure(self, structure: Dict, query: str) -> str:
        """Extract relevant context from document structure"""
        # Simplified extraction - will be improved
        context_parts = []
        
        def traverse_nodes(nodes, depth=0):
            for node in nodes:
                if isinstance(node, dict):
                    if "title" in node:
                        context_parts.append(f"{'  ' * depth}{node['title']}")
                    if "summary" in node:
                        context_parts.append(f"  {node['summary']}")
                    if "nodes" in node:
                        traverse_nodes(node["nodes"], depth + 1)
        
        if isinstance(structure, list):
            traverse_nodes(structure)
        elif isinstance(structure, dict) and "structure" in structure:
            traverse_nodes(structure["structure"])
        
        return "\n".join(context_parts[:10])  # Limit context length
    
    def _extract_sources(self, structure: Dict) -> List[Dict]:
        """Extract source references from structure"""
        sources = []
        
        def traverse_nodes(nodes):
            for node in nodes:
                if isinstance(node, dict):
                    source = {
                        "title": node.get("title", ""),
                        "node_id": node.get("node_id", ""),
                        "pages": f"{node.get('start_index', 0)}-{node.get('end_index', 0)}"
                    }
                    sources.append(source)
                    if "nodes" in node:
                        traverse_nodes(node["nodes"])
        
        if isinstance(structure, list):
            traverse_nodes(structure)
        elif isinstance(structure, dict) and "structure" in structure:
            traverse_nodes(structure["structure"])
        
        return sources[:5]  # Limit to 5 sources
    
    def delete_chat(self, chat_id: int) -> bool:
        """Delete a chat and all its messages"""
        chat = self.get_chat(chat_id)
        if not chat:
            return False
        
        self.db.delete(chat)
        self.db.commit()
        return True





