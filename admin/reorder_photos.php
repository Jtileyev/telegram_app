<?php
require_once 'config.php';
requireLogin();

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Invalid method']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$apartment_id = $input['apartment_id'] ?? null;
$photo_ids = $input['photo_ids'] ?? [];

if (!$apartment_id || empty($photo_ids)) {
    echo json_encode(['success' => false, 'error' => 'Missing data']);
    exit;
}

$db = getDB();

// Verify apartment exists
$stmt = $db->prepare("SELECT id FROM apartments WHERE id = ?");
$stmt->execute([$apartment_id]);
if (!$stmt->fetch()) {
    echo json_encode(['success' => false, 'error' => 'Apartment not found']);
    exit;
}

// Update sort_order for each photo
try {
    $db->beginTransaction();
    
    $stmt = $db->prepare("UPDATE apartment_photos SET sort_order = ? WHERE id = ? AND apartment_id = ?");
    
    foreach ($photo_ids as $index => $photo_id) {
        $stmt->execute([$index, $photo_id, $apartment_id]);
    }
    
    $db->commit();
    echo json_encode(['success' => true]);
} catch (Exception $e) {
    $db->rollBack();
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
