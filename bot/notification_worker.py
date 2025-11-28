"""
Background worker for processing notification queue
Sends pending notifications from database to users via Telegram
"""
import asyncio
import json
from aiogram import Bot

import database as db
from locales import get_text
from logger import setup_logger

logger = setup_logger('notification_worker')

# Mapping of notification types to locale keys
NOTIFICATION_TYPE_TO_LOCALE = {
    'booking_status_confirmed': 'notification_booking_confirmed',
    'booking_status_rejected': 'notification_booking_rejected',
    'booking_status_completed': 'notification_booking_completed',
    'booking_status_cancelled': 'notification_booking_cancelled',
}


async def send_telegram_notification(bot: Bot, telegram_id: int, message: str) -> bool:
    """Send notification to user via Telegram"""
    try:
        await bot.send_message(telegram_id, message, parse_mode='HTML')
        return True
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        return False


def build_notification_message(notification_type: str, data: dict) -> str:
    """Build notification message from type and data"""
    locale_key = NOTIFICATION_TYPE_TO_LOCALE.get(notification_type)
    if not locale_key:
        logger.warning(f"Unknown notification type: {notification_type}")
        return data.get('message', 'Уведомление')

    lang = data.get('lang', 'ru')

    return get_text(
        locale_key,
        lang,
        apartment_title=data.get('apartment_title', ''),
        address=data.get('address', ''),
        check_in=data.get('check_in', ''),
        check_out=data.get('check_out', ''),
        landlord_name=data.get('landlord_name', ''),
        landlord_phone=data.get('landlord_phone', '')
    )


async def process_notifications(bot: Bot):
    """Process pending notifications from queue"""
    notifications = db.get_pending_notifications(limit=50)

    if not notifications:
        return 0

    sent_count = 0
    for notification in notifications:
        telegram_id = notification.get('telegram_id')
        if not telegram_id:
            logger.warning(f"Notification {notification['id']} has no telegram_id, marking as sent")
            db.mark_notification_sent(notification['id'])
            continue

        # Parse notification data
        try:
            data = json.loads(notification['message'])
        except json.JSONDecodeError:
            # Fallback: treat message as plain text
            data = {'message': notification['message'], 'lang': notification.get('language', 'ru')}

        # Build message
        message = build_notification_message(notification['type'], data)

        # Send notification
        success = await send_telegram_notification(bot, telegram_id, message)

        if success:
            db.mark_notification_sent(notification['id'])
            sent_count += 1
            logger.info(f"Sent notification {notification['id']} to user {telegram_id}")
        else:
            logger.error(f"Failed to send notification {notification['id']}")

    return sent_count


async def notification_worker_loop(bot: Bot, interval: int = 10):
    """Background loop that processes notifications every interval seconds"""
    logger.info(f"Notification worker started, checking every {interval} seconds")

    while True:
        try:
            sent = await process_notifications(bot)
            if sent > 0:
                logger.info(f"Processed {sent} notifications")
        except Exception as e:
            logger.error(f"Error in notification worker: {e}")

        await asyncio.sleep(interval)
