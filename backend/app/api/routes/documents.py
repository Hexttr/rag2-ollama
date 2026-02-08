"""
Document API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.document import Document, DocumentStatus
from app.services.document_service import DocumentService
from app.services.pageindex_service import PageIndexService
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/api/documents", tags=["documents"])

class DocumentResponse(BaseModel):
    """Document response model"""
    id: int
    filename: str
    status: str
    created_at: str
    index_path: str | None = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(db: Session = Depends(get_db)):
    """Get all documents"""
    service = DocumentService(db)
    documents = service.get_all_documents()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    service = DocumentService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and index a document"""
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read file content
    content = await file.read()
    
    # Save file
    service = DocumentService(db)
    file_path = service.save_uploaded_file(content, file.filename)
    
    # Create document record
    document = service.create_document(file.filename, file_path)
    
    # Start indexing in background
    background_tasks.add_task(index_document_task, document.id, file_path, db)
    
    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status.value,
        "message": "Document uploaded, indexing started"
    }

async def index_document_task(document_id: int, file_path: str):
    """Background task for indexing document"""
    from app.database.database import SessionLocal
    from app.services.document_service import DocumentService
    from app.services.pageindex_service import PageIndexService
    
    db = SessionLocal()
    try:
        service = DocumentService(db)
        pageindex_service = PageIndexService()
        
        # Update status to indexing
        service.update_document_status(document_id, DocumentStatus.INDEXING)
        
        # Index document
        result = await pageindex_service.index_document(file_path)
        
        # Update status to ready
        service.update_document_status(
            document_id,
            DocumentStatus.READY,
            index_path=result["index_path"]
        )
    except Exception as e:
        # Update status to error
        service = DocumentService(db)
        service.update_document_status(
            document_id,
            DocumentStatus.ERROR,
            error_message=str(e)
        )
    finally:
        db.close()

@router.get("/{document_id}/status")
async def get_document_status(document_id: int, db: Session = Depends(get_db)):
    """Get document indexing status"""
    service = DocumentService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "status": document.status.value,
        "error_message": document.error_message
    }

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    service = DocumentService(db)
    success = service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

