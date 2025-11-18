<?php
require_once 'config.php';
requireLogin();

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_FILES['photo'])) {
    echo json_encode(['success' => false, 'error' => 'No file uploaded']);
    exit;
}

$apartment_id = $_POST['apartment_id'] ?? null;

if (!$apartment_id) {
    echo json_encode(['success' => false, 'error' => 'Apartment ID required']);
    exit;
}

$db = getDB();

// Check if apartment exists
$stmt = $db->prepare("SELECT id FROM apartments WHERE id = ?");
$stmt->execute([$apartment_id]);
if (!$stmt->fetch()) {
    echo json_encode(['success' => false, 'error' => 'Apartment not found']);
    exit;
}

$file = $_FILES['photo'];

if ($file['error'] !== UPLOAD_ERR_OK) {
    echo json_encode(['success' => false, 'error' => 'Upload error: ' . $file['error']]);
    exit;
}

// Validate file type
$allowed = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime = finfo_file($finfo, $file['tmp_name']);
finfo_close($finfo);

if (!in_array($mime, $allowed)) {
    echo json_encode(['success' => false, 'error' => 'Invalid file type']);
    exit;
}

// Validate file size (max 5MB)
if ($file['size'] > 5 * 1024 * 1024) {
    echo json_encode(['success' => false, 'error' => 'File too large (max 5MB)']);
    exit;
}

// Generate filename
$ext = pathinfo($file['name'], PATHINFO_EXTENSION);
$filename = 'apt_' . $apartment_id . '_' . uniqid() . '.' . $ext;
$relativePath = 'uploads/apartments/' . $filename;
$fullPath = UPLOADS_PATH . $filename;

// Ensure directory exists
if (!is_dir(UPLOADS_PATH)) {
    mkdir(UPLOADS_PATH, 0755, true);
}

// Move file
if (!move_uploaded_file($file['tmp_name'], $fullPath)) {
    echo json_encode(['success' => false, 'error' => 'Failed to save file to: ' . $fullPath]);
    exit;
}

// Verify file was saved
if (!file_exists($fullPath)) {
    echo json_encode(['success' => false, 'error' => 'File was not saved: ' . $fullPath]);
    exit;
}

// Check if this is the first photo
$stmt = $db->prepare("SELECT COUNT(*) as count FROM apartment_photos WHERE apartment_id = ?");
$stmt->execute([$apartment_id]);
$count = $stmt->fetch()['count'];
$is_main = $count == 0 ? 1 : 0;

// Insert into database
$stmt = $db->prepare("INSERT INTO apartment_photos (apartment_id, photo_path, is_main, sort_order) VALUES (?, ?, ?, ?)");
$stmt->execute([$apartment_id, $relativePath, $is_main, $count]);

$photo_id = $db->lastInsertId();

echo json_encode([
    'success' => true,
    'photo_id' => $photo_id,
    'photo_url' => '../' . $relativePath,
    'is_main' => $is_main,
    'debug_full_path' => $fullPath,
    'debug_relative_path' => $relativePath
]);
