<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Пользователи';

$db = getDB();

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
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>
</div>

<?php include 'footer.php'; ?>
