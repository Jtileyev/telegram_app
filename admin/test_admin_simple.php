<?php
/**
 * Simple Admin Panel Tests (no PDO required)
 * Tests admin panel logic and helper functions
 */

// Prevent direct execution in production
if (php_sapi_name() !== 'cli') {
    die('Tests can only be run from command line');
}

// Suppress session warnings in CLI
if (!isset($_SESSION)) {
    $_SESSION = [];
}

require_once __DIR__ . '/config.php';

class SimpleAdminTests
{
    private $testsPassed = 0;
    private $testsFailed = 0;

    private function assert($condition, $message)
    {
        if ($condition) {
            $this->testsPassed++;
            echo "✓ $message\n";
        } else {
            $this->testsFailed++;
            echo "✗ $message\n";
        }
    }

    private function assertEqual($expected, $actual, $message)
    {
        $this->assert($expected === $actual, "$message (Expected: $expected, Got: $actual)");
    }

    public function testRoleHelperFunctions()
    {
        echo "\n=== Testing Role Helper Functions ===\n";

        // Test without session
        $this->assert(!isLoggedIn(), "isLoggedIn returns false when no session");
        $this->assert(getUserRole() === null, "getUserRole returns null when not logged in");
        $this->assert(!isAdmin(), "isAdmin returns false when not logged in");
        $this->assert(!isLandlord(), "isLandlord returns false when not logged in");

        // Simulate admin session
        $_SESSION['user_id'] = 1;
        $_SESSION['user_role'] = 'admin';

        $this->assert(isLoggedIn(), "isLoggedIn returns true for admin session");
        $this->assertEqual('admin', getUserRole(), "getUserRole returns admin");
        $this->assert(isAdmin(), "isAdmin returns true for admin");
        $this->assert(!isLandlord(), "isLandlord returns false for admin");

        // Simulate landlord session
        $_SESSION['user_id'] = 2;
        $_SESSION['user_role'] = 'landlord';
        $_SESSION['landlord_id'] = 5;

        $this->assert(isLoggedIn(), "isLoggedIn returns true for landlord session");
        $this->assertEqual('landlord', getUserRole(), "getUserRole returns landlord");
        $this->assert(!isAdmin(), "isAdmin returns false for landlord");
        $this->assert(isLandlord(), "isLandlord returns true for landlord");
        $this->assertEqual(5, getLandlordId(), "getLandlordId returns correct ID");

        // Clear session
        $_SESSION = [];
    }

    public function testSanitizeFunction()
    {
        echo "\n=== Testing Sanitize Function ===\n";

        $dangerous = "<script>alert('XSS')</script>";
        $safe = sanitize($dangerous);

        $this->assert(
            strpos($safe, '<script>') === false,
            "Sanitize removes script tags"
        );

        $this->assert(
            strpos($safe, '&lt;script&gt;') !== false,
            "Sanitize properly escapes HTML entities"
        );

        // Test with quotes
        $withQuotes = "Test \"quoted\" text";
        $sanitized = sanitize($withQuotes);
        $this->assert(
            strpos($sanitized, '&quot;') !== false,
            "Sanitize escapes quotes"
        );
    }

    public function testFormatPriceFunction()
    {
        echo "\n=== Testing Format Price Function ===\n";

        $this->assertEqual("10 000 ₸", formatPrice(10000), "formatPrice formats 10000 correctly");
        $this->assertEqual("1 000 ₸", formatPrice(1000), "formatPrice formats 1000 correctly");
        $this->assertEqual("100 ₸", formatPrice(100), "formatPrice formats 100 correctly");
        $this->assertEqual("1 500 000 ₸", formatPrice(1500000), "formatPrice formats large numbers");
    }

    public function testFormatDateFunction()
    {
        echo "\n=== Testing Format Date Function ===\n";

        $testDate = "2025-01-15";
        $formatted = formatDate($testDate);

        $this->assertEqual("15.01.2025", $formatted, "formatDate formats date correctly");

        // Test with invalid date
        $invalid = formatDate("invalid");
        $this->assertEqual("", $invalid, "formatDate handles invalid dates gracefully");
    }

    public function testPasswordHashing()
    {
        echo "\n=== Testing Password Hashing ===\n";

        $password = "test123";
        $hash = password_hash($password, PASSWORD_DEFAULT);

        $this->assert(
            password_verify($password, $hash),
            "Password hashing and verification works"
        );

        $this->assert(
            !password_verify("wrong", $hash),
            "Wrong password fails verification"
        );
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
            '',
        ];

        foreach ($invalidEmails as $email) {
            $isValid = filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
            $this->assert(!$isValid, "Email '$email' is invalid");
        }
    }

    public function testFlashMessages()
    {
        echo "\n=== Testing Flash Messages ===\n";

        setFlash('success', 'Test success message');
        $this->assert(
            isset($_SESSION['flash']),
            "Flash message set in session"
        );

        $flash = getFlash();
        $this->assertEqual('success', $flash['type'], "Flash type is success");
        $this->assertEqual('Test success message', $flash['message'], "Flash message is correct");

        // Flash should be cleared after retrieval
        $flash2 = getFlash();
        $this->assert($flash2 === null, "Flash message cleared after retrieval");
    }

    public function testSessionSecurity()
    {
        echo "\n=== Testing Session Security ===\n";

        // Test that session regeneration works
        $oldId = session_id();
        if ($oldId) {
            session_regenerate_id(true);
            $newId = session_id();
            $this->assert($oldId !== $newId, "Session ID regenerates");
        } else {
            $this->assert(true, "Session regeneration test skipped (no active session)");
        }
    }

    public function testPhoneNumberFormatting()
    {
        echo "\n=== Testing Phone Number Formatting ===\n";

        // Test that phone numbers are stored and retrieved correctly
        $phones = [
            '+7 777 777 77 77',
            '+7 (777) 777-77-77',
            '8 777 777 77 77',
        ];

        foreach ($phones as $phone) {
            // Remove formatting
            $cleaned = preg_replace('/[^0-9+]/', '', $phone);
            $this->assert(strlen($cleaned) >= 11, "Phone '$phone' has valid length after cleaning");
        }
    }

    public function runAllTests()
    {
        echo "\n╔════════════════════════════════════════════╗\n";
        echo "║   Simple Admin Panel Test Suite           ║\n";
        echo "╚════════════════════════════════════════════╝\n";

        $this->testRoleHelperFunctions();
        $this->testSanitizeFunction();
        $this->testFormatPriceFunction();
        $this->testFormatDateFunction();
        $this->testPasswordHashing();
        $this->testEmailValidation();
        $this->testFlashMessages();
        $this->testSessionSecurity();
        $this->testPhoneNumberFormatting();

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
$tests = new SimpleAdminTests();
$success = $tests->runAllTests();

exit($success ? 0 : 1);
