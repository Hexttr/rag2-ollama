"""
Патчинг PageIndex для работы с Ollama вместо OpenAI
"""
import os
import sys
import openai
import asyncio
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# Настройки Ollama по умолчанию
DEFAULT_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Глобальные переменные для хранения настроек
_ollama_base_url = DEFAULT_OLLAMA_BASE_URL
_ollama_model = DEFAULT_OLLAMA_MODEL
_patched = False


def check_ollama_connection(base_url: Optional[str] = None) -> bool:
    """Проверка подключения к Ollama"""
    try:
        url = (base_url or _ollama_base_url).replace('/v1', '')
        response = httpx.get(f"{url}/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama connection check failed: {e}")
        return False


def patch_pageindex_for_ollama(
    base_url: Optional[str] = None,
    model: Optional[str] = None
) -> bool:
    """
    Патчит функции PageIndex для работы с Ollama
    
    Args:
        base_url: URL Ollama API (по умолчанию http://localhost:11434/v1)
        model: Модель Ollama (по умолчанию llama3.2)
    
    Returns:
        True если патчинг успешен
    """
    global _ollama_base_url, _ollama_model, _patched, _ollama_client, _ollama_async_client
    
    # Устанавливаем настройки
    new_base_url = base_url or DEFAULT_OLLAMA_BASE_URL
    new_model = model or DEFAULT_OLLAMA_MODEL
    
    # Если патчинг уже выполнен, но модель или URL изменились, сбрасываем патчинг
    if _patched:
        if _ollama_base_url != new_base_url or _ollama_model != new_model:
            logger.info(f"Настройки Ollama изменились (было: {_ollama_model}, стало: {new_model}), перепатчиваем...")
            _patched = False
            _ollama_client = None
            _ollama_async_client = None
        else:
            logger.info(f"PageIndex уже патчен для Ollama (model={_ollama_model})")
            return True
    
    # Устанавливаем настройки
    _ollama_base_url = new_base_url
    _ollama_model = new_model
    
    # Проверяем подключение
    if not check_ollama_connection(_ollama_base_url):
        logger.warning("⚠️  Ollama недоступен, но продолжаем патчинг...")
    
    try:
        import sys
        from pathlib import Path
        
        # Добавляем путь к PageIndex в sys.path если его там нет
        pageindex_path = Path(__file__).parent / "PageIndex"
        if str(pageindex_path.parent) not in sys.path:
            sys.path.insert(0, str(pageindex_path.parent))
        
        # Импортируем модуль utils
        # Пробуем разные варианты импорта
        utils = None
        utils_module_name = None
        
        # Пробуем импортировать из PageIndex.pageindex
        try:
            from PageIndex.pageindex import utils
            utils_module_name = 'PageIndex.pageindex.utils'
        except ImportError:
            # Пробуем прямой импорт
            try:
                from pageindex import utils
                utils_module_name = 'pageindex.utils'
            except ImportError:
                # Ищем в sys.modules
                for module_name in list(sys.modules.keys()):
                    if module_name.endswith('.utils') and 'pageindex' in module_name:
                        utils = sys.modules[module_name]
                        utils_module_name = module_name
                        break
        
        # Если не нашли, пробуем импортировать напрямую
        if utils is None:
            try:
                import importlib
                # Пробуем разные варианты имени модуля
                for module_name in ['PageIndex.pageindex.utils', 'pageindex.utils', 'PageIndex.pageindex.utils']:
                    try:
                        utils = importlib.import_module(module_name)
                        utils_module_name = module_name
                        break
                    except ImportError:
                        continue
            except Exception as e:
                logger.error(f"Ошибка при импорте utils: {e}")
        
        if utils is None:
            raise ImportError("Не удалось найти модуль utils из PageIndex")
        
        logger.info(f"Найден модуль utils: {utils_module_name}")
        
        # Создаем клиент OpenAI-совместимый для Ollama
        # ВАЖНО: api_key должен быть строкой, не None
        ollama_client = openai.OpenAI(
            api_key="ollama",  # Не используется, но требуется для совместимости
            base_url=_ollama_base_url
        )
        
        ollama_async_client = openai.AsyncOpenAI(
            api_key="ollama",
            base_url=_ollama_base_url
        )
        
        # Сохраняем клиенты в глобальной области для использования в патченных функциях
        global _ollama_client, _ollama_async_client
        _ollama_client = ollama_client
        _ollama_async_client = ollama_async_client
        
        # Патчим ChatGPT_API
        def patched_ChatGPT_API(model=None, prompt=None, api_key=None, chat_history=None):
            """Патченая версия ChatGPT_API для Ollama"""
            max_retries = 10
            # Используем переданную модель или глобальную
            final_model = model or _ollama_model
            if not model:
                logger.debug(f"Используется модель из настроек патчинга: {final_model}")
            model = final_model
            
            # Используем глобальный клиент Ollama
            client = _ollama_client
            
            for i in range(max_retries):
                try:
                    if chat_history:
                        messages = chat_history.copy()
                        messages.append({"role": "user", "content": prompt})
                    else:
                        messages = [{"role": "user", "content": prompt}]
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0,
                        timeout=900  # 15 минут timeout для больших документов
                    )
                    
                    return response.choices[0].message.content
                except Exception as e:
                    logger.warning(f'************* Retrying ({i+1}/{max_retries}) *************')
                    logger.error(f"Error: {e}")
                    if i < max_retries - 1:
                        import time
                        time.sleep(1)
                    else:
                        logger.error('Max retries reached for prompt: ' + str(prompt)[:100])
                        return "Error"
        
        # Патчим ChatGPT_API_with_finish_reason
        def patched_ChatGPT_API_with_finish_reason(model=None, prompt=None, api_key=None, chat_history=None):
            """Патченая версия ChatGPT_API_with_finish_reason для Ollama"""
            max_retries = 10
            model = model or _ollama_model
            
            # Используем глобальный клиент Ollama
            client = _ollama_client
            
            for i in range(max_retries):
                try:
                    if chat_history:
                        messages = chat_history.copy()
                        messages.append({"role": "user", "content": prompt})
                    else:
                        messages = [{"role": "user", "content": prompt}]
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0,
                        timeout=900  # 15 минут timeout для больших документов
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
                    logger.warning(f'************* Retrying ({i+1}/{max_retries}) *************')
                    logger.error(f"Error: {e}")
                    if i < max_retries - 1:
                        import time
                        time.sleep(1)
                    else:
                        logger.error('Max retries reached for prompt: ' + str(prompt)[:100])
                        return "Error", "error"
        
        # Патчим ChatGPT_API_async
        async def patched_ChatGPT_API_async(model=None, prompt=None, api_key=None):
            """Патченая версия ChatGPT_API_async для Ollama"""
            max_retries = 10
            model = model or _ollama_model
            messages = [{"role": "user", "content": prompt}]
            
            # Используем глобальный асинхронный клиент Ollama
            client = _ollama_async_client
            
            for i in range(max_retries):
                try:
                    response = await client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0,
                        timeout=900  # 15 минут timeout для больших документов
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.warning(f'************* Retrying ({i+1}/{max_retries}) *************')
                    logger.error(f"Error: {e}")
                    if i < max_retries - 1:
                        await asyncio.sleep(1)
                    else:
                        logger.error('Max retries reached for prompt: ' + str(prompt)[:100])
                        return "Error"
        
        # Патчим count_tokens для работы с моделями Ollama
        original_count_tokens = utils.count_tokens
        
        def patched_count_tokens(text, model=None):
            """Патченая версия count_tokens для Ollama"""
            if not text:
                return 0
            try:
                # Пробуем использовать оригинальную функцию
                return original_count_tokens(text, model)
            except Exception:
                # Если не получилось (например, модель Ollama не известна tiktoken),
                # используем универсальный энкодер cl100k_base (используется в GPT-4)
                import tiktoken
                try:
                    enc = tiktoken.get_encoding("cl100k_base")
                    return len(enc.encode(text))
                except Exception:
                    # Если и это не работает, используем простое приближение
                    # ~4 символа = 1 токен
                    return len(text) // 4
        
        # Заменяем функции в модуле
        utils.ChatGPT_API = patched_ChatGPT_API
        utils.ChatGPT_API_with_finish_reason = patched_ChatGPT_API_with_finish_reason
        utils.ChatGPT_API_async = patched_ChatGPT_API_async
        utils.count_tokens = patched_count_tokens
        
        # Проверяем, что патчинг применился
        if hasattr(utils, 'ChatGPT_API') and utils.ChatGPT_API == patched_ChatGPT_API:
            logger.info("Патчинг ChatGPT_API применен успешно")
        else:
            logger.warning("Патчинг ChatGPT_API не применен!")
        
        # Также патчим в sys.modules на случай, если модуль уже закэширован
        if utils_module_name and utils_module_name in sys.modules:
            sys.modules[utils_module_name].ChatGPT_API = patched_ChatGPT_API
            sys.modules[utils_module_name].ChatGPT_API_with_finish_reason = patched_ChatGPT_API_with_finish_reason
            sys.modules[utils_module_name].ChatGPT_API_async = patched_ChatGPT_API_async
            sys.modules[utils_module_name].count_tokens = patched_count_tokens
            logger.info(f"Патчинг применен к sys.modules['{utils_module_name}']")
        
        # КРИТИЧНО: Патчим также в page_index, так как он использует "from .utils import *"
        # Это означает, что функции копируются в пространство имен page_index
        try:
            page_index_module_name = None
            page_index_module = None
            
            # Пробуем найти модуль page_index в sys.modules
            for module_name in list(sys.modules.keys()):
                if 'page_index' in module_name and 'pageindex' in module_name:
                    if not module_name.endswith('.page_index_md'):
                        page_index_module = sys.modules[module_name]
                        page_index_module_name = module_name
                        break
            
            # Если не нашли, пробуем импортировать
            if page_index_module is None:
                try:
                    from PageIndex.pageindex.page_index import ChatGPT_API as _test
                    # Если импорт прошел, значит модуль загружен
                    import PageIndex.pageindex.page_index as page_index_module
                    page_index_module_name = 'PageIndex.pageindex.page_index'
                except ImportError:
                    try:
                        import pageindex.page_index as page_index_module
                        page_index_module_name = 'pageindex.page_index'
                    except ImportError:
                        pass
            
            # Патчим функции в page_index
            if page_index_module is not None:
                if hasattr(page_index_module, 'ChatGPT_API'):
                    page_index_module.ChatGPT_API = patched_ChatGPT_API
                    logger.info(f"Патчинг ChatGPT_API применен к {page_index_module_name}")
                if hasattr(page_index_module, 'ChatGPT_API_with_finish_reason'):
                    page_index_module.ChatGPT_API_with_finish_reason = patched_ChatGPT_API_with_finish_reason
                    logger.info(f"Патчинг ChatGPT_API_with_finish_reason применен к {page_index_module_name}")
                if hasattr(page_index_module, 'ChatGPT_API_async'):
                    page_index_module.ChatGPT_API_async = patched_ChatGPT_API_async
                    logger.info(f"Патчинг ChatGPT_API_async применен к {page_index_module_name}")
                if hasattr(page_index_module, 'count_tokens'):
                    page_index_module.count_tokens = patched_count_tokens
                    logger.info(f"Патчинг count_tokens применен к {page_index_module_name}")
        except Exception as e:
            logger.warning(f"Не удалось патчить page_index модуль: {e}")
        
        _patched = True
        logger.info(f"✅ PageIndex успешно патчен для Ollama (base_url={_ollama_base_url}, model={_ollama_model})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при патчинге PageIndex: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def get_ollama_settings():
    """Получить текущие настройки Ollama"""
    return {
        "base_url": _ollama_base_url,
        "model": _ollama_model,
        "patched": _patched
    }
