<?php
require_once __DIR__ . '/config.php';
requireAdmin();

$phpLiteAdminPath = __DIR__ . '/vendor/phpliteadmin';
if (!is_dir($phpLiteAdminPath)) {
    http_response_code(500);
    echo 'Не удалось загрузить phpLiteAdmin.';
    exit;
}

// phpLiteAdmin expects to run from its own directory
chdir($phpLiteAdminPath);

// phpLiteAdmin 1.9.8.2 still calls removed get_magic_quotes_gpc() on PHP 8+
if (!function_exists('get_magic_quotes_gpc')) {
    function get_magic_quotes_gpc() {
        return false;
    }
}

// Provide mbstring polyfills so phpLiteAdmin works on environments without ext-mbstring
if (!function_exists('mb_strlen')) {
    function mb_strlen($string, $encoding = null) {
        return strlen($string);
    }
}

if (!function_exists('mb_substr')) {
    function mb_substr($string, $start, $length = null, $encoding = null) {
        return $length === null ? substr($string, $start) : substr($string, $start, $length);
    }
}

require_once $phpLiteAdminPath . '/index.php';
