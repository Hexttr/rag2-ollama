"""
Chat API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database.database import get_db
from app.services.chat_service import ChatService
from app.models.chat import Chat, Message

router = APIRouter(prefix="/api/chats", tags=["chats"])

class ChatCreate(BaseModel):
    """Chat creation model"""
    document_id: Optional[int] = None
    title: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    id: int
    document_id: Optional[int]
    title: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    """Message creation model"""
    content: str

class MessageResponse(BaseModel):
    """Message response model"""
    id: int
    chat_id: int
    role: str
    content: str
    sources: Optional[dict] = None
    created_at: str
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    document_id: Optional[int] = None

@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat"""
    service = ChatService(db)
    chat = service.create_chat(
        document_id=chat_data.document_id,
        title=chat_data.title
    )
    return chat

@router.get("/", response_model=List[ChatResponse])
async def get_chats(
    document_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all chats, optionally filtered by document"""
    service = ChatService(db)
    if document_id:
        chats = service.get_chats_by_document(document_id)
    else:
        chats = service.get_all_chats()
    return chats

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: int, db: Session = Depends(get_db)):
    """Get chat by ID"""
    service = ChatService(db)
    chat = service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(chat_id: int, db: Session = Depends(get_db)):
    """Get all messages for a chat"""
    service = ChatService(db)
    chat = service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = service.get_messages(chat_id)
    return messages

@router.post("/{chat_id}/query", response_model=MessageResponse)
async def process_query(
    chat_id: int,
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Process a query and generate response"""
    service = ChatService(db)
    chat = service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Use document_id from request or chat
    document_id = request.document_id or chat.document_id
    
    message = await service.process_query(
        chat_id=chat_id,
        query=request.query,
        document_id=document_id
    )
    
    return message

@router.delete("/{chat_id}")
async def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    """Delete a chat"""
    service = ChatService(db)
    success = service.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat deleted successfully"}



