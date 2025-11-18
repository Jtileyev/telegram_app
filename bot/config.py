# Bot configuration
import os
import sys
from pathlib import Path

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent))
import database as db

def get_bot_token():
    """Get bot token from database"""
    token = db.get_setting('bot_token')
    if not token:
        raise ValueError("BOT_TOKEN not found in database settings. Please add it to the settings table with key 'bot_token'")
    return token

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
