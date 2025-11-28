#!/bin/bash
# Run all tests for the Telegram Rental Bot

echo "════════════════════════════════════════════════════════════"
echo "         Telegram Rental Bot - Complete Test Suite"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_FAILURES=0

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Test 1: Basic database and validation tests
echo -e "${YELLOW}[1/3] Running Basic Tests (Database, Localization, Validation)${NC}"
echo "────────────────────────────────────────────────────────────"
cd bot
python3 tests.py
TEST1_RESULT=$?
cd ..

if [ $TEST1_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Basic tests PASSED${NC}"
else
    echo -e "${RED}✗ Basic tests FAILED${NC}"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
fi
echo ""

# Test 2: Extended bot handler tests
echo -e "${YELLOW}[2/3] Running Extended Bot Handler Tests${NC}"
echo "────────────────────────────────────────────────────────────"
cd bot
python3 test_handlers.py
TEST2_RESULT=$?
cd ..

if [ $TEST2_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Bot handler tests PASSED${NC}"
else
    echo -e "${RED}✗ Bot handler tests FAILED${NC}"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
fi
echo ""

# Test 3: Admin panel tests
echo -e "${YELLOW}[3/3] Running Admin Panel Tests${NC}"
echo "────────────────────────────────────────────────────────────"
cd admin
php test_admin_simple.php
TEST3_RESULT=$?
cd ..

if [ $TEST3_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Admin panel tests PASSED${NC}"
else
    echo -e "${RED}✗ Admin panel tests FAILED${NC}"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo "                     Test Summary"
echo "════════════════════════════════════════════════════════════"

if [ $TOTAL_FAILURES -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "Test Coverage:"
    echo "  ✓ Database operations"
    echo "  ✓ User management"
    echo "  ✓ Localization (RU/KK)"
    echo "  ✓ Phone validation"
    echo "  ✓ Bot handlers and FSM"
    echo "  ✓ Booking flow"
    echo "  ✓ Calendar and date blocking"
    echo "  ✓ Admin authentication"
    echo "  ✓ Role-based access control"
    echo "  ✓ Landlord management"
    echo "  ✓ Review system"
    echo "  ✓ Data sanitization"
    echo ""
    exit 0
else
    echo -e "${RED}✗ $TOTAL_FAILURES TEST SUITE(S) FAILED${NC}"
    echo ""
    exit 1
fi
