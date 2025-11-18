<?php
/**
 * phpLiteAdmin wrapper with authentication
 */

require_once 'config.php';
requireAdmin(); // Only admins can access database management

$pageTitle = 'Управление базой данных';
include 'header.php';
?>
<div class="card">
    <div class="card-body">
        <div class="alert alert-warning mb-3">
            <i class="bi bi-exclamation-triangle me-2"></i>
            <strong>Внимание!</strong> Вы работаете напрямую с базой данных. Будьте осторожны с изменениями!
        </div>
        <iframe src="phpliteadmin.php" style="width:100%; height:800px; border:none;"></iframe>
    </div>
</div>
<?php include 'footer.php';
