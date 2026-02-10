"""
Document API routes
"""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database.database import get_db
from app.services.document_service import DocumentService
from app.services.pageindex_service import PageIndexService
from app.models.document import Document, DocumentStatus
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

class DocumentResponse(BaseModel):
    """Document response model"""
    id: int
    filename: str
    file_path: str
    index_path: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: str
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Загружает и индексирует PDF документ
    """
    try:
        # Проверка типа файла
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Поддерживаются только PDF файлы")
        
        logger.info(f"Начало загрузки файла: {file.filename}")
        
        # Сохранение файла с таймаутом
        document_service = DocumentService(db)
        import asyncio
        try:
            file_content = await asyncio.wait_for(file.read(), timeout=300.0)  # 5 минут на загрузку
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Таймаут загрузки файла. Файл слишком большой или соединение медленное.")
        
        file_size_mb = len(file_content) / 1024 / 1024
        logger.info(f"Файл загружен: {file.filename}, размер: {file_size_mb:.2f} MB")
        
        # Проверка размера файла
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"Файл слишком большой. Максимальный размер: {settings.MAX_FILE_SIZE / 1024 / 1024:.0f} MB"
            )
        
        file_path = document_service.save_uploaded_file(file_content, file.filename)
        
        # Создание записи в БД
        document = document_service.create_document(
            filename=file.filename,
            file_path=file_path
        )
        
        # Запуск индексации в фоне
        background_tasks.add_task(
            index_document_task,
            document_id=document.id,
            file_path=file_path,
            db=db
        )
        
        logger.info(f"Документ {document.id} загружен, индексация запущена в фоне")
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            file_path=document.file_path,
            index_path=document.index_path,
            status=document.status.value,
            error_message=document.error_message,
            created_at=document.created_at.isoformat() if document.created_at else "",
            updated_at=document.updated_at.isoformat() if document.updated_at else None
        )
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке документа: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке документа: {str(e)}")

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(db: Session = Depends(get_db)):
    """Получить список всех документов"""
    try:
        document_service = DocumentService(db)
        documents = document_service.get_all_documents()
        
        return [
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_path=doc.file_path,
                index_path=doc.index_path,
                status=doc.status.value,
                error_message=doc.error_message,
                created_at=doc.created_at.isoformat() if doc.created_at else "",
                updated_at=doc.updated_at.isoformat() if doc.updated_at else None
            )
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Ошибка при получении документов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении документов: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Получить документ по ID"""
    try:
        document_service = DocumentService(db)
        document = document_service.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Документ не найден")
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            file_path=document.file_path,
            index_path=document.index_path,
            status=document.status.value,
            error_message=document.error_message,
            created_at=document.created_at.isoformat() if document.created_at else "",
            updated_at=document.updated_at.isoformat() if document.updated_at else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении документа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении документа: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Удалить документ"""
    try:
        document_service = DocumentService(db)
        success = document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Документ не найден")
        
        return {"message": "Документ удален"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении документа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении документа: {str(e)}")

def index_document_task(document_id: int, file_path: str, db: Session):
    """
    Фоновая задача для индексации документа
    """
    from app.database.database import SessionLocal
    from app.api.routes.websocket import get_connection_manager
    import asyncio
    
    # Создаем новую сессию БД для фоновой задачи
    db_session = SessionLocal()
    document_service = DocumentService(db_session)
    pageindex_service = PageIndexService()
    connection_manager = get_connection_manager()
    
    def send_ws_message(message: dict):
        """Вспомогательная функция для отправки WebSocket сообщений"""
        try:
            # Используем asyncio для отправки в синхронном контексте
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если цикл уже запущен, создаем задачу
                asyncio.create_task(connection_manager.broadcast_to_document(document_id, message))
            else:
                # Если цикл не запущен, запускаем его
                loop.run_until_complete(connection_manager.broadcast_to_document(document_id, message))
        except Exception as ws_error:
            logger.debug(f"Не удалось отправить WebSocket сообщение: {ws_error}")
    
    try:
        logger.info(f"Начало индексации документа {document_id}: {file_path}")
        
        # Отправляем начальный статус через WebSocket
        send_ws_message({
            "type": "indexing_status",
            "status": "indexing",
            "message": "Начало индексации документа...",
            "progress": 0
        })
        
        # Обновляем статус на INDEXING
        document_service.update_document_status(
            document_id=document_id,
            status=DocumentStatus.INDEXING
        )
        
        # Индексируем документ (это может занять много времени для больших файлов)
        import time
        start_time = time.time()
        logger.info(f"Начало индексации документа {document_id}. Это может занять несколько минут для больших файлов...")
        
        # Отправляем прогресс
        send_ws_message({
            "type": "indexing_status",
            "status": "indexing",
            "message": "Извлечение структуры документа...",
            "progress": 10
        })
        
        result = pageindex_service.index_document(
            pdf_path=file_path,
            document_id=document_id
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Индексация документа {document_id} заняла {elapsed_time:.2f} секунд ({elapsed_time/60:.2f} минут)")
        
        # Отправляем успешный статус
        send_ws_message({
            "type": "indexing_status",
            "status": "ready",
            "message": f"Индексация завершена успешно за {elapsed_time/60:.1f} минут",
            "progress": 100
        })
        
        # Обновляем статус на READY
        document_service.update_document_status(
            document_id=document_id,
            status=DocumentStatus.READY,
            index_path=result["index_path"]
        )
        
        logger.info(f"Индексация документа {document_id} завершена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при индексации документа {document_id}: {e}")
        import traceback
        error_msg = f"PageIndex indexing failed: {str(e)}"
        logger.error(traceback.format_exc())
        
        # Отправляем ошибку через WebSocket
        send_ws_message({
            "type": "indexing_status",
            "status": "error",
            "message": error_msg,
            "progress": 0
        })
        
        # Обновляем статус на ERROR
        try:
            document_service.update_document_status(
                document_id=document_id,
                status=DocumentStatus.ERROR,
                error_message=error_msg[:500]  # Ограничиваем длину сообщения об ошибке
            )
        except Exception as update_error:
            logger.error(f"Ошибка при обновлении статуса документа: {update_error}")
        
        raise Exception(error_msg)
    
    finally:
        db_session.close()
