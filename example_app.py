"""
Пример простого приложения на основе PageIndex
Демонстрирует создание системы вопрос-ответ по документам
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from pageindex import page_index_main, config
from pageindex.utils import ChatGPT_API_async, extract_json


class DocumentQASystem:
    """
    Система вопрос-ответ на основе PageIndex
    """
    
    def __init__(self, model: str = "gpt-4o-2024-11-20"):
        self.model = model
        self.tree_structure = None
        self.document_path = None
        
    def index_document(self, pdf_path: str, **kwargs):
        """
        Индексирует документ и создает дерево структуры
        
        Args:
            pdf_path: Путь к PDF файлу
            **kwargs: Дополнительные параметры для PageIndex
        """
        self.document_path = pdf_path
        
        # Настройка параметров
        opt = config(
            model=self.model,
            toc_check_page_num=kwargs.get('toc_check_pages', 20),
            max_page_num_each_node=kwargs.get('max_pages_per_node', 10),
            max_token_num_each_node=kwargs.get('max_tokens_per_node', 20000),
            if_add_node_id=kwargs.get('if_add_node_id', 'yes'),
            if_add_node_summary=kwargs.get('if_add_node_summary', 'yes'),
            if_add_doc_description=kwargs.get('if_add_doc_description', 'yes'),
            if_add_node_text=kwargs.get('if_add_node_text', 'no')
        )
        
        # Генерация дерева структуры
        print(f"Индексирование документа: {pdf_path}")
        self.tree_structure = page_index_main(pdf_path, opt)
        print("Индексирование завершено!")
        
        return self.tree_structure
    
    def save_index(self, output_path: str):
        """Сохраняет индекс в файл"""
        if self.tree_structure:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.tree_structure, f, indent=2, ensure_ascii=False)
            print(f"Индекс сохранен: {output_path}")
    
    def load_index(self, index_path: str):
        """Загружает индекс из файла"""
        with open(index_path, 'r', encoding='utf-8') as f:
            self.tree_structure = json.load(f)
        print(f"Индекс загружен: {index_path}")
    
    async def tree_search(self, query: str, max_nodes: int = 5) -> List[Dict]:
        """
        Выполняет reasoning-based поиск по дереву
        
        Args:
            query: Вопрос пользователя
            max_nodes: Максимальное количество узлов для возврата
            
        Returns:
            Список релевантных узлов дерева
        """
        if not self.tree_structure:
            raise ValueError("Документ не проиндексирован. Сначала вызовите index_document()")
        
        # Создаем упрощенное представление дерева для LLM
        tree_summary = self._create_tree_summary(self.tree_structure)
        
        # Промпт для reasoning-based поиска
        prompt = f"""
Вы - эксперт по анализу документов. Ваша задача - найти наиболее релевантные разделы документа для ответа на вопрос пользователя.

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

Выберите до {max_nodes} наиболее релевантных узлов.
"""
        
        response = await ChatGPT_API_async(model=self.model, prompt=prompt)
        result = extract_json(response)
        
        # Извлекаем node_id из результата
        relevant_node_ids = []
        if 'relevant_nodes' in result:
            for node in result['relevant_nodes'][:max_nodes]:
                if 'node_id' in node:
                    relevant_node_ids.append(node['node_id'])
        
        # Находим полную информацию об узлах
        relevant_nodes = self._find_nodes_by_ids(relevant_node_ids)
        
        return {
            'reasoning': result.get('reasoning', ''),
            'nodes': relevant_nodes,
            'raw_response': result
        }
    
    def _create_tree_summary(self, tree: List[Dict], max_depth: int = 3) -> List[Dict]:
        """Создает упрощенное представление дерева для LLM"""
        summary = []
        
        def traverse(node, depth=0):
            if depth > max_depth:
                return
            
            node_info = {
                'node_id': node.get('node_id', ''),
                'title': node.get('title', ''),
                'summary': node.get('summary', '')[:200] if node.get('summary') else '',
                'start_index': node.get('start_index', 0),
                'end_index': node.get('end_index', 0)
            }
            
            if 'nodes' in node and node['nodes']:
                node_info['children'] = []
                for child in node['nodes']:
                    traverse(child, depth + 1)
                    node_info['children'].append({
                        'node_id': child.get('node_id', ''),
                        'title': child.get('title', ''),
                        'summary': child.get('summary', '')[:200] if child.get('summary') else ''
                    })
            
            summary.append(node_info)
        
        for root_node in tree:
            traverse(root_node)
        
        return summary
    
    def _find_nodes_by_ids(self, node_ids: List[str]) -> List[Dict]:
        """Находит узлы по их ID в дереве"""
        found_nodes = []
        
        def search(node):
            if node.get('node_id') in node_ids:
                found_nodes.append(node)
            if 'nodes' in node:
                for child in node['nodes']:
                    search(child)
        
        for root_node in self.tree_structure:
            search(root_node)
        
        return found_nodes
    
    async def answer_question(self, query: str) -> Dict:
        """
        Полный цикл: поиск релевантных разделов и генерация ответа
        
        Args:
            query: Вопрос пользователя
            
        Returns:
            Словарь с ответом и метаданными
        """
        # 1. Поиск релевантных разделов
        search_result = await self.tree_search(query)
        
        # 2. Формирование контекста из найденных разделов
        context = self._build_context(search_result['nodes'])
        
        # 3. Генерация ответа на основе контекста
        answer = await self._generate_answer(query, context, search_result['reasoning'])
        
        return {
            'question': query,
            'answer': answer,
            'reasoning': search_result['reasoning'],
            'sources': [
                {
                    'title': node.get('title', ''),
                    'node_id': node.get('node_id', ''),
                    'pages': f"{node.get('start_index', 0)}-{node.get('end_index', 0)}"
                }
                for node in search_result['nodes']
            ]
        }
    
    def _build_context(self, nodes: List[Dict]) -> str:
        """Строит контекст из найденных узлов"""
        context_parts = []
        for node in nodes:
            context_parts.append(f"Раздел: {node.get('title', '')}")
            if node.get('summary'):
                context_parts.append(f"Краткое содержание: {node['summary']}")
            if node.get('text'):
                context_parts.append(f"Текст: {node['text'][:1000]}...")
        return "\n\n".join(context_parts)
    
    async def _generate_answer(self, query: str, context: str, reasoning: str) -> str:
        """Генерирует ответ на основе контекста"""
        prompt = f"""
На основе следующего контекста из документа ответьте на вопрос пользователя.

Контекст:
{context}

Рассуждение о релевантности разделов:
{reasoning}

Вопрос: {query}

Дайте точный и полный ответ, используя информацию из предоставленного контекста.
Если информации недостаточно, укажите это.
"""
        
        response = await ChatGPT_API_async(model=self.model, prompt=prompt)
        return response


# Пример использования
async def main():
    """Пример использования системы"""
    
    # Инициализация системы
    qa_system = DocumentQASystem(model="gpt-4o-2024-11-20")
    
    # Индексирование документа (если еще не сделано)
    pdf_path = "path/to/your/document.pdf"
    if not os.path.exists("document_structure.json"):
        qa_system.index_document(pdf_path)
        qa_system.save_index("document_structure.json")
    else:
        qa_system.load_index("document_structure.json")
    
    # Примеры вопросов
    questions = [
        "Каковы основные риски компании?",
        "Какие финансовые показатели были достигнуты?",
        "Каковы планы компании на следующий год?"
    ]
    
    # Ответы на вопросы
    for question in questions:
        print(f"\n{'='*60}")
        print(f"Вопрос: {question}")
        print(f"{'='*60}")
        
        result = await qa_system.answer_question(question)
        
        print(f"\nОтвет:\n{result['answer']}")
        print(f"\nИсточники:")
        for source in result['sources']:
            print(f"  - {source['title']} (страницы {source['pages']})")


if __name__ == "__main__":
    # Запуск примера
    print("Пример системы вопрос-ответ на основе PageIndex")
    print("Убедитесь, что у вас настроен .env файл с CHATGPT_API_KEY")
    print("\nДля запуска раскомментируйте следующую строку:")
    # asyncio.run(main())





