<?php
/**
 * Admin Panel Tests
 * Tests for admin panel logic, authentication, and role-based access
 */

// Prevent direct execution in production
if (php_sapi_name() !== 'cli') {
    die('Tests can only be run from command line');
}

require_once __DIR__ . '/config.php';

class AdminPanelTests
{
    private $db;
    private $testResults = [];
    private $testsPassed = 0;
    private $testsFailed = 0;

    public function __construct()
    {
        // Use test database
        $testDbPath = __DIR__ . '/../database/rental_test.db';

        // Remove old test database
        if (file_exists($testDbPath)) {
            unlink($testDbPath);
        }

        // Create new test database
        $this->db = new PDO('sqlite:' . $testDbPath);
        $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Load schema
        $schema = file_get_contents(__DIR__ . '/../database/schema.sql');
        $this->db->exec($schema);
    }

    public function __destruct()
    {
        // Clean up test database
        $testDbPath = __DIR__ . '/../database/rental_test.db';
        if (file_exists($testDbPath)) {
            unlink($testDbPath);
        }
    }

    private function assert($condition, $message)
    {
        if ($condition) {
            $this->testsPassed++;
            $this->testResults[] = "✓ PASS: $message";
            echo "✓ $message\n";
        } else {
            $this->testsFailed++;
            $this->testResults[] = "✗ FAIL: $message";
            echo "✗ $message\n";
        }
    }

    private function assertEqual($expected, $actual, $message)
    {
        $this->assert($expected === $actual, $message . " (Expected: $expected, Got: $actual)");
    }

    public function testDatabaseConnection()
    {
        echo "\n=== Testing Database Connection ===\n";
        $this->assert($this->db !== null, "Database connection established");
    }

    public function testAdminAuthentication()
    {
        echo "\n=== Testing Admin Authentication ===\n";

        // Test admin exists
        $stmt = $this->db->query("SELECT * FROM admins WHERE username = 'admin'");
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        $this->assert($admin !== false, "Default admin user exists");

        // Test password hashing (admin123)
        $this->assert(
            password_verify('admin123', $admin['password']),
            "Admin password verification works"
        );
    }

    public function testLandlordCreation()
    {
        echo "\n=== Testing Landlord Creation ===\n";

        // Create landlord
        $stmt = $this->db->prepare(
            "INSERT INTO landlords (telegram_id, full_name, phone, email) VALUES (?, ?, ?, ?)"
        );
        $result = $stmt->execute([123456789, "Test Landlord", "+7 777 777 77 77", "test@landlord.com"]);

        $this->assert($result, "Landlord created successfully");

        // Verify landlord
        $stmt = $this->db->prepare("SELECT * FROM landlords WHERE telegram_id = ?");
        $stmt->execute([123456789]);
        $landlord = $stmt->fetch(PDO::FETCH_ASSOC);

        $this->assert($landlord !== false, "Landlord retrieved from database");
        $this->assertEqual("test@landlord.com", $landlord['email'], "Landlord email stored correctly");
    }

    public function testRoleBasedQueries()
    {
        echo "\n=== Testing Role-Based Queries ===\n";

        // Create test landlord
        $stmt = $this->db->prepare(
            "INSERT INTO landlords (telegram_id, full_name, phone, email) VALUES (?, ?, ?, ?)"
        );
        $stmt->execute([987654321, "Role Test Landlord", "+7 777 888 99 00", "role@test.com"]);
        $landlordId = $this->db->lastInsertId();

        // Create apartment for landlord
        $stmt = $this->db->prepare(
            "INSERT INTO apartments (landlord_id, city_id, district_id, title_ru, title_kk, address, price_per_day)
             VALUES (?, ?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([$landlordId, 1, 1, "Test Apartment", "Test Apartment KK", "Test Address", 10000]);
        $apartmentId = $this->db->lastInsertId();

        // Test filtering by landlord_id
        $stmt = $this->db->prepare(
            "SELECT * FROM apartments WHERE landlord_id = ?"
        );
        $stmt->execute([$landlordId]);
        $apartments = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $this->assert(count($apartments) === 1, "Landlord can see only their apartments");
        $this->assertEqual($apartmentId, $apartments[0]['id'], "Correct apartment returned");
    }

    public function testBookingCreation()
    {
        echo "\n=== Testing Booking Creation ===\n";

        // Create test user
        $stmt = $this->db->prepare(
            "INSERT INTO users (telegram_id, username, full_name, phone, language) VALUES (?, ?, ?, ?, ?)"
        );
        $stmt->execute([111222333, "testuser", "Test User", "+7 777 111 22 33", "ru"]);
        $userId = $this->db->lastInsertId();

        // Create landlord and apartment
        $stmt = $this->db->prepare(
            "INSERT INTO landlords (telegram_id, full_name, phone, email) VALUES (?, ?, ?, ?)"
        );
        $stmt->execute([444555666, "Booking Test Landlord", "+7 777 444 55 66", "booking@test.com"]);
        $landlordId = $this->db->lastInsertId();

        $stmt = $this->db->prepare(
            "INSERT INTO apartments (landlord_id, city_id, district_id, title_ru, title_kk, address, price_per_day)
             VALUES (?, ?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([$landlordId, 1, 1, "Booking Test Apt", "Booking Test Apt KK", "Test Address", 15000]);
        $apartmentId = $this->db->lastInsertId();

        // Create booking
        $checkIn = date('Y-m-d', strtotime('+7 days'));
        $checkOut = date('Y-m-d', strtotime('+10 days'));

        $stmt = $this->db->prepare(
            "INSERT INTO bookings (user_id, apartment_id, landlord_id, check_in_date, check_out_date, total_price, platform_fee, status)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([$userId, $apartmentId, $landlordId, $checkIn, $checkOut, 45000, 2250, 'pending']);
        $bookingId = $this->db->lastInsertId();

        $this->assert($bookingId > 0, "Booking created successfully");

        // Test booking status update
        $stmt = $this->db->prepare("UPDATE bookings SET status = ? WHERE id = ?");
        $stmt->execute(['confirmed', $bookingId]);

        $stmt = $this->db->prepare("SELECT status FROM bookings WHERE id = ?");
        $stmt->execute([$bookingId]);
        $booking = $stmt->fetch(PDO::FETCH_ASSOC);

        $this->assertEqual('confirmed', $booking['status'], "Booking status updated correctly");
    }

    public function testEmailValidation()
    {
        echo "\n=== Testing Email Validation ===\n";

        $validEmails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.com',
        ];

        foreach ($validEmails as $email) {
            $isValid = filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
            $this->assert($isValid, "Email '$email' is valid");
        }

        $invalidEmails = [
            'invalid.email',
            '@example.com',
            'user@',
        ];

        foreach ($invalidEmails as $email) {
            $isValid = filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
            $this->assert(!$isValid, "Email '$email' is invalid");
        }
    }

    public function testSanitization()
    {
        echo "\n=== Testing Data Sanitization ===\n";

        $dangerousInput = "<script>alert('XSS')</script>";
        $sanitized = htmlspecialchars($dangerousInput, ENT_QUOTES, 'UTF-8');

        $this->assert(
            strpos($sanitized, '<script>') === false,
            "XSS attempt sanitized"
        );

        $this->assert(
            strpos($sanitized, '&lt;script&gt;') !== false,
            "Dangerous tags properly escaped"
        );
    }

    public function testLandlordRequestFlow()
    {
        echo "\n=== Testing Landlord Request Flow ===\n";

        // Create landlord request
        $stmt = $this->db->prepare(
            "INSERT INTO landlord_requests (telegram_id, full_name, phone, email, status) VALUES (?, ?, ?, ?, ?)"
        );
        $stmt->execute([777888999, "Request Test", "+7 777 888 99 00", "request@test.com", "pending"]);
        $requestId = $this->db->lastInsertId();

        $this->assert($requestId > 0, "Landlord request created");

        // Approve request
        $stmt = $this->db->prepare("SELECT * FROM landlord_requests WHERE id = ?");
        $stmt->execute([$requestId]);
        $request = $stmt->fetch(PDO::FETCH_ASSOC);

        // Create landlord from request
        $stmt = $this->db->prepare(
            "INSERT INTO landlords (telegram_id, full_name, phone, email) VALUES (?, ?, ?, ?)"
        );
        $stmt->execute([
            $request['telegram_id'],
            $request['full_name'],
            $request['phone'],
            $request['email']
        ]);

        // Update request status
        $stmt = $this->db->prepare("UPDATE landlord_requests SET status = 'approved' WHERE id = ?");
        $stmt->execute([$requestId]);

        // Verify
        $stmt = $this->db->prepare("SELECT status FROM landlord_requests WHERE id = ?");
        $stmt->execute([$requestId]);
        $updatedRequest = $stmt->fetch(PDO::FETCH_ASSOC);

        $this->assertEqual('approved', $updatedRequest['status'], "Request status updated to approved");
    }

    public function testReviewSystem()
    {
        echo "\n=== Testing Review System ===\n";

        // Create necessary records
        $stmt = $this->db->prepare(
            "INSERT INTO users (telegram_id, username, full_name, phone, language) VALUES (?, ?, ?, ?, ?)"
        );
        $stmt->execute([999888777, "reviewer", "Review User", "+7 777 999 88 77", "ru"]);
        $userId = $this->db->lastInsertId();

        $stmt = $this->db->prepare(
            "INSERT INTO landlords (telegram_id, full_name, phone, email) VALUES (?, ?, ?, ?)"
        );
        $stmt->execute([666555444, "Review Landlord", "+7 777 666 55 44", "review@test.com"]);
        $landlordId = $this->db->lastInsertId();

        $stmt = $this->db->prepare(
            "INSERT INTO apartments (landlord_id, city_id, district_id, title_ru, title_kk, address, price_per_day)
             VALUES (?, ?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([$landlordId, 1, 1, "Review Test Apt", "Review Test Apt KK", "Test Address", 12000]);
        $apartmentId = $this->db->lastInsertId();

        $checkIn = date('Y-m-d', strtotime('-7 days'));
        $checkOut = date('Y-m-d', strtotime('-3 days'));

        $stmt = $this->db->prepare(
            "INSERT INTO bookings (user_id, apartment_id, landlord_id, check_in_date, check_out_date, total_price, platform_fee, status)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([$userId, $apartmentId, $landlordId, $checkIn, $checkOut, 48000, 2400, 'completed']);
        $bookingId = $this->db->lastInsertId();

        // Create review
        $stmt = $this->db->prepare(
            "INSERT INTO reviews (user_id, apartment_id, booking_id, rating, comment) VALUES (?, ?, ?, ?, ?)"
        );
        $stmt->execute([$userId, $apartmentId, $bookingId, 5, "Отличная квартира!"]);
        $reviewId = $this->db->lastInsertId();

        $this->assert($reviewId > 0, "Review created successfully");

        // Test review visibility toggle
        $stmt = $this->db->prepare("UPDATE reviews SET is_visible = NOT is_visible WHERE id = ?");
        $stmt->execute([$reviewId]);

        $stmt = $this->db->prepare("SELECT is_visible FROM reviews WHERE id = ?");
        $stmt->execute([$reviewId]);
        $review = $stmt->fetch(PDO::FETCH_ASSOC);

        $this->assertEqual(0, $review['is_visible'], "Review visibility toggled");
    }

    public function runAllTests()
    {
        echo "\n╔════════════════════════════════════════════╗\n";
        echo "║     Admin Panel Test Suite                ║\n";
        echo "╚════════════════════════════════════════════╝\n";

        $this->testDatabaseConnection();
        $this->testAdminAuthentication();
        $this->testLandlordCreation();
        $this->testRoleBasedQueries();
        $this->testBookingCreation();
        $this->testEmailValidation();
        $this->testSanitization();
        $this->testLandlordRequestFlow();
        $this->testReviewSystem();

        echo "\n╔════════════════════════════════════════════╗\n";
        echo "║     Test Results                           ║\n";
        echo "╠════════════════════════════════════════════╣\n";
        echo "║  Passed: " . str_pad($this->testsPassed, 3, ' ', STR_PAD_LEFT) . "                              ║\n";
        echo "║  Failed: " . str_pad($this->testsFailed, 3, ' ', STR_PAD_LEFT) . "                              ║\n";
        echo "║  Total:  " . str_pad($this->testsPassed + $this->testsFailed, 3, ' ', STR_PAD_LEFT) . "                              ║\n";
        echo "╚════════════════════════════════════════════╝\n\n";

        return $this->testsFailed === 0;
    }
}

// Run tests
$tests = new AdminPanelTests();
$success = $tests->runAllTests();

exit($success ? 0 : 1);
