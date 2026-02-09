"""
Document service for managing documents
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentStatus
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for document management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(
        self,
        filename: str,
        file_path: str
    ) -> Document:
        """Create a new document record"""
        document = Document(
            filename=filename,
            file_path=file_path,
            status=DocumentStatus.UPLOADING
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents"""
        return self.db.query(Document).order_by(Document.created_at.desc()).all()
    
    def update_document_status(
        self,
        document_id: int,
        status: DocumentStatus,
        index_path: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Document:
        """Update document status"""
        document = self.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        document.status = status
        if index_path:
            document.index_path = index_path
        if error_message:
            document.error_message = error_message
        
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def delete_document(self, document_id: int) -> bool:
        """Delete document and its files"""
        document = self.get_document(document_id)
        if not document:
            return False
        
        # Delete files
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            if document.index_path and os.path.exists(document.index_path):
                os.remove(document.index_path)
        except Exception as e:
            logger.error(f"Failed to delete files for document {document_id}: {e}")
        
        # Delete from database
        self.db.delete(document)
        self.db.commit()
        return True
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to upload directory"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path




