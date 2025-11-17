<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Настройки';

$db = getDB();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    foreach ($_POST as $key => $value) {
        if (strpos($key, 'setting_') === 0) {
            $settingKey = str_replace('setting_', '', $key);
            $stmt = $db->prepare("UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?");
            $stmt->execute([$value, $settingKey]);
        }
    }
    setFlash('success', 'Настройки сохранены');
    header('Location: settings.php');
    exit;
}

$stmt = $db->query("SELECT * FROM settings ORDER BY key");
$settings = $stmt->fetchAll();

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <form method="POST">
            <?php foreach ($settings as $setting): ?>
            <div class="mb-3">
                <label class="form-label">
                    <strong><?= sanitize($setting['key']) ?></strong>
                    <?php if ($setting['description']): ?>
                    <br><small class="text-muted"><?= sanitize($setting['description']) ?></small>
                    <?php endif; ?>
                </label>
                <input type="text" name="setting_<?= $setting['key'] ?>"
                       class="form-control" value="<?= sanitize($setting['value']) ?>">
                <small class="text-muted">Обновлено: <?= $setting['updated_at'] ?></small>
            </div>
            <?php endforeach; ?>

            <hr>
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-check-circle me-1"></i>Сохранить настройки
            </button>
        </form>
    </div>
</div>

<?php include 'footer.php'; ?>
