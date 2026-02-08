"""
Скрипт для ручного запуска индексации документов со статусом UPLOADING
"""
import sys
from pathlib import Path

# Добавляем путь к backend
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Импортируем settings ПЕРЕД импортом сервисов
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.database.database import SessionLocal, init_db
from app.services.document_service import DocumentService
from app.services.pageindex_service import PageIndexService
from app.models.document import Document, DocumentStatus
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_indexing():
    """Исправляет документы со статусом UPLOADING"""
    init_db()
    db = SessionLocal()
    document_service = DocumentService(db)
    pageindex_service = PageIndexService()
    
    try:
        # Получаем все документы
        all_docs = document_service.get_all_documents()
        
        # Фильтруем документы со статусом UPLOADING
        uploading_docs = [doc for doc in all_docs if doc.status == DocumentStatus.UPLOADING]
        
        logger.info(f"Найдено документов со статусом UPLOADING: {len(uploading_docs)}")
        
        if not uploading_docs:
            logger.info("Нет документов для обработки")
            return
        
        for doc in uploading_docs:
            logger.info(f"\n{'='*60}")
            logger.info(f"Обработка документа {doc.id}: {doc.filename}")
            logger.info(f"Статус: {doc.status.value}")
            logger.info(f"Путь к файлу: {doc.file_path}")
            
            # Проверяем, что файл существует
            if not os.path.exists(doc.file_path):
                logger.error(f"❌ Файл не найден: {doc.file_path}")
                document_service.update_document_status(
                    doc.id,
                    DocumentStatus.ERROR,
                    error_message=f"Файл не найден: {doc.file_path}"
                )
                continue
            
            file_size_mb = os.path.getsize(doc.file_path) / 1024 / 1024
            logger.info(f"Размер файла: {file_size_mb:.2f} MB")
            
            try:
                # Обновляем статус на INDEXING
                logger.info("Обновление статуса на INDEXING...")
                document_service.update_document_status(
                    doc.id,
                    DocumentStatus.INDEXING
                )
                
                # Запускаем индексацию
                logger.info("Начало индексации...")
                logger.info("ВНИМАНИЕ: Это может занять 10-30 минут для больших файлов!")
                
                import time
                start_time = time.time()
                
                result = pageindex_service.index_document(
                    pdf_path=doc.file_path,
                    document_id=doc.id
                )
                
                elapsed_time = time.time() - start_time
                logger.info(f"Индексация завершена за {elapsed_time:.2f} секунд ({elapsed_time/60:.2f} минут)")
                
                # Обновляем статус на READY
                logger.info("Обновление статуса на READY...")
                document_service.update_document_status(
                    doc.id,
                    DocumentStatus.READY,
                    index_path=result["index_path"]
                )
                
                logger.info(f"✅ Документ {doc.id} успешно проиндексирован!")
                logger.info(f"Индекс сохранен: {result['index_path']}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка при индексации документа {doc.id}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                document_service.update_document_status(
                    doc.id,
                    DocumentStatus.ERROR,
                    error_message=f"PageIndex indexing failed: {str(e)}"
                )
        
        logger.info(f"\n{'='*60}")
        logger.info("Обработка завершена")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    fix_indexing()
