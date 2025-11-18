<?php
require_once 'config.php';
requireAdmin();

$db = getDB();

// Create amenities table
$db->exec("
CREATE TABLE IF NOT EXISTS amenities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ru TEXT NOT NULL,
    name_kk TEXT NOT NULL,
    icon TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
");

// Insert default amenities
$defaultAmenities = [
    ['Wi-Fi', 'Wi-Fi', '📶', 1],
    ['Кондиционер', 'Кондиционер', '❄️', 2],
    ['Стиральная машина', 'Кір жуғыш машина', '🧺', 3],
    ['Холодильник', 'Тоңазытқыш', '🧊', 4],
    ['Телевизор', 'Теледидар', '📺', 5],
    ['Парковка', 'Паркинг', '🅿️', 6],
    ['Балкон', 'Балкон', '🏢', 7],
    ['Близость к центру', 'Орталыққа жақын', '📍', 8]
];

$stmt = $db->prepare("INSERT INTO amenities (name_ru, name_kk, icon, sort_order) VALUES (?, ?, ?, ?)");

foreach ($defaultAmenities as $amenity) {
    try {
        $stmt->execute($amenity);
    } catch (Exception $e) {
        // Skip if already exists
    }
}

echo "Amenities table created and populated successfully!";
header('Location: amenities.php');
exit;
