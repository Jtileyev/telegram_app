<?php
require_once 'config.php';
requireLogin();

$db = getDB();
$landlord = null;

if (isset($_GET['id'])) {
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ? AND roles LIKE '%landlord%'");
    $stmt->execute([$_GET['id']]);
    $landlord = $stmt->fetch();
    $pageTitle = 'Редактирование арендодателя';
} else {
    $pageTitle = 'Добавление арендодателя';
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    requireCSRF();
    $full_name = $_POST['full_name'];
    $phone = $_POST['phone'];
    $email = $_POST['email'] ?: null;
    $telegram_id = $_POST['telegram_id'] ?: null;

    if ($landlord) {
        $stmt = $db->prepare("
            UPDATE users SET
                full_name = ?, phone = ?, email = ?, telegram_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ");
        $stmt->execute([$full_name, $phone, $email, $telegram_id, $landlord['id']]);
        setFlash('success', 'Арендодатель обновлен');
    } else {
        // Check if user with this email already exists
        $existing = null;
        if ($email) {
            $stmt = $db->prepare("SELECT id, roles FROM users WHERE email = ?");
            $stmt->execute([$email]);
            $existing = $stmt->fetch();
        }

        if ($existing) {
            // Add landlord role to existing user
            $roles = json_decode($existing['roles'], true);
            if (!in_array('landlord', $roles)) {
                $roles[] = 'landlord';
                $stmt = $db->prepare("UPDATE users SET roles = ? WHERE id = ?");
                $stmt->execute([json_encode($roles), $existing['id']]);
            }
            setFlash('success', 'Роль арендодателя добавлена существующему пользователю');
        } else {
            // Create new user with landlord role
            $stmt = $db->prepare("
                INSERT INTO users (full_name, phone, email, telegram_id, roles, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            ");
            $stmt->execute([$full_name, $phone, $email, $telegram_id, json_encode(['landlord'])]);
            setFlash('success', 'Арендодатель добавлен');
        }
    }

    header('Location: landlords.php');
    exit;
}

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <form method="POST">
            <?= csrfField() ?>
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">ФИО *</label>
                        <input type="text" name="full_name" class="form-control"
                               value="<?= $landlord ? sanitize($landlord['full_name']) : '' ?>" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Телефон *</label>
                        <input type="text" name="phone" class="form-control"
                               placeholder="+7 (XXX) XXX XX XX"
                               value="<?= $landlord ? sanitize($landlord['phone']) : '' ?>" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="form-control"
                               value="<?= $landlord ? sanitize($landlord['email']) : '' ?>">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Telegram ID</label>
                        <input type="number" name="telegram_id" class="form-control"
                               value="<?= $landlord ? $landlord['telegram_id'] : '' ?>">
                    </div>
                </div>
            </div>

            <hr>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle me-1"></i>Сохранить
                </button>
                <a href="landlords.php" class="btn btn-secondary">Отмена</a>
            </div>
        </form>
    </div>
</div>

<?php include 'footer.php'; ?>
