from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from datetime import datetime, timedelta
import calendar
from locales import get_text

def get_language_keyboard():
    """Language selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kk")
        ]
    ])
    return keyboard

def get_main_menu_keyboard(lang: str = 'ru'):
    """Main menu reply keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text('btn_search', lang))],
            [
                KeyboardButton(text=get_text('btn_history', lang)),
                KeyboardButton(text=get_text('btn_favorites', lang))
            ],
            [
                KeyboardButton(text=get_text('btn_language', lang)),
                KeyboardButton(text=get_text('btn_landlords', lang))
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

def get_back_keyboard(lang: str = 'ru'):
    """Back button keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text('btn_back', lang))],
            [KeyboardButton(text=get_text('btn_main_menu', lang))]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_cities_keyboard(cities: list, lang: str = 'ru'):
    """Cities selection inline keyboard"""
    buttons = []
    for city in cities:
        name = city['name_ru'] if lang == 'ru' else city['name_kk']
        buttons.append([InlineKeyboardButton(
            text=name,
            callback_data=f"city_{city['id']}"
        )])

    buttons.append([InlineKeyboardButton(
        text=get_text('btn_back', lang),
        callback_data="search_back"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_districts_keyboard(districts: list, lang: str = 'ru'):
    """Districts selection inline keyboard"""
    buttons = []
    row = []
    for i, district in enumerate(districts):
        name = district['name_ru'] if lang == 'ru' else district['name_kk']
        row.append(InlineKeyboardButton(
            text=name,
            callback_data=f"district_{district['id']}"
        ))
        if len(row) == 2 or i == len(districts) - 1:
            buttons.append(row)
            row = []

    buttons.append([InlineKeyboardButton(
        text=get_text('btn_back', lang),
        callback_data="district_back"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_calendar_keyboard(year: int, month: int, lang: str = 'ru',
                          min_date: datetime = None, selected_date: str = None,
                          calendar_type: str = 'check_in', apartment_id: int = None):
    """Calendar inline keyboard for date selection"""
    if min_date is None:
        min_date = datetime.now()

    # Get booked dates if apartment_id is provided
    booked_dates = []
    if apartment_id:
        import database as db
        booked_dates = db.get_booked_dates(apartment_id)

    month_names = get_text('month_names', lang)
    day_names = get_text('day_names', lang)

    buttons = []

    # Month and year header
    header = f"{month_names[month - 1]} {year}"
    buttons.append([
        InlineKeyboardButton(text=get_text('prev_month', lang), callback_data=f"cal_prev_{year}_{month}_{calendar_type}"),
        InlineKeyboardButton(text=header, callback_data="ignore"),
        InlineKeyboardButton(text=get_text('next_month', lang), callback_data=f"cal_next_{year}_{month}_{calendar_type}")
    ])

    # Day names
    buttons.append([InlineKeyboardButton(text=day, callback_data="ignore") for day in day_names])

    # Calendar days
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                date_obj = datetime(year, month, day)
                date_str = date_obj.strftime("%Y-%m-%d")

                # Check if date is booked
                if date_str in booked_dates:
                    row.append(InlineKeyboardButton(text="✖", callback_data="ignore"))
                # Disable past dates
                elif date_obj.date() < min_date.date():
                    row.append(InlineKeyboardButton(text="·", callback_data="ignore"))
                elif date_str == selected_date:
                    row.append(InlineKeyboardButton(text=f"[{day}]", callback_data="ignore"))
                else:
                    row.append(InlineKeyboardButton(
                        text=str(day),
                        callback_data=f"date_{calendar_type}_{date_str}"
                    ))
        buttons.append(row)

    buttons.append([InlineKeyboardButton(
        text=get_text('btn_back', lang),
        callback_data=f"calendar_back_{calendar_type}"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_search_filters_keyboard(filters: dict, count: int, lang: str = 'ru'):
    """Search filters summary with available apartments button"""
    buttons = [
        [InlineKeyboardButton(
            text=get_text('available_apartments', lang, count=count),
            callback_data="show_apartments"
        )],
        [InlineKeyboardButton(
            text=get_text('clear_filters', lang),
            callback_data="clear_filters"
        )],
        [InlineKeyboardButton(
            text=get_text('btn_back', lang),
            callback_data="filters_back"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_apartment_card_keyboard(apartment_id: int, is_favorite: bool, lang: str = 'ru',
                                 has_prev: bool = False, has_next: bool = False):
    """Apartment card inline keyboard"""
    buttons = []

    # Navigation buttons
    nav_row = []
    if has_prev:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"apt_prev_{apartment_id}"))
    if has_next:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"apt_next_{apartment_id}"))
    if nav_row:
        buttons.append(nav_row)

    # Book button
    buttons.append([InlineKeyboardButton(
        text=get_text('btn_book', lang),
        callback_data=f"book_{apartment_id}"
    )])

    # Favorite button
    if is_favorite:
        buttons.append([InlineKeyboardButton(
            text=get_text('btn_in_favorites', lang),
            callback_data=f"unfav_{apartment_id}"
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text=get_text('btn_add_favorite', lang),
            callback_data=f"fav_{apartment_id}"
        )])

    # Reviews button
    buttons.append([InlineKeyboardButton(
        text=get_text('btn_read_reviews', lang),
        callback_data=f"reviews_{apartment_id}"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_contact_keyboard(lang: str = 'ru'):
    """Contact sharing keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text=get_text('share_contact', lang),
                request_contact=True
            )],
            [KeyboardButton(text=get_text('btn_back', lang))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_booking_confirmed_keyboard(booking_id: int, lang: str = 'ru'):
    """Booking confirmed keyboard"""
    buttons = [
        [InlineKeyboardButton(
            text=get_text('btn_write_landlord', lang),
            callback_data=f"chat_{booking_id}"
        )],
        [InlineKeyboardButton(
            text=get_text('btn_booking_details', lang),
            callback_data=f"booking_details_{booking_id}"
        )],
        [InlineKeyboardButton(
            text=get_text('btn_cancel_booking', lang),
            callback_data=f"cancel_booking_{booking_id}"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_booking_keyboard(booking_id: int, lang: str = 'ru'):
    """Cancel booking confirmation keyboard"""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text('btn_yes_cancel', lang),
                callback_data=f"confirm_cancel_{booking_id}"
            ),
            InlineKeyboardButton(
                text=get_text('btn_no_keep', lang),
                callback_data=f"keep_booking_{booking_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_landlord_menu_keyboard(lang: str = 'ru'):
    """Landlord section menu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text('btn_conditions', lang))],
            [KeyboardButton(text=get_text('btn_connect', lang))],
            [KeyboardButton(text=get_text('btn_main_menu', lang))]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_rating_keyboard(lang: str = 'ru'):
    """Rating selection keyboard (1-5 stars)"""
    buttons = [[
        InlineKeyboardButton(text="⭐", callback_data="rating_1"),
        InlineKeyboardButton(text="⭐⭐", callback_data="rating_2"),
        InlineKeyboardButton(text="⭐⭐⭐", callback_data="rating_3"),
        InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rating_4"),
        InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rating_5")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_review_actions_keyboard(review_id: int, lang: str = 'ru'):
    """Review helpful/not helpful buttons"""
    buttons = [[
        InlineKeyboardButton(
            text=get_text('review_helpful', lang, count=0),
            callback_data=f"helpful_{review_id}"
        ),
        InlineKeyboardButton(
            text=get_text('review_not_helpful', lang, count=0),
            callback_data=f"not_helpful_{review_id}"
        )
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_reviews_pagination_keyboard(apartment_id: int, page: int, total_pages: int, lang: str = 'ru'):
    """Reviews pagination keyboard"""
    buttons = []
    nav_row = []

    if page > 1:
        nav_row.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"reviews_page_{apartment_id}_{page - 1}"
        ))

    nav_row.append(InlineKeyboardButton(
        text=f"{page}/{total_pages}",
        callback_data="ignore"
    ))

    if page < total_pages:
        nav_row.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"reviews_page_{apartment_id}_{page + 1}"
        ))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(
        text=get_text('btn_back', lang),
        callback_data="reviews_back"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_no_apartments_keyboard(lang: str = 'ru'):
    """No apartments found keyboard"""
    buttons = [
        [InlineKeyboardButton(
            text=get_text('change_filters', lang),
            callback_data="change_filters"
        )],
        [InlineKeyboardButton(
            text=get_text('clear_filters', lang),
            callback_data="clear_all_filters"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_remove_favorite_keyboard(apartment_id: int, lang: str = 'ru'):
    """Confirm remove from favorites keyboard"""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text('btn_yes_cancel', lang),
                callback_data=f"confirm_unfav_{apartment_id}"
            ),
            InlineKeyboardButton(
                text=get_text('btn_no_keep', lang),
                callback_data=f"keep_fav_{apartment_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
