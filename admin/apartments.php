<?php
require_once 'config.php';
requireLogin();

// Show inactive apartments toggle
$showInactive = isset($_GET['show_inactive']) && $_GET['show_inactive'] === '1';

$pageTitle = 'Квартиры';
$toggleBtn = $showInactive
    ? '<a href="apartments.php" class="btn btn-outline-secondary"><i class="bi bi-eye-slash me-1"></i>Скрыть неактивные</a>'
    : '<a href="apartments.php?show_inactive=1" class="btn btn-outline-secondary"><i class="bi bi-eye me-1"></i>Показать неактивные</a>';
$pageActions = $toggleBtn . ' <a href="apartment_edit.php" class="btn btn-primary"><i class="bi bi-plus-circle me-1"></i>Добавить</a>';

$db = getDB();

// Handle delete
if (isset($_GET['delete']) && is_numeric($_GET['delete'])) {
    $stmt = $db->prepare("UPDATE apartments SET is_active = 0 WHERE id = ?");
    $stmt->execute([$_GET['delete']]);
    setFlash('success', 'Квартира деактивирована');
    $redirect = $showInactive ? 'apartments.php?show_inactive=1' : 'apartments.php';
    header('Location: ' . $redirect);
    exit;
}

// Handle activate
if (isset($_GET['activate']) && is_numeric($_GET['activate'])) {
    $stmt = $db->prepare("UPDATE apartments SET is_active = 1 WHERE id = ?");
    $stmt->execute([$_GET['activate']]);
    setFlash('success', 'Квартира активирована');
    $redirect = $showInactive ? 'apartments.php?show_inactive=1' : 'apartments.php';
    header('Location: ' . $redirect);
    exit;
}

// Get apartments
$query = "
    SELECT a.*, u.full_name as landlord_name, u.phone as landlord_phone,
           c.name_ru as city_name, d.name_ru as district_name
    FROM apartments a
    JOIN users u ON a.landlord_id = u.id
    JOIN cities c ON a.city_id = c.id
    JOIN districts d ON a.district_id = d.id
    WHERE 1=1
";

// Filter inactive apartments unless show_inactive is set
if (!$showInactive) {
    $query .= " AND a.is_active = 1";
}

// Filter by landlord if not admin
$params = [];
if (isLandlord() && !isAdmin()) {
    $query .= " AND a.landlord_id = ?";
    $params[] = getUserId();
}

$stmt = $db->prepare($query . " ORDER BY a.is_active DESC, a.created_at DESC");
$stmt->execute($params);

$apartments = $stmt->fetchAll();

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <?php if (empty($apartments)): ?>
        <p class="text-muted">Нет квартир</p>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Фото</th>
                        <th>Название</th>
                        <th>Город/Район</th>
                        <th>Цена</th>
                        <th>Рейтинг</th>
                        <th>Арендодатель</th>
                        <th>Статус</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($apartments as $apt): ?>
                    <tr>
                        <td>#<?= $apt['id'] ?></td>
                        <td>
                            <?php
                            $photoStmt = $db->prepare("SELECT photo_path FROM apartment_photos WHERE apartment_id = ? ORDER BY is_main DESC LIMIT 1");
                            $photoStmt->execute([$apt['id']]);
                            $photo = $photoStmt->fetchColumn();
                            if ($photo):
                            ?>
                            <img src="uploads/apartments/<?= basename($photo) ?>"
                                 style="width: 60px; height: 40px; object-fit: cover;"
                                 class="rounded">
                            <?php else: ?>
                            <div class="bg-light rounded d-flex align-items-center justify-content-center"
                                 style="width: 60px; height: 40px;">
                                <i class="bi bi-house text-muted"></i>
                            </div>
                            <?php endif; ?>
                        </td>
                        <td>
                            <strong><?= sanitize($apt['title_ru']) ?></strong>
                            <br>
                            <small class="text-muted"><?= sanitize($apt['address']) ?></small>
                        </td>
                        <td>
                            <?= sanitize($apt['city_name']) ?><br>
                            <small class="text-muted"><?= sanitize($apt['district_name']) ?></small>
                        </td>
                        <td><?= formatPrice($apt['price_per_day']) ?>/сутки</td>
                        <td>
                            ⭐ <?= $apt['rating'] ?>
                            <small class="text-muted">(<?= $apt['reviews_count'] ?>)</small>
                        </td>
                        <td>
                            <?= sanitize($apt['landlord_name']) ?><br>
                            <small class="text-muted"><?= $apt['landlord_phone'] ?></small>
                        </td>
                        <td>
                            <?php if ($apt['is_active']): ?>
                            <span class="badge bg-success">Активна</span>
                            <?php else: ?>
                            <span class="badge bg-secondary">Неактивна</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <a href="apartment_edit.php?id=<?= $apt['id'] ?>"
                                   class="btn btn-outline-primary" title="Редактировать">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <?php if ($apt['is_active']): ?>
                                <a href="?delete=<?= $apt['id'] ?>"
                                   class="btn btn-outline-danger"
                                   title="Деактивировать"
                                   onclick="return confirm('Деактивировать квартиру?')">
                                    <i class="bi bi-x-circle"></i>
                                </a>
                                <?php else: ?>
                                <a href="?activate=<?= $apt['id'] ?>"
                                   class="btn btn-outline-success" title="Активировать">
                                    <i class="bi bi-check-circle"></i>
                                </a>
                                <?php endif; ?>
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
