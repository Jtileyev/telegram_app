<?php
require_once 'config.php';
requireLogin();

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_POST['photo_id'])) {
    echo json_encode(['success' => false, 'error' => 'Invalid request']);
    exit;
}

$photo_id = $_POST['photo_id'];
$db = getDB();

// Get photo info
$stmt = $db->prepare("SELECT * FROM apartment_photos WHERE id = ?");
$stmt->execute([$photo_id]);
$photo = $stmt->fetch();

if (!$photo) {
    echo json_encode(['success' => false, 'error' => 'Photo not found']);
    exit;
}

// Check if user has permission (admin or owner)
if (!isAdmin()) {
    $stmt = $db->prepare("SELECT landlord_id FROM apartments WHERE id = ?");
    $stmt->execute([$photo['apartment_id']]);
    $apartment = $stmt->fetch();

    if (!$apartment || $apartment['landlord_id'] != getUserId()) {
        echo json_encode(['success' => false, 'error' => 'Access denied']);
        exit;
    }
}

// Delete file from disk
$fullPath = '../' . $photo['photo_path'];
if (file_exists($fullPath)) {
    unlink($fullPath);
}

// Delete from database
$stmt = $db->prepare("DELETE FROM apartment_photos WHERE id = ?");
$stmt->execute([$photo_id]);

// If this was the main photo, set another photo as main
if ($photo['is_main']) {
    $stmt = $db->prepare("SELECT id FROM apartment_photos WHERE apartment_id = ? ORDER BY sort_order LIMIT 1");
    $stmt->execute([$photo['apartment_id']]);
    $newMain = $stmt->fetch();

    if ($newMain) {
        $stmt = $db->prepare("UPDATE apartment_photos SET is_main = 1 WHERE id = ?");
        $stmt->execute([$newMain['id']]);
    }
}

echo json_encode(['success' => true]);
