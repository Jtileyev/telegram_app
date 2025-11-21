"""
Telegram Notification System
Sends notifications to users and landlords via Telegram
"""
import asyncio
from aiogram import Bot


async def send_notification(telegram_id: int, message: str, bot_token: str):
    """Send notification to user via Telegram"""
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(telegram_id, message, parse_mode='HTML')
    finally:
        await bot.session.close()


def notify_landlord_approved(telegram_id: int, landlord_name: str, bot_token: str):
    """Notify landlord that their request was approved"""
    message = f"""✅ <b>Ваша заявка одобрена!</b>

Здравствуйте, {landlord_name}!

Ваша заявка на подключение к платформе "Аставайся" была одобрена.

Вы можете войти в панель управления используя ваш email.

Добро пожаловать в нашу команду! 🎉"""

    asyncio.run(send_notification(telegram_id, message, bot_token))


def notify_booking_status(telegram_id: int, status: str, apartment_title: str, bot_token: str):
    """Notify user about booking status change"""
    status_messages = {
        'confirmed': f'✅ Ваше бронирование подтверждено!\n\nКвартира: {apartment_title}',
        'rejected': f'❌ Ваше бронирование отклонено.\n\nКвартира: {apartment_title}',
        'completed': f'✅ Бронирование завершено.\n\nКвартира: {apartment_title}\n\nПожалуйста, оставьте отзыв!'
    }

    message = status_messages.get(status, f'Статус бронирования изменен: {status}')
    asyncio.run(send_notification(telegram_id, message, bot_token))


def notify_landlord_new_booking(landlord_telegram_id: int, booking_info: dict, bot_token: str):
    """Notify landlord about new booking request"""
    message = f"""🔔 <b>Новая заявка на бронирование!</b>

📍 Квартира: {booking_info.get('apartment_title', 'N/A')}
👤 Гость: {booking_info.get('user_name', 'N/A')}
📞 Телефон: {booking_info.get('user_phone', 'N/A')}

📅 Заезд: {booking_info.get('check_in', 'N/A')}
📅 Выезд: {booking_info.get('check_out', 'N/A')}
💰 Сумма: {booking_info.get('total_price', 0)} ₸

⏳ Статус: Ожидает подтверждения

Пожалуйста, подтвердите или отклоните бронирование в панели управления."""

    try:
        asyncio.run(send_notification(landlord_telegram_id, message, bot_token))
    except Exception as e:
        print(f"Error sending notification to landlord: {e}")
