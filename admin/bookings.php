<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Бронирования';

$db = getDB();

// Handle status update
if (isset($_POST['update_status'])) {
    requireCSRF();
    $booking_id = $_POST['booking_id'];
    $new_status = $_POST['status'];

    try {
        // Get current booking status and details for notification
        $stmt = $db->prepare("
            SELECT b.status as old_status, b.user_id, b.check_in_date, b.check_out_date,
                   a.title_ru, a.address,
                   landlord.full_name as landlord_name, landlord.phone as landlord_phone,
                   renter.language as user_language
            FROM bookings b
            JOIN apartments a ON b.apartment_id = a.id
            JOIN users landlord ON b.landlord_id = landlord.id
            JOIN users renter ON b.user_id = renter.id
            WHERE b.id = ?
        ");
        $stmt->execute([$booking_id]);
        $booking_info = $stmt->fetch();

        if (!$booking_info) {
            setFlash('danger', 'Бронирование не найдено');
            header('Location: bookings.php');
            exit;
        }

        // Update booking status
        $stmt = $db->prepare("UPDATE bookings SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
        $stmt->execute([$new_status, $booking_id]);

        // Create notification if status changed to a notifiable status
        if ($booking_info['old_status'] !== $new_status) {
            $notifiable_statuses = ['confirmed', 'rejected', 'completed', 'cancelled'];
            if (in_array($new_status, $notifiable_statuses)) {
                $lang = $booking_info['user_language'] ?: 'ru';

                $notification_data = json_encode([
                    'status' => $new_status,
                    'apartment_title' => $booking_info['title_ru'],
                    'address' => $booking_info['address'],
                    'check_in' => formatDate($booking_info['check_in_date']),
                    'check_out' => formatDate($booking_info['check_out_date']),
                    'landlord_name' => $booking_info['landlord_name'],
                    'landlord_phone' => $booking_info['landlord_phone'],
                    'lang' => $lang
                ], JSON_UNESCAPED_UNICODE);

                $stmt = $db->prepare("
                    INSERT INTO notifications (user_id, type, message, is_sent, scheduled_at)
                    VALUES (?, ?, ?, 0, NULL)
                ");
                $stmt->execute([
                    $booking_info['user_id'],
                    'booking_status_' . $new_status,
                    $notification_data
                ]);
            }
        }

        setFlash('success', 'Статус обновлен');
    } catch (Exception $e) {
        setFlash('danger', 'Ошибка при обновлении статуса: ' . $e->getMessage());
    }

    header('Location: bookings.php');
    exit;
}

// Filter by status
$statusFilter = $_GET['status'] ?? 'all';

$query = "
    SELECT b.*, renter.full_name as user_name, renter.phone as user_phone, renter.telegram_id as user_telegram,
           a.title_ru as apartment_title, a.address, a.promotion_id as apartment_promotion_id,
           landlord.full_name as landlord_name, landlord.phone as landlord_phone,
           p.name as promotion_name, p.bookings_required, p.free_days as promotion_free_days,
           upp.completed_bookings,
           (SELECT COUNT(*) FROM bookings b2
            WHERE b2.user_id = b.user_id AND b2.apartment_id = b.apartment_id
           ) as user_apartment_bookings_count
    FROM bookings b
    JOIN users renter ON b.user_id = renter.id
    JOIN apartments a ON b.apartment_id = a.id
    JOIN users landlord ON b.landlord_id = landlord.id
    LEFT JOIN promotions p ON b.promotion_id = p.id
    LEFT JOIN user_promotion_progress upp ON upp.user_id = b.user_id AND upp.apartment_id = b.apartment_id
    WHERE 1=1
";

// Filter by landlord if not admin
if (isLandlord() && !isAdmin()) {
    $query .= " AND b.landlord_id = ?";
    $params = [getUserId()];

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
                        <th>Акция</th>
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
                            <?php if ($booking['user_apartment_bookings_count'] > 1): ?>
                            <br>
                            <span class="badge bg-primary" title="Сколько раз этот пользователь бронировал эту квартиру">
                                <i class="bi bi-arrow-repeat"></i> <?= $booking['user_apartment_bookings_count'] ?> бр.
                            </span>
                            <?php endif; ?>
                            <?php if ($booking['user_telegram']): ?>
                            <br>
                            <?php 
                            $tgLink = is_numeric($booking['user_telegram']) 
                                ? 'tg://user?id=' . $booking['user_telegram']
                                : 'https://t.me/' . $booking['user_telegram'];
                            ?>
                            <a href="<?= $tgLink ?>" 
                               target="_blank" 
                               class="btn btn-sm btn-outline-info mt-1"
                               title="Написать в Telegram">
                                <i class="bi bi-telegram"></i> Написать
                            </a>
                            <?php endif; ?>
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
                        <td>
                            <?php if ($booking['promotion_discount_days'] > 0): ?>
                            <span class="text-success"><?= formatPrice($booking['total_price']) ?></span>
                            <br><small class="text-muted">Было: <?= formatPrice($booking['original_price']) ?></small>
                            <?php else: ?>
                            <?= formatPrice($booking['total_price']) ?>
                            <?php endif; ?>
                        </td>
                        <td><?= formatPrice($booking['platform_fee']) ?></td>
                        <td>
                            <?php if ($booking['promotion_discount_days'] > 0): ?>
                            <span class="badge bg-success" title="<?= sanitize($booking['promotion_name']) ?>">
                                <i class="bi bi-gift"></i> -<?= $booking['promotion_discount_days'] ?> дн.
                            </span>
                            <?php elseif ($booking['apartment_promotion_id']): ?>
                            <small class="text-muted" title="Прогресс по акции">
                                <?= $booking['completed_bookings'] ?? 0 ?>/<?= $booking['bookings_required'] ?? 0 ?>
                            </small>
                            <?php else: ?>
                            -
                            <?php endif; ?>
                        </td>
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
                                <?= csrfField() ?>
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
