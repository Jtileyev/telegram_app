<?php
// Admin panel configuration

// Load .env file
function loadEnv($path) {
    if (!file_exists($path)) return;
    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0) continue;
        if (strpos($line, '=') === false) continue;
        list($name, $value) = explode('=', $line, 2);
        $name = trim($name);
        $value = trim($value);
        if (!getenv($name)) {
            putenv("$name=$value");
            $_ENV[$name] = $value;
        }
    }
}
loadEnv(__DIR__ . '/../.env');

define('DB_PATH', __DIR__ . '/../database/rental.db');
define('UPLOADS_PATH', __DIR__ . '/../uploads/apartments/');
define('SESSION_LIFETIME', 31536000); // 1 year (365 days)

// Admin credentials from .env (for initial setup/reset)
define('ADMIN_EMAIL', getenv('ADMIN_EMAIL') ?: 'admin@example.com');
define('ADMIN_PASSWORD', getenv('ADMIN_PASSWORD') ?: 'change_me_on_first_login');

// Start session with 1 year lifetime (avoid duplicate starts when embedding other scripts)
if (session_status() === PHP_SESSION_NONE) {
    // Set session cookie lifetime to 1 year
    ini_set('session.gc_maxlifetime', SESSION_LIFETIME);
    ini_set('session.cookie_lifetime', SESSION_LIFETIME);
    
    session_set_cookie_params([
        'lifetime' => SESSION_LIFETIME,
        'path' => '/',
        'secure' => isset($_SERVER['HTTPS']),
        'httponly' => true,
        'samesite' => 'Lax'
    ]);
    
    session_start();
    
    // Refresh session cookie on each request to extend lifetime
    if (isset($_COOKIE[session_name()])) {
        setcookie(session_name(), session_id(), [
            'expires' => time() + SESSION_LIFETIME,
            'path' => '/',
            'secure' => isset($_SERVER['HTTPS']),
            'httponly' => true,
            'samesite' => 'Lax'
        ]);
    }
}

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

// CSRF Protection
function generateCSRFToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function validateCSRFToken($token) {
    return isset($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
}

function csrfField() {
    return '<input type="hidden" name="csrf_token" value="' . generateCSRFToken() . '">';
}

function requireCSRF() {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        if (!validateCSRFToken($_POST['csrf_token'] ?? '')) {
            setFlash('danger', 'Ошибка безопасности. Попробуйте снова.');
            header('Location: ' . $_SERVER['PHP_SELF']);
            exit;
        }
    }
}
