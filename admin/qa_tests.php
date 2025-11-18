<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'QA Тесты';

// Run tests if requested
$testResults = null;
$testOutput = '';
$runTime = 0;

if (isset($_POST['run_tests'])) {
    $startTime = microtime(true);

    // Run Python tests
    $pythonPath = 'python3';
    $testsPath = __DIR__ . '/../bot/tests.py';

    // Execute tests
    $command = escapeshellcmd("$pythonPath $testsPath 2>&1");
    $output = [];
    $returnCode = 0;
    exec($command, $output, $returnCode);

    $testOutput = implode("\n", $output);
    $runTime = microtime(true) - $startTime;

    // Parse test results
    $testResults = [
        'success' => $returnCode === 0,
        'return_code' => $returnCode,
        'output' => $testOutput,
        'run_time' => round($runTime, 2),
        'timestamp' => date('Y-m-d H:i:s')
    ];

    // Save test results to database
    $db = getDB();
    $stmt = $db->prepare("
        INSERT INTO settings (key, value, description, updated_at)
        VALUES ('last_test_run', ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            description = excluded.description,
            updated_at = CURRENT_TIMESTAMP
    ");
    $stmt->execute([
        json_encode($testResults),
        'Last QA test run results'
    ]);

    setFlash(
        $testResults['success'] ? 'success' : 'danger',
        $testResults['success'] ? 'Все тесты пройдены успешно!' : 'Некоторые тесты провалились!'
    );
}

// Get last test run
$db = getDB();
$stmt = $db->query("SELECT value FROM settings WHERE key = 'last_test_run'");
$lastTest = $stmt->fetchColumn();
$lastTestResults = $lastTest ? json_decode($lastTest, true) : null;

// Get database statistics
$stats = [];
$stats['users'] = $db->query("SELECT COUNT(*) FROM users")->fetchColumn();
$stats['apartments'] = $db->query("SELECT COUNT(*) FROM apartments")->fetchColumn();
$stats['bookings'] = $db->query("SELECT COUNT(*) FROM bookings")->fetchColumn();
$stats['reviews'] = $db->query("SELECT COUNT(*) FROM reviews")->fetchColumn();
$stats['landlords'] = $db->query("SELECT COUNT(*) FROM landlords")->fetchColumn();

include 'header.php';
?>

<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Запуск QA тестов</h5>
                <form method="POST" class="d-inline">
                    <button type="submit" name="run_tests" class="btn btn-primary">
                        <i class="bi bi-play-circle me-1"></i>Запустить тесты
                    </button>
                </form>
            </div>
            <div class="card-body">
                <p class="text-muted">
                    Автоматические тесты проверяют работоспособность основных функций системы:
                    базы данных, локализации, валидации и бизнес-логики.
                </p>

                <?php if ($testResults): ?>
                <div class="alert alert-<?= $testResults['success'] ? 'success' : 'danger' ?>">
                    <h6>
                        <i class="bi bi-<?= $testResults['success'] ? 'check-circle' : 'x-circle' ?> me-2"></i>
                        Результат: <?= $testResults['success'] ? 'Успешно' : 'Провалено' ?>
                    </h6>
                    <small>
                        Время выполнения: <?= $testResults['run_time'] ?> сек<br>
                        Дата: <?= $testResults['timestamp'] ?>
                    </small>
                </div>

                <div class="card bg-dark text-white">
                    <div class="card-header">
                        <h6 class="mb-0">Вывод тестов</h6>
                    </div>
                    <div class="card-body">
                        <pre class="mb-0" style="max-height: 400px; overflow-y: auto; font-size: 12px;"><?= htmlspecialchars($testResults['output']) ?></pre>
                    </div>
                </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>

<?php if ($lastTestResults): ?>
<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Последний запуск тестов</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <div class="display-1">
                                <i class="bi bi-<?= $lastTestResults['success'] ? 'check-circle text-success' : 'x-circle text-danger' ?>"></i>
                            </div>
                            <h6 class="mt-2"><?= $lastTestResults['success'] ? 'Успешно' : 'Провалено' ?></h6>
                        </div>
                    </div>
                    <div class="col-md-9">
                        <table class="table table-sm">
                            <tr>
                                <th>Дата запуска:</th>
                                <td><?= $lastTestResults['timestamp'] ?></td>
                            </tr>
                            <tr>
                                <th>Время выполнения:</th>
                                <td><?= $lastTestResults['run_time'] ?> секунд</td>
                            </tr>
                            <tr>
                                <th>Код возврата:</th>
                                <td><?= $lastTestResults['return_code'] ?></td>
                            </tr>
                        </table>

                        <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#lastTestOutput">
                            <i class="bi bi-code me-1"></i>Показать вывод
                        </button>

                        <div class="collapse mt-3" id="lastTestOutput">
                            <div class="card bg-dark text-white">
                                <div class="card-body">
                                    <pre class="mb-0" style="max-height: 300px; overflow-y: auto; font-size: 12px;"><?= htmlspecialchars($lastTestResults['output']) ?></pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<?php endif; ?>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Статистика базы данных</h5>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-md-2">
                        <div class="p-3 bg-light rounded">
                            <h3 class="text-primary"><?= $stats['users'] ?></h3>
                            <small class="text-muted">Пользователей</small>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="p-3 bg-light rounded">
                            <h3 class="text-success"><?= $stats['apartments'] ?></h3>
                            <small class="text-muted">Квартир</small>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="p-3 bg-light rounded">
                            <h3 class="text-info"><?= $stats['bookings'] ?></h3>
                            <small class="text-muted">Бронирований</small>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="p-3 bg-light rounded">
                            <h3 class="text-warning"><?= $stats['reviews'] ?></h3>
                            <small class="text-muted">Отзывов</small>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="p-3 bg-light rounded">
                            <h3 class="text-secondary"><?= $stats['landlords'] ?></h3>
                            <small class="text-muted">Арендодателей</small>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="p-3 bg-light rounded">
                            <?php
                            $dbSize = filesize(DB_PATH);
                            $dbSizeMB = round($dbSize / 1024 / 1024, 2);
                            ?>
                            <h3 class="text-dark"><?= $dbSizeMB ?> MB</h3>
                            <small class="text-muted">Размер БД</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Покрытие тестами</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Модуль</th>
                                <th>Описание</th>
                                <th>Статус</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Database</strong></td>
                                <td>Операции с базой данных (создание, чтение, обновление)</td>
                                <td><span class="badge bg-success">Покрыто</span></td>
                            </tr>
                            <tr>
                                <td><strong>Localization</strong></td>
                                <td>Мультиязычность (RU/KK)</td>
                                <td><span class="badge bg-success">Покрыто</span></td>
                            </tr>
                            <tr>
                                <td><strong>Validation</strong></td>
                                <td>Валидация данных (телефон, email)</td>
                                <td><span class="badge bg-success">Покрыто</span></td>
                            </tr>
                            <tr>
                                <td><strong>Business Logic</strong></td>
                                <td>Бизнес-логика (бронирования, отзывы)</td>
                                <td><span class="badge bg-success">Покрыто</span></td>
                            </tr>
                            <tr>
                                <td><strong>Bot Handlers</strong></td>
                                <td>Обработчики команд бота</td>
                                <td><span class="badge bg-warning">Частично</span></td>
                            </tr>
                            <tr>
                                <td><strong>Admin Panel</strong></td>
                                <td>Административная панель</td>
                                <td><span class="badge bg-warning">Частично</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
