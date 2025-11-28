# Задача 007: Добавить middleware для обработки ошибок

## Приоритет: 🟢 Низкий

## Описание
Сейчас ошибки обрабатываются в каждом обработчике отдельно. 
Нужен централизованный middleware для логирования и обработки исключений.

## Решение

### Создать bot/middleware/error_handler.py
```python
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from logger import setup_logger, log_error

logger = setup_logger('error_middleware')


class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware for centralized error handling"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            log_error(logger, e, f"Handler error for {type(event).__name__}")
            
            # Отправить пользователю сообщение об ошибке
            try:
                if isinstance(event, Message):
                    await event.answer(
                        "❌ Произошла ошибка. Попробуйте позже.",
                        reply_markup=get_main_menu_keyboard('ru')
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "❌ Произошла ошибка",
                        show_alert=True
                    )
            except:
                pass  # Не удалось отправить сообщение
            
            return None
```

### Подключить в main.py
```python
from middleware.error_handler import ErrorHandlerMiddleware

dp.message.middleware(ErrorHandlerMiddleware())
dp.callback_query.middleware(ErrorHandlerMiddleware())
```

## Проверка
- [ ] Все необработанные исключения логируются
- [ ] Пользователь получает понятное сообщение об ошибке
- [ ] Бот не падает при ошибках
