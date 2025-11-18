"""
Rate Limiting Middleware for Telegram Bot
Prevents spam and abuse by limiting requests per user
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


class RateLimiter(BaseMiddleware):
    """
    Rate limiting middleware to prevent spam and abuse

    Implements token bucket algorithm with per-user limits
    """

    def __init__(
        self,
        rate_limit: int = 10,  # requests per period
        period: int = 60,  # period in seconds
        burst_limit: int = 20,  # max burst
    ):
        """
        Initialize rate limiter

        Args:
            rate_limit: Number of requests allowed per period
            period: Time period in seconds
            burst_limit: Maximum burst requests allowed
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.period = period
        self.burst_limit = burst_limit

        # Storage: user_id -> (tokens, last_update)
        self.buckets: Dict[int, tuple[float, datetime]] = {}

        # Throttle tracking: user_id -> last_warning_time
        self.throttled_users: Dict[int, datetime] = {}

        # Statistics
        self.stats = defaultdict(int)

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """
        Process incoming update with rate limiting

        Args:
            handler: Next handler in chain
            event: Incoming message or callback query
            data: Handler data

        Returns:
            Result from next handler or None if rate limited
        """
        user_id = event.from_user.id

        # Check if user is allowed
        if not await self._check_rate_limit(user_id):
            # User exceeded rate limit
            await self._handle_rate_limit_exceeded(event, user_id)
            return None

        # Update statistics
        self.stats['total_requests'] += 1

        # Continue to next handler
        return await handler(event, data)

    async def _check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user is within rate limit

        Args:
            user_id: Telegram user ID

        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now()

        # Get or create bucket for user
        if user_id not in self.buckets:
            self.buckets[user_id] = (self.rate_limit, now)
            return True

        tokens, last_update = self.buckets[user_id]

        # Calculate time passed
        time_passed = (now - last_update).total_seconds()

        # Refill tokens based on time passed
        new_tokens = min(
            self.burst_limit,
            tokens + (time_passed * self.rate_limit / self.period)
        )

        # Check if user has tokens
        if new_tokens < 1:
            # Rate limited
            self.stats['rate_limited'] += 1
            return False

        # Consume one token
        self.buckets[user_id] = (new_tokens - 1, now)
        return True

    async def _handle_rate_limit_exceeded(
        self,
        event: Message | CallbackQuery,
        user_id: int
    ):
        """
        Handle rate limit exceeded event

        Args:
            event: Message or callback query event
            user_id: User ID that exceeded limit
        """
        now = datetime.now()

        # Check if we already warned this user recently (last 5 minutes)
        if user_id in self.throttled_users:
            last_warning = self.throttled_users[user_id]
            if (now - last_warning).total_seconds() < 300:  # 5 minutes
                # Don't send another warning
                return

        # Update warning time
        self.throttled_users[user_id] = now

        # Send warning message
        warning_text = (
            "⚠️ Слишком много запросов!\n"
            "Пожалуйста, подождите немного перед следующим действием.\n\n"
            f"Лимит: {self.rate_limit} запросов в {self.period} секунд"
        )

        try:
            if isinstance(event, Message):
                await event.answer(warning_text)
            elif isinstance(event, CallbackQuery):
                await event.answer(warning_text, show_alert=True)
        except Exception:
            # Failed to send warning, ignore
            pass

    async def _cleanup_task(self):
        """
        Periodic cleanup task to remove old entries
        Runs every 5 minutes
        """
        while True:
            await asyncio.sleep(300)  # 5 minutes
            await self._cleanup()

    async def _cleanup(self):
        """
        Remove old entries from buckets and throttled users
        """
        now = datetime.now()
        cleanup_threshold = timedelta(hours=1)

        # Clean up buckets
        old_users = [
            user_id
            for user_id, (_, last_update) in self.buckets.items()
            if now - last_update > cleanup_threshold
        ]
        for user_id in old_users:
            del self.buckets[user_id]

        # Clean up throttled users
        old_throttled = [
            user_id
            for user_id, last_warning in self.throttled_users.items()
            if now - last_warning > cleanup_threshold
        ]
        for user_id in old_throttled:
            del self.throttled_users[user_id]

        # Log cleanup
        if old_users or old_throttled:
            from logger import logger
            logger.debug(
                f"Rate limiter cleanup: removed {len(old_users)} buckets, "
                f"{len(old_throttled)} throttled users"
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics

        Returns:
            Dictionary with statistics
        """
        return {
            'total_requests': self.stats['total_requests'],
            'rate_limited': self.stats['rate_limited'],
            'active_users': len(self.buckets),
            'throttled_users': len(self.throttled_users),
            'rate_limit': self.rate_limit,
            'period': self.period,
            'burst_limit': self.burst_limit,
        }


# Create default rate limiter instance
# 10 requests per minute, with burst up to 20
default_rate_limiter = RateLimiter(
    rate_limit=10,
    period=60,
    burst_limit=20
)
