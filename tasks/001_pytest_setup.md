# Задача 001: Настройка pytest для автотестов

## Приоритет: 🟡 Средний

## Описание
Тесты в `bot/tests.py` не запускаются через стандартный pytest runner. Нужно настроить pytest и убедиться, что тесты работают.

## Шаги выполнения

### 1. Добавить pytest в зависимости
В файле `requirements.txt` добавить:
```
pytest==7.4.3
pytest-asyncio==0.21.1
```

### 2. Создать конфигурацию pytest
Создать файл `pytest.ini` в корне проекта:
```ini
[pytest]
testpaths = bot
python_files = tests.py test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

### 3. Проверить запуск тестов
```bash
source venv/bin/activate
pip install pytest pytest-asyncio
pytest bot/tests.py -v
```

### 4. Исправить возможные проблемы
- Убедиться, что все импорты работают
- Проверить, что тестовая БД создаётся корректно

## Критерии завершения
- [ ] pytest добавлен в requirements.txt
- [ ] Создан pytest.ini
- [ ] Команда `pytest` успешно запускает тесты
- [ ] Все тесты проходят (или понятно, какие нужно исправить)

## Связанные файлы
- `requirements.txt`
- `bot/tests.py`
- `pytest.ini` (создать)
