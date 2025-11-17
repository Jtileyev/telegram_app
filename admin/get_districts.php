<?php
require_once 'config.php';
requireLogin();

header('Content-Type: application/json');

if (!isset($_GET['city_id']) || !is_numeric($_GET['city_id'])) {
    echo json_encode([]);
    exit;
}

$db = getDB();
$stmt = $db->prepare("SELECT id, name_ru FROM districts WHERE city_id = ? ORDER BY name_ru");
$stmt->execute([$_GET['city_id']]);
$districts = $stmt->fetchAll();

echo json_encode($districts);
