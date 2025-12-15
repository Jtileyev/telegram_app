# Задача 002: CSRF защита в админ-панели

## Приоритет: 🔴 Высокий

## Описание
В PHP админ-панели отсутствует защита от CSRF атак. Нужно добавить CSRF токены во все формы.

## Шаги выполнения

### 1. Создать функции для работы с CSRF токенами
В файле `admin/config.php` добавить функции:

```php
// Generate CSRF token
function generateCSRFToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

// Validate CSRF token
function validateCSRFToken($token) {
    return isset($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
}

// Get CSRF input field
function csrfField() {
    return '<input type="hidden" name="csrf_token" value="' . generateCSRFToken() . '">';
}
```

### 2. Добавить CSRF поле во все формы
В каждой форме после `<form ...>` добавить:
```php
<?= csrfField() ?>
```

### 3. Валидировать токен при обработке POST-запросов
В начале обработки каждого POST-запроса добавить:
```php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!validateCSRFToken($_POST['csrf_token'] ?? '')) {
        setFlash('danger', 'Ошибка безопасности. Попробуйте снова.');
        header('Location: ' . $_SERVER['PHP_SELF']);
        exit;
    }
}
```

## Файлы для изменения
- `admin/config.php` - добавить функции
- `admin/login.php` - форма входа
- `admin/apartment_edit.php` - форма редактирования квартиры
- `admin/landlord_edit.php` - форма арендодателя
- `admin/user_edit.php` - форма пользователя
- `admin/promotion_edit.php` - форма акции
- `admin/settings.php` - форма настроек
- `admin/cities.php` - формы городов/районов
- `admin/amenity_edit.php` - форма удобств
- `admin/translations.php` - форма переводов
- `admin/bookings.php` - кнопки изменения статуса
- `admin/requests.php` - кнопки обработки заявок
- `admin/reviews.php` - модерация отзывов

## Критерии завершения
- [ ] Функции CSRF добавлены в config.php
- [ ] Все POST-формы содержат CSRF токен
- [ ] Все POST-обработчики валидируют токен
- [ ] Проверено, что формы работают корректно

## Примечания
- Токен должен быть уникальным для каждой сессии
- При невалидном токене показывать ошибку и редиректить
