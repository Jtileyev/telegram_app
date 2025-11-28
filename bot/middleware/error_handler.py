"""
Centralized error handling middleware
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from logger import setup_logger, log_error

logger = setup_logger('error_middleware')


class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware for centralized error handling and logging"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            # Get user info for logging
            user_id = None
            if isinstance(event, (Message, CallbackQuery)):
                user_id = event.from_user.id if event.from_user else None

            context = f"Handler for {type(event).__name__}"
            if user_id:
                context += f" (user: {user_id})"

            log_error(logger, e, context)

            # Send error message to user
            try:
                error_text = "❌ Произошла ошибка. Попробуйте позже."

                if isinstance(event, Message):
                    await event.answer(error_text)
                elif isinstance(event, CallbackQuery):
                    await event.answer(error_text, show_alert=True)
            except Exception:
                pass  # Failed to send error message

            return None
