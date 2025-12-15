# Localization strings for Russian and Kazakh languages

MESSAGES = {
    'ru': {
        # Language selection
        'choose_language': '🌐 Выберите язык / Тілді таңдаңыз:',
        'language_set': 'Язык установлен: Русский',

        # Welcome and registration
        'welcome': '''🏠 Добро пожаловать в "Аставайся"!

Сервис посуточной аренды квартир.

Здесь вы можете:
• Найти квартиру для аренды
• Сравнить цены и условия
• Забронировать жилье онлайн''',
        'enter_full_name': '📝 Пожалуйста, введите ваше ФИО:',
        'enter_phone': '📱 Введите номер телефона в формате:\n+7 (XXX) XXX XX XX',
        'invalid_phone': '⚠️ Некорректный номер телефона\nИспользуйте формат: +7 (XXX) XXX XX XX',
        'registration_complete': '✅ Регистрация завершена!\n\nДобро пожаловать, {name}!',
        'welcome_back': '👋 С возвращением, {name}!',

        # Main menu buttons
        'btn_search': '🔍 Поиск',
        'btn_history': '📋 История аренды',
        'btn_favorites': '⭐ Избранные',
        'btn_language': '🌐 Сменить язык',
        'btn_landlords': '🏠 Арендодателям',
        'btn_clear_chat': '🗑 Очистить чат',
        'btn_back': '⬅️ Назад',
        'btn_main_menu': '🏠 Главное меню',
        'chat_cleared': '✅ Чат очищен',

        # Search
        'search_title': '🔍 Поиск квартиры',
        'select_city': '🏙 Выберите город:',
        'select_district': '📍 Выберите район:',
        'all_districts': '🌐 Все районы',
        'select_check_in': '📅 Выберите дату заселения:',
        'select_check_out': '📅 Выберите дату выезда:',
        'clear_filters': '🗑 Очистить фильтры',
        'filters_cleared': '✅ Фильтры очищены',
        'active_filters': '''📌 Активные фильтры:
━━━━━━━━━━━━━━━━━━━
🏙 Город: {city}
📍 Район: {district}
📅 Заселение: {check_in}
📅 Выезд: {check_out}''',
        'active_filters_no_dates': '''📌 Активные фильтры:
━━━━━━━━━━━━━━━━━━━
🏙 Город: {city}
📍 Район: {district}''',
        'available_apartments': '🏠 Доступные варианты ({count})',
        'no_apartments': '''🔍 По вашим фильтрам не найдено квартир

Попробуйте:
• Расширить диапазон дат
• Выбрать другой район
• Убрать некоторые фильтры''',
        'change_filters': '🔄 Изменить фильтры',
        'invalid_dates': '⚠️ Дата выезда должна быть позже даты заселения\nПожалуйста, выберите корректные даты.',

        # Apartment card
        'price_per_day': '💰 {price} ₸/сутки',
        'price_per_month': '💰 {price} ₸/месяц',
        'address': '📍 {address}',
        'rating': '⭐ {rating} ({count} отзывов)',
        'no_reviews': 'Пока нет отзывов',
        'amenities': '🏷 Удобства:',
        'btn_book': '📞 Забронировать',
        'btn_add_favorite': '⭐ В избранное',
        'btn_remove_favorite': '🗑 Убрать из избранного',
        'btn_in_favorites': '⭐ В избранном',
        'btn_read_reviews': '📝 Читать отзывы',
        'btn_view_map': '🗺 Показать на карте',
        'btn_prev_apartment': '⬅️ Предыдущая',
        'btn_next_apartment': 'Следующая ➡️',
        'added_to_favorites': '✅ Квартира добавлена в избранное',
        'removed_from_favorites': '✅ Квартира удалена из избранного',

        # Booking
        'share_contact': '📱 Поделиться номером',
        'total': 'Итого',
        'promotion_applied': 'Акция применена',
        'booking_created': '''✅ Заявка успешно создана!
Ожидайте ответа от арендодателя.
Мы уведомим вас о статусе бронирования.''',
        'booking_confirmed': '''✅ Бронирование подтверждено!

📍 Адрес: {address}
📅 Заселение: {check_in}
📅 Выезд: {check_out}
💰 Стоимость: {total_price} ₸
💳 Комиссия платформы: {fee} ₸ ({percent}%)
💵 К оплате арендодателю: {to_landlord} ₸

ℹ️ Оплата производится напрямую арендодателю
📞 Контакт арендодателя: {phone}''',
        'booking_rejected': '''❌ К сожалению, арендодатель отклонил вашу заявку.

Попробуйте выбрать другую квартиру.''',
        'apartment_booked': '''⚠️ К сожалению, эта квартира уже забронирована на выбранные даты.''',
        'btn_write_landlord': '💬 Написать арендодателю',
        'btn_booking_details': '📋 Детали бронирования',
        'btn_cancel_booking': '❌ Отменить бронирование',
        'cancel_booking_confirm': '''❓ Вы уверены, что хотите отменить бронирование?

📍 Адрес: {address}
📅 Период: {check_in} - {check_out}''',
        'btn_yes_cancel': '✅ Да, отменить',
        'btn_no_keep': '❌ Нет, оставить',
        'booking_cancelled': '✅ Бронирование отменено',

        # History
        'history_title': '📋 История аренды',
        'history_empty': '📋 История аренды пуста',
        'status_pending': '⏳ Ожидает подтверждения',
        'status_confirmed': '✅ Подтверждено',
        'status_completed': '✔️ Завершено',
        'status_rejected': '❌ Отклонено',
        'status_cancelled': '🚫 Отменено',

        # Favorites
        'favorites_title': '⭐ Избранные квартиры',
        'favorites_empty': '⭐ Список избранного пуст',
        'confirm_remove_favorite': '❓ Удалить квартиру из избранного?',

        # Reviews
        'reviews_title': '📝 Отзывы',
        'review_helpful': '👍 Полезно ({count})',
        'review_not_helpful': '👎 Не полезно ({count})',
        'leave_review': '''🏠 Вы завершили аренду квартиры по адресу:
{address}

Поделитесь впечатлениями! Это поможет другим пользователям.''',
        'btn_leave_review': '📝 Оставить отзыв',
        'select_rating': 'Выберите оценку (от 1 до 5):',
        'enter_comment': 'Напишите комментарий (минимум 10 символов):',
        'review_saved': '''✅ Спасибо за отзыв!
Ваше мнение помогает улучшить сервис.''',
        'comment_too_short': '⚠️ Комментарий должен содержать минимум 10 символов',

        # Landlords section
        'landlords_menu': '🏠 Раздел для арендодателей',
        'btn_conditions': '📄 Условия',
        'btn_connect': '🔗 Подключиться к платформе',
        'conditions_text': '''📄 Условия сотрудничества:

• Комиссия платформы: 5% от суммы аренды
• Быстрое подключение
• Круглосуточная поддержка
• Проверенные арендаторы
• Гибкие настройки объявлений''',
        'connect_request_sent': '''✅ Ваша заявка успешно создана!
С вами скоро свяжутся.''',
        'enter_landlord_name': '📝 Введите ваше ФИО:',
        'enter_landlord_phone': '📱 Введите номер телефона:',
        'enter_landlord_email': '📧 Введите ваш email:\n(Он понадобится для входа в панель управления)',
        'invalid_email': '⚠️ Некорректный email\nИспользуйте формат: example@domain.com',

        # Errors
        'error_occurred': '''❌ Произошла ошибка

Не удалось загрузить данные. Проверьте интернет-соединение и попробуйте снова.''',
        'btn_retry': '🔄 Попробовать снова',
        'landlord_no_response': '''⏰ Арендодатель еще не ответил на вашу заявку

Мы отправили напоминание. Обычно арендодатели отвечают в течение 24 часов.''',
        'btn_cancel_request': 'Отменить заявку',
        'btn_contact_support': 'Связаться с поддержкой',

        # Notifications
        'notification_booking_confirmed': '''✅ Ваше бронирование подтверждено!

🏠 {apartment_title}
📍 {address}
📅 Заезд: {check_in}
📅 Выезд: {check_out}

📞 Контакт арендодателя: {landlord_phone}
👤 {landlord_name}

Приятного проживания!''',
        'notification_booking_rejected': '''❌ К сожалению, ваше бронирование отклонено.

🏠 {apartment_title}
📍 {address}
📅 Даты: {check_in} - {check_out}

Попробуйте выбрать другую квартиру или даты.''',
        'notification_booking_completed': '''✅ Бронирование завершено!

🏠 {apartment_title}
📍 {address}
📅 Даты: {check_in} - {check_out}

Спасибо, что воспользовались нашим сервисом!
Пожалуйста, оставьте отзыв о квартире.''',
        'notification_booking_cancelled': '''🚫 Бронирование отменено.

🏠 {apartment_title}
📍 {address}
📅 Даты: {check_in} - {check_out}''',
        'reminder_check_in': '''⏰ Напоминание!

Завтра у вас заселение в квартиру:
📍 {address}
📅 {date}

Свяжитесь с арендодателем для уточнения деталей.''',

        # Calendar
        'month_names': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
        'day_names': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
        'prev_month': '◀️',
        'next_month': '▶️',

        # Missing keys
        'feature_coming_soon': '🚧 Эта функция скоро будет доступна',
        'booking_kept': '✅ Бронирование сохранено',
        'rating_selected': '⭐ Вы выбрали оценку: {rating}',
        'enter_review_comment': '📝 Напишите ваш отзыв:',
        'marked_helpful': '👍 Спасибо за отзыв!',
        'marked_not_helpful': '👎 Спасибо за отзыв!',
        'kept_in_favorites': '⭐ Квартира осталась в избранном',
        'confirm_cancel_booking': '❓ Вы уверены, что хотите отменить бронирование?',

        # Landlord reply
        'landlord_reply': '💬 Ответ арендодателя:',

        # Detailed ratings
        'rate_cleanliness': '🧹 Оцените чистоту:',
        'rate_accuracy': '📝 Насколько описание соответствовало реальности?',
        'rate_communication': '💬 Оцените общение с арендодателем:',
        'rate_location': '📍 Оцените расположение:',
        'btn_skip_details': '⏭ Пропустить детали',
        'detailed_ratings': '🧹 {cleanliness} | 📝 {accuracy} | 💬 {communication} | 📍 {location}',

        # Messaging
        'enter_message': '✏️ Введите сообщение:',
        'message_sent': '✅ Сообщение отправлено',
        'no_messages': '📭 Нет сообщений',
        'new_message_notification': '''💬 Новое сообщение!

От: {sender_name}
Бронирование: {apartment_title}

{message}''',
        'messages_history': '💬 История сообщений',
        'btn_reply': '↩️ Ответить',

        # Review additional texts
        'btn_skip_comment': '⏭ Пропустить',
        'review_prompt': '📝 Пожалуйста, оставьте отзыв о квартире',
        'already_reviewed': '✅ Вы уже оставили отзыв для этого бронирования',
        'cannot_leave_review': '❌ Вы не можете оставить отзыв для этого бронирования',
        'review_submitted': '✅ Спасибо за ваш отзыв!',

        # Actions and validation
        'actions_prompt': '👇 Действия:',
        'apartment_not_found': '❌ Квартира не найдена',
        'apartment_inactive': '⚠️ Эта квартира временно недоступна',
        'booking_not_found': '❌ Бронирование не найдено',
        'free_days': 'бесплатно',
        'day_singular': 'день',
        'day_few': 'дня',
        'day_many': 'дней',
        'you_save': '💵 Вы экономите: {amount} ₸',
        'photo_not_available': '📷 Фото временно недоступно',
        'search_expired': '⚠️ Сессия поиска истекла. Пожалуйста, начните поиск заново.',
    },

    'kk': {
        # Language selection
        'choose_language': '🌐 Тілді таңдаңыз / Выберите язык:',
        'language_set': 'Тіл орнатылды: Қазақша',

        # Welcome and registration
        'welcome': '''🏠 "Аставайся" қызметіне қош келдіңіз!

Тәулік бойынша пәтер жалдау қызметі.

Мұнда сіз:
• Жалға пәтер таба аласыз
• Бағалар мен шарттарды салыстыра аласыз
• Тұрғын үйді онлайн броньдай аласыз''',
        'enter_full_name': '📝 Толық атыңызды енгізіңіз:',
        'enter_phone': '📱 Телефон нөміріңізді форматта енгізіңіз:\n+7 (XXX) XXX XX XX',
        'invalid_phone': '⚠️ Телефон нөмірі дұрыс емес\nФорматты пайдаланыңыз: +7 (XXX) XXX XX XX',
        'registration_complete': '✅ Тіркелу аяқталды!\n\nҚош келдіңіз, {name}!',
        'welcome_back': '👋 Қайта оралуыңызбен, {name}!',

        # Main menu buttons
        'btn_search': '🔍 Іздеу',
        'btn_history': '📋 Жалдау тарихы',
        'btn_favorites': '⭐ Таңдаулылар',
        'btn_language': '🌐 Тілді өзгерту',
        'btn_landlords': '🏠 Жалға берушілерге',
        'btn_clear_chat': '🗑 Чатты тазалау',
        'btn_back': '⬅️ Артқа',
        'btn_main_menu': '🏠 Басты мәзір',
        'chat_cleared': '✅ Чат тазаланды',

        # Search
        'search_title': '🔍 Пәтер іздеу',
        'select_city': '🏙 Қаланы таңдаңыз:',
        'select_district': '📍 Ауданды таңдаңыз:',
        'all_districts': '🌐 Барлық аудандар',
        'select_check_in': '📅 Кіру күнін таңдаңыз:',
        'select_check_out': '📅 Шығу күнін таңдаңыз:',
        'clear_filters': '🗑 Сүзгілерді тазалау',
        'filters_cleared': '✅ Сүзгілер тазаланды',
        'active_filters': '''📌 Белсенді сүзгілер:
━━━━━━━━━━━━━━━━━━━
🏙 Қала: {city}
📍 Аудан: {district}
📅 Кіру: {check_in}
📅 Шығу: {check_out}''',
        'active_filters_no_dates': '''📌 Белсенді сүзгілер:
━━━━━━━━━━━━━━━━━━━
🏙 Қала: {city}
📍 Аудан: {district}''',
        'available_apartments': '🏠 Қолжетімді нұсқалар ({count})',
        'no_apartments': '''🔍 Сүзгілеріңіз бойынша пәтер табылмады

Көріңіз:
• Күндер ауқымын кеңейтіңіз
• Басқа ауданды таңдаңыз
• Кейбір сүзгілерді алып тастаңыз''',
        'change_filters': '🔄 Сүзгілерді өзгерту',
        'invalid_dates': '⚠️ Шығу күні кіру күнінен кейін болуы керек\nДұрыс күндерді таңдаңыз.',

        # Apartment card
        'price_per_day': '💰 {price} ₸/тәулік',
        'price_per_month': '💰 {price} ₸/ай',
        'address': '📍 {address}',
        'rating': '⭐ {rating} ({count} пікір)',
        'no_reviews': 'Әлі пікір жоқ',
        'amenities': '🏷 Ыңғайлылықтар:',
        'btn_book': '📞 Броньдау',
        'btn_add_favorite': '⭐ Таңдаулыларға',
        'btn_remove_favorite': '🗑 Таңдаулылардан алып тастау',
        'btn_in_favorites': '⭐ Таңдаулыларда',
        'btn_read_reviews': '📝 Пікірлерді оқу',
        'btn_view_map': '🗺 Картадан көру',
        'btn_prev_apartment': '⬅️ Алдыңғы',
        'btn_next_apartment': 'Келесі ➡️',
        'added_to_favorites': '✅ Пәтер таңдаулыларға қосылды',
        'removed_from_favorites': '✅ Пәтер таңдаулылардан алынды',

        # Booking
        'share_contact': '📱 Нөмірмен бөлісу',
        'total': 'Барлығы',
        'promotion_applied': 'Акция қолданылды',
        'booking_created': '''✅ Өтініш сәтті жасалды!
Жалға берушінің жауабын күтіңіз.
Біз сізге броньдау күйі туралы хабарлаймыз.''',
        'booking_confirmed': '''✅ Броньдау расталды!

📍 Мекенжай: {address}
📅 Кіру: {check_in}
📅 Шығу: {check_out}
💰 Құны: {total_price} ₸
💳 Платформа комиссиясы: {fee} ₸ ({percent}%)
💵 Жалға берушіге төлеу: {to_landlord} ₸

ℹ️ Төлем тікелей жалға берушіге жасалады
📞 Жалға берушінің байланысы: {phone}''',
        'booking_rejected': '''❌ Өкінішке орай, жалға беруші өтінішіңізді қабылдамады.

Басқа пәтер таңдап көріңіз.''',
        'apartment_booked': '''⚠️ Өкінішке орай, бұл пәтер таңдалған күндерде броньдалған.''',
        'btn_write_landlord': '💬 Жалға берушіге жазу',
        'btn_booking_details': '📋 Броньдау мәліметтері',
        'btn_cancel_booking': '❌ Броньдауды болдырмау',
        'cancel_booking_confirm': '''❓ Броньдауды болдырмағыңыз келетініне сенімдісіз бе?

📍 Мекенжай: {address}
📅 Кезең: {check_in} - {check_out}''',
        'btn_yes_cancel': '✅ Иә, болдырмау',
        'btn_no_keep': '❌ Жоқ, қалдыру',
        'booking_cancelled': '✅ Броньдау болдырылмады',

        # History
        'history_title': '📋 Жалдау тарихы',
        'history_empty': '📋 Жалдау тарихы бос',
        'status_pending': '⏳ Растауды күтуде',
        'status_confirmed': '✅ Расталды',
        'status_completed': '✔️ Аяқталды',
        'status_rejected': '❌ Қабылданбады',
        'status_cancelled': '🚫 Болдырылмады',

        # Favorites
        'favorites_title': '⭐ Таңдаулы пәтерлер',
        'favorites_empty': '⭐ Таңдаулылар тізімі бос',
        'confirm_remove_favorite': '❓ Пәтерді таңдаулылардан алып тастау керек пе?',

        # Reviews
        'reviews_title': '📝 Пікірлер',
        'review_helpful': '👍 Пайдалы ({count})',
        'review_not_helpful': '👎 Пайдасыз ({count})',
        'leave_review': '''🏠 Сіз пәтерді жалдауды аяқтадыңыз:
{address}

Әсерлеріңізбен бөлісіңіз! Бұл басқа пайдаланушыларға көмектеседі.''',
        'btn_leave_review': '📝 Пікір қалдыру',
        'select_rating': 'Бағаңызды таңдаңыз (1-ден 5-ке дейін):',
        'enter_comment': 'Пікір жазыңыз (кемінде 10 таңба):',
        'review_saved': '''✅ Пікіріңізге рахмет!
Сіздің пікіріңіз қызметті жақсартуға көмектеседі.''',
        'comment_too_short': '⚠️ Пікір кемінде 10 таңбадан тұруы керек',

        # Landlords section
        'landlords_menu': '🏠 Жалға берушілер бөлімі',
        'btn_conditions': '📄 Шарттар',
        'btn_connect': '🔗 Платформаға қосылу',
        'conditions_text': '''📄 Ынтымақтастық шарттары:

• Платформа комиссиясы: жалдау сомасынан 5%
• Жылдам қосылу
• Тәулік бойы қолдау
• Тексерілген жалға алушылар
• Икемді хабарландыру параметрлері''',
        'connect_request_sent': '''✅ Өтінішіңіз сәтті жасалды!
Сізбен жақын арада байланысады.''',
        'enter_landlord_name': '📝 Толық атыңызды енгізіңіз:',
        'enter_landlord_phone': '📱 Телефон нөміріңізді енгізіңіз:',
        'enter_landlord_email': '📧 Email енгізіңіз:\n(Басқару панеліне кіру үшін қажет)',
        'invalid_email': '⚠️ Email дұрыс емес\nФорматты пайдаланыңыз: example@domain.com',

        # Errors
        'error_occurred': '''❌ Қате орын алды

Деректерді жүктеу мүмкін болмады. Интернет байланысын тексеріп, қайталаңыз.''',
        'btn_retry': '🔄 Қайталап көру',
        'landlord_no_response': '''⏰ Жалға беруші әлі өтінішіңізге жауап бермеді

Біз еске салу жібердік. Әдетте жалға берушілер 24 сағат ішінде жауап береді.''',
        'btn_cancel_request': 'Өтінішті болдырмау',
        'btn_contact_support': 'Қолдау қызметіне хабарласу',

        # Notifications
        'notification_booking_confirmed': '''✅ Сіздің броньдауыңыз расталды!

🏠 {apartment_title}
📍 {address}
📅 Кіру: {check_in}
📅 Шығу: {check_out}

📞 Жалға берушінің байланысы: {landlord_phone}
👤 {landlord_name}

Жағымды тұруыңызды тілейміз!''',
        'notification_booking_rejected': '''❌ Өкінішке орай, сіздің броньдауыңыз қабылданбады.

🏠 {apartment_title}
📍 {address}
📅 Күндер: {check_in} - {check_out}

Басқа пәтер немесе күндерді таңдап көріңіз.''',
        'notification_booking_completed': '''✅ Броньдау аяқталды!

🏠 {apartment_title}
📍 {address}
📅 Күндер: {check_in} - {check_out}

Біздің қызметті пайдаланғаныңызға рахмет!
Пәтер туралы пікір қалдырыңыз.''',
        'notification_booking_cancelled': '''🚫 Броньдау болдырылмады.

🏠 {apartment_title}
📍 {address}
📅 Күндер: {check_in} - {check_out}''',
        'reminder_check_in': '''⏰ Еске салу!

Ертең сіздің пәтерге кіруіңіз:
📍 {address}
📅 {date}

Мәліметтерді нақтылау үшін жалға берушімен байланысыңыз.''',

        # Calendar
        'month_names': ['Қаңтар', 'Ақпан', 'Наурыз', 'Сәуір', 'Мамыр', 'Маусым',
                       'Шілде', 'Тамыз', 'Қыркүйек', 'Қазан', 'Қараша', 'Желтоқсан'],
        'day_names': ['Дс', 'Сс', 'Ср', 'Бс', 'Жм', 'Сб', 'Жс'],
        'prev_month': '◀️',
        'next_month': '▶️',

        # Missing keys
        'feature_coming_soon': '🚧 Бұл функция жақында қолжетімді болады',
        'booking_kept': '✅ Броньдау сақталды',
        'rating_selected': '⭐ Сіз бағаны таңдадыңыз: {rating}',
        'enter_review_comment': '📝 Пікіріңізді жазыңыз:',
        'marked_helpful': '👍 Пікіріңізге рахмет!',
        'marked_not_helpful': '👎 Пікіріңізге рахмет!',
        'kept_in_favorites': '⭐ Пәтер таңдаулыларда қалды',
        'confirm_cancel_booking': '❓ Броньдауды болдырмағыңыз келетініне сенімдісіз бе?',

        # Landlord reply
        'landlord_reply': '💬 Жалға берушінің жауабы:',

        # Detailed ratings
        'rate_cleanliness': '🧹 Тазалықты бағалаңыз:',
        'rate_accuracy': '📝 Сипаттама шындыққа қаншалықты сәйкес келді?',
        'rate_communication': '💬 Жалға берушімен қарым-қатынасты бағалаңыз:',
        'rate_location': '📍 Орналасуды бағалаңыз:',
        'btn_skip_details': '⏭ Мәліметтерді өткізіп жіберу',
        'detailed_ratings': '🧹 {cleanliness} | 📝 {accuracy} | 💬 {communication} | 📍 {location}',

        # Messaging
        'enter_message': '✏️ Хабарламаңызды жазыңыз:',
        'message_sent': '✅ Хабарлама жіберілді',
        'no_messages': '📭 Хабарламалар жоқ',
        'new_message_notification': '''💬 Жаңа хабарлама!

Кімнен: {sender_name}
Броньдау: {apartment_title}

{message}''',
        'messages_history': '💬 Хабарламалар тарихы',
        'btn_reply': '↩️ Жауап беру',

        # Review additional texts
        'btn_skip_comment': '⏭ Өткізіп жіберу',
        'review_prompt': '📝 Пәтер туралы пікір қалдырыңыз',
        'already_reviewed': '✅ Сіз бұл броньдау үшін пікір қалдырдыңыз',
        'cannot_leave_review': '❌ Сіз бұл броньдау үшін пікір қалдыра алмайсыз',
        'review_submitted': '✅ Пікіріңізге рахмет!',

        # Actions and validation
        'actions_prompt': '👇 Әрекеттер:',
        'apartment_not_found': '❌ Пәтер табылмады',
        'apartment_inactive': '⚠️ Бұл пәтер уақытша қолжетімсіз',
        'booking_not_found': '❌ Броньдау табылмады',
        'free_days': 'тегін',
        'day_singular': 'күн',
        'day_few': 'күн',
        'day_many': 'күн',
        'you_save': '💵 Сіз үнемдейсіз: {amount} ₸',
        'photo_not_available': '📷 Фото уақытша қолжетімсіз',
        'search_expired': '⚠️ Іздеу сессиясының мерзімі аяқталды. Қайтадан іздеуді бастаңыз.',
    }
}

def get_text(key: str, lang: str = 'ru', **kwargs) -> str:
    """Get localized text by key"""
    text = MESSAGES.get(lang, MESSAGES['ru']).get(key, MESSAGES['ru'].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text
