<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Бронирования';

$db = getDB();

// Handle status update
if (isset($_POST['update_status'])) {
    $booking_id = $_POST['booking_id'];
    $status = $_POST['status'];
    $stmt = $db->prepare("UPDATE bookings SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
    $stmt->execute([$status, $booking_id]);
    setFlash('success', 'Статус обновлен');
    header('Location: bookings.php');
    exit;
}

// Filter by status
$statusFilter = $_GET['status'] ?? 'all';

$query = "
    SELECT b.*, u.full_name as user_name, u.phone as user_phone, u.telegram_id as user_telegram,
           a.title_ru as apartment_title, a.address,
           l.full_name as landlord_name, l.phone as landlord_phone
    FROM bookings b
    JOIN users u ON b.user_id = u.id
    JOIN apartments a ON b.apartment_id = a.id
    JOIN landlords l ON b.landlord_id = l.id
    WHERE 1=1
";

// Filter by landlord if not admin
if (isLandlord()) {
    $query .= " AND b.landlord_id = ?";
    $params = [getLandlordId()];

    if ($statusFilter !== 'all') {
        $query .= " AND b.status = ?";
        $params[] = $statusFilter;
    }

    $stmt = $db->prepare($query . " ORDER BY b.created_at DESC");
    $stmt->execute($params);
} else {
    if ($statusFilter !== 'all') {
        $query .= " AND b.status = ?";
        $stmt = $db->prepare($query . " ORDER BY b.created_at DESC");
        $stmt->execute([$statusFilter]);
    } else {
        $stmt = $db->query($query . " ORDER BY b.created_at DESC");
    }
}

$bookings = $stmt->fetchAll();

include 'header.php';
?>

<div class="mb-3">
    <div class="btn-group">
        <a href="?status=all" class="btn <?= $statusFilter === 'all' ? 'btn-primary' : 'btn-outline-primary' ?>">Все</a>
        <a href="?status=pending" class="btn <?= $statusFilter === 'pending' ? 'btn-warning' : 'btn-outline-warning' ?>">Ожидают</a>
        <a href="?status=confirmed" class="btn <?= $statusFilter === 'confirmed' ? 'btn-success' : 'btn-outline-success' ?>">Подтверждены</a>
        <a href="?status=completed" class="btn <?= $statusFilter === 'completed' ? 'btn-info' : 'btn-outline-info' ?>">Завершены</a>
        <a href="?status=rejected" class="btn <?= $statusFilter === 'rejected' ? 'btn-danger' : 'btn-outline-danger' ?>">Отклонены</a>
        <a href="?status=cancelled" class="btn <?= $statusFilter === 'cancelled' ? 'btn-secondary' : 'btn-outline-secondary' ?>">Отменены</a>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <?php if (empty($bookings)): ?>
        <p class="text-muted">Нет бронирований</p>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Пользователь</th>
                        <th>Квартира</th>
                        <th>Арендодатель</th>
                        <th>Даты</th>
                        <th>Сумма</th>
                        <th>Комиссия</th>
                        <th>Статус</th>
                        <th>Создано</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($bookings as $booking): ?>
                    <tr>
                        <td>#<?= $booking['id'] ?></td>
                        <td>
                            <strong><?= sanitize($booking['user_name']) ?></strong><br>
                            <small class="text-muted"><?= $booking['user_phone'] ?></small><br>
                            <small class="text-muted">TG: <?= $booking['user_telegram'] ?></small>
                        </td>
                        <td>
                            <?= sanitize($booking['apartment_title']) ?><br>
                            <small class="text-muted"><?= sanitize($booking['address']) ?></small>
                        </td>
                        <td>
                            <?= sanitize($booking['landlord_name']) ?><br>
                            <small class="text-muted"><?= $booking['landlord_phone'] ?></small>
                        </td>
                        <td>
                            <?= formatDate($booking['check_in_date']) ?><br>
                            <?= formatDate($booking['check_out_date']) ?>
                        </td>
                        <td><?= formatPrice($booking['total_price']) ?></td>
                        <td><?= formatPrice($booking['platform_fee']) ?></td>
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
                        <td>
                            <small><?= date('d.m.Y H:i', strtotime($booking['created_at'])) ?></small>
                        </td>
                        <td>
                            <form method="POST" class="d-inline">
                                <input type="hidden" name="booking_id" value="<?= $booking['id'] ?>">
                                <select name="status" class="form-select form-select-sm mb-1" style="width: 140px;">
                                    <option value="pending" <?= $booking['status'] === 'pending' ? 'selected' : '' ?>>Ожидает</option>
                                    <option value="confirmed" <?= $booking['status'] === 'confirmed' ? 'selected' : '' ?>>Подтверждено</option>
                                    <option value="completed" <?= $booking['status'] === 'completed' ? 'selected' : '' ?>>Завершено</option>
                                    <option value="rejected" <?= $booking['status'] === 'rejected' ? 'selected' : '' ?>>Отклонено</option>
                                    <option value="cancelled" <?= $booking['status'] === 'cancelled' ? 'selected' : '' ?>>Отменено</option>
                                </select>
                                <button type="submit" name="update_status" class="btn btn-sm btn-outline-primary">
                                    <i class="bi bi-check"></i>
                                </button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>
</div>

<?php include 'footer.php'; ?>
