<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= isset($pageTitle) ? $pageTitle . ' - ' : '' ?>Аставайся - Админ панель</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.min.css" rel="stylesheet">
    <style>
        .sidebar {
            min-height: 100vh;
            background-color: #343a40;
        }
        .sidebar .nav-link {
            color: rgba(255,255,255,.75);
        }
        .sidebar .nav-link:hover {
            color: #fff;
        }
        .sidebar .nav-link.active {
            color: #fff;
            background-color: rgba(255,255,255,.1);
        }
        .main-content {
            min-height: 100vh;
            background-color: #f8f9fa;
        }
        .stat-card {
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        /* Mobile menu toggle button */
        .mobile-menu-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1050;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        /* Mobile responsive styles */
        @media (max-width: 767.98px) {
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                width: 280px;
                height: 100vh;
                z-index: 1040;
                transform: translateX(-100%);
                transition: transform 0.3s ease-in-out;
                overflow-y: auto;
            }
            .sidebar.show {
                transform: translateX(0);
            }
            .sidebar-backdrop {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
                z-index: 1035;
                display: none;
            }
            .sidebar-backdrop.show {
                display: block;
            }
            .main-content {
                margin-left: 0 !important;
                width: 100% !important;
                padding: 0 10px !important;
            }
            .main-content h1.h2 {
                font-size: 1.4rem;
            }
            /* Responsive stat cards */
            .stat-card .card-body {
                padding: 0.75rem;
            }
            .stat-card h2 {
                font-size: 1.5rem;
            }
            .stat-card .fs-1 {
                font-size: 2rem !important;
            }
            /* Responsive tables */
            .table-responsive {
                font-size: 0.85rem;
            }
            .table td, .table th {
                padding: 0.5rem 0.25rem;
                white-space: nowrap;
            }
            /* Responsive buttons */
            .btn-group {
                flex-wrap: wrap;
                gap: 0.25rem;
            }
            .btn-group .btn {
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
            }
            /* Responsive forms */
            .form-select-sm {
                font-size: 0.75rem;
            }
            /* Hide some columns on mobile */
            .hide-mobile {
                display: none !important;
            }
        }
        
        /* Tablet styles */
        @media (min-width: 768px) and (max-width: 991.98px) {
            .stat-card h2 {
                font-size: 1.3rem;
            }
            .table-responsive {
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <!-- Mobile sidebar backdrop -->
    <div class="sidebar-backdrop" id="sidebarBackdrop"></div>
    
    <!-- Mobile menu toggle button -->
    <button class="btn btn-dark mobile-menu-toggle d-md-none" id="mobileMenuToggle" type="button">
        <i class="bi bi-list fs-4"></i>
    </button>
    
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse p-0">
                <div class="position-sticky pt-3">
                    <div class="px-3 mb-4">
                        <h5 class="text-white">🏠 Аставайся</h5>
                        <small class="text-muted">Админ панель</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'index.php' ? 'active' : '' ?>" href="index.php">
                                <i class="bi bi-speedometer2 me-2"></i>Дашборд
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'apartments.php' ? 'active' : '' ?>" href="apartments.php">
                                <i class="bi bi-house me-2"></i>Квартиры
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'bookings.php' ? 'active' : '' ?>" href="bookings.php">
                                <i class="bi bi-calendar-check me-2"></i>Бронирования
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'reviews.php' ? 'active' : '' ?>" href="reviews.php">
                                <i class="bi bi-star me-2"></i>Отзывы
                            </a>
                        </li>
                        <?php if (isAdmin()): ?>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'users.php' ? 'active' : '' ?>" href="users.php">
                                <i class="bi bi-people me-2"></i>Пользователи
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'landlords.php' ? 'active' : '' ?>" href="landlords.php">
                                <i class="bi bi-person-badge me-2"></i>Арендодатели
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'cities.php' ? 'active' : '' ?>" href="cities.php">
                                <i class="bi bi-geo-alt me-2"></i>Города и районы
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= in_array(basename($_SERVER['PHP_SELF']), ['amenities.php', 'amenity_edit.php']) ? 'active' : '' ?>" href="amenities.php">
                                <i class="bi bi-grid-3x3-gap me-2"></i>Удобства
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= in_array(basename($_SERVER['PHP_SELF']), ['promotions.php', 'promotion_edit.php']) ? 'active' : '' ?>" href="promotions.php">
                                <i class="bi bi-gift me-2"></i>Акции
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'requests.php' ? 'active' : '' ?>" href="requests.php">
                                <i class="bi bi-envelope me-2"></i>Заявки
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'translations.php' ? 'active' : '' ?>" href="translations.php">
                                <i class="bi bi-translate me-2"></i>Редактор переводов
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'settings.php' ? 'active' : '' ?>" href="settings.php">
                                <i class="bi bi-gear me-2"></i>Настройки
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'qa_tests.php' ? 'active' : '' ?>" href="qa_tests.php">
                                <i class="bi bi-check2-square me-2"></i>QA Тесты
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'db_admin.php' ? 'active' : '' ?>" href="db_admin.php">
                                <i class="bi bi-database-gear me-2"></i>phpLiteAdmin
                            </a>
                        </li>
                        <?php endif; ?>
                        <li class="nav-item mt-4">
                            <a class="nav-link text-danger" href="logout.php">
                                <i class="bi bi-box-arrow-right me-2"></i>Выход
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2"><?= isset($pageTitle) ? $pageTitle : 'Дашборд' ?></h1>
                    <div class="btn-toolbar mb-2 mb-md-0">
                        <?php if (isset($pageActions)): ?>
                            <?= $pageActions ?>
                        <?php endif; ?>
                    </div>
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
