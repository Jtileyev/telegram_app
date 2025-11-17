<?php
// Admin panel configuration

define('DB_PATH', __DIR__ . '/../database/rental.db');
define('UPLOADS_PATH', __DIR__ . '/../uploads/apartments/');
define('SESSION_LIFETIME', 3600); // 1 hour

// Start session
session_start();

// Check if admin is logged in
function isLoggedIn() {
    return isset($_SESSION['admin_id']) && !empty($_SESSION['admin_id']);
}

// Redirect if not logged in
function requireLogin() {
    if (!isLoggedIn()) {
        header('Location: login.php');
        exit;
    }
}

// Database connection
function getDB() {
    static $db = null;
    if ($db === null) {
        $db = new PDO('sqlite:' . DB_PATH);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    }
    return $db;
}

// Format price
function formatPrice($price) {
    return number_format($price, 0, '.', ' ') . ' ₸';
}

// Format date
function formatDate($date) {
    return date('d.m.Y', strtotime($date));
}

// Sanitize input
function sanitize($input) {
    return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
}

// Flash messages
function setFlash($type, $message) {
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

function getFlash() {
    if (isset($_SESSION['flash'])) {
        $flash = $_SESSION['flash'];
        unset($_SESSION['flash']);
        return $flash;
    }
    return null;
}
