<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Арендодатели';
$pageActions = '<a href="landlord_edit.php" class="btn btn-primary"><i class="bi bi-plus-circle me-1"></i>Добавить</a>';

$db = getDB();

// Handle landlord deletion
if (isset($_POST['delete_landlord']) && is_numeric($_POST['delete_landlord'])) {
    $landlordId = $_POST['delete_landlord'];

    // Check if user exists and has landlord role
    $stmt = $db->prepare("SELECT id, roles FROM users WHERE id = ?");
    $stmt->execute([$landlordId]);
    $user = $stmt->fetch();

    if ($user) {
        $roles = json_decode($user['roles'], true);
        // Remove landlord role
        $roles = array_diff($roles, ['landlord']);

        if (empty($roles)) {
            // If no roles left, deactivate user
            $stmt = $db->prepare("UPDATE users SET is_active = 0 WHERE id = ?");
            $stmt->execute([$landlordId]);
        } else {
            // Update roles
            $stmt = $db->prepare("UPDATE users SET roles = ? WHERE id = ?");
            $stmt->execute([json_encode(array_values($roles)), $landlordId]);
        }
        setFlash('success', 'Арендодатель успешно удален');
    } else {
        setFlash('danger', 'Арендодатель не найден');
    }

    header('Location: landlords.php');
    exit;
}

// Handle toggle status
if (isset($_GET['toggle']) && is_numeric($_GET['toggle'])) {
    $stmt = $db->prepare("UPDATE users SET is_active = NOT is_active WHERE id = ?");
    $stmt->execute([$_GET['toggle']]);
    setFlash('success', 'Статус обновлен');
    header('Location: landlords.php');
    exit;
}

$stmt = $db->query("
    SELECT u.*,
           (SELECT COUNT(*) FROM apartments WHERE landlord_id = u.id) as apartments_count,
           (SELECT COUNT(*) FROM bookings WHERE landlord_id = u.id) as bookings_count
    FROM users u
    WHERE u.roles LIKE '%landlord%'
    ORDER BY u.created_at DESC
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
                                <button type="button"
                                        class="btn btn-outline-danger"
                                        data-bs-toggle="modal"
                                        data-bs-target="#deleteModal<?= $landlord['id'] ?>"
                                        title="Удалить">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>

                    <!-- Delete Confirmation Modal -->
                    <div class="modal fade" id="deleteModal<?= $landlord['id'] ?>" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header bg-danger text-white">
                                    <h5 class="modal-title">
                                        <i class="bi bi-exclamation-triangle me-2"></i>Подтверждение удаления
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="alert alert-warning">
                                        <i class="bi bi-exclamation-circle me-2"></i>
                                        <strong>Внимание!</strong> Это действие необратимо.
                                    </div>

                                    <p>Вы действительно хотите удалить арендодателя <strong><?= sanitize($landlord['full_name']) ?></strong>?</p>

                                    <div class="card bg-light">
                                        <div class="card-body">
                                            <h6 class="text-danger mb-3">Будут также удалены:</h6>
                                            <ul class="mb-0">
                                                <li><strong><?= $landlord['apartments_count'] ?></strong> квартир(ы)</li>
                                                <li><strong><?= $landlord['bookings_count'] ?></strong> бронирований(е)</li>
                                                <li>Все связанные отзывы</li>
                                                <li>Все связанные фотографии</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                        <i class="bi bi-x-circle me-1"></i>Отмена
                                    </button>
                                    <form method="POST" class="d-inline">
                                        <input type="hidden" name="delete_landlord" value="<?= $landlord['id'] ?>">
                                        <button type="submit" class="btn btn-danger">
                                            <i class="bi bi-trash me-1"></i>Удалить
                                        </button>
                                    </form>
                                </div>
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
