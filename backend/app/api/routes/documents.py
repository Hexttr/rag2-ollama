"""
Document API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
import logging

logger = logging.getLogger(__name__)
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

@router.get("", response_model=List[DocumentResponse])
@router.get("/", response_model=List[DocumentResponse])
async def get_documents(db: Session = Depends(get_db)):
    """Get all documents"""
    try:
        service = DocumentService(db)
        documents = service.get_all_documents()
        logger.info(f"Retrieved {len(documents)} documents")
        # Convert to response models
        return [DocumentResponse.from_orm(doc) for doc in documents]
    except Exception as e:
        logger.error(f"Error getting documents: {e}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")

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
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        
        # Validate file
        if not file.filename:
            logger.error("No filename provided")
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not file.filename.endswith('.pdf'):
            logger.error(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        logger.info(f"Reading file content: {file.filename}")
        content = await file.read()
        logger.info(f"File read, size: {len(content)} bytes")
        
        if len(content) == 0:
            logger.error("File is empty")
            raise HTTPException(status_code=400, detail="File is empty")
        
        logger.info(f"Uploading file: {file.filename}, size: {len(content)} bytes")
        
        # Save file
        service = DocumentService(db)
        try:
            file_path = service.save_uploaded_file(content, file.filename)
            logger.info(f"File saved to: {file_path}")
        except Exception as e:
            logger.error(f"Error saving file: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        
        # Create document record
        try:
            document = service.create_document(file.filename, file_path)
            logger.info(f"Document created with ID: {document.id}")
        except Exception as e:
            logger.error(f"Error creating document record: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error creating document record: {str(e)}")
        
        # Start indexing in background
        try:
            background_tasks.add_task(index_document_task, document.id, file_path)
            logger.info(f"Background indexing task added for document {document.id}")
        except Exception as e:
            logger.error(f"Error adding background task: {e}", exc_info=True)
            # Don't fail the upload if background task fails
        
        return {
            "id": document.id,
            "filename": document.filename,
            "status": document.status.value,
            "message": "Document uploaded, indexing started"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

async def index_document_task(document_id: int, file_path: str):
    """Background task for indexing document"""
    from app.database.database import SessionLocal
    from app.services.document_service import DocumentService
    from app.services.pageindex_service import PageIndexService
    from app.api.routes.websocket import get_connection_manager
    import traceback
    
    db = SessionLocal()
    manager = get_connection_manager()
    
    try:
        logger.info(f"Starting indexing task for document {document_id}, file: {file_path}")
        
        service = DocumentService(db)
        
        # Update status to indexing
        service.update_document_status(document_id, DocumentStatus.INDEXING)
        logger.info(f"Document {document_id} status updated to INDEXING")
        
        # Notify: indexing started
        try:
            await manager.broadcast_to_document(document_id, {
                "type": "status_update",
                "status": "indexing",
                "message": "Индексация началась..."
            })
        except Exception as ws_error:
            logger.warning(f"WebSocket notification failed: {ws_error}")
        
        # Initialize PageIndex service
        try:
            pageindex_service = PageIndexService()
            logger.info("PageIndexService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PageIndexService: {e}")
            raise
        
        # Notify: processing
        try:
            await manager.broadcast_to_document(document_id, {
                "type": "status_update",
                "status": "indexing",
                "message": "Обработка документа..."
            })
        except Exception as ws_error:
            logger.warning(f"WebSocket notification failed: {ws_error}")
        
        # Index document
        logger.info(f"Starting PageIndex indexing for: {file_path}")
        result = await pageindex_service.index_document(file_path)
        logger.info(f"Indexing completed, index saved to: {result['index_path']}")
        
        # Notify: indexing complete
        try:
            await manager.broadcast_to_document(document_id, {
                "type": "status_update",
                "status": "ready",
                "message": "Индексация завершена",
                "index_path": result["index_path"]
            })
        except Exception as ws_error:
            logger.warning(f"WebSocket notification failed: {ws_error}")
        
        # Update status to ready
        service.update_document_status(
            document_id,
            DocumentStatus.READY,
            index_path=result["index_path"]
        )
        logger.info(f"Document {document_id} status updated to READY")
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"Indexing failed for document {document_id}: {error_msg}")
        logger.error(f"Traceback: {error_trace}")
        
        # Notify: error
        try:
            await manager.broadcast_to_document(document_id, {
                "type": "status_update",
                "status": "error",
                "message": f"Ошибка индексации: {error_msg}"
            })
        except Exception as ws_error:
            logger.warning(f"WebSocket notification failed: {ws_error}")
        
        # Update status to error
        try:
            service = DocumentService(db)
            service.update_document_status(
                document_id,
                DocumentStatus.ERROR,
                error_message=error_msg
            )
        except Exception as db_error:
            logger.error(f"Failed to update document status to ERROR: {db_error}")
    finally:
        db.close()
        logger.info(f"Indexing task completed for document {document_id}")

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

