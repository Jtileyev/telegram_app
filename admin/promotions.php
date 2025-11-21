<?php
require_once 'config.php';
requireAdmin(); // Only admins can manage promotions

$pageTitle = 'Акции';

$db = getDB();

// Handle delete
if (isset($_GET['delete']) && is_numeric($_GET['delete'])) {
    $stmt = $db->prepare("DELETE FROM promotions WHERE id = ?");
    $stmt->execute([$_GET['delete']]);
    setFlash('success', 'Акция удалена');
    header('Location: promotions.php');
    exit;
}

// Handle toggle active
if (isset($_GET['toggle']) && is_numeric($_GET['toggle'])) {
    $stmt = $db->prepare("UPDATE promotions SET is_active = NOT is_active, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
    $stmt->execute([$_GET['toggle']]);
    setFlash('success', 'Статус акции изменен');
    header('Location: promotions.php');
    exit;
}

// Get all promotions
$promotions = $db->query("SELECT * FROM promotions ORDER BY created_at DESC")->fetchAll();

// Get usage statistics for each promotion
$promotion_stats = [];
foreach ($promotions as $promotion) {
    $stmt = $db->prepare("
        SELECT COUNT(*) as apartment_count
        FROM apartments
        WHERE promotion_id = ?
    ");
    $stmt->execute([$promotion['id']]);
    $apartment_count = $stmt->fetch()['apartment_count'];

    $stmt = $db->prepare("
        SELECT COUNT(*) as bookings_with_discount
        FROM bookings
        WHERE promotion_id = ? AND promotion_discount_days > 0
    ");
    $stmt->execute([$promotion['id']]);
    $bookings_with_discount = $stmt->fetch()['bookings_with_discount'];

    $promotion_stats[$promotion['id']] = [
        'apartment_count' => $apartment_count,
        'bookings_with_discount' => $bookings_with_discount
    ];
}

include 'header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <h1><i class="bi bi-gift me-2"></i><?= $pageTitle ?></h1>
    <a href="promotion_edit.php" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i>Добавить акцию
    </a>
</div>

<?php
$flash = getFlash();
if ($flash):
?>
<div class="alert alert-<?= $flash['type'] ?> alert-dismissible fade show" role="alert">
    <?= $flash['message'] ?>
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
<?php endif; ?>

<div class="card">
    <div class="card-body">
        <?php if (empty($promotions)): ?>
        <div class="text-center py-5">
            <i class="bi bi-gift" style="font-size: 4rem; color: #ccc;"></i>
            <p class="text-muted mt-3">Нет акций. Создайте первую акцию для программы лояльности.</p>
            <a href="promotion_edit.php" class="btn btn-primary mt-2">
                <i class="bi bi-plus-circle me-1"></i>Создать акцию
            </a>
        </div>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th style="width: 50px;">ID</th>
                        <th>Название</th>
                        <th>Описание</th>
                        <th style="width: 120px;">Условие</th>
                        <th style="width: 120px;">Бонус</th>
                        <th style="width: 100px;">Квартир</th>
                        <th style="width: 100px;">Применено</th>
                        <th style="width: 100px;">Статус</th>
                        <th style="width: 150px;">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($promotions as $promo): ?>
                    <?php $stats = $promotion_stats[$promo['id']]; ?>
                    <tr>
                        <td>#<?= $promo['id'] ?></td>
                        <td>
                            <strong><?= sanitize($promo['name']) ?></strong>
                        </td>
                        <td>
                            <small class="text-muted"><?= sanitize($promo['description']) ?: '-' ?></small>
                        </td>
                        <td>
                            <span class="badge bg-info"><?= $promo['bookings_required'] ?>-е заселение</span>
                        </td>
                        <td>
                            <span class="badge bg-success"><?= $promo['free_days'] ?> бесплатных дней</span>
                        </td>
                        <td>
                            <span class="badge bg-secondary"><?= $stats['apartment_count'] ?></span>
                        </td>
                        <td>
                            <span class="badge bg-primary"><?= $stats['bookings_with_discount'] ?></span>
                        </td>
                        <td>
                            <?php if ($promo['is_active']): ?>
                            <span class="badge bg-success">Активна</span>
                            <?php else: ?>
                            <span class="badge bg-secondary">Неактивна</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <a href="promotion_edit.php?id=<?= $promo['id'] ?>" class="btn btn-outline-primary" title="Редактировать">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <a href="?toggle=<?= $promo['id'] ?>" class="btn btn-outline-warning" title="Переключить статус">
                                    <i class="bi bi-toggle-<?= $promo['is_active'] ? 'on' : 'off' ?>"></i>
                                </a>
                                <?php if ($stats['apartment_count'] == 0): ?>
                                <a href="?delete=<?= $promo['id'] ?>" class="btn btn-outline-danger"
                                   onclick="return confirm('Удалить эту акцию?')" title="Удалить">
                                    <i class="bi bi-trash"></i>
                                </a>
                                <?php else: ?>
                                <button class="btn btn-outline-danger" disabled title="Нельзя удалить: используется в квартирах">
                                    <i class="bi bi-trash"></i>
                                </button>
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

<div class="card mt-4">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-info-circle me-2"></i>Как работают акции</h5>
    </div>
    <div class="card-body">
        <ol>
            <li><strong>Создайте акцию</strong> — укажите название, описание, количество заселений и бонус.</li>
            <li><strong>Привяжите к квартире</strong> — в карточке квартиры выберите нужную акцию из списка.</li>
            <li><strong>Система автоматически учитывает</strong> — сколько раз пользователь снимал эту квартиру.</li>
            <li><strong>При N-ом заселении</strong> — бонус применяется автоматически (бесплатные дни).</li>
            <li><strong>После бонуса</strong> — цикл обнуляется, и начинается новый отсчёт.</li>
        </ol>
        <div class="alert alert-info mb-0 mt-3">
            <i class="bi bi-lightbulb me-2"></i>
            <strong>Пример:</strong> Акция "6+1" означает, что на 6-ом заселении пользователь получает 1 бесплатный день.
            Если бронирование на 10 дней, он заплатит за 9.
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
