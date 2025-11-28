#!/usr/bin/env python3
"""
CLI script to notify landlord about request approval
Usage: python3 notify_landlord.py <telegram_id> <name>
"""
import sys
import os

# Add bot directory to path
sys.path.insert(0, os.path.dirname(__file__))

from notifications import notify_landlord_approved
from config import get_bot_token  # Fixed: use get_bot_token() function instead of BOT_TOKEN


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: notify_landlord.py <telegram_id> <name>")
        sys.exit(1)

    telegram_id = int(sys.argv[1])
    name = sys.argv[2]

    try:
        bot_token = get_bot_token()  # Fixed: call the function to get token
        notify_landlord_approved(telegram_id, name, bot_token)
        print(f"Notification sent to {name} (TG ID: {telegram_id})")
    except Exception as e:
        print(f"Error sending notification: {e}")
        sys.exit(1)
