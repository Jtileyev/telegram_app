<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Арендодатели';
$pageActions = '<a href="landlord_edit.php" class="btn btn-primary"><i class="bi bi-plus-circle me-1"></i>Добавить</a>';

$db = getDB();

// Handle delete/activate
if (isset($_GET['toggle']) && is_numeric($_GET['toggle'])) {
    $stmt = $db->prepare("UPDATE landlords SET is_active = NOT is_active WHERE id = ?");
    $stmt->execute([$_GET['toggle']]);
    setFlash('success', 'Статус обновлен');
    header('Location: landlords.php');
    exit;
}

$stmt = $db->query("
    SELECT l.*,
           (SELECT COUNT(*) FROM apartments WHERE landlord_id = l.id) as apartments_count,
           (SELECT COUNT(*) FROM bookings WHERE landlord_id = l.id) as bookings_count
    FROM landlords l
    ORDER BY l.created_at DESC
");
$landlords = $stmt->fetchAll();

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <?php if (empty($landlords)): ?>
        <p class="text-muted">Нет арендодателей</p>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>ФИО</th>
                        <th>Телефон</th>
                        <th>Email</th>
                        <th>Telegram ID</th>
                        <th>Квартир</th>
                        <th>Бронирований</th>
                        <th>Статус</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($landlords as $landlord): ?>
                    <tr>
                        <td>#<?= $landlord['id'] ?></td>
                        <td><strong><?= sanitize($landlord['full_name']) ?></strong></td>
                        <td><?= $landlord['phone'] ?></td>
                        <td><?= $landlord['email'] ?: '-' ?></td>
                        <td><?= $landlord['telegram_id'] ?: '-' ?></td>
                        <td><span class="badge bg-info"><?= $landlord['apartments_count'] ?></span></td>
                        <td><span class="badge bg-primary"><?= $landlord['bookings_count'] ?></span></td>
                        <td>
                            <?php if ($landlord['is_active']): ?>
                            <span class="badge bg-success">Активен</span>
                            <?php else: ?>
                            <span class="badge bg-secondary">Неактивен</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <a href="landlord_edit.php?id=<?= $landlord['id'] ?>"
                                   class="btn btn-outline-primary" title="Редактировать">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <a href="?toggle=<?= $landlord['id'] ?>"
                                   class="btn btn-outline-warning" title="Переключить статус">
                                    <i class="bi bi-toggle-on"></i>
                                </a>
                            </div>
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
