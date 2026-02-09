"""
PageIndex service for document indexing and search
"""
import os
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Добавляем путь к корню проекта в sys.path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Патчим PageIndex для Ollama ПЕРЕД импортом
try:
    from pageindex_ollama import patch_pageindex_for_ollama, check_ollama_connection
    
    # Проверяем и патчим
    if not patch_pageindex_for_ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL
    ):
        logger.error("Не удалось настроить PageIndex для Ollama")
except ImportError as e:
    logger.error(f"Не удалось импортировать pageindex_ollama: {e}")
    raise

# Теперь импортируем PageIndex (уже с патчем)
try:
    # Пытаемся импортировать из локального PageIndex
    from PageIndex.pageindex import page_index_main, config
    # КРИТИЧНО: Патчим также page_index модуль, так как он использует "from .utils import *"
    try:
        import PageIndex.pageindex.page_index as page_index_module
        from pageindex_ollama import get_ollama_settings
        ollama_settings = get_ollama_settings()
        if ollama_settings.get('patched'):
            # Применяем патчинг к page_index модулю
            import openai
            ollama_client = openai.OpenAI(
                api_key="ollama",
                base_url=ollama_settings['base_url']
            )
            ollama_async_client = openai.AsyncOpenAI(
                api_key="ollama",
                base_url=ollama_settings['base_url']
            )
            
            # Патчим функции в page_index
            def patched_ChatGPT_API(model=None, prompt=None, api_key=None, chat_history=None):
                max_retries = 10
                model = model or ollama_settings['model']
                for i in range(max_retries):
                    try:
                        if chat_history:
                            messages = chat_history.copy()
                            messages.append({"role": "user", "content": prompt})
                        else:
                            messages = [{"role": "user", "content": prompt}]
                        response = ollama_client.chat.completions.create(
                            model=model, messages=messages, temperature=0, timeout=300
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        if i < max_retries - 1:
                            import time
                            time.sleep(1)
                        else:
                            return "Error"
            
            async def patched_ChatGPT_API_async(model=None, prompt=None, api_key=None):
                max_retries = 10
                model = model or ollama_settings['model']
                messages = [{"role": "user", "content": prompt}]
                for i in range(max_retries):
                    try:
                        response = await ollama_async_client.chat.completions.create(
                            model=model, messages=messages, temperature=0, timeout=300
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        if i < max_retries - 1:
                            import asyncio
                            await asyncio.sleep(1)
                        else:
                            return "Error"
            
            def patched_ChatGPT_API_with_finish_reason(model=None, prompt=None, api_key=None, chat_history=None):
                max_retries = 10
                model = model or ollama_settings['model']
                for i in range(max_retries):
                    try:
                        if chat_history:
                            messages = chat_history.copy()
                            messages.append({"role": "user", "content": prompt})
                        else:
                            messages = [{"role": "user", "content": prompt}]
                        response = ollama_client.chat.completions.create(
                            model=model, messages=messages, temperature=0
                        )
                        finish_reason = response.choices[0].finish_reason
                        if finish_reason == "length":
                            return response.choices[0].message.content, "max_output_reached"
                        elif finish_reason == "error":
                            # Если finish_reason == "error", пробуем повторить запрос
                            logger.warning(f"Ollama вернул finish_reason='error', повторяю запрос ({i+1}/{max_retries})")
                            if i < max_retries - 1:
                                import time
                                time.sleep(1)
                                continue
                            else:
                                logger.error("Max retries reached, finish_reason='error'")
                                return "Error", "error"
                        else:
                            return response.choices[0].message.content, "finished"
                    except Exception as e:
                        if i < max_retries - 1:
                            import time
                            time.sleep(1)
                        else:
                            return "Error", "error"
            
            # Применяем патчинг
            page_index_module.ChatGPT_API = patched_ChatGPT_API
            page_index_module.ChatGPT_API_async = patched_ChatGPT_API_async
            page_index_module.ChatGPT_API_with_finish_reason = patched_ChatGPT_API_with_finish_reason
            logger.info("Патчинг применен к page_index модулю")
    except Exception as e:
        logger.warning(f"Не удалось патчить page_index модуль: {e}")
        
except ImportError:
    # Если не получилось, пробуем напрямую
    try:
        from pageindex import page_index_main, config
    except ImportError as e:
        logger.error(f"Не удалось импортировать PageIndex: {e}")
        raise

class PageIndexService:
    """Service for PageIndex document indexing and search"""
    
    def __init__(self):
        self.index_dir = Path(settings.INDEX_DIR)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Проверяем подключение к Ollama
        if not check_ollama_connection(settings.OLLAMA_BASE_URL):
            logger.warning("⚠️  Ollama недоступен! Убедитесь, что Ollama запущен.")
    
    def index_document(
        self,
        pdf_path: str,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Индексирует PDF документ используя PageIndex
        
        Args:
            pdf_path: Путь к PDF файлу
            document_id: ID документа (опционально, для имени файла индекса)
        
        Returns:
            Словарь с результатами индексации
        """
        try:
            import os
            file_size_mb = os.path.getsize(pdf_path) / 1024 / 1024
            logger.info(f"Начало индексации документа: {pdf_path}")
            logger.info(f"Размер файла: {file_size_mb:.2f} MB")
            logger.info(f"Используемая модель Ollama: {settings.OLLAMA_MODEL}")
            
            # Настройка опций PageIndex
            opt = config(
                model=settings.OLLAMA_MODEL,
                toc_check_page_num=20,
                max_page_num_each_node=settings.PAGEINDEX_MAX_PAGES_PER_NODE,
                max_token_num_each_node=settings.PAGEINDEX_MAX_TOKENS_PER_NODE,
                if_add_node_id='yes',
                if_add_node_summary='yes',
                if_add_doc_description='no',
                if_add_node_text='no'
            )
            
            logger.info("Настройки PageIndex применены, начинаю индексацию...")
            logger.info("ВНИМАНИЕ: Индексация больших файлов может занять 10-30 минут или больше!")
            
            # Индексируем документ
            import time
            start_time = time.time()
            result = page_index_main(pdf_path, opt)
            elapsed_time = time.time() - start_time
            logger.info(f"Индексация завершена за {elapsed_time:.2f} секунд ({elapsed_time/60:.2f} минут)")
            
            # Сохраняем индекс
            if document_id:
                index_filename = f"document_{document_id}_index.json"
            else:
                pdf_name = Path(pdf_path).stem
                index_filename = f"{pdf_name}_index.json"
            
            index_path = self.index_dir / index_filename
            
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Индексация завершена. Индекс сохранен: {index_path}")
            
            return {
                "success": True,
                "index_path": str(index_path),
                "structure": result
            }
            
        except Exception as e:
            logger.error(f"Ошибка при индексации документа: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def load_index(self, index_path: str) -> Dict[str, Any]:
        """
        Загружает индекс из файла
        
        Args:
            index_path: Путь к файлу индекса
        
        Returns:
            Словарь с данными индекса
        """
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке индекса: {e}")
            raise
    
    async def search_tree(
        self,
        index_path: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Поиск в дереве документа (упрощенная версия)
        
        Args:
            index_path: Путь к файлу индекса
            query: Поисковый запрос
        
        Returns:
            Результаты поиска
        """
        try:
            index_data = self.load_index(index_path)
            
            # Упрощенный поиск - в будущем можно улучшить
            # с использованием tree search из PageIndex
            return {
                "query": query,
                "index": index_data,
                "results": []  # TODO: Реализовать tree search
            }
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            raise
