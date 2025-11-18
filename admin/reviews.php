<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Отзывы';

$db = getDB();

// Handle visibility toggle
if (isset($_GET['toggle_visibility']) && is_numeric($_GET['toggle_visibility'])) {
    $stmt = $db->prepare("UPDATE reviews SET is_visible = NOT is_visible WHERE id = ?");
    $stmt->execute([$_GET['toggle_visibility']]);
    setFlash('success', 'Видимость отзыва изменена');
    header('Location: reviews.php');
    exit;
}

$query = "
    SELECT r.*, u.full_name as user_name, a.title_ru as apartment_title, a.address
    FROM reviews r
    JOIN users u ON r.user_id = u.id
    JOIN apartments a ON r.apartment_id = a.id
    WHERE 1=1
";

// Filter by landlord if not admin
if (isLandlord() && !isAdmin()) {
    $query .= " AND a.landlord_id = ?";
    $stmt = $db->prepare($query . " ORDER BY r.created_at DESC");
    $stmt->execute([getUserId()]);
} else {
    $stmt = $db->query($query . " ORDER BY r.created_at DESC");
}

$reviews = $stmt->fetchAll();

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <?php if (empty($reviews)): ?>
        <p class="text-muted">Нет отзывов</p>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Пользователь</th>
                        <th>Квартира</th>
                        <th>Рейтинг</th>
                        <th>Комментарий</th>
                        <th>Дата</th>
                        <th>Видимость</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($reviews as $review): ?>
                    <tr>
                        <td>#<?= $review['id'] ?></td>
                        <td><?= sanitize($review['user_name']) ?></td>
                        <td>
                            <?= sanitize($review['apartment_title']) ?><br>
                            <small class="text-muted"><?= sanitize($review['address']) ?></small>
                        </td>
                        <td>
                            <span class="text-warning">
                                <?= str_repeat('⭐', $review['rating']) ?>
                            </span>
                            <?= $review['rating'] ?>.0
                        </td>
                        <td>
                            <?php if ($review['comment']): ?>
                            <div style="max-width: 300px; white-space: pre-wrap;">
                                <?= sanitize(mb_substr($review['comment'], 0, 100)) ?>
                                <?= mb_strlen($review['comment']) > 100 ? '...' : '' ?>
                            </div>
                            <?php else: ?>
                            <span class="text-muted">Без комментария</span>
                            <?php endif; ?>
                        </td>
                        <td><?= date('d.m.Y H:i', strtotime($review['created_at'])) ?></td>
                        <td>
                            <?php if ($review['is_visible']): ?>
                            <span class="badge bg-success">Виден</span>
                            <?php else: ?>
                            <span class="badge bg-danger">Скрыт</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <a href="?toggle_visibility=<?= $review['id'] ?>"
                               class="btn btn-sm btn-outline-warning" title="Переключить видимость">
                                <i class="bi bi-eye"></i>
                            </a>
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
