<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Настройки';

$db = getDB();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    requireCSRF();
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

// Русские переводы для настроек
$settingsTranslations = [
    'bot_token' => [
        'name' => 'Токен бота',
        'description' => 'Токен Telegram-бота от @BotFather'
    ],
    'platform_fee_percent' => [
        'name' => 'Комиссия платформы (%)',
        'description' => 'Процент комиссии с каждого бронирования'
    ],
    'reminder_hours_before' => [
        'name' => 'Напоминание (часов)',
        'description' => 'За сколько часов до заезда отправлять напоминание'
    ],
    'charge_fee_for_admins' => [
        'name' => 'Комиссия с администраторов',
        'description' => 'Взимать комиссию платформы с бронирований квартир администраторов',
        'type' => 'boolean'
    ],
];

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <form method="POST">
            <?= csrfField() ?>
            <?php foreach ($settings as $setting): 
                $key = $setting['key'];
                $translation = $settingsTranslations[$key] ?? null;
                $displayName = $translation['name'] ?? $key;
                $displayDesc = $translation['description'] ?? $setting['description'];
            ?>
            <div class="mb-3">
                <label class="form-label">
                    <strong><?= sanitize($displayName) ?></strong>
                    <?php if ($displayDesc): ?>
                    <br><small class="text-muted"><?= sanitize($displayDesc) ?></small>
                    <?php endif; ?>
                </label>
                <?php if (isset($translation['type']) && $translation['type'] === 'boolean'): ?>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" 
                           id="switch_<?= $setting['key'] ?>"
                           <?= $setting['value'] === '1' ? 'checked' : '' ?>
                           onchange="document.getElementById('hidden_<?= $setting['key'] ?>').value = this.checked ? '1' : '0'">
                    <input type="hidden" name="setting_<?= $setting['key'] ?>" 
                           id="hidden_<?= $setting['key'] ?>" 
                           value="<?= sanitize($setting['value']) ?>">
                    <label class="form-check-label" for="switch_<?= $setting['key'] ?>">
                        <?= $setting['value'] === '1' ? 'Включено' : 'Выключено' ?>
                    </label>
                </div>
                <?php else: ?>
                <input type="text" name="setting_<?= $setting['key'] ?>"
                       class="form-control" value="<?= sanitize($setting['value']) ?>">
                <?php endif; ?>
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
