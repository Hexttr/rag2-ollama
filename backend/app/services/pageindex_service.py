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

# Add parent directory to path for pageindex_ollama
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from pageindex_ollama import patch_pageindex_for_ollama, check_ollama_connection
from pageindex import page_index_main, config

logger = logging.getLogger(__name__)

class PageIndexService:
    """Service for document indexing with PageIndex and Ollama"""
    
    def __init__(self):
        # Patch PageIndex for Ollama
        if not check_ollama_connection():
            logger.warning("Ollama connection check failed, but continuing...")
        
        patch_pageindex_for_ollama()
        logger.info("PageIndex patched for Ollama")
    
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
            output_dir = output_dir or settings.INDEX_DIR
            os.makedirs(output_dir, exist_ok=True)
            
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
            
            logger.info(f"Starting indexing for: {pdf_path}")
            
            # Index document
            result = page_index_main(pdf_path, opt)
            
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
        # This will be implemented with Ollama service
        # For now, return structure
        index_data = self.load_index(index_path)
        return {
            "query": query,
            "index": index_data,
            "max_nodes": max_nodes
        }

