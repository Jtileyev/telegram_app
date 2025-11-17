<?php
require_once 'config.php';
requireLogin();

$pageTitle = 'SQLite Browser';

$db = getDB();

// Get all tables
$tablesStmt = $db->query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name");
$tables = $tablesStmt->fetchAll(PDO::FETCH_COLUMN);

$selectedTable = $_GET['table'] ?? '';
$tableData = [];
$columns = [];
$rowCount = 0;

// Handle custom query
$customQuery = '';
$queryResult = null;
$queryError = '';

if (isset($_POST['run_query'])) {
    $customQuery = $_POST['query'] ?? '';
    if (!empty($customQuery)) {
        try {
            // Check if it's a SELECT query
            if (stripos(trim($customQuery), 'SELECT') === 0) {
                $stmt = $db->query($customQuery);
                $queryResult = $stmt->fetchAll();
            } else {
                $affected = $db->exec($customQuery);
                setFlash('success', "Запрос выполнен. Затронуто строк: $affected");
                header('Location: sqlite_browser.php');
                exit;
            }
        } catch (PDOException $e) {
            $queryError = $e->getMessage();
        }
    }
}

// Handle row delete
if (isset($_GET['delete']) && !empty($selectedTable)) {
    $id = $_GET['delete'];
    try {
        $stmt = $db->prepare("DELETE FROM $selectedTable WHERE id = ?");
        $stmt->execute([$id]);
        setFlash('success', 'Запись удалена');
        header("Location: sqlite_browser.php?table=$selectedTable");
        exit;
    } catch (PDOException $e) {
        setFlash('danger', 'Ошибка: ' . $e->getMessage());
    }
}

// Get table data
if (!empty($selectedTable) && in_array($selectedTable, $tables)) {
    $page = max(1, intval($_GET['page'] ?? 1));
    $perPage = 20;
    $offset = ($page - 1) * $perPage;

    // Get columns info
    $columnsStmt = $db->query("PRAGMA table_info($selectedTable)");
    $columns = $columnsStmt->fetchAll();

    // Get total count
    $countStmt = $db->query("SELECT COUNT(*) FROM $selectedTable");
    $rowCount = $countStmt->fetchColumn();

    // Get data
    $dataStmt = $db->query("SELECT * FROM $selectedTable LIMIT $perPage OFFSET $offset");
    $tableData = $dataStmt->fetchAll();

    $totalPages = ceil($rowCount / $perPage);
}

include 'header.php';
?>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">Таблицы</h6>
            </div>
            <div class="list-group list-group-flush">
                <?php foreach ($tables as $table): ?>
                <a href="?table=<?= $table ?>"
                   class="list-group-item list-group-item-action <?= $table === $selectedTable ? 'active' : '' ?>">
                    <i class="bi bi-table me-2"></i><?= $table ?>
                </a>
                <?php endforeach; ?>
            </div>
        </div>
    </div>

    <div class="col-md-9">
        <!-- Custom Query -->
        <div class="card mb-4">
            <div class="card-header">
                <h6 class="mb-0">SQL Запрос</h6>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <textarea name="query" class="form-control font-monospace" rows="4"
                                  placeholder="SELECT * FROM users LIMIT 10"><?= sanitize($customQuery) ?></textarea>
                    </div>
                    <button type="submit" name="run_query" class="btn btn-primary">
                        <i class="bi bi-play-fill me-1"></i>Выполнить
                    </button>
                </form>

                <?php if ($queryError): ?>
                <div class="alert alert-danger mt-3">
                    <strong>Ошибка:</strong> <?= sanitize($queryError) ?>
                </div>
                <?php endif; ?>

                <?php if ($queryResult !== null): ?>
                <div class="mt-3">
                    <h6>Результат (<?= count($queryResult) ?> строк):</h6>
                    <?php if (!empty($queryResult)): ?>
                    <div class="table-responsive">
                        <table class="table table-sm table-bordered">
                            <thead class="table-dark">
                                <tr>
                                    <?php foreach (array_keys($queryResult[0]) as $col): ?>
                                    <th><?= $col ?></th>
                                    <?php endforeach; ?>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($queryResult as $row): ?>
                                <tr>
                                    <?php foreach ($row as $value): ?>
                                    <td>
                                        <small><?= sanitize(mb_substr($value ?? 'NULL', 0, 100)) ?></small>
                                    </td>
                                    <?php endforeach; ?>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                    <?php else: ?>
                    <p class="text-muted">Нет результатов</p>
                    <?php endif; ?>
                </div>
                <?php endif; ?>
            </div>
        </div>

        <!-- Table Data -->
        <?php if (!empty($selectedTable)): ?>
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">
                    <i class="bi bi-table me-1"></i>
                    <?= $selectedTable ?>
                    <span class="badge bg-secondary"><?= $rowCount ?> записей</span>
                </h6>
            </div>
            <div class="card-body">
                <!-- Table Structure -->
                <div class="mb-3">
                    <button class="btn btn-sm btn-outline-info" type="button" data-bs-toggle="collapse"
                            data-bs-target="#tableStructure">
                        <i class="bi bi-info-circle me-1"></i>Структура таблицы
                    </button>
                    <div class="collapse mt-2" id="tableStructure">
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>Колонка</th>
                                    <th>Тип</th>
                                    <th>NOT NULL</th>
                                    <th>По умолчанию</th>
                                    <th>PK</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($columns as $col): ?>
                                <tr>
                                    <td><strong><?= $col['name'] ?></strong></td>
                                    <td><code><?= $col['type'] ?></code></td>
                                    <td><?= $col['notnull'] ? 'Да' : 'Нет' ?></td>
                                    <td><?= $col['dflt_value'] ?? '-' ?></td>
                                    <td><?= $col['pk'] ? '✓' : '' ?></td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Data -->
                <?php if (empty($tableData)): ?>
                <p class="text-muted">Таблица пуста</p>
                <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-sm table-bordered table-hover">
                        <thead class="table-dark">
                            <tr>
                                <?php foreach ($columns as $col): ?>
                                <th><?= $col['name'] ?></th>
                                <?php endforeach; ?>
                                <th>Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($tableData as $row): ?>
                            <tr>
                                <?php foreach ($columns as $col): ?>
                                <td>
                                    <small>
                                        <?php
                                        $value = $row[$col['name']];
                                        if ($value === null) {
                                            echo '<span class="text-muted">NULL</span>';
                                        } elseif (strlen($value) > 50) {
                                            echo sanitize(mb_substr($value, 0, 50)) . '...';
                                        } else {
                                            echo sanitize($value);
                                        }
                                        ?>
                                    </small>
                                </td>
                                <?php endforeach; ?>
                                <td>
                                    <?php if (isset($row['id'])): ?>
                                    <a href="?table=<?= $selectedTable ?>&delete=<?= $row['id'] ?>"
                                       class="btn btn-sm btn-outline-danger"
                                       onclick="return confirm('Удалить запись?')">
                                        <i class="bi bi-trash"></i>
                                    </a>
                                    <?php endif; ?>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <?php if ($totalPages > 1): ?>
                <nav>
                    <ul class="pagination pagination-sm justify-content-center">
                        <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                        <li class="page-item <?= $i === $page ? 'active' : '' ?>">
                            <a class="page-link" href="?table=<?= $selectedTable ?>&page=<?= $i ?>">
                                <?= $i ?>
                            </a>
                        </li>
                        <?php endfor; ?>
                    </ul>
                </nav>
                <?php endif; ?>
                <?php endif; ?>
            </div>
        </div>
        <?php else: ?>
        <div class="card">
            <div class="card-body text-center text-muted">
                <i class="bi bi-arrow-left fs-1"></i>
                <p>Выберите таблицу слева для просмотра данных</p>
            </div>
        </div>
        <?php endif; ?>
    </div>
</div>

<?php include 'footer.php'; ?>
