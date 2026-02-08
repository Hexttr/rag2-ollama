"""
Запуск PageIndex с поддержкой Ollama
Использование: python run_pageindex_ollama.py --pdf_path document.pdf
"""

import os
import sys
import argparse
import json

# Импортируем и патчим функции для Ollama
from pageindex_ollama import patch_pageindex_for_ollama, check_ollama_connection

# Проверяем подключение к Ollama
if not check_ollama_connection():
    print("⚠️  Внимание: Ollama недоступен!")
    print("   Убедитесь, что Ollama запущен: ollama serve")
    print("   Или используйте OpenAI API (см. оригинальный run_pageindex.py)")
    response = input("   Продолжить все равно? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

# Патчим PageIndex для работы с Ollama
if not patch_pageindex_for_ollama():
    print("❌ Не удалось настроить PageIndex для Ollama")
    sys.exit(1)

# Теперь импортируем функции PageIndex (уже с патчем)
from pageindex import page_index_main, config

if __name__ == "__main__":
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(description='Обработка PDF с PageIndex через Ollama')
    parser.add_argument('--pdf_path', type=str, required=True, help='Путь к PDF файлу')
    parser.add_argument('--md_path', type=str, help='Путь к Markdown файлу')
    
    # Параметры модели Ollama
    parser.add_argument('--model', type=str, default=os.getenv('OLLAMA_MODEL', 'llama3.2'),
                       help='Модель Ollama (по умолчанию: llama3.2)')
    
    # Параметры PageIndex
    parser.add_argument('--toc-check-pages', type=int, default=20,
                       help='Количество страниц для проверки оглавления')
    parser.add_argument('--max-pages-per-node', type=int, default=10,
                       help='Максимальное количество страниц на узел')
    parser.add_argument('--max-tokens-per-node', type=int, default=20000,
                       help='Максимальное количество токенов на узел')
    parser.add_argument('--if-add-node-id', type=str, default='yes',
                       help='Добавлять ID узла (yes/no)')
    parser.add_argument('--if-add-node-summary', type=str, default='yes',
                       help='Добавлять summary узла (yes/no)')
    parser.add_argument('--if-add-doc-description', type=str, default='no',
                       help='Добавлять описание документа (yes/no)')
    parser.add_argument('--if-add-node-text', type=str, default='no',
                       help='Добавлять текст узла (yes/no)')
    
    args = parser.parse_args()
    
    # Валидация входных данных
    if not args.pdf_path and not args.md_path:
        raise ValueError("Необходимо указать --pdf_path или --md_path")
    if args.pdf_path and args.md_path:
        raise ValueError("Укажите только один из --pdf_path или --md_path")
    
    if args.pdf_path:
        if not args.pdf_path.lower().endswith('.pdf'):
            raise ValueError("PDF файл должен иметь расширение .pdf")
        if not os.path.isfile(args.pdf_path):
            raise ValueError(f"PDF файл не найден: {args.pdf_path}")
        
        print(f"📄 Обработка PDF: {args.pdf_path}")
        print(f"🤖 Модель Ollama: {args.model}")
        print(f"⏳ Это может занять некоторое время...\n")
        
        # Настройка опций
        opt = config(
            model=args.model,  # Используем модель Ollama
            toc_check_page_num=args.toc_check_pages,
            max_page_num_each_node=args.max_pages_per_node,
            max_token_num_each_node=args.max_tokens_per_node,
            if_add_node_id=args.if_add_node_id,
            if_add_node_summary=args.if_add_node_summary,
            if_add_doc_description=args.if_add_doc_description,
            if_add_node_text=args.if_add_node_text
        )
        
        # Обработка PDF
        try:
            toc_with_page_number = page_index_main(args.pdf_path, opt)
            print('\n✅ Обработка завершена, сохранение в файл...')
            
            # Сохранение результатов
            pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
            output_dir = './results'
            output_file = f'{output_dir}/{pdf_name}_structure.json'
            os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(toc_with_page_number, f, indent=2, ensure_ascii=False)
            
            print(f'✅ Структура сохранена: {output_file}')
        except Exception as e:
            print(f"❌ Ошибка при обработке: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif args.md_path:
        print("⚠️  Поддержка Markdown через Ollama пока не реализована")
        print("   Используйте оригинальный run_pageindex.py с OpenAI API")
        sys.exit(1)

