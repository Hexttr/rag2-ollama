"""
PageIndex service for document indexing
"""
import os
import json
import sys
from pathlib import Path
from typing import Dict, Optional
from app.core.config import settings
import logging

# Add paths for PageIndex and pageindex_ollama
project_root = Path(__file__).parent.parent.parent.parent
pageindex_path = project_root / "PageIndex"
pageindex_ollama_path = project_root / "pageindex_ollama.py"

# Add paths in correct order
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(pageindex_path) not in sys.path:
    sys.path.insert(0, str(pageindex_path))

# Log paths for debugging
logger_temp = logging.getLogger(__name__)
try:
    logger_temp.info(f"Project root: {project_root}")
    logger_temp.info(f"PageIndex path: {pageindex_path}")
    logger_temp.info(f"PageIndex exists: {pageindex_path.exists()}")
    logger_temp.info(f"pageindex_ollama exists: {pageindex_ollama_path.exists()}")
except:
    pass  # Don't fail if logging fails

try:
    # First import pageindex_ollama (it's in project root)
    import pageindex_ollama
    patch_pageindex_for_ollama = pageindex_ollama.patch_pageindex_for_ollama
    check_ollama_connection = pageindex_ollama.check_ollama_connection
    
    # IMPORTANT: Patch PageIndex BEFORE importing it!
    # This ensures that when PageIndex imports utils, it gets the patched version
    patch_result = patch_pageindex_for_ollama()
    if not patch_result:
        logger_temp.warning("Failed to patch PageIndex for Ollama, but continuing...")
    else:
        logger_temp.info("PageIndex patched for Ollama (before import)")
    
    # Then import PageIndex modules (they will use patched functions)
    from pageindex.page_index import page_index_main
    from pageindex.utils import config
    
    # CRITICAL: Re-patch after import because page_index uses "from .utils import *"
    # which copies functions to its namespace, so we need to patch both
    patch_result2 = patch_pageindex_for_ollama()
    if patch_result2:
        logger_temp.info("PageIndex re-patched after import (for page_index module)")
    
    PAGEINDEX_AVAILABLE = True
    logger_temp.info("PageIndex modules imported successfully")
except ImportError as e:
    logging.error(f"Failed to import PageIndex: {e}")
    import traceback
    logging.error(traceback.format_exc())
    # Fallback - will be handled in __init__
    patch_pageindex_for_ollama = None
    check_ollama_connection = None
    page_index_main = None
    config = None
    PAGEINDEX_AVAILABLE = False

logger = logging.getLogger(__name__)

class PageIndexService:
    """Service for document indexing with PageIndex and Ollama"""
    
    def __init__(self):
        # Patch is already applied at module level, but verify it's still patched
        if not PAGEINDEX_AVAILABLE or patch_pageindex_for_ollama is None:
            error_msg = "PageIndex modules not available. Make sure PageIndex is in the project root."
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        try:
            if check_ollama_connection and not check_ollama_connection():
                logger.warning("Ollama connection check failed, but continuing...")
            
            # Re-apply patch to ensure it's still active (in case of module reload)
            patch_result = patch_pageindex_for_ollama()
            if patch_result:
                logger.info("PageIndex patched for Ollama (verified)")
            else:
                logger.warning("Failed to verify patch, but continuing...")
        except Exception as e:
            logger.error(f"Error patching PageIndex: {e}")
            raise
    
    async def index_document(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Index a PDF document using PageIndex
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save index (default: settings.INDEX_DIR)
        
        Returns:
            Dictionary with index structure
        """
        try:
            # Check if file exists
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            output_dir = output_dir or settings.INDEX_DIR
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Configuring PageIndex for: {pdf_path}")
            
            # Configure PageIndex options
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
            
            logger.info(f"Starting PageIndex indexing for: {pdf_path}")
            logger.info(f"Model: {settings.OLLAMA_MODEL}")
            logger.info(f"Max pages per node: {settings.PAGEINDEX_MAX_PAGES_PER_NODE}")
            
            # Index document (this is synchronous, but we're in async function)
            # Run in executor to avoid blocking
            # IMPORTANT: Re-apply patch in the executor thread to ensure it's active
            import asyncio
            loop = asyncio.get_event_loop()
            
            def _index_with_patch(pdf_path, opt):
                """Wrapper that ensures patch is applied in executor thread"""
                # Re-apply patch in this thread to ensure it's active
                # This is critical because executor runs in a separate thread
                try:
                    # Re-import and patch in this thread
                    import sys
                    from pathlib import Path
                    project_root = Path(__file__).parent.parent.parent.parent
                    if str(project_root) not in sys.path:
                        sys.path.insert(0, str(project_root))
                    if str(project_root / "PageIndex") not in sys.path:
                        sys.path.insert(0, str(project_root / "PageIndex"))
                    
                    # Import and patch
                    import pageindex_ollama
                    patch_result = pageindex_ollama.patch_pageindex_for_ollama()
                    if patch_result:
                        logger.info("Patch re-applied in executor thread")
                    else:
                        logger.warning("Failed to re-apply patch in executor thread")
                    
                    # Verify patch
                    from pageindex import utils
                    if utils.ChatGPT_API is not pageindex_ollama.ChatGPT_API_ollama:
                        logger.error("Patch verification failed in executor thread!")
                        logger.error(f"Expected: {pageindex_ollama.ChatGPT_API_ollama}")
                        logger.error(f"Got: {utils.ChatGPT_API}")
                    else:
                        logger.info("Patch verified successfully in executor thread")
                    
                    # Also patch page_index if it's imported
                    try:
                        from pageindex import page_index
                        page_index.ChatGPT_API = pageindex_ollama.ChatGPT_API_ollama
                        page_index.ChatGPT_API_async = pageindex_ollama.ChatGPT_API_async_ollama
                        page_index.ChatGPT_API_with_finish_reason = pageindex_ollama.ChatGPT_API_with_finish_reason_ollama
                        logger.info("page_index module patched in executor thread")
                    except ImportError:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error re-applying patch in executor: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                
                # Now run indexing
                return page_index_main(pdf_path, opt)
            
            result = await loop.run_in_executor(None, _index_with_patch, pdf_path, opt)
            
            logger.info(f"Indexing completed, saving index...")
            
            # Save index to file
            pdf_name = Path(pdf_path).stem
            index_path = os.path.join(output_dir, f"{pdf_name}_structure.json")
            
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Index saved to: {index_path}")
            
            return {
                "index_path": index_path,
                "structure": result
            }
            
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def load_index(self, index_path: str) -> Dict:
        """Load index from file"""
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise
    
    async def search_tree(
        self,
        index_path: str,
        query: str,
        max_nodes: int = 5
    ) -> Dict:
        """
        Search through document tree using reasoning
        
        Args:
            index_path: Path to index file
            query: Search query
            max_nodes: Maximum number of nodes to return
        
        Returns:
            Dictionary with relevant nodes and reasoning
        """
        from app.services.ollama_service import OllamaService
        
        index_data = self.load_index(index_path)
        ollama_service = OllamaService()
        
        # Create tree summary for LLM
        tree_summary = self._create_tree_summary(index_data.get("structure", []))
        
        # Reasoning-based search prompt
        prompt = f"""Вы - эксперт по анализу документов. Ваша задача - найти наиболее релевантные разделы документа для ответа на вопрос пользователя.

Структура документа:
{json.dumps(tree_summary, indent=2, ensure_ascii=False)}

Вопрос пользователя: {query}

Проанализируйте структуру документа и определите, какие разделы наиболее релевантны для ответа на вопрос.

Верните JSON в следующем формате:
{{
    "reasoning": "Ваше рассуждение о том, почему выбранные разделы релевантны",
    "relevant_nodes": [
        {{
            "node_id": "ID узла",
            "title": "Название раздела",
            "relevance_score": "высокая/средняя/низкая",
            "reason": "Почему этот раздел релевантен"
        }}
    ]
}}

Выберите до {max_nodes} наиболее релевантных узлов."""
        
        try:
            response = await ollama_service.generate_response(prompt)
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                result = {
                    "reasoning": response[:200],
                    "relevant_nodes": []
                }
            
            # Find actual nodes in structure
            relevant_nodes = []
            if "relevant_nodes" in result:
                node_ids = [node.get("node_id") for node in result["relevant_nodes"]]
                relevant_nodes = self._find_nodes_by_ids(
                    index_data.get("structure", []),
                    node_ids
                )
            
            return {
                "query": query,
                "reasoning": result.get("reasoning", ""),
                "nodes": relevant_nodes,
                "index": index_data
            }
        except Exception as e:
            logger.error(f"Tree search failed: {e}")
            # Fallback: return full structure
            return {
                "query": query,
                "reasoning": "Ошибка при поиске, возвращена полная структура",
                "nodes": [],
                "index": index_data
            }
    
    def _create_tree_summary(self, tree: list, max_depth: int = 3) -> list:
        """Create simplified tree representation for LLM"""
        summary = []
        
        def traverse(node, depth=0):
            if depth > max_depth:
                return
            
            if isinstance(node, dict):
                node_info = {
                    "node_id": node.get("node_id", ""),
                    "title": node.get("title", ""),
                    "summary": node.get("summary", "")[:200] if node.get("summary") else "",
                    "start_index": node.get("start_index", 0),
                    "end_index": node.get("end_index", 0)
                }
                
                if "nodes" in node and node["nodes"]:
                    node_info["children"] = []
                    for child in node["nodes"]:
                        child_info = traverse(child, depth + 1)
                        if child_info:
                            node_info["children"].append({
                                "node_id": child.get("node_id", ""),
                                "title": child.get("title", ""),
                                "summary": child.get("summary", "")[:200] if child.get("summary") else ""
                            })
                
                return node_info
            return None
        
        for root_node in tree:
            node_info = traverse(root_node)
            if node_info:
                summary.append(node_info)
        
        return summary
    
    def _find_nodes_by_ids(self, tree: list, node_ids: list) -> list:
        """Find nodes by their IDs in the tree"""
        found_nodes = []
        
        def search(node):
            if isinstance(node, dict):
                if node.get("node_id") in node_ids:
                    found_nodes.append(node)
                if "nodes" in node:
                    for child in node["nodes"]:
                        search(child)
        
        for root_node in tree:
            search(root_node)
        
        return found_nodes

