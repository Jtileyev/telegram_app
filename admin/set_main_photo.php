<?php
require_once 'config.php';
requireLogin();

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_POST['photo_id']) || !isset($_POST['apartment_id'])) {
    echo json_encode(['success' => false, 'error' => 'Invalid request']);
    exit;
}

$photo_id = $_POST['photo_id'];
$apartment_id = $_POST['apartment_id'];
$db = getDB();

// Check if user has permission (admin or owner)
if (!isAdmin()) {
    $stmt = $db->prepare("SELECT landlord_id FROM apartments WHERE id = ?");
    $stmt->execute([$apartment_id]);
    $apartment = $stmt->fetch();

    if (!$apartment || $apartment['landlord_id'] != getUserId()) {
        echo json_encode(['success' => false, 'error' => 'Access denied']);
        exit;
    }
}

// Verify photo belongs to this apartment
$stmt = $db->prepare("SELECT id FROM apartment_photos WHERE id = ? AND apartment_id = ?");
$stmt->execute([$photo_id, $apartment_id]);
if (!$stmt->fetch()) {
    echo json_encode(['success' => false, 'error' => 'Photo not found']);
    exit;
}

// Remove main flag from all photos of this apartment
$stmt = $db->prepare("UPDATE apartment_photos SET is_main = 0 WHERE apartment_id = ?");
$stmt->execute([$apartment_id]);

// Set this photo as main
$stmt = $db->prepare("UPDATE apartment_photos SET is_main = 1 WHERE id = ?");
$stmt->execute([$photo_id]);

echo json_encode(['success' => true]);
