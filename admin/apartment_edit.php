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
    $promotion_id = !empty($_POST['promotion_id']) ? (int)$_POST['promotion_id'] : null;

    if ($apartment) {
        // Update
        $stmt = $db->prepare("
            UPDATE apartments SET
                landlord_id = ?, city_id = ?, district_id = ?,
                title_ru = ?, title_kk = ?, description_ru = ?, description_kk = ?,
                address = ?, price_per_day = ?, price_per_month = ?,
                gis_link = ?, amenities = ?, promotion_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ");
        $stmt->execute([
            $landlord_id, $city_id, $district_id,
            $title_ru, $title_kk, $description_ru, $description_kk,
            $address, $price_per_day, $price_per_month,
            $gis_link, $amenities, $promotion_id,
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
                gis_link, amenities, promotion_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ");
        $stmt->execute([
            $landlord_id, $city_id, $district_id,
            $title_ru, $title_kk, $description_ru, $description_kk,
            $address, $price_per_day, $price_per_month,
            $gis_link, $amenities, $promotion_id
        ]);
        $apt_id = $db->lastInsertId();
        setFlash('success', 'Квартира добавлена');
    }

    // Photo uploads are now handled via AJAX in upload_apartment_photo.php

    header('Location: apartments.php');
    exit;
}

// Get data for dropdowns
$landlords = $db->query("SELECT id, full_name, phone FROM users WHERE is_active = 1 AND roles LIKE '%landlord%' ORDER BY full_name")->fetchAll();
$cities = $db->query("SELECT id, name_ru FROM cities ORDER BY name_ru")->fetchAll();
$promotions = $db->query("SELECT id, name, bookings_required, free_days FROM promotions ORDER BY is_active DESC, name")->fetchAll();

// Get amenities from database
try {
    $allAmenities = $db->query("SELECT * FROM amenities WHERE is_active = 1 ORDER BY sort_order ASC, name_ru ASC")->fetchAll();
} catch (Exception $e) {
    // Fallback to hardcoded amenities if table doesn't exist
    $allAmenities = [
        ['id' => 'wifi', 'name_ru' => 'Wi-Fi', 'icon' => '📶'],
        ['id' => 'ac', 'name_ru' => 'Кондиционер', 'icon' => '❄️'],
        ['id' => 'washer', 'name_ru' => 'Стиральная машина', 'icon' => '🧺'],
        ['id' => 'fridge', 'name_ru' => 'Холодильник', 'icon' => '🧊'],
        ['id' => 'tv', 'name_ru' => 'Телевизор', 'icon' => '📺'],
        ['id' => 'parking', 'name_ru' => 'Парковка', 'icon' => '🅿️'],
        ['id' => 'balcony', 'name_ru' => 'Балкон', 'icon' => '🏢'],
        ['id' => 'center', 'name_ru' => 'Близость к центру', 'icon' => '📍']
    ];
}

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
                        <label class="form-label">Программа лояльности (Акция)</label>
                        <select name="promotion_id" class="form-select">
                            <option value="">Без акции</option>
                            <?php foreach ($promotions as $promo): ?>
                            <option value="<?= $promo['id'] ?>"
                                    <?= ($apartment && $apartment['promotion_id'] == $promo['id']) ? 'selected' : '' ?>>
                                <?= sanitize($promo['name']) ?> (<?= $promo['bookings_required'] ?>-е заселение → <?= $promo['free_days'] ?> дней)
                            </option>
                            <?php endforeach; ?>
                        </select>
                        <small class="text-muted">
                            Выберите акцию из списка.
                            <?php if (isAdmin()): ?>
                            <a href="promotions.php" target="_blank">Управление акциями</a>
                            <?php endif; ?>
                        </small>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Удобства</label>
                        <?php if (empty($allAmenities)): ?>
                        <p class="text-muted small">
                            Нет доступных удобств.
                            <?php if (isAdmin()): ?>
                            <a href="amenities.php">Добавить удобства</a>
                            <?php endif; ?>
                        </p>
                        <?php else: ?>
                        <div class="row">
                            <?php foreach ($allAmenities as $amenity): ?>
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input type="checkbox" name="amenities[]" value="<?= sanitize($amenity['name_ru']) ?>"
                                           class="form-check-input" id="amenity_<?= $amenity['id'] ?>"
                                           <?= in_array($amenity['name_ru'], $selectedAmenities) ? 'checked' : '' ?>>
                                    <label class="form-check-label" for="amenity_<?= $amenity['id'] ?>">
                                        <?= $amenity['icon'] ? $amenity['icon'] . ' ' : '' ?><?= sanitize($amenity['name_ru']) ?>
                                    </label>
                                </div>
                            </div>
                            <?php endforeach; ?>
                        </div>
                        <?php endif; ?>
                    </div>

                    <?php if ($apartment): ?>
                    <div class="mb-3">
                        <label class="form-label">Фотографии</label>
                        <input type="file" id="photo_upload" class="form-control" accept="image/*">
                        <small class="text-muted">Первая фотография будет главной. Максимум 5MB</small>
                        <div id="upload_progress" class="mt-2" style="display: none;">
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 100%">Загрузка...</div>
                            </div>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Текущие фотографии</label>
                        <div id="photos_container" class="d-flex flex-wrap gap-2">
                            <?php
                            $stmt = $db->prepare("SELECT * FROM apartment_photos WHERE apartment_id = ? ORDER BY is_main DESC, sort_order ASC");
                            $stmt->execute([$apartment['id']]);
                            $photos = $stmt->fetchAll();
                            foreach ($photos as $photo):
                            ?>
                            <div class="position-relative photo-item" data-photo-id="<?= $photo['id'] ?>">
                                <img src="../<?= sanitize($photo['photo_path']) ?>"
                                     style="width: 150px; height: 100px; object-fit: cover;"
                                     class="rounded">
                                <?php if ($photo['is_main']): ?>
                                <span class="position-absolute top-0 start-0 badge bg-primary">Главная</span>
                                <?php else: ?>
                                <button type="button" class="btn btn-sm btn-success position-absolute top-0 start-0 set-main-btn"
                                        data-photo-id="<?= $photo['id'] ?>" title="Сделать главной">
                                    <i class="bi bi-star"></i>
                                </button>
                                <?php endif; ?>
                                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 delete-photo-btn"
                                        data-photo-id="<?= $photo['id'] ?>" title="Удалить">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    <?php else: ?>
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        Сохраните квартиру, чтобы добавить фотографии
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

// Photo upload handling
const photoUpload = document.getElementById('photo_upload');
const uploadProgress = document.getElementById('upload_progress');
const photosContainer = document.getElementById('photos_container');

if (photoUpload) {
    photoUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('photo', file);
        formData.append('apartment_id', <?= $apartment['id'] ?>);

        uploadProgress.style.display = 'block';

        fetch('upload_apartment_photo.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadProgress.style.display = 'none';

            if (data.success) {
                // Add new photo to container
                const photoDiv = document.createElement('div');
                photoDiv.className = 'position-relative photo-item';
                photoDiv.setAttribute('data-photo-id', data.photo_id);

                let buttonHtml = '';
                if (data.is_main) {
                    buttonHtml = '<span class="position-absolute top-0 start-0 badge bg-primary">Главная</span>';
                } else {
                    buttonHtml = `<button type="button" class="btn btn-sm btn-success position-absolute top-0 start-0 set-main-btn"
                                         data-photo-id="${data.photo_id}" title="Сделать главной">
                                    <i class="bi bi-star"></i>
                                  </button>`;
                }

                photoDiv.innerHTML = `
                    <img src="${data.photo_url}"
                         style="width: 150px; height: 100px; object-fit: cover;"
                         class="rounded">
                    ${buttonHtml}
                    <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 delete-photo-btn"
                            data-photo-id="${data.photo_id}" title="Удалить">
                        <i class="bi bi-trash"></i>
                    </button>
                `;

                photosContainer.appendChild(photoDiv);
                photoUpload.value = ''; // Reset file input

                // Attach event listeners to new buttons
                attachPhotoButtonListeners();
            } else {
                alert('Ошибка загрузки: ' + data.error);
            }
        })
        .catch(error => {
            uploadProgress.style.display = 'none';
            alert('Ошибка загрузки фотографии');
            console.error(error);
        });
    });
}

// Delete photo handler
function attachPhotoButtonListeners() {
    document.querySelectorAll('.delete-photo-btn').forEach(btn => {
        btn.onclick = function(e) {
            e.preventDefault();
            if (!confirm('Удалить эту фотографию?')) return;

            const photoId = this.getAttribute('data-photo-id');

            fetch('delete_apartment_photo.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'photo_id=' + photoId
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove photo from DOM
                    const photoItem = document.querySelector(`.photo-item[data-photo-id="${photoId}"]`);
                    if (photoItem) photoItem.remove();
                } else {
                    alert('Ошибка удаления: ' + data.error);
                }
            })
            .catch(error => {
                alert('Ошибка удаления фотографии');
                console.error(error);
            });
        };
    });

    document.querySelectorAll('.set-main-btn').forEach(btn => {
        btn.onclick = function(e) {
            e.preventDefault();

            const photoId = this.getAttribute('data-photo-id');

            fetch('set_main_photo.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'photo_id=' + photoId + '&apartment_id=<?= $apartment['id'] ?>'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload page to update UI
                    location.reload();
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(error => {
                alert('Ошибка установки главной фотографии');
                console.error(error);
            });
        };
    });
}

// Attach listeners on page load
attachPhotoButtonListeners();
<?php endif; ?>
</script>

<?php include 'footer.php'; ?>
