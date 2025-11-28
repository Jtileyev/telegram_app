"""
Astavaisya Telegram Bot - Main entry point
"""
import asyncio
import signal
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from logger import setup_logger
from rate_limiter import default_rate_limiter
from middleware import ErrorHandlerMiddleware
from handlers import (
    registration_router,
    search_router,
    booking_router,
    reviews_router,
    favorites_router,
    landlords_router,
    common_router,
    calendar_router,
)

logger = setup_logger('telegram_bot')

bot = None
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def main():
    """Start bot with graceful shutdown support"""
    global bot

    import config

    # Initialize database
    db.init_db()

    # Get bot token and initialize bot
    try:
        bot_token = config.get_bot_token()
        bot = Bot(token=bot_token)
        logger.info("Bot initialized with token from database")
    except ValueError as e:
        logger.error(f"Failed to get bot token: {e}")
        return

    # Register middleware (order matters - error handler should be outer)
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    dp.message.middleware(default_rate_limiter)
    dp.callback_query.middleware(default_rate_limiter)
    logger.info("Middleware enabled: ErrorHandler, RateLimiter")

    # Include routers (order matters - more specific first)
    dp.include_router(registration_router)
    dp.include_router(search_router)
    dp.include_router(booking_router)
    dp.include_router(calendar_router)
    dp.include_router(reviews_router)
    dp.include_router(favorites_router)
    dp.include_router(landlords_router)
    dp.include_router(common_router)

    # Graceful shutdown handler
    async def shutdown():
        """Cleanup on shutdown"""
        logger.info("Shutting down bot...")
        await dp.stop_polling()
        if bot:
            await bot.session.close()
        logger.info("Bot stopped gracefully")

    # Setup signal handlers
    loop = asyncio.get_event_loop()

    def signal_handler(sig):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        asyncio.create_task(shutdown())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))

    # Start polling
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        if bot and bot.session:
            await bot.session.close()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
