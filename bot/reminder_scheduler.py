"""
Check-in reminder scheduler
Sends reminders to users before their check-in date
"""
import asyncio
from aiogram import Bot

import database as db
from locales import get_text
from logger import setup_logger

logger = setup_logger('reminder_scheduler')

# Default reminder hours (can be overridden from settings)
DEFAULT_REMINDER_HOURS = 24


async def send_checkin_reminder(bot: Bot, booking: dict) -> bool:
    """Send check-in reminder to user"""
    telegram_id = booking.get('telegram_id')
    if not telegram_id:
        return False

    lang = booking.get('language', 'ru')
    title = booking['title_ru'] if lang == 'ru' else booking.get('title_kk', booking['title_ru'])

    message = get_text('reminder_check_in', lang,
        address=booking['address'],
        date=booking['check_in_date']
    )

    # Add landlord contact info
    message += f"\n\n📞 {booking['landlord_name']}: {booking['landlord_phone']}"

    try:
        await bot.send_message(telegram_id, message, parse_mode='HTML')
        return True
    except Exception as e:
        logger.error(f"Failed to send reminder to {telegram_id}: {e}")
        return False


async def process_reminders(bot: Bot):
    """Process and send all pending check-in reminders"""
    # Get reminder hours from settings or use default
    hours_setting = db.get_setting('reminder_hours_before')
    hours_before = int(hours_setting) if hours_setting else DEFAULT_REMINDER_HOURS

    bookings = db.get_bookings_for_reminder(hours_before)

    if not bookings:
        return 0

    sent_count = 0
    for booking in bookings:
        success = await send_checkin_reminder(bot, booking)
        if success:
            db.mark_reminder_sent(booking['id'])
            sent_count += 1
            logger.info(f"Sent check-in reminder for booking {booking['id']}")

    return sent_count


async def reminder_scheduler_loop(bot: Bot, interval: int = 3600):
    """Background loop that checks for reminders every interval seconds (default: 1 hour)"""
    logger.info(f"Reminder scheduler started, checking every {interval} seconds")

    while True:
        try:
            sent = await process_reminders(bot)
            if sent > 0:
                logger.info(f"Sent {sent} check-in reminders")
        except Exception as e:
            logger.error(f"Error in reminder scheduler: {e}")

        await asyncio.sleep(interval)
