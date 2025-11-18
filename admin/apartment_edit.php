<?php
require_once 'config.php';
requireLogin();

$db = getDB();
$apartment = null;

if (isset($_GET['id'])) {
    $stmt = $db->prepare("SELECT * FROM apartments WHERE id = ?");
    $stmt->execute([$_GET['id']]);
    $apartment = $stmt->fetch();
    $pageTitle = 'Редактирование квартиры';
} else {
    $pageTitle = 'Добавление квартиры';
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $landlord_id = $_POST['landlord_id'];
    $city_id = $_POST['city_id'];
    $district_id = $_POST['district_id'];
    $title_ru = $_POST['title_ru'];
    $title_kk = $_POST['title_kk'];
    $description_ru = $_POST['description_ru'];
    $description_kk = $_POST['description_kk'];
    $address = $_POST['address'];
    $price_per_day = $_POST['price_per_day'];
    $price_per_month = $_POST['price_per_month'] ?: null;
    $gis_link = $_POST['gis_link'];
    $amenities = json_encode($_POST['amenities'] ?? [], JSON_UNESCAPED_UNICODE);
    $promotion = $_POST['promotion'];

    if ($apartment) {
        // Update
        $stmt = $db->prepare("
            UPDATE apartments SET
                landlord_id = ?, city_id = ?, district_id = ?,
                title_ru = ?, title_kk = ?, description_ru = ?, description_kk = ?,
                address = ?, price_per_day = ?, price_per_month = ?,
                gis_link = ?, amenities = ?, promotion = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ");
        $stmt->execute([
            $landlord_id, $city_id, $district_id,
            $title_ru, $title_kk, $description_ru, $description_kk,
            $address, $price_per_day, $price_per_month,
            $gis_link, $amenities, $promotion,
            $apartment['id']
        ]);
        $apt_id = $apartment['id'];
        setFlash('success', 'Квартира обновлена');
    } else {
        // Insert
        $stmt = $db->prepare("
            INSERT INTO apartments (
                landlord_id, city_id, district_id,
                title_ru, title_kk, description_ru, description_kk,
                address, price_per_day, price_per_month,
                gis_link, amenities, promotion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ");
        $stmt->execute([
            $landlord_id, $city_id, $district_id,
            $title_ru, $title_kk, $description_ru, $description_kk,
            $address, $price_per_day, $price_per_month,
            $gis_link, $amenities, $promotion
        ]);
        $apt_id = $db->lastInsertId();
        setFlash('success', 'Квартира добавлена');
    }

    // Handle photo uploads
    if (!empty($_FILES['photos']['name'][0])) {
        foreach ($_FILES['photos']['tmp_name'] as $key => $tmp_name) {
            if ($_FILES['photos']['error'][$key] === UPLOAD_ERR_OK) {
                $ext = pathinfo($_FILES['photos']['name'][$key], PATHINFO_EXTENSION);
                $filename = 'apt_' . $apt_id . '_' . time() . '_' . $key . '.' . $ext;
                $filepath = UPLOADS_PATH . $filename;

                if (move_uploaded_file($tmp_name, $filepath)) {
                    $stmt = $db->prepare("INSERT INTO apartment_photos (apartment_id, photo_path, is_main) VALUES (?, ?, ?)");
                    $stmt->execute([$apt_id, $filepath, $key === 0 ? 1 : 0]);
                }
            }
        }
    }

    header('Location: apartments.php');
    exit;
}

// Get data for dropdowns
$landlords = $db->query("SELECT id, full_name, phone FROM users WHERE is_active = 1 AND roles LIKE '%landlord%' ORDER BY full_name")->fetchAll();
$cities = $db->query("SELECT id, name_ru FROM cities ORDER BY name_ru")->fetchAll();

$selectedAmenities = $apartment && $apartment['amenities'] ? json_decode($apartment['amenities'], true) : [];

include 'header.php';
?>

<div class="card">
    <div class="card-body">
        <form method="POST" enctype="multipart/form-data">
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Арендодатель *</label>
                        <select name="landlord_id" class="form-select" required>
                            <option value="">Выберите арендодателя</option>
                            <?php foreach ($landlords as $l): ?>
                            <option value="<?= $l['id'] ?>" <?= ($apartment && $apartment['landlord_id'] == $l['id']) ? 'selected' : '' ?>>
                                <?= sanitize($l['full_name']) ?> (<?= $l['phone'] ?>)
                            </option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Город *</label>
                        <select name="city_id" id="city_id" class="form-select" required>
                            <option value="">Выберите город</option>
                            <?php foreach ($cities as $c): ?>
                            <option value="<?= $c['id'] ?>" <?= ($apartment && $apartment['city_id'] == $c['id']) ? 'selected' : '' ?>>
                                <?= sanitize($c['name_ru']) ?>
                            </option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Район *</label>
                        <select name="district_id" id="district_id" class="form-select" required>
                            <option value="">Сначала выберите город</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Название (Русский) *</label>
                        <input type="text" name="title_ru" class="form-control"
                               value="<?= $apartment ? sanitize($apartment['title_ru']) : '' ?>" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Название (Казахский) *</label>
                        <input type="text" name="title_kk" class="form-control"
                               value="<?= $apartment ? sanitize($apartment['title_kk']) : '' ?>" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Адрес *</label>
                        <input type="text" name="address" class="form-control"
                               value="<?= $apartment ? sanitize($apartment['address']) : '' ?>" required>
                    </div>

                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Цена за сутки (₸) *</label>
                                <input type="number" name="price_per_day" class="form-control"
                                       value="<?= $apartment ? $apartment['price_per_day'] : '' ?>" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Цена за месяц (₸)</label>
                                <input type="number" name="price_per_month" class="form-control"
                                       value="<?= $apartment ? $apartment['price_per_month'] : '' ?>">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Описание (Русский)</label>
                        <textarea name="description_ru" class="form-control" rows="4"><?= $apartment ? sanitize($apartment['description_ru']) : '' ?></textarea>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Описание (Казахский)</label>
                        <textarea name="description_kk" class="form-control" rows="4"><?= $apartment ? sanitize($apartment['description_kk']) : '' ?></textarea>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Ссылка 2GIS</label>
                        <input type="url" name="gis_link" class="form-control"
                               value="<?= $apartment ? sanitize($apartment['gis_link']) : '' ?>">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Акция</label>
                        <input type="text" name="promotion" class="form-control"
                               placeholder="Например: 6-ое заселение бесплатно"
                               value="<?= $apartment ? sanitize($apartment['promotion']) : '' ?>">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Удобства</label>
                        <div class="row">
                            <?php
                            $allAmenities = ['Wi-Fi', 'Кондиционер', 'Стиральная машина', 'Холодильник',
                                           'Телевизор', 'Парковка', 'Балкон', 'Близость к центру'];
                            foreach ($allAmenities as $amenity):
                            ?>
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input type="checkbox" name="amenities[]" value="<?= $amenity ?>"
                                           class="form-check-input" id="amenity_<?= $amenity ?>"
                                           <?= in_array($amenity, $selectedAmenities) ? 'checked' : '' ?>>
                                    <label class="form-check-label" for="amenity_<?= $amenity ?>">
                                        <?= $amenity ?>
                                    </label>
                                </div>
                            </div>
                            <?php endforeach; ?>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Фотографии</label>
                        <input type="file" name="photos[]" class="form-control" multiple accept="image/*">
                        <small class="text-muted">Первая фотография будет главной</small>
                    </div>

                    <?php if ($apartment): ?>
                    <div class="mb-3">
                        <label class="form-label">Текущие фотографии</label>
                        <div class="d-flex flex-wrap gap-2">
                            <?php
                            $stmt = $db->prepare("SELECT * FROM apartment_photos WHERE apartment_id = ?");
                            $stmt->execute([$apartment['id']]);
                            $photos = $stmt->fetchAll();
                            foreach ($photos as $photo):
                            ?>
                            <div class="position-relative">
                                <img src="../uploads/apartments/<?= basename($photo['photo_path']) ?>"
                                     style="width: 100px; height: 70px; object-fit: cover;"
                                     class="rounded">
                                <?php if ($photo['is_main']): ?>
                                <span class="position-absolute top-0 start-0 badge bg-primary">Главная</span>
                                <?php endif; ?>
                            </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    <?php endif; ?>
                </div>
            </div>

            <hr>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle me-1"></i>Сохранить
                </button>
                <a href="apartments.php" class="btn btn-secondary">Отмена</a>
            </div>
        </form>
    </div>
</div>

<script>
// Load districts when city changes
document.getElementById('city_id').addEventListener('change', function() {
    const cityId = this.value;
    const districtSelect = document.getElementById('district_id');

    if (!cityId) {
        districtSelect.innerHTML = '<option value="">Сначала выберите город</option>';
        return;
    }

    // Fetch districts via AJAX
    fetch('get_districts.php?city_id=' + cityId)
        .then(response => response.json())
        .then(data => {
            districtSelect.innerHTML = '<option value="">Выберите район</option>';
            data.forEach(district => {
                const option = document.createElement('option');
                option.value = district.id;
                option.textContent = district.name_ru;
                <?php if ($apartment): ?>
                if (district.id == <?= $apartment['district_id'] ?>) {
                    option.selected = true;
                }
                <?php endif; ?>
                districtSelect.appendChild(option);
            });
        });
});

// Trigger change on page load if editing
<?php if ($apartment): ?>
document.getElementById('city_id').dispatchEvent(new Event('change'));
<?php endif; ?>
</script>

<?php include 'footer.php'; ?>
