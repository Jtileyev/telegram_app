<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Пользователи';

$db = getDB();

// Handle user deletion
if (isset($_GET['delete']) && is_numeric($_GET['delete'])) {
    $userId = $_GET['delete'];

    // Check if user exists
    $stmt = $db->prepare("SELECT id FROM users WHERE id = ?");
    $stmt->execute([$userId]);

    if ($stmt->fetch()) {
        // Delete user (cascading will handle related records)
        $stmt = $db->prepare("DELETE FROM users WHERE id = ?");
        $stmt->execute([$userId]);
        setFlash('success', 'Пользователь успешно удален');
    } else {
        setFlash('danger', 'Пользователь не найден');
    }

    header('Location: users.php');
    exit;
}

$stmt = $db->query("
    SELECT u.*,
           (SELECT COUNT(*) FROM bookings WHERE user_id = u.id) as bookings_count,
           (SELECT COUNT(*) FROM favorites WHERE user_id = u.id) as favorites_count
    FROM users u
    ORDER BY u.created_at DESC
");
$users = $stmt->fetchAll();

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <?php if (empty($users)): ?>
        <p class="text-muted">Нет пользователей</p>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Telegram ID</th>
                        <th>ФИО</th>
                        <th>Телефон</th>
                        <th>Язык</th>
                        <th>Бронирований</th>
                        <th>В избранном</th>
                        <th>Зарегистрирован</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                    <tr>
                        <td>#<?= $user['id'] ?></td>
                        <td><?= $user['telegram_id'] ?></td>
                        <td>
                            <strong><?= sanitize($user['full_name'] ?: 'Не указано') ?></strong>
                            <?php if ($user['username']): ?>
                            <br><small class="text-muted">@<?= $user['username'] ?></small>
                            <?php endif; ?>
                        </td>
                        <td><?= $user['phone'] ?: '-' ?></td>
                        <td>
                            <?= $user['language'] === 'ru' ? '🇷🇺 Русский' : '🇰🇿 Қазақша' ?>
                        </td>
                        <td>
                            <span class="badge bg-info"><?= $user['bookings_count'] ?></span>
                        </td>
                        <td>
                            <span class="badge bg-warning"><?= $user['favorites_count'] ?></span>
                        </td>
                        <td>
                            <?= date('d.m.Y H:i', strtotime($user['created_at'])) ?>
                        </td>
                        <td>
                            <a href="?delete=<?= $user['id'] ?>"
                               class="btn btn-sm btn-outline-danger"
                               onclick="return confirm('Вы уверены, что хотите удалить пользователя <?= sanitize($user['full_name'] ?: 'ID: ' . $user['id']) ?>?\n\nБудут также удалены:\n- Все бронирования (<?= $user['bookings_count'] ?>)\n- Избранное (<?= $user['favorites_count'] ?>)\n\nЭто действие необратимо!')"
                               title="Удалить">
                                <i class="bi bi-trash"></i>
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
