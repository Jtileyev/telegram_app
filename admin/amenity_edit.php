<?php
require_once 'config.php';
requireAdmin(); // Only admins can edit amenities

$db = getDB();
$amenity = null;

if (isset($_GET['id'])) {
    $stmt = $db->prepare("SELECT * FROM amenities WHERE id = ?");
    $stmt->execute([$_GET['id']]);
    $amenity = $stmt->fetch();
    $pageTitle = 'Редактирование удобства';
} else {
    $pageTitle = 'Добавление удобства';
}

if (!$amenity && isset($_GET['id'])) {
    setFlash('danger', 'Удобство не найдено');
    header('Location: amenities.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    requireCSRF();
    $name_ru = trim($_POST['name_ru']);
    $name_kk = trim($_POST['name_kk']);
    $icon = trim($_POST['icon']) ?: null;
    $sort_order = (int)$_POST['sort_order'];
    $is_active = isset($_POST['is_active']) ? 1 : 0;

    if (empty($name_ru) || empty($name_kk)) {
        setFlash('danger', 'Заполните обязательные поля');
    } else {
        if ($amenity) {
            // Update
            $stmt = $db->prepare("
                UPDATE amenities SET
                    name_ru = ?, name_kk = ?, icon = ?,
                    sort_order = ?, is_active = ?
                WHERE id = ?
            ");
            $stmt->execute([$name_ru, $name_kk, $icon, $sort_order, $is_active, $amenity['id']]);
            setFlash('success', 'Удобство обновлено');
        } else {
            // Insert
            $stmt = $db->prepare("
                INSERT INTO amenities (name_ru, name_kk, icon, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?)
            ");
            $stmt->execute([$name_ru, $name_kk, $icon, $sort_order, $is_active]);
            setFlash('success', 'Удобство добавлено');
        }

        header('Location: amenities.php');
        exit;
    }
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
                        <label class="form-label">Название (Русский) *</label>
                        <input type="text" name="name_ru" class="form-control"
                               value="<?= $amenity ? sanitize($amenity['name_ru']) : '' ?>" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Название (Казахский) *</label>
                        <input type="text" name="name_kk" class="form-control"
                               value="<?= $amenity ? sanitize($amenity['name_kk']) : '' ?>" required>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Иконка (emoji)</label>
                        <input type="text" name="icon" class="form-control" maxlength="10"
                               value="<?= $amenity ? sanitize($amenity['icon']) : '' ?>"
                               placeholder="📶">
                        <small class="text-muted">Необязательно. Например: 📶 ❄️ 🧺 🧊 📺 🅿️</small>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Порядок сортировки</label>
                        <input type="number" name="sort_order" class="form-control"
                               value="<?= $amenity ? $amenity['sort_order'] : 0 ?>" min="0">
                        <small class="text-muted">Чем меньше число, тем выше в списке</small>
                    </div>

                    <div class="mb-3">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" name="is_active" id="is_active"
                                   <?= (!$amenity || $amenity['is_active']) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="is_active">
                                Активно
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <hr>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle me-1"></i>Сохранить
                </button>
                <a href="amenities.php" class="btn btn-secondary">Отмена</a>
            </div>
        </form>
    </div>
</div>

<?php include 'footer.php'; ?>
