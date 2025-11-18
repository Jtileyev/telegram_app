-- Migration: Add Promotions System
-- This migration adds support for promotional offers with loyalty program

-- 1. Create promotions table
CREATE TABLE IF NOT EXISTS promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    bookings_required INTEGER NOT NULL, -- Number of bookings required to get bonus (N)
    free_days INTEGER NOT NULL, -- Number of free days given as bonus (X)
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create user_promotion_progress table to track user's progress per apartment
CREATE TABLE IF NOT EXISTS user_promotion_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    apartment_id INTEGER NOT NULL,
    promotion_id INTEGER NOT NULL,
    completed_bookings INTEGER DEFAULT 0, -- Number of completed bookings in current cycle
    cycle_number INTEGER DEFAULT 1, -- Which cycle the user is on (resets after each bonus)
    last_booking_id INTEGER, -- Last completed booking
    bonus_applied_at TIMESTAMP, -- When the last bonus was applied
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (apartment_id) REFERENCES apartments(id) ON DELETE CASCADE,
    FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE CASCADE,
    FOREIGN KEY (last_booking_id) REFERENCES bookings(id),
    UNIQUE(user_id, apartment_id, promotion_id)
);

-- 3. Add promotion_id to apartments table (replace old promotion text field)
-- First, we'll rename the old column and create a new one
ALTER TABLE apartments RENAME COLUMN promotion TO promotion_text_old;
ALTER TABLE apartments ADD COLUMN promotion_id INTEGER REFERENCES promotions(id) ON DELETE SET NULL;

-- 4. Add promotion fields to bookings table to track bonus application
ALTER TABLE bookings ADD COLUMN promotion_id INTEGER REFERENCES promotions(id);
ALTER TABLE bookings ADD COLUMN promotion_discount_days INTEGER DEFAULT 0; -- Number of free days applied
ALTER TABLE bookings ADD COLUMN original_price REAL; -- Original price before promotion discount

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_promotions_active ON promotions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_user ON user_promotion_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_apartment ON user_promotion_progress(apartment_id);
CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_user_apartment ON user_promotion_progress(user_id, apartment_id);
CREATE INDEX IF NOT EXISTS idx_apartments_promotion ON apartments(promotion_id);
CREATE INDEX IF NOT EXISTS idx_bookings_promotion ON bookings(promotion_id);

-- 6. Insert some example promotions (optional - can be removed in production)
INSERT INTO promotions (name, description, bookings_required, free_days, is_active) VALUES
    ('Акция "6+1"', 'Каждое 6-е заселение - 1 бесплатный день', 6, 1, 1),
    ('Акция "3+2"', 'Каждое 3-е заселение - 2 бесплатных дня', 3, 2, 0),
    ('Акция "10+3"', 'Каждое 10-е заселение - 3 бесплатных дня', 10, 3, 1);
