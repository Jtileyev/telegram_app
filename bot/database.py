import sqlite3
import json
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'rental.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()

    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("✓ Database schema initialized")

# User operations
def get_user(telegram_id: int):
    """Get user by telegram ID"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(telegram_id: int, username: str = None, lang: str = 'ru'):
    """Create new user"""
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (telegram_id, username, language, roles) VALUES (?, ?, ?, ?)",
        (telegram_id, username, lang, json.dumps(['user']))
    )
    conn.commit()
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return user_id

def update_user(telegram_id: int, **kwargs):
    """Update user data"""
    conn = get_connection()
    updates = ', '.join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [telegram_id]
    conn.execute(
        f"UPDATE users SET {updates}, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
        values
    )
    conn.commit()
    conn.close()

def get_user_language(telegram_id: int) -> str:
    """Get user's preferred language"""
    user = get_user(telegram_id)
    return user['language'] if user else 'ru'

# User roles management
def has_role(user_id: int, role: str) -> bool:
    """Check if user has a specific role"""
    conn = get_connection()
    cursor = conn.execute("SELECT roles FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    roles = json.loads(row['roles']) if row['roles'] else []
    return role in roles

def get_user_roles(user_id: int) -> list:
    """Get user's roles"""
    conn = get_connection()
    cursor = conn.execute("SELECT roles FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return []

    return json.loads(row['roles']) if row['roles'] else []

def add_role(user_id: int, role: str):
    """Add role to user"""
    roles = get_user_roles(user_id)
    if role not in roles:
        roles.append(role)
        conn = get_connection()
        conn.execute(
            "UPDATE users SET roles = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(roles), user_id)
        )
        conn.commit()
        conn.close()

def remove_role(user_id: int, role: str):
    """Remove role from user"""
    roles = get_user_roles(user_id)
    if role in roles:
        roles.remove(role)
        conn = get_connection()
        conn.execute(
            "UPDATE users SET roles = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(roles), user_id)
        )
        conn.commit()
        conn.close()

def get_users_by_role(role: str):
    """Get all users with specific role"""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM users WHERE is_active = 1")
    users = []
    for row in cursor.fetchall():
        user = dict(row)
        roles = json.loads(user['roles']) if user['roles'] else []
        if role in roles:
            users.append(user)
    conn.close()
    return users

# User state management
def get_user_state(user_id: int):
    """Get user's current state"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT state, data FROM user_states WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'state': row['state'],
            'data': json.loads(row['data']) if row['data'] else {}
        }
    return {'state': None, 'data': {}}

def set_user_state(user_id: int, state: str, data: dict = None):
    """Set user's current state"""
    conn = get_connection()
    data_json = json.dumps(data or {}, ensure_ascii=False)
    conn.execute("""
        INSERT INTO user_states (user_id, state, data)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            state = excluded.state,
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, state, data_json))
    conn.commit()
    conn.close()

def clear_user_state(user_id: int):
    """Clear user's state"""
    conn = get_connection()
    conn.execute("DELETE FROM user_states WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# City and district operations
def get_cities():
    """Get all cities"""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM cities ORDER BY name_ru")
    cities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cities

def get_districts(city_id: int):
    """Get districts by city"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM districts WHERE city_id = ? ORDER BY name_ru",
        (city_id,)
    )
    districts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return districts

def get_city_by_id(city_id: int):
    """Get city by ID"""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
    city = cursor.fetchone()
    conn.close()
    return dict(city) if city else None

def get_district_by_id(district_id: int):
    """Get district by ID"""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM districts WHERE id = ?", (district_id,))
    district = cursor.fetchone()
    conn.close()
    return dict(district) if district else None

# Apartment operations
def get_apartments(city_id: int = None, district_id: int = None):
    """Get available apartments with filters"""
    conn = get_connection()

    query = """
        SELECT a.*, u.phone as landlord_phone, u.full_name as landlord_name,
               c.name_ru as city_name_ru, c.name_kk as city_name_kk,
               d.name_ru as district_name_ru, d.name_kk as district_name_kk
        FROM apartments a
        JOIN users u ON a.landlord_id = u.id
        JOIN cities c ON a.city_id = c.id
        JOIN districts d ON a.district_id = d.id
        WHERE a.is_active = 1 AND u.is_active = 1
    """
    params = []

    if city_id:
        query += " AND a.city_id = ?"
        params.append(city_id)

    if district_id:
        query += " AND a.district_id = ?"
        params.append(district_id)

    query += " ORDER BY a.rating DESC, a.created_at DESC"

    cursor = conn.execute(query, params)
    apartments = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Get photos for each apartment
    for apt in apartments:
        apt['photos'] = get_apartment_photos(apt['id'])
        apt['amenities'] = json.loads(apt['amenities']) if apt['amenities'] else []

    return apartments

def get_apartment_by_id(apartment_id: int):
    """Get apartment by ID"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT a.*, u.phone as landlord_phone, u.full_name as landlord_name,
               u.telegram_id as landlord_telegram_id,
               c.name_ru as city_name_ru, c.name_kk as city_name_kk,
               d.name_ru as district_name_ru, d.name_kk as district_name_kk
        FROM apartments a
        JOIN users u ON a.landlord_id = u.id
        JOIN cities c ON a.city_id = c.id
        JOIN districts d ON a.district_id = d.id
        WHERE a.id = ?
    """, (apartment_id,))
    apt = cursor.fetchone()
    conn.close()

    if apt:
        apt = dict(apt)
        apt['photos'] = get_apartment_photos(apartment_id)
        apt['amenities'] = json.loads(apt['amenities']) if apt['amenities'] else []
    return apt

def get_apartment_photos(apartment_id: int):
    """Get photos for apartment"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT photo_path FROM apartment_photos WHERE apartment_id = ? ORDER BY is_main DESC, sort_order",
        (apartment_id,)
    )
    photos = []
    project_root = Path(__file__).parent.parent
    for row in cursor.fetchall():
        photo_path = row['photo_path']
        # Convert relative path to absolute path
        if not Path(photo_path).is_absolute():
            photo_path = str(project_root / photo_path)
        photos.append(photo_path)
    conn.close()
    return photos

# Booking operations
def create_booking(user_id: int, apartment_id: int, landlord_id: int,
                   check_in: str, check_out: str, total_price: float, platform_fee: float):
    """Create new booking"""
    conn = get_connection()
    conn.execute("""
        INSERT INTO bookings (user_id, apartment_id, landlord_id,
                             check_in_date, check_out_date, total_price, platform_fee)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, apartment_id, landlord_id, check_in, check_out, total_price, platform_fee))
    conn.commit()
    booking_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return booking_id

def get_user_bookings(user_id: int):
    """Get user's booking history"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT b.*, a.title_ru, a.title_kk, a.address, a.price_per_day,
               u.phone as landlord_phone, u.full_name as landlord_name
        FROM bookings b
        JOIN apartments a ON b.apartment_id = a.id
        JOIN users u ON b.landlord_id = u.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    """, (user_id,))
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings

def get_booking_by_id(booking_id: int):
    """Get booking by ID"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT b.*, a.title_ru, a.title_kk, a.address, a.price_per_day,
               landlord.phone as landlord_phone, landlord.full_name as landlord_name,
               landlord.telegram_id as landlord_telegram_id,
               renter.telegram_id as user_telegram_id, renter.full_name as user_name, renter.phone as user_phone
        FROM bookings b
        JOIN apartments a ON b.apartment_id = a.id
        JOIN users landlord ON b.landlord_id = landlord.id
        JOIN users renter ON b.user_id = renter.id
        WHERE b.id = ?
    """, (booking_id,))
    booking = cursor.fetchone()
    conn.close()
    return dict(booking) if booking else None

def update_booking_status(booking_id: int, status: str):
    """Update booking status"""
    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, booking_id)
    )
    conn.commit()
    conn.close()

def check_apartment_availability(apartment_id: int, check_in: str, check_out: str):
    """Check if apartment is available for given dates (only confirmed bookings block dates)"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT COUNT(*) as count FROM bookings
        WHERE apartment_id = ?
        AND status = 'confirmed'
        AND (
            (check_in_date <= ? AND check_out_date > ?)
            OR (check_in_date < ? AND check_out_date >= ?)
            OR (check_in_date >= ? AND check_out_date <= ?)
        )
    """, (apartment_id, check_out, check_in, check_out, check_in, check_in, check_out))
    count = cursor.fetchone()['count']
    conn.close()
    return count == 0

def get_booked_dates(apartment_id: int):
    """Get all booked dates for apartment (only confirmed bookings)"""
    from datetime import datetime, timedelta

    conn = get_connection()
    cursor = conn.execute("""
        SELECT check_in_date, check_out_date
        FROM bookings
        WHERE apartment_id = ? AND status = 'confirmed'
    """, (apartment_id,))

    booked_dates = set()
    for row in cursor.fetchall():
        check_in = datetime.strptime(row['check_in_date'], "%Y-%m-%d").date()
        check_out = datetime.strptime(row['check_out_date'], "%Y-%m-%d").date()

        current = check_in
        while current < check_out:
            booked_dates.add(current.isoformat())
            current += timedelta(days=1)

    conn.close()
    return list(booked_dates)

# Favorites operations
def add_to_favorites(user_id: int, apartment_id: int):
    """Add apartment to favorites"""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO favorites (user_id, apartment_id) VALUES (?, ?)",
            (user_id, apartment_id)
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def remove_from_favorites(user_id: int, apartment_id: int):
    """Remove apartment from favorites"""
    conn = get_connection()
    conn.execute(
        "DELETE FROM favorites WHERE user_id = ? AND apartment_id = ?",
        (user_id, apartment_id)
    )
    conn.commit()
    conn.close()

def get_user_favorites(user_id: int):
    """Get user's favorite apartments"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT a.*, u.phone as landlord_phone, u.full_name as landlord_name,
               c.name_ru as city_name_ru, c.name_kk as city_name_kk,
               d.name_ru as district_name_ru, d.name_kk as district_name_kk
        FROM favorites f
        JOIN apartments a ON f.apartment_id = a.id
        JOIN users u ON a.landlord_id = u.id
        JOIN cities c ON a.city_id = c.id
        JOIN districts d ON a.district_id = d.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """, (user_id,))
    apartments = [dict(row) for row in cursor.fetchall()]
    conn.close()

    for apt in apartments:
        apt['photos'] = get_apartment_photos(apt['id'])
        apt['amenities'] = json.loads(apt['amenities']) if apt['amenities'] else []

    return apartments

def is_favorite(user_id: int, apartment_id: int):
    """Check if apartment is in user's favorites"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM favorites WHERE user_id = ? AND apartment_id = ?",
        (user_id, apartment_id)
    )
    result = cursor.fetchone() is not None
    conn.close()
    return result

# Review operations
def get_apartment_reviews(apartment_id: int, limit: int = 10, offset: int = 0):
    """Get reviews for apartment"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT r.*, u.full_name as user_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.apartment_id = ? AND r.is_visible = 1
        ORDER BY r.created_at DESC
        LIMIT ? OFFSET ?
    """, (apartment_id, limit, offset))
    reviews = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reviews

def create_review(user_id: int, apartment_id: int, booking_id: int,
                  rating: int, comment: str = None, **criteria):
    """Create new review"""
    conn = get_connection()
    conn.execute("""
        INSERT INTO reviews (user_id, apartment_id, booking_id, rating, comment,
                            cleanliness_rating, accuracy_rating, communication_rating, location_rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, apartment_id, booking_id, rating, comment,
          criteria.get('cleanliness'), criteria.get('accuracy'),
          criteria.get('communication'), criteria.get('location')))
    conn.commit()

    # Update apartment rating
    cursor = conn.execute(
        "SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE apartment_id = ? AND is_visible = 1",
        (apartment_id,)
    )
    row = cursor.fetchone()
    conn.execute(
        "UPDATE apartments SET rating = ?, reviews_count = ? WHERE id = ?",
        (round(row['avg_rating'], 1), row['count'], apartment_id)
    )
    conn.commit()
    conn.close()

def can_leave_review(user_id: int, booking_id: int):
    """Check if user can leave review for booking"""
    conn = get_connection()
    # Check if booking is completed and no review exists
    cursor = conn.execute("""
        SELECT 1 FROM bookings b
        LEFT JOIN reviews r ON b.id = r.booking_id
        WHERE b.id = ? AND b.user_id = ? AND b.status = 'completed' AND r.id IS NULL
    """, (booking_id, user_id))
    result = cursor.fetchone() is not None
    conn.close()
    return result

# Landlord operations
def create_landlord_request(telegram_id: int, full_name: str, phone: str, email: str):
    """Create landlord connection request"""
    conn = get_connection()
    conn.execute(
        "INSERT INTO landlord_requests (telegram_id, full_name, phone, email) VALUES (?, ?, ?, ?)",
        (telegram_id, full_name, phone, email)
    )
    conn.commit()
    conn.close()

def get_landlord_by_telegram_id(telegram_id: int):
    """Get landlord by telegram ID (user with landlord role)"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    user = dict(user)
    roles = json.loads(user['roles']) if user['roles'] else []

    # Return user if they have landlord role
    return user if 'landlord' in roles else None

# Messages operations
def create_message(booking_id: int, sender_id: int, message: str):
    """Create new message"""
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (booking_id, sender_id, message) VALUES (?, ?, ?)",
        (booking_id, sender_id, message)
    )
    conn.commit()
    conn.close()

def get_booking_messages(booking_id: int):
    """Get all messages for booking"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM messages WHERE booking_id = ? ORDER BY created_at",
        (booking_id,)
    )
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

# Settings operations
def get_setting(key: str):
    """Get setting value"""
    conn = get_connection()
    cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else None

def set_setting(key: str, value: str):
    """Set setting value"""
    conn = get_connection()
    conn.execute(
        "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
        (value, key)
    )
    conn.commit()
    conn.close()
