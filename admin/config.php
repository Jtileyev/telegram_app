<?php
// Admin panel configuration

define('DB_PATH', __DIR__ . '/../database/rental.db');
define('UPLOADS_PATH', __DIR__ . '/../uploads/apartments/');
define('SESSION_LIFETIME', 3600); // 1 hour

// Start session
session_start();

// Check if user is logged in
function isLoggedIn() {
    return isset($_SESSION['user_id']) && !empty($_SESSION['user_id']) && isset($_SESSION['user_roles']);
}

// Get current user roles (array)
function getUserRoles() {
    return $_SESSION['user_roles'] ?? [];
}

// Check if user has specific role
function hasRole($role) {
    $roles = getUserRoles();
    return in_array($role, $roles);
}

// Get current user ID
function getUserId() {
    return $_SESSION['user_id'] ?? null;
}

// Check if current user is admin
function isAdmin() {
    return isLoggedIn() && hasRole('admin');
}

// Check if current user is landlord
function isLandlord() {
    return isLoggedIn() && hasRole('landlord');
}

// Redirect if not logged in
function requireLogin() {
    if (!isLoggedIn()) {
        header('Location: login.php');
        exit;
    }
}

// Require admin role
function requireAdmin() {
    requireLogin();
    if (!isAdmin()) {
        header('Location: index.php');
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
