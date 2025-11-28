-- Migration 002: Add promotions support
-- Note: This migration assumes promotions table already exists from schema.sql
-- It adds any missing columns or indexes

-- Add promotion tracking columns to bookings if not exist
-- SQLite doesn't support IF NOT EXISTS for columns, so we use a safe approach

-- Create user_promotion_progress table if not exists
CREATE TABLE IF NOT EXISTS user_promotion_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    apartment_id INTEGER NOT NULL,
    promotion_id INTEGER NOT NULL,
    bookings_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (apartment_id) REFERENCES apartments(id),
    FOREIGN KEY (promotion_id) REFERENCES promotions(id),
    UNIQUE(user_id, apartment_id, promotion_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_user 
ON user_promotion_progress(user_id);

CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_apartment 
ON user_promotion_progress(apartment_id);
