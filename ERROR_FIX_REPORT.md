# Отчет об исправлении ошибки индексации

## Ошибка
```
PageIndex indexing failed: unsupported operand type(s) for +: 'int' and 'NoneType'
```

## Причина
Ошибка возникала при попытке выполнить арифметические операции с `None` значениями:
1. В функции `post_processing` - попытка вычесть 1 из `None` или использовать `None` как индекс
2. В функции `process_large_node_recursively` - попытка использовать `None` как `start_index`
3. В функции `add_page_offset_to_toc_json` - попытка сложить `None` с числом

## Исправления

### 1. `PageIndex/pageindex/utils.py` - функция `post_processing`
**Было:**
```python
if structure[i + 1].get('appear_start') == 'yes':
    item['end_index'] = structure[i + 1]['physical_index']-1
else:
    item['end_index'] = structure[i + 1]['physical_index']
```

**Стало:**
```python
next_physical_index = structure[i + 1].get('physical_index')
if next_physical_index is not None:
    if structure[i + 1].get('appear_start') == 'yes':
        item['end_index'] = next_physical_index - 1
    else:
        item['end_index'] = next_physical_index
else:
    # If next item has no physical_index, use end_physical_index
    item['end_index'] = end_physical_index
```

### 2. `PageIndex/pageindex/page_index.py` - функция `process_large_node_recursively`
**Было:**
```python
node['end_index'] = valid_node_toc_items[1]['start_index'] if len(valid_node_toc_items) > 1 else node['end_index']
node['end_index'] = valid_node_toc_items[0]['start_index'] if valid_node_toc_items else node['end_index']
```

**Стало:**
```python
if len(valid_node_toc_items) > 1 and valid_node_toc_items[1].get('start_index') is not None:
    node['end_index'] = valid_node_toc_items[1]['start_index']
if valid_node_toc_items and valid_node_toc_items[0].get('start_index') is not None:
    node['end_index'] = valid_node_toc_items[0]['start_index']
```

### 3. `PageIndex/pageindex/page_index.py` - функция `add_page_offset_to_toc_json`
**Было:**
```python
def add_page_offset_to_toc_json(data, offset):
    for i in range(len(data)):
        if data[i].get('page') is not None and isinstance(data[i]['page'], int):
            data[i]['physical_index'] = data[i]['page'] + offset
```

**Стало:**
```python
def add_page_offset_to_toc_json(data, offset):
    if offset is None:
        # If offset is None, don't apply it
        return data
    for i in range(len(data)):
        if data[i].get('page') is not None and isinstance(data[i]['page'], int):
            data[i]['physical_index'] = data[i]['page'] + offset
```

## Результат
✅ Все места, где могла возникнуть ошибка `int + NoneType`, теперь защищены проверками на `None`.

## Следующие шаги
1. Перезапустить индексацию документов 5 и 6
2. Проверить, что ошибка больше не возникает
3. Мониторить логи на наличие других ошибок

