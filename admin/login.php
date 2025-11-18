<?php
require_once 'config.php';

// Logout if already logged in and accessing login page
if (isLoggedIn() && !isset($_POST['email']) && !isset($_POST['password'])) {
    // Don't auto-logout, just redirect
    if (isset($_GET['logout'])) {
        session_destroy();
    } else {
        header('Location: index.php');
        exit;
    }
}

$error = '';
$step = 'email'; // 'email', 'password', or 'set_password'
$email = '';
$user = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $db = getDB();

    // Step 1: Check email
    if (isset($_POST['check_email'])) {
        $email = trim($_POST['email']);

        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $error = 'Введите корректный email';
        } else {
            // Check in users table
            $stmt = $db->prepare("SELECT * FROM users WHERE email = ? AND is_active = 1");
            $stmt->execute([$email]);
            $foundUser = $stmt->fetch();

            if ($foundUser) {
                $roles = json_decode($foundUser['roles'], true) ?: [];

                // Check if user has admin or landlord role
                if (in_array('admin', $roles) || in_array('landlord', $roles)) {
                    $user = [
                        'id' => $foundUser['id'],
                        'email' => $foundUser['email'],
                        'full_name' => $foundUser['full_name'],
                        'password' => $foundUser['password'],
                        'roles' => $roles
                    ];

                    // Check if password is set
                    if (empty($foundUser['password'])) {
                        $step = 'set_password';
                    } else {
                        $step = 'password';
                    }
                } else {
                    $error = 'У вас нет доступа к админ-панели';
                }
            } else {
                $error = 'Пользователь с таким email не найден';
            }

            // Store user data in session temporarily
            if ($user) {
                $_SESSION['temp_user'] = $user;
            }
        }
    }

    // Step 2: Check password
    elseif (isset($_POST['check_password'])) {
        if (isset($_SESSION['temp_user'])) {
            $user = $_SESSION['temp_user'];
            $password = $_POST['password'];

            if (password_verify($password, $user['password'])) {
                // Login successful
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['user_roles'] = $user['roles'];
                $_SESSION['user_email'] = $user['email'];
                $_SESSION['user_name'] = $user['full_name'];

                // Update last login
                $stmt = $db->prepare("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?");
                $stmt->execute([$user['id']]);

                unset($_SESSION['temp_user']);
                header('Location: index.php');
                exit;
            } else {
                $error = 'Неверный пароль';
                $step = 'password';
                $email = $user['email'];
            }
        } else {
            header('Location: login.php');
            exit;
        }
    }

    // Step 3: Set new password
    elseif (isset($_POST['set_password'])) {
        if (isset($_SESSION['temp_user'])) {
            $user = $_SESSION['temp_user'];
            $password = $_POST['new_password'];
            $confirm_password = $_POST['confirm_password'];

            if (strlen($password) < 6) {
                $error = 'Пароль должен содержать минимум 6 символов';
                $step = 'set_password';
                $email = $user['email'];
            } elseif ($password !== $confirm_password) {
                $error = 'Пароли не совпадают';
                $step = 'set_password';
                $email = $user['email'];
            } else {
                // Set password
                $hashed_password = password_hash($password, PASSWORD_DEFAULT);

                $stmt = $db->prepare("UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
                $stmt->execute([$hashed_password, $user['id']]);

                // Auto-login
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['user_roles'] = $user['roles'];
                $_SESSION['user_email'] = $user['email'];
                $_SESSION['user_name'] = $user['full_name'];

                unset($_SESSION['temp_user']);
                header('Location: index.php');
                exit;
            }
        } else {
            header('Location: login.php');
            exit;
        }
    }
}

// Get user data if in password step
if (($step === 'password' || $step === 'set_password') && isset($_SESSION['temp_user'])) {
    $user = $_SESSION['temp_user'];
    $email = $user['email'];
}
?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход - Аставайся Админ</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .login-card {
            max-width: 400px;
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="card shadow">
            <div class="card-body p-4">
                <div class="text-center mb-4">
                    <h3>🏠 Аставайся</h3>
                    <p class="text-muted">Вход в панель управления</p>
                </div>

                <?php if ($error): ?>
                <div class="alert alert-danger"><?= $error ?></div>
                <?php endif; ?>

                <?php if ($step === 'email'): ?>
                <!-- Step 1: Email -->
                <form method="POST">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email"
                               placeholder="your@email.com" value="<?= htmlspecialchars($email) ?>" required autofocus>
                        <small class="text-muted">Введите ваш email для входа</small>
                    </div>
                    <button type="submit" name="check_email" class="btn btn-primary w-100">Продолжить</button>
                </form>

                <?php elseif ($step === 'password'): ?>
                <!-- Step 2: Password -->
                <div class="mb-3">
                    <strong><?= htmlspecialchars($user['full_name'] ?? $email) ?></strong><br>
                    <small class="text-muted"><?= htmlspecialchars($email) ?></small>
                </div>

                <form method="POST">
                    <div class="mb-3">
                        <label for="password" class="form-label">Пароль</label>
                        <input type="password" class="form-control" id="password" name="password" required autofocus>
                    </div>
                    <button type="submit" name="check_password" class="btn btn-primary w-100">Войти</button>
                </form>

                <div class="text-center mt-3">
                    <a href="login.php" class="text-muted small">← Назад</a>
                </div>

                <?php elseif ($step === 'set_password'): ?>
                <!-- Step 3: Set Password -->
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    <strong>Добро пожаловать!</strong><br>
                    Вы впервые входите в систему. Пожалуйста, создайте пароль для вашего аккаунта.
                </div>

                <div class="mb-3">
                    <strong><?= htmlspecialchars($user['full_name']) ?></strong><br>
                    <small class="text-muted"><?= htmlspecialchars($email) ?></small>
                </div>

                <form method="POST">
                    <div class="mb-3">
                        <label for="new_password" class="form-label">Новый пароль</label>
                        <input type="password" class="form-control" id="new_password" name="new_password"
                               minlength="6" required autofocus>
                        <small class="text-muted">Минимум 6 символов</small>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password" class="form-label">Подтвердите пароль</label>
                        <input type="password" class="form-control" id="confirm_password" name="confirm_password"
                               minlength="6" required>
                    </div>
                    <button type="submit" name="set_password" class="btn btn-primary w-100">Создать пароль и войти</button>
                </form>
                <?php endif; ?>
            </div>
        </div>
    </div>
</body>
</html>
