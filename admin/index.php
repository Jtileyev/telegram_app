<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Дашборд';

$db = getDB();

// Get statistics
$stats = [];

// Total users
$stmt = $db->query("SELECT COUNT(*) as count FROM users");
$stats['users'] = $stmt->fetch()['count'];

// Total apartments
$stmt = $db->query("SELECT COUNT(*) as count FROM apartments WHERE is_active = 1");
$stats['apartments'] = $stmt->fetch()['count'];

// Total bookings
$stmt = $db->query("SELECT COUNT(*) as count FROM bookings");
$stats['bookings'] = $stmt->fetch()['count'];

// Pending bookings
$stmt = $db->query("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'");
$stats['pending'] = $stmt->fetch()['count'];

// Total revenue (platform fees) - check if we should exclude admin landlords
$chargeAdmins = '0';
$stmt = $db->prepare("SELECT value FROM settings WHERE key = 'charge_fee_for_admins'");
$stmt->execute();
$row = $stmt->fetch();
if ($row) {
    $chargeAdmins = $row['value'];
}

if ($chargeAdmins === '0') {
    // Exclude bookings where landlord is admin
    $stmt = $db->query("
        SELECT COALESCE(SUM(b.platform_fee), 0) as total 
        FROM bookings b
        JOIN users u ON b.landlord_id = u.id
        WHERE b.status = 'completed' 
        AND u.roles NOT LIKE '%admin%'
    ");
} else {
    // Include all bookings
    $stmt = $db->query("SELECT COALESCE(SUM(platform_fee), 0) as total FROM bookings WHERE status = 'completed'");
}
$stats['revenue'] = $stmt->fetch()['total'];

// Total landlords (users with landlord role)
$stmt = $db->query("SELECT COUNT(*) as count FROM users WHERE is_active = 1 AND roles LIKE '%landlord%'");
$stats['landlords'] = $stmt->fetch()['count'];

// Pending requests
$stmt = $db->query("SELECT COUNT(*) as count FROM landlord_requests WHERE status = 'pending'");
$stats['requests'] = $stmt->fetch()['count'];

// Recent bookings
$stmt = $db->query("
    SELECT b.*, u.full_name as user_name, a.title_ru as apartment_title, a.address
    FROM bookings b
    JOIN users u ON b.user_id = u.id
    JOIN apartments a ON b.apartment_id = a.id
    ORDER BY b.created_at DESC
    LIMIT 10
");
$recentBookings = $stmt->fetchAll();

// Recent users
$stmt = $db->query("
    SELECT * FROM users ORDER BY created_at DESC LIMIT 5
");
$recentUsers = $stmt->fetchAll();

include 'header.php';
?>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card stat-card bg-primary text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Пользователи</h6>
                        <h2 class="mb-0"><?= $stats['users'] ?></h2>
                    </div>
                    <i class="bi bi-people fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card bg-success text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Квартиры</h6>
                        <h2 class="mb-0"><?= $stats['apartments'] ?></h2>
                    </div>
                    <i class="bi bi-house fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card bg-info text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Бронирования</h6>
                        <h2 class="mb-0"><?= $stats['bookings'] ?></h2>
                    </div>
                    <i class="bi bi-calendar-check fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card bg-warning text-dark">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Ожидают</h6>
                        <h2 class="mb-0"><?= $stats['pending'] ?></h2>
                    </div>
                    <i class="bi bi-clock fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-4">
        <div class="card stat-card bg-dark text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Доход платформы</h6>
                        <h2 class="mb-0"><?= formatPrice($stats['revenue']) ?></h2>
                    </div>
                    <i class="bi bi-cash-coin fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card bg-secondary text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Арендодатели</h6>
                        <h2 class="mb-0"><?= $stats['landlords'] ?></h2>
                    </div>
                    <i class="bi bi-person-badge fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card bg-danger text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Новые заявки</h6>
                        <h2 class="mb-0"><?= $stats['requests'] ?></h2>
                    </div>
                    <i class="bi bi-envelope-exclamation fs-1 opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Последние бронирования</h5>
            </div>
            <div class="card-body">
                <?php if (empty($recentBookings)): ?>
                <p class="text-muted">Нет бронирований</p>
                <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Пользователь</th>
                                <th>Квартира</th>
                                <th>Даты</th>
                                <th>Сумма</th>
                                <th>Статус</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recentBookings as $booking): ?>
                            <tr>
                                <td>#<?= $booking['id'] ?></td>
                                <td><?= sanitize($booking['user_name']) ?></td>
                                <td><?= sanitize($booking['apartment_title']) ?></td>
                                <td>
                                    <?= formatDate($booking['check_in_date']) ?> -<br>
                                    <?= formatDate($booking['check_out_date']) ?>
                                </td>
                                <td><?= formatPrice($booking['total_price']) ?></td>
                                <td>
                                    <?php
                                    $statusClasses = [
                                        'pending' => 'warning',
                                        'confirmed' => 'success',
                                        'completed' => 'info',
                                        'rejected' => 'danger',
                                        'cancelled' => 'secondary'
                                    ];
                                    $statusLabels = [
                                        'pending' => 'Ожидает',
                                        'confirmed' => 'Подтверждено',
                                        'completed' => 'Завершено',
                                        'rejected' => 'Отклонено',
                                        'cancelled' => 'Отменено'
                                    ];
                                    ?>
                                    <span class="badge bg-<?= $statusClasses[$booking['status']] ?>">
                                        <?= $statusLabels[$booking['status']] ?>
                                    </span>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Новые пользователи</h5>
            </div>
            <div class="card-body">
                <?php if (empty($recentUsers)): ?>
                <p class="text-muted">Нет пользователей</p>
                <?php else: ?>
                <ul class="list-group list-group-flush">
                    <?php foreach ($recentUsers as $user): ?>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <strong><?= sanitize($user['full_name'] ?: 'Без имени') ?></strong>
                            <br>
                            <small class="text-muted"><?= $user['phone'] ?: 'Нет телефона' ?></small>
                        </div>
                        <small class="text-muted">
                            <?= date('d.m.Y H:i', strtotime($user['created_at'])) ?>
                        </small>
                    </li>
                    <?php endforeach; ?>
                </ul>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
