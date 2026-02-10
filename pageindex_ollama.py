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
_ollama_client = None
_ollama_async_client = None


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
        _ollama_client = ollama_client
        _ollama_async_client = ollama_async_client
        
        # Патчим ChatGPT_API
        def patched_ChatGPT_API(model=None, prompt=None, api_key=None, chat_history=None):
            """Патченая версия ChatGPT_API для Ollama"""
            max_retries = 10
            # КРИТИЧНО: Всегда используем модель из настроек Ollama, игнорируя переданную модель
            original_model = model
            final_model = _ollama_model
            
            # Проверяем, не является ли переданная модель OpenAI моделью
            if model and (model.startswith("gpt-") or model.startswith("claude-") or "openai" in model.lower()):
                logger.warning(f"🚫 Обнаружена OpenAI модель '{model}', принудительно заменяем на '{final_model}'")
                model = final_model
            elif model and model != _ollama_model:
                logger.warning(f"⚠️ Игнорируем переданную модель '{model}', используем '{final_model}' из настроек Ollama")
                model = final_model
            elif model is None:
                model = final_model
                logger.debug(f"Используется модель из настроек: '{model}'")
            
            # Дополнительная проверка перед запросом
            if model != _ollama_model:
                logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: модель '{model}' не совпадает с настройкой '{_ollama_model}'! Принудительно заменяем.")
                model = _ollama_model
            
            # Используем глобальный клиент Ollama
            client = _ollama_client
            
            for i in range(max_retries):
                try:
                    if chat_history:
                        messages = chat_history.copy()
                        messages.append({"role": "user", "content": prompt})
                    else:
                        messages = [{"role": "user", "content": prompt}]
                    
                    # КРИТИЧНО: Финальная проверка перед запросом
                    if model != _ollama_model:
                        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: модель '{model}' не совпадает с '{_ollama_model}'! Принудительно заменяем.")
                        model = _ollama_model
                    
                    # КРИТИЧНО: Логируем модель перед запросом для отладки
                    logger.info(f"🔍 Отправка запроса в Ollama с моделью: '{model}' (должна быть '{_ollama_model}')")
                    logger.debug(f"📝 Промпт (первые 100 символов): {str(prompt)[:100]}")
                    
                    # Дополнительная проверка: убеждаемся что модель точно правильная
                    assert model == _ollama_model, f"Модель должна быть '{_ollama_model}', но получили '{model}'"
                    
                    # КРИТИЧНО: Логируем детали запроса
                    logger.debug(f"📤 Запрос к Ollama: model='{model}', messages_count={len(messages)}")
                    
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=0,
                            timeout=900  # 15 минут timeout для больших документов
                        )
                        
                        # Проверяем, какая модель реально использовалась (если доступно)
                        if hasattr(response, 'model'):
                            logger.debug(f"📥 Ответ от Ollama: использована модель '{response.model}'")
                            
                    except Exception as api_error:
                        # Логируем детали ошибки
                        error_str = str(api_error)
                        logger.error(f"❌ Ошибка API Ollama: {error_str}")
                        if "46.9" in error_str or "memory" in error_str.lower():
                            logger.error(f"🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Ollama пытается загрузить большую модель!")
                            logger.error(f"🚨 Переданная модель: '{model}', ожидаемая: '{_ollama_model}'")
                            # Проверяем, может быть проблема в имени модели
                            if ":" in model:
                                logger.warning(f"⚠️ Имя модели содержит ':', возможно Ollama интерпретирует его неправильно")
                        raise
                    
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
            # КРИТИЧНО: Всегда используем модель из настроек Ollama, игнорируя переданную модель
            # так как переданная модель может быть "gpt-4o-2024-11-20" или другой OpenAI моделью
            original_model = model
            final_model = _ollama_model
            
            # Проверяем, не является ли переданная модель OpenAI моделью
            if model and (model.startswith("gpt-") or model.startswith("claude-") or "openai" in model.lower()):
                logger.warning(f"🚫 Обнаружена OpenAI модель '{model}', принудительно заменяем на '{final_model}'")
                model = final_model
            elif model and model != _ollama_model:
                logger.warning(f"⚠️ Игнорируем переданную модель '{model}', используем '{final_model}' из настроек Ollama")
                model = final_model
            elif model is None:
                model = final_model
                logger.debug(f"Используется модель из настроек: '{model}'")
            
            # Дополнительная проверка перед запросом
            if model != _ollama_model:
                logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: модель '{model}' не совпадает с настройкой '{_ollama_model}'! Принудительно заменяем.")
                model = _ollama_model
            
            # Используем глобальный клиент Ollama
            client = _ollama_client
            
            for i in range(max_retries):
                try:
                    if chat_history:
                        messages = chat_history.copy()
                        messages.append({"role": "user", "content": prompt})
                    else:
                        messages = [{"role": "user", "content": prompt}]
                    
                    # КРИТИЧНО: Финальная проверка перед запросом
                    if model != _ollama_model:
                        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: модель '{model}' не совпадает с '{_ollama_model}'! Принудительно заменяем.")
                        model = _ollama_model
                    
                    # КРИТИЧНО: Логируем модель перед запросом для отладки
                    logger.info(f"🔍 Отправка запроса в Ollama с моделью: '{model}' (должна быть '{_ollama_model}')")
                    logger.debug(f"📝 Промпт (первые 100 символов): {str(prompt)[:100]}")
                    
                    # Дополнительная проверка: убеждаемся что модель точно правильная
                    assert model == _ollama_model, f"Модель должна быть '{_ollama_model}', но получили '{model}'"
                    
                    # КРИТИЧНО: Логируем детали запроса
                    logger.debug(f"📤 Запрос к Ollama: model='{model}', messages_count={len(messages)}")
                    
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=0,
                            timeout=900  # 15 минут timeout для больших документов
                        )
                        
                        # Проверяем, какая модель реально использовалась (если доступно)
                        if hasattr(response, 'model'):
                            logger.debug(f"📥 Ответ от Ollama: использована модель '{response.model}'")
                        if hasattr(response, 'usage'):
                            logger.debug(f"📊 Использовано токенов: {response.usage}")
                            
                    except Exception as api_error:
                        # Логируем детали ошибки
                        error_str = str(api_error)
                        logger.error(f"❌ Ошибка API Ollama: {error_str}")
                        if "46.9" in error_str or "memory" in error_str.lower():
                            logger.error(f"🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Ollama пытается загрузить большую модель!")
                            logger.error(f"🚨 Переданная модель: '{model}', ожидаемая: '{_ollama_model}'")
                            # Проверяем, может быть проблема в имени модели
                            if ":" in model:
                                logger.warning(f"⚠️ Имя модели содержит ':', возможно Ollama интерпретирует его неправильно")
                        raise
                    
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
        async def patched_ChatGPT_API_async(model=None, prompt=None, api_key=None, chat_history=None):
            """Патченая версия ChatGPT_API_async для Ollama"""
            max_retries = 10
            # ВАЖНО: Всегда используем модель из настроек Ollama, игнорируя переданную модель
            final_model = _ollama_model
            if model and model != _ollama_model:
                logger.warning(f"Игнорируем переданную модель '{model}', используем '{final_model}' из настроек Ollama")
            model = final_model
            
            # Используем глобальный асинхронный клиент Ollama
            if _ollama_async_client is None:
                logger.error("Ollama async client не инициализирован! Патчинг не был выполнен.")
                return "Error"
            client = _ollama_async_client
            
            # Подготовка сообщений
            if chat_history:
                messages = chat_history.copy()
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]
            
            for i in range(max_retries):
                try:
                    # КРИТИЧНО: Логируем модель перед запросом для отладки
                    logger.info(f"🔍 Отправка async запроса в Ollama с моделью: '{model}' (должна быть '{_ollama_model}')")
                    
                    response = await client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0,
                        timeout=900  # 15 минут timeout для больших документов
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.warning(f'************* Retrying async ({i+1}/{max_retries}) *************')
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
        # Нужно патчить ВСЕ модули, которые импортировали функции через "from .utils import *"
        try:
            # Список модулей для патчинга
            modules_to_patch = []
            
            # Пробуем найти все модули pageindex в sys.modules
            for module_name in list(sys.modules.keys()):
                if 'pageindex' in module_name.lower() or 'page_index' in module_name.lower():
                    if not module_name.endswith('.page_index_md'):
                        module = sys.modules[module_name]
                        if hasattr(module, 'ChatGPT_API') or hasattr(module, 'ChatGPT_API_with_finish_reason'):
                            modules_to_patch.append((module_name, module))
            
            # Если не нашли, пробуем импортировать напрямую
            if not modules_to_patch:
                try:
                    import PageIndex.pageindex.page_index as page_index_module
                    modules_to_patch.append(('PageIndex.pageindex.page_index', page_index_module))
                except ImportError:
                    try:
                        import pageindex.page_index as page_index_module
                        modules_to_patch.append(('pageindex.page_index', page_index_module))
                    except ImportError:
                        pass
            
            # Патчим все найденные модули
            for module_name, module in modules_to_patch:
                patched_count = 0
                if hasattr(module, 'ChatGPT_API'):
                    module.ChatGPT_API = patched_ChatGPT_API
                    patched_count += 1
                if hasattr(module, 'ChatGPT_API_with_finish_reason'):
                    module.ChatGPT_API_with_finish_reason = patched_ChatGPT_API_with_finish_reason
                    patched_count += 1
                if hasattr(module, 'ChatGPT_API_async'):
                    module.ChatGPT_API_async = patched_ChatGPT_API_async
                    patched_count += 1
                if hasattr(module, 'count_tokens'):
                    module.count_tokens = patched_count_tokens
                    patched_count += 1
                
                if patched_count > 0:
                    logger.info(f"✅ Патчинг применен к {module_name} ({patched_count} функций)")
                else:
                    logger.debug(f"Модуль {module_name} не содержит функций для патчинга")
                    
        except Exception as e:
            logger.warning(f"⚠️ Не удалось патчить page_index модули: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        _patched = True
        
        # Обновляем настройки для get_ollama_settings
        global _ollama_settings
        _ollama_settings = {
            'base_url': _ollama_base_url,
            'model': _ollama_model,
            'patched': True
        }
        
        logger.info(f"✅ PageIndex успешно патчен для Ollama (base_url={_ollama_base_url}, model={_ollama_model})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при патчинге PageIndex: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def get_ollama_settings():
    """Получить текущие настройки Ollama"""
    global _ollama_settings
    if not _ollama_settings:
        _ollama_settings = {
            "base_url": _ollama_base_url,
            "model": _ollama_model,
            "patched": _patched
        }
    return _ollama_settings
