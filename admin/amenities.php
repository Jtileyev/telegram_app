<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Удобства';

$db = getDB();

// Check if amenities table exists, if not create it
try {
    $db->query("SELECT COUNT(*) FROM amenities")->fetch();
} catch (Exception $e) {
    // Table doesn't exist, redirect to create it
    header('Location: create_amenities_table.php');
    exit;
}

// Handle delete
if (isset($_GET['delete']) && is_numeric($_GET['delete']) && isAdmin()) {
    $stmt = $db->prepare("DELETE FROM amenities WHERE id = ?");
    $stmt->execute([$_GET['delete']]);
    setFlash('success', 'Удобство удалено');
    header('Location: amenities.php');
    exit;
}

// Handle toggle active
if (isset($_GET['toggle']) && is_numeric($_GET['toggle']) && isAdmin()) {
    $stmt = $db->prepare("UPDATE amenities SET is_active = NOT is_active WHERE id = ?");
    $stmt->execute([$_GET['toggle']]);
    setFlash('success', 'Статус изменен');
    header('Location: amenities.php');
    exit;
}

$amenities = $db->query("SELECT * FROM amenities ORDER BY sort_order ASC, name_ru ASC")->fetchAll();

include 'header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <h1><?= $pageTitle ?></h1>
    <?php if (isAdmin()): ?>
    <a href="amenity_edit.php" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i>Добавить удобство
    </a>
    <?php endif; ?>
</div>

<div class="card">
    <div class="card-body">
        <?php if (empty($amenities)): ?>
        <p class="text-muted">Нет удобств</p>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th style="width: 50px;">ID</th>
                        <th style="width: 60px;">Иконка</th>
                        <th>Название (RU)</th>
                        <th>Название (KK)</th>
                        <th style="width: 100px;">Порядок</th>
                        <th style="width: 100px;">Статус</th>
                        <th style="width: 150px;">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($amenities as $amenity): ?>
                    <tr>
                        <td>#<?= $amenity['id'] ?></td>
                        <td style="font-size: 24px;"><?= $amenity['icon'] ?: '-' ?></td>
                        <td><?= sanitize($amenity['name_ru']) ?></td>
                        <td><?= sanitize($amenity['name_kk']) ?></td>
                        <td><?= $amenity['sort_order'] ?></td>
                        <td>
                            <?php if ($amenity['is_active']): ?>
                            <span class="badge bg-success">Активно</span>
                            <?php else: ?>
                            <span class="badge bg-secondary">Неактивно</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <?php if (isAdmin()): ?>
                                <a href="amenity_edit.php?id=<?= $amenity['id'] ?>" class="btn btn-outline-primary" title="Редактировать">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <a href="?toggle=<?= $amenity['id'] ?>" class="btn btn-outline-warning" title="Переключить статус">
                                    <i class="bi bi-toggle-<?= $amenity['is_active'] ? 'on' : 'off' ?>"></i>
                                </a>
                                <a href="?delete=<?= $amenity['id'] ?>" class="btn btn-outline-danger"
                                   onclick="return confirm('Удалить это удобство?')" title="Удалить">
                                    <i class="bi bi-trash"></i>
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
