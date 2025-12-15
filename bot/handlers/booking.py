"""
Booking handlers - booking flow
"""
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import (
    get_main_menu_keyboard, get_calendar_keyboard, get_contact_keyboard,
    get_cancel_booking_keyboard, get_booking_created_keyboard
)
from locales import get_text
from logger import setup_logger, get_audit_logger, log_booking_action, log_error
from notifications import notify_landlord_new_booking
from constants import PRICE_CURRENCY
from utils import format_price
from services.booking_service import BookingService

router = Router()
logger = setup_logger('booking')
audit_logger = get_audit_logger()
booking_service = BookingService()


class BookingStates(StatesGroup):
    confirming = State()
    waiting_contact = State()


@router.callback_query(F.data.startswith("book_"))
async def start_booking(callback: CallbackQuery, state: FSMContext):
    """Start booking process"""
    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    # Validate apartment exists and is active
    apartment = db.get_apartment_by_id(apartment_id)
    if not apartment:
        await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
        return
    
    if not apartment.get('is_active'):
        await callback.answer(get_text('apartment_inactive', lang), show_alert=True)
        return

    data = await state.get_data()
    filters = data.get('filters', {})

    await state.update_data(booking_apartment_id=apartment_id)

    if filters.get('check_in') and filters.get('check_out'):
        if not db.check_apartment_availability(apartment_id, filters.get('check_in'), filters.get('check_out')):
            await callback.answer(get_text('apartment_booked', lang), show_alert=True)
            return

        if user.get('phone'):
            await create_booking_request(callback.message, state, user)
        else:
            await callback.message.answer(
                get_text('enter_phone', lang),
                reply_markup=get_contact_keyboard(lang)
            )
            await state.set_state(BookingStates.waiting_contact)
    else:
        min_date = datetime.now()
        await callback.message.answer(
            get_text('select_check_in', lang),
            reply_markup=get_calendar_keyboard(
                min_date.year, min_date.month, lang,
                min_date=min_date,
                calendar_type='check_in',
                apartment_id=apartment_id
            )
        )
        await state.set_state(BookingStates.confirming)

    await callback.answer()


async def create_booking_request(message: Message, state: FSMContext, user: dict):
    """Create booking request using BookingService"""
    from config import get_bot_token

    data = await state.get_data()
    apartment_id = data.get('booking_apartment_id')
    filters = data.get('filters', {})
    lang = user['language']

    # Validate dates using service
    is_valid, error_msg = booking_service.validate_booking_dates(
        filters['check_in'], filters['check_out']
    )
    if not is_valid:
        await message.answer(error_msg, reply_markup=get_main_menu_keyboard(lang))
        await state.clear()
        return

    # Check availability using service
    if not booking_service.check_availability(apartment_id, filters['check_in'], filters['check_out']):
        await message.answer(
            get_text('apartment_booked', lang),
            reply_markup=get_main_menu_keyboard(lang)
        )
        await state.clear()
        return

    apartment = db.get_apartment_by_id(apartment_id)

    # Calculate price using service
    total_price, original_total_price, days, should_apply_bonus, discount_days = \
        booking_service.calculate_booking_price(
            apartment_id, user['id'],
            filters['check_in'], filters['check_out']
        )

    # Calculate platform fee using service
    platform_fee = booking_service.get_platform_fee(total_price)

    try:
        booking_id = db.create_booking(
            user['id'], apartment_id, apartment['landlord_id'],
            filters['check_in'], filters['check_out'],
            total_price, platform_fee
        )

        if should_apply_bonus and apartment.get('promotion_id'):
            db.apply_promotion_to_booking(
                booking_id,
                apartment['promotion_id'],
                discount_days,
                original_total_price
            )

        confirmation_text = get_text('booking_created', lang) + "\n\n"
        confirmation_text += f"📅 {filters['check_in']} - {filters['check_out']}\n"
        confirmation_text += f"🏠 {days} " + get_text('days', lang) + "\n"
        confirmation_text += f"💰 {get_text('total', lang)}: {format_price(total_price)} {PRICE_CURRENCY}\n"

        if should_apply_bonus:
            from utils import pluralize_days
            confirmation_text += f"\n🎉 *{get_text('promotion_applied', lang)}*\n"
            confirmation_text += f"🎁 -{discount_days} {pluralize_days(discount_days, lang)} {get_text('free_days', lang)}!\n"
            confirmation_text += get_text('you_save', lang, amount=format_price(original_total_price - total_price)) + "\n"

        log_booking_action(
            audit_logger,
            user['id'],
            booking_id,
            "Booking created",
            f"Apartment {apartment_id}, Total: {total_price}{PRICE_CURRENCY}, Dates: {filters['check_in']} to {filters['check_out']}"
        )

        # Get landlord telegram_id for the keyboard
        landlord_telegram_id = apartment.get('landlord_telegram_id')
        keyboard = get_booking_created_keyboard(booking_id, landlord_telegram_id, lang)

        await message.answer(
            confirmation_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        # Also send main menu
        await message.answer(
            get_text('actions_prompt', lang),
            reply_markup=get_main_menu_keyboard(lang)
        )

        # Notify landlord
        try:
            landlord_telegram_id = apartment.get('landlord_telegram_id')
            if landlord_telegram_id:
                apartment_title = apartment['title_ru'] if lang == 'ru' else apartment['title_kk']
                bot_token = get_bot_token()

                await notify_landlord_new_booking(
                    landlord_telegram_id=landlord_telegram_id,
                    booking_id=booking_id,
                    apartment_title=apartment_title,
                    guest_name=user['full_name'],
                    guest_phone=user.get('phone', 'N/A'),
                    check_in=filters['check_in'],
                    check_out=filters['check_out'],
                    total_price=total_price,
                    bot_token=bot_token
                )
        except Exception as e:
            log_error(logger, e, "notify_landlord_new_booking")

        await state.clear()

    except ValueError as e:
        error_messages = {
            "Check-in date cannot be in the past": "booking_past_dates",
            "Check-out date must be after check-in date": "booking_invalid_dates",
            "Minimum booking duration is 1 day": "booking_min_duration",
            "User account is not active": "booking_user_inactive",
            "Landlord account is not active": "booking_landlord_inactive",
            "Apartment is not active": "booking_apartment_inactive",
            "Apartment is already booked for selected dates": "apartment_booked"
        }

        error_key = error_messages.get(str(e), 'booking_error')
        error_text = get_text(error_key, lang) if error_key in ['apartment_booked'] else str(e)

        await message.answer(
            error_text,
            reply_markup=get_main_menu_keyboard(lang)
        )
        await state.clear()


@router.message(BookingStates.waiting_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    """Handle contact sharing"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)

    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone

    db.update_user(telegram_id, phone=phone)
    user = db.get_user(telegram_id)

    await create_booking_request(message, state, user)


@router.callback_query(F.data.startswith("cancel_booking_"))
async def cancel_booking_confirm(callback: CallbackQuery):
    """Confirm booking cancellation"""
    booking_id = int(callback.data.split("_")[2])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)
    user = db.get_user(telegram_id)

    # Validate booking exists and belongs to user
    booking = db.get_booking_by_id(booking_id)
    if not booking:
        await callback.answer(get_text('booking_not_found', lang), show_alert=True)
        return
    
    if booking['user_id'] != user['id']:
        await callback.answer(get_text('booking_not_found', lang), show_alert=True)
        return

    await callback.message.answer(
        get_text('confirm_cancel_booking', lang),
        reply_markup=get_cancel_booking_keyboard(booking_id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel_"))
async def confirm_cancel_booking(callback: CallbackQuery):
    """Confirm and cancel booking"""
    booking_id = int(callback.data.split("_")[2])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)
    user = db.get_user(telegram_id)

    # Validate booking exists and belongs to user
    booking = db.get_booking_by_id(booking_id)
    if not booking or booking['user_id'] != user['id']:
        await callback.answer(get_text('booking_not_found', lang), show_alert=True)
        return

    db.update_booking_status(booking_id, 'cancelled')

    await callback.message.edit_text(get_text('booking_cancelled', lang))
    await callback.answer()


@router.callback_query(F.data.startswith("keep_booking_"))
async def keep_booking(callback: CallbackQuery):
    """Keep booking (don't cancel)"""
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    await callback.message.edit_text(get_text('booking_kept', lang))
    await callback.answer()
