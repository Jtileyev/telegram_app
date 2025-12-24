"""
Calendar handlers - date selection for bookings
"""
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import get_calendar_keyboard, get_contact_keyboard, get_main_menu_keyboard
from locales import get_text

router = Router()


@router.callback_query(F.data.startswith("cal_prev_") | F.data.startswith("cal_next_"))
async def calendar_navigation(callback: CallbackQuery, state: FSMContext):
    """Navigate calendar months"""
    parts = callback.data.split("_")
    direction = parts[1]  # prev or next
    year = int(parts[2])
    month = int(parts[3])
    calendar_type = parts[4] if len(parts) > 4 else 'check_in'

    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    if direction == "prev":
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    else:
        month += 1
        if month > 12:
            month = 1
            year += 1

    data = await state.get_data()
    filters = data.get('filters', {})
    min_date = datetime.now()
    selected_date = filters.get(calendar_type)

    keyboard = get_calendar_keyboard(year, month, lang, min_date, selected_date, calendar_type)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("date_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    """Handle date selection"""
    from .booking import BookingStates, create_booking_request

    # Parse: date_check_in_2025-12-17 or date_check_out_2025-12-17
    # Split only first part, then extract type and date
    _, rest = callback.data.split("_", 1)  # rest = "check_in_2025-12-17"
    if rest.startswith("check_in_"):
        calendar_type = "check_in"
        date_str = rest[9:]  # Remove "check_in_"
    elif rest.startswith("check_out_"):
        calendar_type = "check_out"
        date_str = rest[10:]  # Remove "check_out_"
    else:
        # Fallback for unexpected format
        parts = callback.data.split("_")
        calendar_type = parts[1]
        date_str = parts[-1]

    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    data = await state.get_data()
    filters = data.get('filters', {})
    filters[calendar_type] = date_str
    await state.update_data(filters=filters)

    current_state = await state.get_state()

    # If we're in booking flow
    if current_state == BookingStates.confirming.state:
        if calendar_type == 'check_in':
            apartment_id = data.get('booking_apartment_id')
            check_in_date = datetime.strptime(date_str, "%Y-%m-%d")
            min_checkout = check_in_date + timedelta(days=1)

            # Replace calendar with check_out calendar
            await callback.message.edit_text(
                get_text('select_check_out', lang),
                reply_markup=get_calendar_keyboard(
                    min_checkout.year, min_checkout.month, lang,
                    min_date=min_checkout,
                    calendar_type='check_out',
                    apartment_id=apartment_id
                )
            )
        elif calendar_type == 'check_out':
            check_in = filters.get('check_in')
            check_out = date_str
            apartment_id = data.get('booking_apartment_id')

            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

            if check_out_date <= check_in_date:
                await callback.answer(get_text('invalid_dates', lang), show_alert=True)
                return

            if not db.check_apartment_availability(apartment_id, check_in, check_out):
                await callback.answer(get_text('apartment_booked', lang), show_alert=True)
                return

            # Remove calendar keyboard after check_out selection
            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except Exception:
                pass

            if user.get('phone'):
                await create_booking_request(callback.message, state, user)
            else:
                await callback.message.answer(
                    get_text('enter_phone', lang),
                    reply_markup=get_contact_keyboard(lang)
                )
                await state.set_state(BookingStates.waiting_contact)
    else:
        # Remove calendar keyboard for non-booking flow
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await callback.message.answer(get_text(f'{calendar_type}_selected', lang, date=date_str))

    await callback.answer()


@router.callback_query(F.data.startswith("calendar_back_"))
async def calendar_back(callback: CallbackQuery, state: FSMContext):
    """Back from calendar"""
    from .search import show_filters_summary

    # Remove calendar keyboard
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    data = await state.get_data()
    filters = data.get('filters', {})

    await show_filters_summary(callback.message, filters, lang)
    await callback.answer()


# Booking details and chat handlers
@router.callback_query(F.data.startswith("chat_"))
async def chat_with_landlord(callback: CallbackQuery):
    """Start chat with landlord"""
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)
    await callback.answer(get_text('feature_coming_soon', lang), show_alert=True)


@router.callback_query(F.data.startswith("booking_details_"))
async def show_booking_details(callback: CallbackQuery):
    """Show booking details"""
    from utils import format_price
    
    booking_id = int(callback.data.split("_")[2])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    booking = db.get_booking_by_id(booking_id)

    if booking:
        title = booking['title_ru'] if lang == 'ru' else booking['title_kk']
        status_key = f"status_{booking['status']}"
        text = f"🏠 *{title}*\n"
        text += f"📍 {booking['address']}\n"
        text += f"📅 {booking['check_in_date']} - {booking['check_out_date']}\n"
        text += f"💰 {format_price(booking['total_price'])} ₸\n"
        text += f"📋 {get_text(status_key, lang)}"

        await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()
