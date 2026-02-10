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
                # ВАЖНО: Всегда используем модель из настроек Ollama
                final_model = ollama_settings['model']
                if model and model != final_model:
                    logger.warning(f"Игнорируем переданную модель '{model}', используем '{final_model}' из настроек Ollama")
                model = final_model
                for i in range(max_retries):
                    try:
                        if chat_history:
                            messages = chat_history.copy()
                            messages.append({"role": "user", "content": prompt})
                        else:
                            messages = [{"role": "user", "content": prompt}]
                        response = ollama_client.chat.completions.create(
                            model=model, messages=messages, temperature=0, timeout=900  # 15 минут для больших документов
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        if i < max_retries - 1:
                            import time
                            time.sleep(1)
                        else:
                            return "Error"
            
            async def patched_ChatGPT_API_async(model=None, prompt=None, api_key=None, chat_history=None):
                max_retries = 10
                # ВАЖНО: Всегда используем модель из настроек Ollama
                final_model = ollama_settings['model']
                if model and model != final_model:
                    logger.warning(f"Игнорируем переданную модель '{model}', используем '{final_model}' из настроек Ollama")
                model = final_model
                
                # Подготовка сообщений
                if chat_history:
                    messages = chat_history.copy()
                    messages.append({"role": "user", "content": prompt})
                else:
                    messages = [{"role": "user", "content": prompt}]
                
                for i in range(max_retries):
                    try:
                        response = await ollama_async_client.chat.completions.create(
                            model=model, messages=messages, temperature=0, timeout=900  # 15 минут для больших документов
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        logger.warning(f"Ошибка в async запросе ({i+1}/{max_retries}): {e}")
                        if i < max_retries - 1:
                            import asyncio
                            await asyncio.sleep(1)
                        else:
                            logger.error(f"Max retries reached for async prompt: {str(prompt)[:100]}")
                            return "Error"
            
            def patched_ChatGPT_API_with_finish_reason(model=None, prompt=None, api_key=None, chat_history=None):
                max_retries = 10
                # ВАЖНО: Всегда используем модель из настроек Ollama
                final_model = ollama_settings['model']
                if model and model != final_model:
                    logger.warning(f"Игнорируем переданную модель '{model}', используем '{final_model}' из настроек Ollama")
                model = final_model
                for i in range(max_retries):
                    try:
                        if chat_history:
                            messages = chat_history.copy()
                            messages.append({"role": "user", "content": prompt})
                        else:
                            messages = [{"role": "user", "content": prompt}]
                        response = ollama_client.chat.completions.create(
                            model=model, messages=messages, temperature=0, timeout=900  # 15 минут для больших документов
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
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")
            
            file_size_mb = os.path.getsize(pdf_path) / 1024 / 1024
            logger.info(f"Начало индексации документа: {pdf_path}")
            logger.info(f"Размер файла: {file_size_mb:.2f} MB")
            logger.info(f"Используемая модель Ollama: {settings.OLLAMA_MODEL}")
            
            # Проверяем подключение к Ollama перед началом
            from pageindex_ollama import check_ollama_connection
            if not check_ollama_connection(settings.OLLAMA_BASE_URL):
                raise ConnectionError("Ollama недоступен! Убедитесь, что Ollama запущен и доступен по адресу " + settings.OLLAMA_BASE_URL)
            
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
            logger.info("Процесс индексации включает:")
            logger.info("  1. Извлечение оглавления")
            logger.info("  2. Проверку страниц")
            logger.info("  3. Генерацию summary для узлов")
            logger.info("  4. Построение дерева структуры")
            
            # Индексируем документ
            import time
            start_time = time.time()
            
            try:
                result = page_index_main(pdf_path, opt)
            except Exception as indexing_error:
                logger.error(f"Ошибка при вызове page_index_main: {indexing_error}")
                import traceback
                logger.error(traceback.format_exc())
                raise
            
            elapsed_time = time.time() - start_time
            logger.info(f"Индексация завершена за {elapsed_time:.2f} секунд ({elapsed_time/60:.2f} минут)")
            
            # Валидация результата
            if not result:
                raise ValueError("PageIndex вернул пустой результат")
            
            if 'structure' not in result:
                logger.warning("Результат индексации не содержит 'structure', проверяю формат...")
                # Возможно, результат уже является структурой
                if isinstance(result, list):
                    result = {'structure': result, 'doc_name': Path(pdf_path).stem}
                else:
                    raise ValueError("Неожиданный формат результата от PageIndex")
            
            # Сохраняем индекс
            if document_id:
                index_filename = f"document_{document_id}_index.json"
            else:
                pdf_name = Path(pdf_path).stem
                index_filename = f"{pdf_name}_index.json"
            
            index_path = self.index_dir / index_filename
            
            # Создаем директорию если не существует
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Индексация завершена. Индекс сохранен: {index_path}")
            
            # Логируем статистику
            structure = result.get('structure', [])
            if structure:
                node_count = self._count_nodes(structure)
                logger.info(f"Создано узлов в дереве: {node_count}")
            
            return {
                "success": True,
                "index_path": str(index_path),
                "structure": result
            }
            
        except FileNotFoundError:
            raise
        except ConnectionError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при индексации документа: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _count_nodes(self, structure: list) -> int:
        """Рекурсивно подсчитывает количество узлов в дереве"""
        count = 0
        for node in structure:
            if isinstance(node, dict):
                count += 1
                if 'nodes' in node:
                    count += self._count_nodes(node['nodes'])
        return count
    
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
        Reasoning-based поиск в дереве документа используя LLM
        
        Args:
            index_path: Путь к файлу индекса
            query: Поисковый запрос
        
        Returns:
            Результаты поиска с найденными узлами и контекстом
        """
        # Валидация входных данных
        if not query or not query.strip():
            raise ValueError("Поисковый запрос не может быть пустым")
        
        if not index_path or not Path(index_path).exists():
            raise FileNotFoundError(f"Индекс не найден: {index_path}")
        
        try:
            index_data = self.load_index(index_path)
            
            # Получаем структуру дерева
            structure = index_data.get('structure', [])
            if not structure:
                logger.warning("Структура документа пуста")
                return {
                    "query": query,
                    "node_list": [],
                    "context": "",
                    "sources": []
                }
            
            # Создаем упрощенную версию дерева без текста для поиска
            tree_without_text = self._remove_fields_from_tree(structure.copy(), fields=['text'])
            
            # Формируем промпт для tree search
            import json
            search_prompt = f"""
You are given a question and a tree structure of a document.
Each node contains a node id, node title, and a corresponding summary.
Your task is to find all nodes that are likely to contain the answer to the question.

Question: {query}

Document tree structure:
{json.dumps(tree_without_text, indent=2, ensure_ascii=False)}

Please reply in the following JSON format:
{{
    "thinking": "<Your thinking process on which nodes are relevant to the question>",
    "node_list": ["node_id_1", "node_id_2", ..., "node_id_n"]
}}
Directly return the final JSON structure. Do not output anything else.
"""
            
            # Проверяем размер дерева - если слишком большое, обрезаем для промпта
            tree_json = json.dumps(tree_without_text, indent=2, ensure_ascii=False)
            max_tree_size = 50000  # Ограничение размера дерева в промпте
            
            if len(tree_json) > max_tree_size:
                logger.warning(f"Дерево слишком большое ({len(tree_json)} символов), обрезаем для промпта")
                # Берем только верхние уровни дерева
                tree_without_text = self._truncate_tree_for_search(tree_without_text, max_depth=2)
                tree_json = json.dumps(tree_without_text, indent=2, ensure_ascii=False)
            
            # Выполняем tree search через Ollama
            from pageindex_ollama import get_ollama_settings, check_ollama_connection
            ollama_settings = get_ollama_settings()
            model = ollama_settings.get('model', settings.OLLAMA_MODEL)
            
            # Проверяем подключение к Ollama
            if not check_ollama_connection(settings.OLLAMA_BASE_URL):
                logger.warning("Ollama недоступен, используем keyword search")
                return self._simple_keyword_search(structure, query)
            
            # Используем патченную функцию ChatGPT_API
            try:
                from PageIndex.pageindex.utils import ChatGPT_API
                tree_search_result = ChatGPT_API(model=model, prompt=search_prompt)
                
                # Проверяем, что результат не пустой
                if not tree_search_result or tree_search_result == "Error":
                    logger.warning("LLM вернул ошибку, используем keyword search")
                    return self._simple_keyword_search(structure, query)
                    
            except Exception as e:
                logger.error(f"Ошибка при вызове LLM для tree search: {e}")
                # Fallback: используем простой поиск по ключевым словам
                return self._simple_keyword_search(structure, query)
            
            # Парсим результат
            try:
                from PageIndex.pageindex.utils import extract_json
                tree_search_json = extract_json(tree_search_result)
            except Exception as e:
                logger.error(f"Ошибка при парсинге результата tree search: {e}")
                return self._simple_keyword_search(structure, query)
            
            node_list = tree_search_json.get('node_list', [])
            thinking = tree_search_json.get('thinking', '')
            
            logger.info(f"Tree search found {len(node_list)} relevant nodes")
            logger.debug(f"Thinking: {thinking}")
            
            # Создаем маппинг узлов для быстрого доступа
            node_map = self._create_node_mapping(structure)
            
            # Извлекаем контекст из найденных узлов
            retrieved_nodes = []
            context_parts = []
            sources = []
            
            for node_id in node_list:
                if node_id in node_map:
                    node = node_map[node_id]
                    retrieved_nodes.append(node)
                    
                    # Добавляем контекст
                    if 'summary' in node and node['summary']:
                        context_parts.append(f"Section: {node.get('title', 'Unknown')}\n{node['summary']}")
                    
                    # Добавляем источник
                    sources.append({
                        "node_id": node_id,
                        "title": node.get('title', 'Unknown'),
                        "pages": f"{node.get('start_index', 0)}-{node.get('end_index', 0)}"
                    })
            
            context = "\n\n".join(context_parts)
            
            return {
                "query": query,
                "thinking": thinking,
                "node_list": node_list,
                "retrieved_nodes": retrieved_nodes,
                "context": context,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _remove_fields_from_tree(self, tree: Any, fields: list) -> Any:
        """Рекурсивно удаляет поля из дерева"""
        if isinstance(tree, dict):
            result = {}
            for key, value in tree.items():
                if key not in fields:
                    result[key] = self._remove_fields_from_tree(value, fields)
            return result
        elif isinstance(tree, list):
            return [self._remove_fields_from_tree(item, fields) for item in tree]
        else:
            return tree
    
    def _create_node_mapping(self, structure: list) -> Dict[str, Dict]:
        """Создает маппинг node_id -> node для быстрого доступа"""
        node_map = {}
        
        def traverse(nodes):
            for node in nodes:
                if isinstance(node, dict):
                    node_id = node.get('node_id')
                    if node_id:
                        node_map[node_id] = node
                    if 'nodes' in node:
                        traverse(node['nodes'])
        
        traverse(structure)
        return node_map
    
    def _truncate_tree_for_search(self, tree: Any, max_depth: int = 2, current_depth: int = 0) -> Any:
        """Рекурсивно обрезает дерево до определенной глубины для поиска"""
        if current_depth >= max_depth:
            # На максимальной глубине оставляем только заголовки
            if isinstance(tree, dict):
                return {
                    'node_id': tree.get('node_id'),
                    'title': tree.get('title'),
                    'summary': tree.get('summary', '')[:200] if tree.get('summary') else ''  # Обрезаем summary
                }
            return tree
        
        if isinstance(tree, dict):
            result = {}
            for key, value in tree.items():
                if key == 'nodes' and current_depth < max_depth:
                    # Рекурсивно обрабатываем дочерние узлы
                    result[key] = [self._truncate_tree_for_search(node, max_depth, current_depth + 1) 
                                  for node in (value if isinstance(value, list) else [])]
                elif key not in ['text']:  # Исключаем большие поля
                    result[key] = self._truncate_tree_for_search(value, max_depth, current_depth)
            return result
        elif isinstance(tree, list):
            return [self._truncate_tree_for_search(item, max_depth, current_depth) for item in tree]
        else:
            return tree
    
    def _simple_keyword_search(self, structure: list, query: str) -> Dict[str, Any]:
        """Простой поиск по ключевым словам как fallback"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        relevant_nodes = []
        
        def traverse(nodes):
            for node in nodes:
                if isinstance(node, dict):
                    title = node.get('title', '').lower()
                    summary = node.get('summary', '').lower()
                    
                    # Простой подсчет совпадений
                    title_matches = sum(1 for word in query_words if word in title)
                    summary_matches = sum(1 for word in query_words if word in summary)
                    
                    if title_matches > 0 or summary_matches > 0:
                        relevant_nodes.append({
                            'node_id': node.get('node_id'),
                            'title': node.get('title'),
                            'summary': node.get('summary'),
                            'start_index': node.get('start_index'),
                            'end_index': node.get('end_index'),
                            'relevance_score': title_matches * 2 + summary_matches
                        })
                    
                    if 'nodes' in node:
                        traverse(node['nodes'])
        
        traverse(structure)
        
        # Сортируем по релевантности
        relevant_nodes.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            "query": query,
            "node_list": [n['node_id'] for n in relevant_nodes[:5] if n.get('node_id')],
            "retrieved_nodes": relevant_nodes[:5],
            "context": "\n\n".join([f"Section: {n['title']}\n{n.get('summary', '')}" for n in relevant_nodes[:5]]),
            "sources": [{
                "node_id": n['node_id'],
                "title": n['title'],
                "pages": f"{n.get('start_index', 0)}-{n.get('end_index', 0)}"
            } for n in relevant_nodes[:5]]
        }
