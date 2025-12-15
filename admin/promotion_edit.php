<?php
require_once 'config.php';
requireAdmin(); // Only admins can edit promotions

$db = getDB();
$promotion = null;

if (isset($_GET['id'])) {
    $stmt = $db->prepare("SELECT * FROM promotions WHERE id = ?");
    $stmt->execute([$_GET['id']]);
    $promotion = $stmt->fetch();
    $pageTitle = 'Редактирование акции';
} else {
    $pageTitle = 'Добавление акции';
}

if (!$promotion && isset($_GET['id'])) {
    setFlash('danger', 'Акция не найдена');
    header('Location: promotions.php');
    exit;
}

// Get usage stats if editing
$usage_stats = null;
if ($promotion) {
    $stmt = $db->prepare("
        SELECT
            COUNT(DISTINCT a.id) as apartment_count,
            COUNT(DISTINCT b.id) as total_bookings,
            COUNT(DISTINCT CASE WHEN b.promotion_discount_days > 0 THEN b.id END) as bookings_with_bonus
        FROM apartments a
        LEFT JOIN bookings b ON a.id = b.apartment_id AND b.promotion_id = ?
        WHERE a.promotion_id = ?
    ");
    $stmt->execute([$promotion['id'], $promotion['id']]);
    $usage_stats = $stmt->fetch();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    requireCSRF();
    $name = trim($_POST['name']);
    $description = trim($_POST['description']) ?: null;
    $bookings_required = (int)$_POST['bookings_required'];
    $free_days = (int)$_POST['free_days'];
    $is_active = isset($_POST['is_active']) ? 1 : 0;

    $errors = [];

    if (empty($name)) {
        $errors[] = 'Укажите название акции';
    }

    if ($bookings_required < 1 || $bookings_required > 100) {
        $errors[] = 'Количество заселений должно быть от 1 до 100';
    }

    if ($free_days < 1 || $free_days > 30) {
        $errors[] = 'Количество бесплатных дней должно быть от 1 до 30';
    }

    if (empty($errors)) {
        if ($promotion) {
            // Update
            $stmt = $db->prepare("
                UPDATE promotions SET
                    name = ?, description = ?, bookings_required = ?,
                    free_days = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ");
            $stmt->execute([$name, $description, $bookings_required, $free_days, $is_active, $promotion['id']]);
            setFlash('success', 'Акция обновлена');
        } else {
            // Insert
            $stmt = $db->prepare("
                INSERT INTO promotions (name, description, bookings_required, free_days, is_active)
                VALUES (?, ?, ?, ?, ?)
            ");
            $stmt->execute([$name, $description, $bookings_required, $free_days, $is_active]);
            setFlash('success', 'Акция добавлена');
        }

        header('Location: promotions.php');
        exit;
    } else {
        setFlash('danger', implode('<br>', $errors));
    }
}

include 'header.php';
?>

<div class="mb-4">
    <a href="promotions.php" class="btn btn-sm btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i>Назад к списку
    </a>
</div>

<?php
$flash = getFlash();
if ($flash):
?>
<div class="alert alert-<?= $flash['type'] ?> alert-dismissible fade show" role="alert">
    <?= $flash['message'] ?>
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
<?php endif; ?>

<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-<?= $promotion ? 'pencil' : 'plus-circle' ?> me-2"></i>
                    <?= $pageTitle ?>
                </h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <?= csrfField() ?>
                    <div class="mb-3">
                        <label class="form-label">Название акции *</label>
                        <input type="text" name="name" class="form-control" required
                               value="<?= $promotion ? sanitize($promotion['name']) : '' ?>"
                               placeholder='Например: Акция "6+1"'>
                        <small class="text-muted">Краткое название для отображения в списке</small>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Описание</label>
                        <textarea name="description" class="form-control" rows="3"
                                  placeholder="Дополнительная информация об акции"><?= $promotion ? sanitize($promotion['description']) : '' ?></textarea>
                        <small class="text-muted">Необязательно. Будет показано пользователям</small>
                    </div>

                    <hr class="my-4">

                    <h6 class="mb-3">Условия акции</h6>

                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Количество заселений до бонуса *</label>
                                <input type="number" name="bookings_required" class="form-control" required
                                       value="<?= $promotion ? $promotion['bookings_required'] : 6 ?>"
                                       min="1" max="100">
                                <small class="text-muted">На каком заселении применяется бонус (N)</small>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Количество бесплатных дней *</label>
                                <input type="number" name="free_days" class="form-control" required
                                       value="<?= $promotion ? $promotion['free_days'] : 1 ?>"
                                       min="1" max="30">
                                <small class="text-muted">Сколько дней дарится бесплатно (X)</small>
                            </div>
                        </div>
                    </div>

                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        <strong>Как это работает:</strong>
                        <ul class="mb-0 mt-2">
                            <li>Пользователь бронирует эту квартиру несколько раз</li>
                            <li>На N-ом заселении ему дарятся X бесплатных дней</li>
                            <li>После применения бонуса цикл обнуляется</li>
                        </ul>
                    </div>

                    <div class="mb-3">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" name="is_active" id="is_active"
                                   <?= (!$promotion || $promotion['is_active']) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="is_active">
                                <strong>Акция активна</strong>
                            </label>
                        </div>
                        <small class="text-muted">Неактивные акции не применяются к новым бронированиям</small>
                    </div>

                    <hr>
                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle me-1"></i>Сохранить
                        </button>
                        <a href="promotions.php" class="btn btn-secondary">Отмена</a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <?php if ($promotion && $usage_stats): ?>
        <div class="card mb-3">
            <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-bar-chart me-2"></i>Статистика использования</h6>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="text-muted">Квартир с акцией:</span>
                        <strong><?= $usage_stats['apartment_count'] ?></strong>
                    </div>
                    <div class="progress" style="height: 5px;">
                        <div class="progress-bar bg-primary" style="width: 100%"></div>
                    </div>
                </div>

                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="text-muted">Всего бронирований:</span>
                        <strong><?= $usage_stats['total_bookings'] ?></strong>
                    </div>
                </div>

                <div>
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="text-muted">Применено бонусов:</span>
                        <strong class="text-success"><?= $usage_stats['bookings_with_bonus'] ?></strong>
                    </div>
                    <div class="progress" style="height: 5px;">
                        <div class="progress-bar bg-success"
                             style="width: <?= $usage_stats['total_bookings'] > 0 ? ($usage_stats['bookings_with_bonus'] / $usage_stats['total_bookings'] * 100) : 0 ?>%">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <?php endif; ?>

        <div class="card">
            <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-lightbulb me-2"></i>Примеры акций</h6>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <strong>Акция "6+1"</strong>
                    <p class="mb-0 small text-muted">6 заселений → 1 бесплатный день</p>
                </div>
                <div class="mb-3">
                    <strong>Акция "3+2"</strong>
                    <p class="mb-0 small text-muted">3 заселения → 2 бесплатных дня</p>
                </div>
                <div>
                    <strong>Акция "10+3"</strong>
                    <p class="mb-0 small text-muted">10 заселений → 3 бесплатных дня</p>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
