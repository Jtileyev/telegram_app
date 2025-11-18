<?php
/**
 * phpLiteAdmin wrapper with authentication
 */

require_once 'config.php';
requireAdmin(); // Only admins can access database management

// Configure phpLiteAdmin
$directory = __DIR__ . '/../database/';
$databases = [
    [
        'path' => 'rental.db',
        'name' => 'Rental Database'
    ]
];

// Password for phpLiteAdmin (use session-based auth)
$password = 'phpliteadmin_' . session_id();

// Subdirectory
$subdirectory = '';

// Check if we're embedding in iframe or standalone
$embed = isset($_GET['embed']) && $_GET['embed'] === '1';

if (!$embed) {
    // Standalone mode - show with admin header
    $pageTitle = 'Управление базой данных';
    include 'header.php';
    echo '<div class="card">';
    echo '<div class="card-body">';
    echo '<div class="alert alert-warning">';
    echo '<i class="bi bi-exclamation-triangle me-2"></i>';
    echo '<strong>Внимание!</strong> Вы работаете напрямую с базой данных. Будьте осторожны с изменениями!';
    echo '</div>';
    echo '<iframe src="db_admin.php?embed=1" style="width:100%; height:800px; border:none;"></iframe>';
    echo '</div>';
    echo '</div>';
    include 'footer.php';
    exit;
}

// Embedded mode - show phpLiteAdmin
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Admin</title>
    <style>
        body {
            margin: 0;
            padding: 10px;
            font-family: Arial, sans-serif;
        }
    </style>
</head>
<body>
<?php
// Set phpLiteAdmin configuration
define('PHPLITEADMIN_DIRECTORY', $directory);
define('PHPLITEADMIN_PASSWORD', md5($password));

// Include phpLiteAdmin
include 'phpliteadmin.php';
?>
</body>
</html>
