"""
Notification service - handles all notifications
"""
from typing import Optional
from aiogram import Bot

from constants import PRICE_CURRENCY
from utils import format_price


class NotificationService:
    """Service for sending notifications"""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    async def send_message(self, telegram_id: int, message: str, parse_mode: str = 'HTML'):
        """Send a message to a user"""
        bot = Bot(token=self.bot_token)
        try:
            await bot.send_message(telegram_id, message, parse_mode=parse_mode)
        finally:
            await bot.session.close()

    async def notify_landlord_new_booking(
        self,
        landlord_telegram_id: int,
        booking_id: int,
        apartment_title: str,
        guest_name: str,
        guest_phone: str,
        check_in: str,
        check_out: str,
        total_price: float
    ):
        """Notify landlord about new booking"""
        message = f"""🔔 <b>Новое бронирование!</b>

📍 Квартира: {apartment_title}
👤 Гость: {guest_name}
📞 Телефон: {guest_phone}

📅 Заезд: {check_in}
📅 Выезд: {check_out}
💰 Сумма: {format_price(total_price)} {PRICE_CURRENCY}

Бронирование #{booking_id}

⏳ Статус: Ожидает подтверждения

Пожалуйста, подтвердите или отклоните бронирование в админ-панели."""

        await self.send_message(landlord_telegram_id, message)

    async def notify_booking_status_change(
        self,
        user_telegram_id: int,
        status: str,
        apartment_title: str
    ):
        """Notify user about booking status change"""
        status_messages = {
            'confirmed': f'✅ Ваше бронирование подтверждено!\n\nКвартира: {apartment_title}',
            'rejected': f'❌ Ваше бронирование отклонено.\n\nКвартира: {apartment_title}',
            'completed': f'✅ Бронирование завершено.\n\nКвартира: {apartment_title}\n\nПожалуйста, оставьте отзыв!'
        }

        message = status_messages.get(status, f'Статус бронирования изменен: {status}')
        await self.send_message(user_telegram_id, message)

    async def notify_landlord_approved(
        self,
        landlord_telegram_id: int,
        landlord_name: str
    ):
        """Notify landlord that their request was approved"""
        message = f"""✅ <b>Ваша заявка одобрена!</b>

Здравствуйте, {landlord_name}!

Ваша заявка на подключение к платформе "Аставайся" была одобрена.

Вы можете войти в панель управления используя ваш email.

Добро пожаловать в нашу команду! 🎉"""

        await self.send_message(landlord_telegram_id, message)
