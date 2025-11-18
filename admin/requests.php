<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Заявки арендодателей';

$db = getDB();

// Handle approve
if (isset($_GET['approve']) && is_numeric($_GET['approve'])) {
    $stmt = $db->prepare("SELECT * FROM landlord_requests WHERE id = ?");
    $stmt->execute([$_GET['approve']]);
    $request = $stmt->fetch();

    if ($request) {
        // Check if user already exists
        $stmt = $db->prepare("SELECT id, roles FROM users WHERE email = ? OR telegram_id = ?");
        $stmt->execute([$request['email'], $request['telegram_id']]);
        $existing = $stmt->fetch();

        if ($existing) {
            // Add landlord role to existing user
            $roles = json_decode($existing['roles'], true);
            if (!in_array('landlord', $roles)) {
                $roles[] = 'landlord';
                $stmt = $db->prepare("UPDATE users SET roles = ?, full_name = ?, phone = ? WHERE id = ?");
                $stmt->execute([json_encode($roles), $request['full_name'], $request['phone'], $existing['id']]);
            }
        } else {
            // Create new user with landlord role
            $stmt = $db->prepare("INSERT INTO users (telegram_id, full_name, phone, email, roles, is_active) VALUES (?, ?, ?, ?, ?, 1)");
            $stmt->execute([$request['telegram_id'], $request['full_name'], $request['phone'], $request['email'], json_encode(['landlord'])]);
        }

        // Update request status
        $stmt = $db->prepare("UPDATE landlord_requests SET status = 'approved', processed_at = CURRENT_TIMESTAMP WHERE id = ?");
        $stmt->execute([$_GET['approve']]);

        // Send Telegram notification
        $notifyScript = __DIR__ . '/../bot/notify_landlord.py';
        $command = sprintf(
            "python3 %s %d %s > /dev/null 2>&1 &",
            escapeshellarg($notifyScript),
            $request['telegram_id'],
            escapeshellarg($request['full_name'])
        );
        exec($command);

        setFlash('success', 'Заявка одобрена, арендодатель создан');
    }
    header('Location: requests.php');
    exit;
}

// Handle reject
if (isset($_GET['reject']) && is_numeric($_GET['reject'])) {
    $stmt = $db->prepare("UPDATE landlord_requests SET status = 'rejected', processed_at = CURRENT_TIMESTAMP WHERE id = ?");
    $stmt->execute([$_GET['reject']]);
    setFlash('warning', 'Заявка отклонена');
    header('Location: requests.php');
    exit;
}

$stmt = $db->query("SELECT * FROM landlord_requests ORDER BY created_at DESC");
$requests = $stmt->fetchAll();

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <?php if (empty($requests)): ?>
        <p class="text-muted">Нет заявок</p>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Telegram ID</th>
                        <th>ФИО</th>
                        <th>Телефон</th>
                        <th>Email</th>
                        <th>Статус</th>
                        <th>Создана</th>
                        <th>Обработана</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($requests as $request): ?>
                    <tr>
                        <td>#<?= $request['id'] ?></td>
                        <td><?= $request['telegram_id'] ?></td>
                        <td><strong><?= sanitize($request['full_name']) ?></strong></td>
                        <td><?= $request['phone'] ?></td>
                        <td><?= sanitize($request['email']) ?></td>
                        <td>
                            <?php
                            $statusClasses = [
                                'pending' => 'warning',
                                'approved' => 'success',
                                'rejected' => 'danger'
                            ];
                            $statusLabels = [
                                'pending' => 'Ожидает',
                                'approved' => 'Одобрена',
                                'rejected' => 'Отклонена'
                            ];
                            ?>
                            <span class="badge bg-<?= $statusClasses[$request['status']] ?>">
                                <?= $statusLabels[$request['status']] ?>
                            </span>
                        </td>
                        <td><?= date('d.m.Y H:i', strtotime($request['created_at'])) ?></td>
                        <td>
                            <?= $request['processed_at'] ? date('d.m.Y H:i', strtotime($request['processed_at'])) : '-' ?>
                        </td>
                        <td>
                            <?php if ($request['status'] === 'pending'): ?>
                            <div class="btn-group btn-group-sm">
                                <a href="?approve=<?= $request['id'] ?>"
                                   class="btn btn-success" title="Одобрить">
                                    <i class="bi bi-check-lg"></i>
                                </a>
                                <a href="?reject=<?= $request['id'] ?>"
                                   class="btn btn-danger" title="Отклонить"
                                   onclick="return confirm('Отклонить заявку?')">
                                    <i class="bi bi-x-lg"></i>
                                </a>
                            </div>
                            <?php else: ?>
                            -
                            <?php endif; ?>
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
