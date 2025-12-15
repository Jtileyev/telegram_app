<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'Города и районы';

$db = getDB();

// Handle city add
if (isset($_POST['add_city'])) {
    requireCSRF();
    $stmt = $db->prepare("INSERT INTO cities (name_ru, name_kk) VALUES (?, ?)");
    $stmt->execute([$_POST['city_name_ru'], $_POST['city_name_kk']]);
    setFlash('success', 'Город добавлен');
    header('Location: cities.php');
    exit;
}

// Handle district add
if (isset($_POST['add_district'])) {
    requireCSRF();
    $stmt = $db->prepare("INSERT INTO districts (city_id, name_ru, name_kk) VALUES (?, ?, ?)");
    $stmt->execute([$_POST['city_id'], $_POST['district_name_ru'], $_POST['district_name_kk']]);
    setFlash('success', 'Район добавлен');
    header('Location: cities.php');
    exit;
}

// Handle delete
if (isset($_GET['delete_city']) && is_numeric($_GET['delete_city'])) {
    // Проверяем, есть ли квартиры в этом городе
    $stmt = $db->prepare("SELECT COUNT(*) as cnt FROM apartments WHERE city_id = ?");
    $stmt->execute([$_GET['delete_city']]);
    $count = $stmt->fetch()['cnt'];
    
    if ($count > 0) {
        setFlash('danger', 'Невозможно удалить город: в нем есть ' . $count . ' квартир(а)');
    } else {
        $stmt = $db->prepare("DELETE FROM cities WHERE id = ?");
        $stmt->execute([$_GET['delete_city']]);
        setFlash('success', 'Город удален');
    }
    header('Location: cities.php');
    exit;
}

if (isset($_GET['delete_district']) && is_numeric($_GET['delete_district'])) {
    // Проверяем, есть ли квартиры в этом районе
    $stmt = $db->prepare("SELECT COUNT(*) as cnt FROM apartments WHERE district_id = ?");
    $stmt->execute([$_GET['delete_district']]);
    $count = $stmt->fetch()['cnt'];
    
    if ($count > 0) {
        setFlash('danger', 'Невозможно удалить район: в нем есть ' . $count . ' квартир(а)');
    } else {
        $stmt = $db->prepare("DELETE FROM districts WHERE id = ?");
        $stmt->execute([$_GET['delete_district']]);
        setFlash('success', 'Район удален');
    }
    header('Location: cities.php');
    exit;
}

$cities = $db->query("SELECT * FROM cities ORDER BY name_ru")->fetchAll();

include 'header.php';
?>

<div class="row">
    <div class="col-md-6">
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Добавить город</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <?= csrfField() ?>
                    <div class="mb-3">
                        <input type="text" name="city_name_ru" class="form-control"
                               placeholder="Название (Русский)" required>
                    </div>
                    <div class="mb-3">
                        <input type="text" name="city_name_kk" class="form-control"
                               placeholder="Название (Казахский)" required>
                    </div>
                    <button type="submit" name="add_city" class="btn btn-primary">Добавить город</button>
                </form>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Добавить район</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <?= csrfField() ?>
                    <div class="mb-3">
                        <select name="city_id" class="form-select" required>
                            <option value="">Выберите город</option>
                            <?php foreach ($cities as $city): ?>
                            <option value="<?= $city['id'] ?>"><?= sanitize($city['name_ru']) ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div class="mb-3">
                        <input type="text" name="district_name_ru" class="form-control"
                               placeholder="Название (Русский)" required>
                    </div>
                    <div class="mb-3">
                        <input type="text" name="district_name_kk" class="form-control"
                               placeholder="Название (Казахский)" required>
                    </div>
                    <button type="submit" name="add_district" class="btn btn-primary">Добавить район</button>
                </form>
            </div>
        </div>
    </div>
</div>

<?php foreach ($cities as $city): ?>
<div class="card mb-3">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><?= sanitize($city['name_ru']) ?> / <?= sanitize($city['name_kk']) ?></h5>
        <a href="?delete_city=<?= $city['id'] ?>" class="btn btn-sm btn-outline-danger"
           onclick="return confirm('Удалить город и все его районы?')">
            <i class="bi bi-trash"></i>
        </a>
    </div>
    <div class="card-body">
        <?php
        $stmt = $db->prepare("SELECT * FROM districts WHERE city_id = ? ORDER BY name_ru");
        $stmt->execute([$city['id']]);
        $districts = $stmt->fetchAll();
        ?>
        <?php if (empty($districts)): ?>
        <p class="text-muted">Нет районов</p>
        <?php else: ?>
        <div class="row">
            <?php foreach ($districts as $district): ?>
            <div class="col-md-4 mb-2">
                <div class="d-flex justify-content-between align-items-center bg-light p-2 rounded">
                    <span>
                        <?= sanitize($district['name_ru']) ?><br>
                        <small class="text-muted"><?= sanitize($district['name_kk']) ?></small>
                    </span>
                    <a href="?delete_district=<?= $district['id'] ?>"
                       class="btn btn-sm btn-outline-danger"
                       onclick="return confirm('Удалить район?')">
                        <i class="bi bi-x"></i>
                    </a>
                </div>
            </div>
            <?php endforeach; ?>
        </div>
        <?php endif; ?>
    </div>
</div>
<?php endforeach; ?>

<?php include 'footer.php'; ?>
