<?php
require_once 'config.php';
requireAdmin(); // Only admins can edit users

$db = getDB();
$user = null;

if (isset($_GET['id'])) {
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$_GET['id']]);
    $user = $stmt->fetch();
    $pageTitle = 'Редактирование пользователя';
} else {
    $pageTitle = 'Добавление пользователя';
}

if (!$user && isset($_GET['id'])) {
    setFlash('danger', 'Пользователь не найден');
    header('Location: users.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    requireCSRF();
    $telegram_id = $_POST['telegram_id'] ?: null;
    $email = $_POST['email'] ?: null;
    $username = $_POST['username'] ?: null;
    $full_name = $_POST['full_name'] ?: null;
    $phone = $_POST['phone'] ?: null;
    $language = $_POST['language'] ?? 'ru';
    $roles = $_POST['roles'] ?? [];
    $is_active = isset($_POST['is_active']) ? 1 : 0;

    // Handle password change
    $password = null;
    if (!empty($_POST['password'])) {
        $password = password_hash($_POST['password'], PASSWORD_DEFAULT);
    }

    if ($user) {
        // Update existing user
        $sql = "UPDATE users SET
                telegram_id = ?, email = ?, username = ?, full_name = ?,
                phone = ?, language = ?, roles = ?, is_active = ?,
                updated_at = CURRENT_TIMESTAMP";
        $params = [$telegram_id, $email, $username, $full_name, $phone, $language, json_encode($roles), $is_active];

        if ($password) {
            $sql .= ", password = ?";
            $params[] = $password;
        }

        $sql .= " WHERE id = ?";
        $params[] = $user['id'];

        $stmt = $db->prepare($sql);
        $stmt->execute($params);
        setFlash('success', 'Пользователь обновлен');
    } else {
        // Create new user
        if (empty($telegram_id) && empty($email)) {
            setFlash('danger', 'Укажите хотя бы Telegram ID или Email');
            header('Location: user_edit.php');
            exit;
        }

        $stmt = $db->prepare("
            INSERT INTO users (telegram_id, email, username, full_name, phone, language, roles, password, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ");
        $stmt->execute([
            $telegram_id, $email, $username, $full_name, $phone,
            $language, json_encode($roles), $password, $is_active
        ]);
        setFlash('success', 'Пользователь добавлен');
    }

    header('Location: users.php');
    exit;
}

// Parse current roles
$currentRoles = [];
if ($user && !empty($user['roles'])) {
    $decoded = json_decode($user['roles'], true);
    $currentRoles = is_array($decoded) ? $decoded : [];
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
                        <label class="form-label">Telegram ID</label>
                        <input type="number" name="telegram_id" class="form-control"
                               value="<?= $user ? $user['telegram_id'] : '' ?>">
                        <small class="text-muted">Уникальный ID пользователя в Telegram</small>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="form-control"
                               value="<?= $user ? sanitize($user['email']) : '' ?>">
                        <small class="text-muted">Для входа в админ панель</small>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Username (Telegram)</label>
                        <input type="text" name="username" class="form-control"
                               value="<?= $user ? sanitize($user['username']) : '' ?>">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">ФИО</label>
                        <input type="text" name="full_name" class="form-control"
                               value="<?= $user ? sanitize($user['full_name']) : '' ?>">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Телефон</label>
                        <input type="text" name="phone" class="form-control"
                               placeholder="+7 (XXX) XXX XX XX"
                               value="<?= $user ? sanitize($user['phone']) : '' ?>">
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Язык</label>
                        <select name="language" class="form-select">
                            <option value="ru" <?= ($user && $user['language'] === 'ru') ? 'selected' : '' ?>>🇷🇺 Русский</option>
                            <option value="kk" <?= ($user && $user['language'] === 'kk') ? 'selected' : '' ?>>🇰🇿 Қазақша</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Роли</label>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="roles[]" value="user" id="role_user"
                                   <?= in_array('user', $currentRoles) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="role_user">
                                Пользователь (обычный пользователь бота)
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="roles[]" value="landlord" id="role_landlord"
                                   <?= in_array('landlord', $currentRoles) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="role_landlord">
                                Арендодатель (может управлять квартирами)
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="roles[]" value="admin" id="role_admin"
                                   <?= in_array('admin', $currentRoles) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="role_admin">
                                Администратор (полный доступ)
                            </label>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">
                            <?= $user ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль' ?>
                        </label>
                        <input type="password" name="password" class="form-control"
                               minlength="6" <?= $user ? '' : 'required' ?>>
                        <small class="text-muted">Минимум 6 символов</small>
                    </div>

                    <div class="mb-3">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" name="is_active" id="is_active"
                                   <?= (!$user || $user['is_active']) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="is_active">
                                Активен
                            </label>
                        </div>
                    </div>

                    <?php if ($user): ?>
                    <div class="mb-3">
                        <label class="form-label">Создан</label>
                        <input type="text" class="form-control" value="<?= $user['created_at'] ? date('d.m.Y H:i', strtotime($user['created_at'])) : 'Н/Д' ?>" disabled>
                    </div>

                    <?php if (!empty($user['last_login'])): ?>
                    <div class="mb-3">
                        <label class="form-label">Последний вход</label>
                        <input type="text" class="form-control" value="<?= date('d.m.Y H:i', strtotime($user['last_login'])) ?>" disabled>
                    </div>
                    <?php endif; ?>
                    <?php endif; ?>
                </div>
            </div>

            <hr>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle me-1"></i>Сохранить
                </button>
                <a href="users.php" class="btn btn-secondary">Отмена</a>
            </div>
        </form>
    </div>
</div>

<?php include 'footer.php'; ?>
