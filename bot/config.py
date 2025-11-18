# Bot configuration
import os

# Telegram Bot Token (get from @BotFather)
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Database path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'rental.db')

# Uploads directory
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')

# Platform settings
PLATFORM_FEE_PERCENT = 5.0

# Reminder settings
REMINDER_HOURS_BEFORE_CHECKIN = 24
REMINDER_HOURS_AFTER_CHECKOUT = 48

# Review settings
MIN_REVIEW_LENGTH = 10
MAX_REVIEW_LENGTH = 500
REVIEW_EDIT_DAYS = 7
