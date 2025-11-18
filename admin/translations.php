<?php
require_once 'config.php';
requireAdmin(); // Only admins can edit translations

$pageTitle = 'Редактор переводов';

$db = getDB();

// Handle translation update
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['update_translation'])) {
    $key = $_POST['key'];
    $text_ru = $_POST['text_ru'];
    $text_kk = $_POST['text_kk'];

    // Update or insert translation
    $stmt = $db->prepare("
        INSERT INTO translations (key, text_ru, text_kk, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            text_ru = excluded.text_ru,
            text_kk = excluded.text_kk,
            updated_at = CURRENT_TIMESTAMP
    ");
    $stmt->execute([$key, $text_ru, $text_kk]);

    setFlash('success', 'Перевод успешно обновлен');
    header('Location: translations.php');
    exit;
}

// Handle reset to default
if (isset($_GET['reset']) && !empty($_GET['reset'])) {
    $key = $_GET['reset'];
    $stmt = $db->prepare("DELETE FROM translations WHERE key = ?");
    $stmt->execute([$key]);
    setFlash('success', 'Перевод сброшен к значению по умолчанию');
    header('Location: translations.php');
    exit;
}

// Get all translations from database
$stmt = $db->query("SELECT * FROM translations ORDER BY key");
$db_translations = [];
foreach ($stmt->fetchAll() as $row) {
    $db_translations[$row['key']] = $row;
}

// Load default translations from Python file
$locales_file = __DIR__ . '/../bot/locales.py';
$default_translations = [];

if (file_exists($locales_file)) {
    $content = file_get_contents($locales_file);

    // Parse Russian translations
    if (preg_match("/'ru':\s*\{(.*?)\n\s*\},\s*'kk'/s", $content, $matches)) {
        $ru_block = $matches[1];
        preg_match_all("/'([^']+)':\s*'''(.+?)'''/s", $ru_block, $multiline_matches);
        preg_match_all("/'([^']+)':\s*'([^']*?)'/", $ru_block, $single_matches);

        foreach ($multiline_matches[1] as $i => $key) {
            $default_translations[$key]['text_ru'] = trim($multiline_matches[2][$i]);
        }
        foreach ($single_matches[1] as $i => $key) {
            if (!isset($default_translations[$key])) {
                $default_translations[$key]['text_ru'] = $single_matches[2][$i];
            }
        }
    }

    // Parse Kazakh translations
    if (preg_match("/'kk':\s*\{(.*?)\n\s*\}/s", $content, $matches)) {
        $kk_block = $matches[1];
        preg_match_all("/'([^']+)':\s*'''(.+?)'''/s", $kk_block, $multiline_matches);
        preg_match_all("/'([^']+)':\s*'([^']*?)'/", $kk_block, $single_matches);

        foreach ($multiline_matches[1] as $i => $key) {
            $default_translations[$key]['text_kk'] = trim($multiline_matches[2][$i]);
        }
        foreach ($single_matches[1] as $i => $key) {
            if (!isset($default_translations[$key]['text_kk'])) {
                $default_translations[$key]['text_kk'] = $single_matches[2][$i];
            }
        }
    }
}

// Merge database translations with defaults
$all_translations = [];
foreach ($default_translations as $key => $texts) {
    if (isset($texts['text_ru']) && isset($texts['text_kk'])) {
        $all_translations[$key] = [
            'key' => $key,
            'text_ru' => $db_translations[$key]['text_ru'] ?? $texts['text_ru'],
            'text_kk' => $db_translations[$key]['text_kk'] ?? $texts['text_kk'],
            'default_ru' => $texts['text_ru'],
            'default_kk' => $texts['text_kk'],
            'is_custom' => isset($db_translations[$key])
        ];
    }
}

// Sort by key
ksort($all_translations);

// Pagination
$per_page = 20;
$page = isset($_GET['page']) ? max(1, intval($_GET['page'])) : 1;
$offset = ($page - 1) * $per_page;
$total = count($all_translations);
$total_pages = ceil($total / $per_page);
$translations_page = array_slice($all_translations, $offset, $per_page);

// Search filter
$search = isset($_GET['search']) ? trim($_GET['search']) : '';
if ($search) {
    $translations_page = array_filter($all_translations, function($t) use ($search) {
        return stripos($t['key'], $search) !== false ||
               stripos($t['text_ru'], $search) !== false ||
               stripos($t['text_kk'], $search) !== false;
    });
    $total = count($translations_page);
    $total_pages = ceil($total / $per_page);
    $translations_page = array_slice($translations_page, $offset, $per_page);
}

include 'header.php';
?>

<div class="card mb-4">
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <p class="mb-0">
                    <i class="bi bi-info-circle me-2"></i>
                    Здесь вы можете редактировать тексты бота на русском и казахском языках.
                </p>
            </div>
            <div class="col-md-6">
                <form method="GET" class="d-flex">
                    <input type="text" name="search" class="form-control me-2"
                           placeholder="Поиск по ключу или тексту..."
                           value="<?= htmlspecialchars($search) ?>">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-search"></i>
                    </button>
                    <?php if ($search): ?>
                    <a href="translations.php" class="btn btn-secondary ms-2">
                        <i class="bi bi-x"></i>
                    </a>
                    <?php endif; ?>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th style="width: 20%">Ключ</th>
                        <th style="width: 35%">Русский</th>
                        <th style="width: 35%">Казахский</th>
                        <th style="width: 10%">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($translations_page as $trans): ?>
                    <tr>
                        <td>
                            <code><?= htmlspecialchars($trans['key']) ?></code>
                            <?php if ($trans['is_custom']): ?>
                            <br><span class="badge bg-success">Изменен</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <button type="button" class="btn btn-link btn-sm p-0"
                                    data-bs-toggle="modal"
                                    data-bs-target="#editModal<?= md5($trans['key']) ?>">
                                <small><?= nl2br(htmlspecialchars(substr($trans['text_ru'], 0, 100))) ?><?= strlen($trans['text_ru']) > 100 ? '...' : '' ?></small>
                            </button>
                        </td>
                        <td>
                            <button type="button" class="btn btn-link btn-sm p-0"
                                    data-bs-toggle="modal"
                                    data-bs-target="#editModal<?= md5($trans['key']) ?>">
                                <small><?= nl2br(htmlspecialchars(substr($trans['text_kk'], 0, 100))) ?><?= strlen($trans['text_kk']) > 100 ? '...' : '' ?></small>
                            </button>
                        </td>
                        <td>
                            <button type="button" class="btn btn-sm btn-outline-primary"
                                    data-bs-toggle="modal"
                                    data-bs-target="#editModal<?= md5($trans['key']) ?>">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <?php if ($trans['is_custom']): ?>
                            <a href="?reset=<?= urlencode($trans['key']) ?>"
                               class="btn btn-sm btn-outline-warning"
                               onclick="return confirm('Сбросить перевод к значению по умолчанию?')"
                               title="Сбросить">
                                <i class="bi bi-arrow-counterclockwise"></i>
                            </a>
                            <?php endif; ?>
                        </td>
                    </tr>

                    <!-- Edit Modal -->
                    <div class="modal fade" id="editModal<?= md5($trans['key']) ?>" tabindex="-1">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <form method="POST">
                                    <div class="modal-header">
                                        <h5 class="modal-title">
                                            <i class="bi bi-pencil me-2"></i>Редактирование перевода
                                        </h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <input type="hidden" name="key" value="<?= htmlspecialchars($trans['key']) ?>">

                                        <div class="mb-3">
                                            <label class="form-label">Ключ:</label>
                                            <code><?= htmlspecialchars($trans['key']) ?></code>
                                        </div>

                                        <div class="mb-3">
                                            <label class="form-label">🇷🇺 Русский:</label>
                                            <textarea name="text_ru" class="form-control" rows="5" required><?= htmlspecialchars($trans['text_ru']) ?></textarea>
                                            <?php if ($trans['is_custom'] && $trans['text_ru'] !== $trans['default_ru']): ?>
                                            <small class="text-muted">
                                                По умолчанию: <?= nl2br(htmlspecialchars($trans['default_ru'])) ?>
                                            </small>
                                            <?php endif; ?>
                                        </div>

                                        <div class="mb-3">
                                            <label class="form-label">🇰🇿 Казахский:</label>
                                            <textarea name="text_kk" class="form-control" rows="5" required><?= htmlspecialchars($trans['text_kk']) ?></textarea>
                                            <?php if ($trans['is_custom'] && $trans['text_kk'] !== $trans['default_kk']): ?>
                                            <small class="text-muted">
                                                По умолчанию: <?= nl2br(htmlspecialchars($trans['default_kk'])) ?>
                                            </small>
                                            <?php endif; ?>
                                        </div>

                                        <div class="alert alert-info">
                                            <i class="bi bi-info-circle me-2"></i>
                                            <small>
                                                Поддерживаются переменные: {name}, {price}, {address}, {date}, и др.<br>
                                                Используйте \n для переноса строки.
                                            </small>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                            Отмена
                                        </button>
                                        <button type="submit" name="update_translation" class="btn btn-primary">
                                            <i class="bi bi-save me-1"></i>Сохранить
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                    <?php endforeach; ?>

                    <?php if (empty($translations_page)): ?>
                    <tr>
                        <td colspan="4" class="text-center text-muted">
                            <?= $search ? 'Ничего не найдено' : 'Нет переводов' ?>
                        </td>
                    </tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

        <?php if ($total_pages > 1): ?>
        <nav>
            <ul class="pagination justify-content-center">
                <li class="page-item <?= $page <= 1 ? 'disabled' : '' ?>">
                    <a class="page-link" href="?page=<?= $page - 1 ?><?= $search ? '&search=' . urlencode($search) : '' ?>">
                        Назад
                    </a>
                </li>
                <?php for ($i = max(1, $page - 2); $i <= min($total_pages, $page + 2); $i++): ?>
                <li class="page-item <?= $i == $page ? 'active' : '' ?>">
                    <a class="page-link" href="?page=<?= $i ?><?= $search ? '&search=' . urlencode($search) : '' ?>">
                        <?= $i ?>
                    </a>
                </li>
                <?php endfor; ?>
                <li class="page-item <?= $page >= $total_pages ? 'disabled' : '' ?>">
                    <a class="page-link" href="?page=<?= $page + 1 ?><?= $search ? '&search=' . urlencode($search) : '' ?>">
                        Вперед
                    </a>
                </li>
            </ul>
        </nav>
        <?php endif; ?>

        <div class="text-center text-muted mt-3">
            <small>Всего переводов: <?= $total ?> | Страница <?= $page ?> из <?= $total_pages ?></small>
        </div>
    </div>
</div>

<?php include 'footer.php'; ?>
