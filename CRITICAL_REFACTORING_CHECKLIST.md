# CRITICAL REFACTORING CHECKLIST

## Highest Priority Refactoring Issues

### Issue #1: N+1 Query Problem (Database Performance Killer)
**Status**: CRITICAL - Impacts performance severely
**Location**: `/home/user/telegram_app/bot/database.py` lines 243-245, 517-519
**Problem**: 
```python
for apt in apartments:
    apt['photos'] = get_apartment_photos(apt['id'])  # Query per apartment!
```
**Impact**: 1 query becomes N+1 queries (51 queries instead of 1 for 50 apartments)
**Time to Fix**: 2-3 hours
**Priority**: DO FIRST - Massive performance impact

---

### Issue #2: Database Connection Management (Code Smell)
**Status**: CRITICAL - Architectural issue affecting all database code
**Location**: `/home/user/telegram_app/bot/database.py` - 59 get_connection() calls
**Problem**:
```python
# Every single function does this:
def get_user(telegram_id: int):
    conn = get_connection()  # Open
    # ... code ...
    conn.close()  # Close (easy to forget)
    return result
```
**Issues**:
- 59 connection open/close cycles
- Manual resource management error-prone
- No connection pooling
- Difficult to refactor

**Impact**: Performance, maintainability, error-prone code
**Time to Fix**: 1-2 hours
**Priority**: DO SECOND - Foundation for other improvements

---

### Issue #3: No Error Handling in Critical Operations
**Status**: HIGH - Correctness issue
**Location**: `/home/user/telegram_app/bot/main.py` lines 1215-1217, 1293-1295
**Problem**:
```python
# No error handling when canceling bookings:
conn.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
conn.commit()
conn.close()

# No error handling in review pagination:
total = conn.execute("SELECT COUNT(*) FROM reviews WHERE apartment_id = ?", (apartment_id,)).fetchone()[0]
```
**Impact**: Silent failures, data inconsistency, unhandled exceptions
**Time to Fix**: 2-3 hours
**Priority**: DO THIRD - Fix critical path first

---

### Issue #4: Hard to Test Code (No Dependency Injection)
**Status**: HIGH - Maintainability and testing issue
**Location**: Throughout `/home/user/telegram_app/bot/main.py`
**Problem**:
```python
# Can't test without real database, real Message objects:
async def create_booking_request(message: Message, state: FSMContext, user: dict):
    data = await state.get_data()
    apartment = db.get_apartment_by_id(apartment_id)  # Hard dependency!
    # ... 130 lines of mixed logic ...
```
**Issues**:
- No mocking possible
- All tests need real database
- Cannot test business logic separately
- Tests are slow and brittle

**Impact**: No unit tests, slow integration tests, cannot fix bugs without fear
**Time to Fix**: 4-5 hours (break into smaller functions first)
**Priority**: DO FOURTH - Essential for adding tests

---

### Issue #5: Main.py Too Large (1,364 lines)
**Status**: HIGH - Maintainability issue
**Location**: `/home/user/telegram_app/bot/main.py`
**Problem**:
- 58 handler functions
- Mixed concerns (handlers, formatting, validation, FSM)
- Hard to find related code
- Difficult to navigate

**Impact**: Hard to maintain, difficult to debug, confusing for new developers
**Time to Fix**: 4-5 hours (modular extraction)
**Priority**: DO FIFTH - After database refactoring

---

## Quick Check: Known Issues

### Code Duplication Hotspots
- [ ] Phone validation (appears in 3+ places)
- [ ] Email validation (appears in 1+ places)
- [ ] Back button handling (appears in 4+ places)
- [ ] Promotion text formatting (lines 91-107, 829-838)
- [ ] Review formatting (lines 956-966, 1285-1290)

### Missing Validations
- [ ] Booking cancellation has no error handling
- [ ] Review pagination has no error handling
- [ ] Photo uploads have generic exception handling
- [ ] No try/except in booking creation for edge cases

### Missing Patterns
- [ ] No Service Layer (logic mixed in handlers)
- [ ] No Repository Pattern (raw SQL everywhere)
- [ ] No Dependency Injection (hard-coded imports)
- [ ] No Custom Exceptions (generic exceptions only)
- [ ] No Error Handler Middleware

### Performance Issues
- [ ] N+1 queries in get_apartments() and get_user_favorites()
- [ ] No caching for cities, districts, amenities
- [ ] 59 database connection open/close cycles per request
- [ ] Synchronous database operations in async handlers

### Type Hinting Issues
- [ ] database.py missing return types on most functions
- [ ] No type hints for dict values in handlers
- [ ] No Optional[] types where needed
- [ ] No Union types for fallback values

---

## Immediate Action Items (Next 2 Days)

### Must Do Today
1. [ ] Create `/bot/validators.py` - Extract phone and email validation (30 min)
2. [ ] Create `/bot/formatters.py` - Extract text formatting (30 min)
3. [ ] Fix duplicate `import re` in main.py line 496 (5 min)
4. [ ] Add error handling to booking cancellation (line 1215-1217) (15 min)
5. [ ] Add error handling to review pagination (line 1293-1295) (15 min)

**Total Time**: 1.5 hours

### Should Do This Week
1. [ ] Create DatabaseManager class (1-2 hours)
2. [ ] Fix N+1 query in get_apartments() (2-3 hours)
3. [ ] Extract handlers into separate files (2-3 hours)
4. [ ] Add basic caching for static data (1-2 hours)
5. [ ] Convert config.py to use pydantic Settings (1 hour)

**Total Time**: 7-10 hours

---

## Specific Line Numbers to Fix

### HIGH Priority Fixes

1. **Line 496 in main.py**
   - Issue: Duplicate `import re` inside function
   - Fix: Remove, use top-level import
   - Time: 1 min

2. **Lines 243-245 in database.py**
   - Issue: N+1 query in get_apartments
   - Fix: Use LEFT JOIN and reconstruct in memory
   - Time: 2 hours

3. **Lines 517-519 in database.py**
   - Issue: N+1 query in get_user_favorites
   - Fix: Use LEFT JOIN eager loading
   - Time: 1 hour

4. **Lines 1215-1217 in main.py**
   - Issue: No error handling in booking cancellation
   - Fix: Add try/except, return result status
   - Time: 30 min

5. **Lines 1293-1295 in main.py**
   - Issue: No error handling in review count
   - Fix: Add try/except, log error, provide default
   - Time: 30 min

6. **Lines 859-862 in main.py**
   - Issue: Raw database access in handler
   - Fix: Extract to UserService.get_landlord()
   - Time: 1 hour

### MEDIUM Priority Refactoring

7. **Lines 82-129 in main.py** - format_apartment_card()
   - Issue: 48-line function with mixed concerns
   - Fix: Extract into separate formatter functions
   - Time: 1.5 hours

8. **Lines 780-910 in main.py** - create_booking_request()
   - Issue: 131-line function with too many responsibilities
   - Fix: Extract business logic to BookingService
   - Time: 3-4 hours

9. **Lines 8-39 in database.py** - get_connection()
   - Issue: Manual connection management in 59 places
   - Fix: Create DatabaseManager class
   - Time: 2-3 hours

10. **Lines 29-50 in main.py** - FSM State definitions
    - Issue: Mixed concerns in SearchStates
    - Fix: Separate into SearchStates, ApartmentBrowsingStates, BookingStates
    - Time: 1 hour

---

## Testing After Each Fix

After each major refactoring:

```bash
# Run all tests
python -m pytest tests/ -v

# Check for N+1 queries
# Add query logging to database.py

# Run type checker
mypy bot/

# Check code coverage
pytest --cov=bot tests/
```

---

## Validation Checklist

For each issue fixed:

- [ ] Code compiles/runs without errors
- [ ] Existing functionality unchanged
- [ ] Related tests pass
- [ ] Code follows project style
- [ ] No new warnings introduced
- [ ] Documentation updated if needed
- [ ] Performance improved (measure if applicable)

---

## Success Metrics

Track improvements:

1. **Performance**
   - Database queries: Should drop from 50+ to 1-2 per request
   - Response time: Should improve by 30-50%

2. **Code Quality**
   - main.py: From 1,364 to ~400 lines
   - Duplicate code: From 15+ instances to 0
   - Test coverage: From 0% to 60%+

3. **Maintainability**
   - Functions > 50 lines: From 4 to 0
   - Cyclomatic complexity: Decrease by 40%
   - Time to find code: 10 mins to 1 min

---

## References

Full details in: `/home/user/telegram_app/REFACTORING_ANALYSIS.md`

---

End of Checklist
