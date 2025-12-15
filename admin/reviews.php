<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Отзывы';

$db = getDB();

// Handle approve review
if (isset($_GET['approve']) && is_numeric($_GET['approve'])) {
    $review_id = $_GET['approve'];
    
    // Get review and apartment info
    $stmt = $db->prepare("SELECT apartment_id FROM reviews WHERE id = ?");
    $stmt->execute([$review_id]);
    $review = $stmt->fetch();
    
    if ($review) {
        // Approve review
        $stmt = $db->prepare("UPDATE reviews SET is_visible = 1, moderation_status = 'approved', updated_at = CURRENT_TIMESTAMP WHERE id = ?");
        $stmt->execute([$review_id]);
        
        // Update apartment rating
        $stmt = $db->prepare("SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE apartment_id = ? AND is_visible = 1");
        $stmt->execute([$review['apartment_id']]);
        $row = $stmt->fetch();
        
        $stmt = $db->prepare("UPDATE apartments SET rating = ?, reviews_count = ? WHERE id = ?");
        $stmt->execute([round($row['avg_rating'], 1), $row['count'], $review['apartment_id']]);
        
        setFlash('success', 'Отзыв одобрен');
    }
    header('Location: reviews.php' . (isset($_GET['filter']) ? '?filter=' . $_GET['filter'] : ''));
    exit;
}

// Handle reject review
if (isset($_GET['reject']) && is_numeric($_GET['reject'])) {
    $review_id = $_GET['reject'];
    
    // Get review and apartment info
    $stmt = $db->prepare("SELECT apartment_id FROM reviews WHERE id = ?");
    $stmt->execute([$review_id]);
    $review = $stmt->fetch();
    
    if ($review) {
        // Reject review
        $stmt = $db->prepare("UPDATE reviews SET is_visible = 0, moderation_status = 'rejected', updated_at = CURRENT_TIMESTAMP WHERE id = ?");
        $stmt->execute([$review_id]);
        
        // Update apartment rating (recalculate without this review)
        $stmt = $db->prepare("SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE apartment_id = ? AND is_visible = 1");
        $stmt->execute([$review['apartment_id']]);
        $row = $stmt->fetch();
        
        $stmt = $db->prepare("UPDATE apartments SET rating = ?, reviews_count = ? WHERE id = ?");
        $stmt->execute([round($row['avg_rating'] ?? 0, 1), $row['count'], $review['apartment_id']]);
        
        setFlash('warning', 'Отзыв отклонён');
    }
    header('Location: reviews.php' . (isset($_GET['filter']) ? '?filter=' . $_GET['filter'] : ''));
    exit;
}

// Handle landlord reply
if (isset($_POST['save_reply'])) {
    requireCSRF();
    $review_id = $_POST['review_id'];
    $reply = trim($_POST['landlord_reply']);
    
    $stmt = $db->prepare("UPDATE reviews SET landlord_reply = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
    $stmt->execute([$reply ?: null, $review_id]);
    setFlash('success', 'Ответ сохранен');
    header('Location: reviews.php');
    exit;
}

// Filter
$filter = $_GET['filter'] ?? 'all';
$filterCondition = '';
if ($filter === 'pending') {
    $filterCondition = " AND (r.moderation_status = 'pending' OR r.moderation_status IS NULL)";
} elseif ($filter === 'approved') {
    $filterCondition = " AND r.moderation_status = 'approved'";
} elseif ($filter === 'rejected') {
    $filterCondition = " AND r.moderation_status = 'rejected'";
}

$query = "
    SELECT r.*, u.full_name as user_name, a.title_ru as apartment_title, a.address
    FROM reviews r
    JOIN users u ON r.user_id = u.id
    JOIN apartments a ON r.apartment_id = a.id
    WHERE 1=1 $filterCondition
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

// Count by status
$countQuery = "SELECT moderation_status, COUNT(*) as cnt FROM reviews GROUP BY moderation_status";
$counts = ['all' => 0, 'pending' => 0, 'approved' => 0, 'rejected' => 0];
foreach ($db->query($countQuery)->fetchAll() as $row) {
    $status = $row['moderation_status'] ?? 'pending';
    $counts[$status] = $row['cnt'];
    $counts['all'] += $row['cnt'];
}

include 'header.php';
?>

<div class="mb-4">
    <div class="btn-group" role="group">
        <a href="?filter=all" class="btn btn-<?= $filter === 'all' ? 'primary' : 'outline-primary' ?>">
            Все <span class="badge bg-secondary"><?= $counts['all'] ?></span>
        </a>
        <a href="?filter=pending" class="btn btn-<?= $filter === 'pending' ? 'warning' : 'outline-warning' ?>">
            На модерации <span class="badge bg-secondary"><?= $counts['pending'] ?></span>
        </a>
        <a href="?filter=approved" class="btn btn-<?= $filter === 'approved' ? 'success' : 'outline-success' ?>">
            Одобренные <span class="badge bg-secondary"><?= $counts['approved'] ?></span>
        </a>
        <a href="?filter=rejected" class="btn btn-<?= $filter === 'rejected' ? 'danger' : 'outline-danger' ?>">
            Отклонённые <span class="badge bg-secondary"><?= $counts['rejected'] ?></span>
        </a>
    </div>
</div>

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
                        <th>Статус</th>
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
                            <?php if ($review['landlord_reply']): ?>
                            <div class="mt-2 p-2 bg-light rounded">
                                <small class="text-primary"><i class="bi bi-reply"></i> Ваш ответ:</small><br>
                                <small><?= sanitize(mb_substr($review['landlord_reply'], 0, 80)) ?><?= mb_strlen($review['landlord_reply']) > 80 ? '...' : '' ?></small>
                            </div>
                            <?php endif; ?>
                        </td>
                        <td><?= date('d.m.Y H:i', strtotime($review['created_at'])) ?></td>
                        <td>
                            <?php
                            $status = $review['moderation_status'] ?? 'pending';
                            $statusClasses = [
                                'pending' => 'warning',
                                'approved' => 'success',
                                'rejected' => 'danger'
                            ];
                            $statusLabels = [
                                'pending' => 'На модерации',
                                'approved' => 'Одобрен',
                                'rejected' => 'Отклонён'
                            ];
                            ?>
                            <span class="badge bg-<?= $statusClasses[$status] ?? 'secondary' ?>">
                                <?= $statusLabels[$status] ?? $status ?>
                            </span>
                        </td>
                        <td>
                            <?php if ($status === 'pending'): ?>
                            <a href="?approve=<?= $review['id'] ?>&filter=<?= $filter ?>"
                               class="btn btn-sm btn-success" title="Одобрить">
                                <i class="bi bi-check-lg"></i>
                            </a>
                            <a href="?reject=<?= $review['id'] ?>&filter=<?= $filter ?>"
                               class="btn btn-sm btn-danger" title="Отклонить"
                               onclick="return confirm('Отклонить этот отзыв?')">
                                <i class="bi bi-x-lg"></i>
                            </a>
                            <?php elseif ($status === 'approved'): ?>
                            <a href="?reject=<?= $review['id'] ?>&filter=<?= $filter ?>"
                               class="btn btn-sm btn-outline-danger" title="Отклонить"
                               onclick="return confirm('Отклонить этот отзыв?')">
                                <i class="bi bi-x-lg"></i>
                            </a>
                            <?php elseif ($status === 'rejected'): ?>
                            <a href="?approve=<?= $review['id'] ?>&filter=<?= $filter ?>"
                               class="btn btn-sm btn-outline-success" title="Одобрить">
                                <i class="bi bi-check-lg"></i>
                            </a>
                            <?php endif; ?>
                            <button type="button" class="btn btn-sm btn-outline-primary"
                                    data-bs-toggle="modal" data-bs-target="#replyModal<?= $review['id'] ?>"
                                    title="Ответить">
                                <i class="bi bi-reply"></i>
                            </button>
                        </td>
                    </tr>
                    
                    <!-- Reply Modal -->
                    <div class="modal fade" id="replyModal<?= $review['id'] ?>" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <form method="POST">
                                    <?= csrfField() ?>
                                    <div class="modal-header">
                                        <h5 class="modal-title">Ответ на отзыв #<?= $review['id'] ?></h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label">Отзыв пользователя:</label>
                                            <p class="text-muted"><?= sanitize($review['comment'] ?: 'Без комментария') ?></p>
                                        </div>
                                        <input type="hidden" name="review_id" value="<?= $review['id'] ?>">
                                        <div class="mb-3">
                                            <label for="landlord_reply" class="form-label">Ваш ответ:</label>
                                            <textarea class="form-control" name="landlord_reply" rows="4"
                                                      placeholder="Введите ответ на отзыв..."><?= sanitize($review['landlord_reply'] ?? '') ?></textarea>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                                        <button type="submit" name="save_reply" class="btn btn-primary">Сохранить</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>
</div>

<?php include 'footer.php'; ?>
