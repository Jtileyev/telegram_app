-- Astavaisya Rental Bot Database Schema (Updated)
-- Merged users, admins, and landlords into single users table with roles

-- Users table (merged from users, admins, and landlords)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    email TEXT UNIQUE,
    username TEXT,
    password TEXT,
    full_name TEXT,
    phone TEXT,
    language TEXT DEFAULT 'ru',
    roles TEXT DEFAULT '["user"]', -- JSON array: ["user"], ["admin"], ["landlord"] or combinations
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Cities table (will be populated via init script)
CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ru TEXT NOT NULL,
    name_kk TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Districts table (will be populated via init script)
CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL,
    name_ru TEXT NOT NULL,
    name_kk TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

-- Promotions table for managing promotional offers
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

-- Apartments table (landlord_id now references users table)
CREATE TABLE IF NOT EXISTS apartments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landlord_id INTEGER NOT NULL,
    city_id INTEGER NOT NULL,
    district_id INTEGER NOT NULL,
    title_ru TEXT NOT NULL,
    title_kk TEXT NOT NULL,
    description_ru TEXT,
    description_kk TEXT,
    address TEXT NOT NULL,
    price_per_day REAL NOT NULL,
    price_per_month REAL,
    gis_link TEXT,
    amenities TEXT, -- JSON array
    promotion_id INTEGER, -- Reference to promotions table
    rating REAL DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (landlord_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES cities(id),
    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE SET NULL
);

-- Apartment photos
CREATE TABLE IF NOT EXISTS apartment_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apartment_id INTEGER NOT NULL,
    photo_path TEXT NOT NULL,
    is_main BOOLEAN DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (apartment_id) REFERENCES apartments(id) ON DELETE CASCADE
);

-- Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    apartment_id INTEGER NOT NULL,
    landlord_id INTEGER NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    total_price REAL NOT NULL,
    platform_fee REAL NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, confirmed, completed, rejected, cancelled
    promotion_id INTEGER, -- Applied promotion (if any)
    promotion_discount_days INTEGER DEFAULT 0, -- Number of free days applied
    original_price REAL, -- Original price before promotion discount
    reminder_sent BOOLEAN DEFAULT 0, -- Check-in reminder sent flag
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (apartment_id) REFERENCES apartments(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id),
    FOREIGN KEY (promotion_id) REFERENCES promotions(id)
);

-- Favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    apartment_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (apartment_id) REFERENCES apartments(id) ON DELETE CASCADE,
    UNIQUE(user_id, apartment_id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    apartment_id INTEGER NOT NULL,
    booking_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    cleanliness_rating INTEGER CHECK(cleanliness_rating >= 1 AND cleanliness_rating <= 5),
    accuracy_rating INTEGER CHECK(accuracy_rating >= 1 AND accuracy_rating <= 5),
    communication_rating INTEGER CHECK(communication_rating >= 1 AND communication_rating <= 5),
    location_rating INTEGER CHECK(location_rating >= 1 AND location_rating <= 5),
    comment TEXT,
    landlord_reply TEXT,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    is_visible BOOLEAN DEFAULT 0,
    moderation_status TEXT DEFAULT 'pending', -- pending, approved, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (apartment_id) REFERENCES apartments(id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- Messages table (chat between user and landlord)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id)
);

-- Landlord requests (connection requests)
CREATE TABLE IF NOT EXISTS landlord_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, approved, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Bot settings
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Translations table
CREATE TABLE IF NOT EXISTS translations (
    key TEXT PRIMARY KEY,
    text_ru TEXT NOT NULL,
    text_kk TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Notifications queue
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    is_sent BOOLEAN DEFAULT 0,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- User states for bot conversation
CREATE TABLE IF NOT EXISTS user_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    state TEXT,
    data TEXT, -- JSON data for current state
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User promotion progress tracking
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

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_telegram ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_apartments_city ON apartments(city_id);
CREATE INDEX IF NOT EXISTS idx_apartments_district ON apartments(district_id);
CREATE INDEX IF NOT EXISTS idx_apartments_landlord ON apartments(landlord_id);
CREATE INDEX IF NOT EXISTS idx_apartments_promotion ON apartments(promotion_id);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_apartment ON bookings(apartment_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_promotion ON bookings(promotion_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_apartment ON reviews(apartment_id);
CREATE INDEX IF NOT EXISTS idx_messages_booking ON messages(booking_id);
CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key);
CREATE INDEX IF NOT EXISTS idx_promotions_active ON promotions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_user ON user_promotion_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_apartment ON user_promotion_progress(apartment_id);
CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_user_apartment ON user_promotion_progress(user_id, apartment_id);

-- Insert default system settings (only settings, no cities/districts)
INSERT OR IGNORE INTO settings (key, value, description) VALUES
('platform_fee_percent', '5', 'Platform fee percentage'),
('bot_token', '', 'Telegram bot token'),
('reminder_hours_before', '24', 'Hours before check-in to send reminder');
