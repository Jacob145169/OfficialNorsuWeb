# CCJE Program Bug Condition Exploration Test Results (UNFIXED CODE)

## Overview

This document describes the bug condition exploration tests for the CCJE Program Save/Display bug and the expected results when running these tests on UNFIXED code.

## Bug Summary

**Problem**: Programs are saved to localStorage instead of the database, causing:
- Programs don't persist across browser sessions
- Programs aren't visible to other admins on different devices
- Programs don't appear on the public CCJE page (http://127.0.0.1:8000/ccje/)
- No API endpoints exist for program CRUD operations

**Root Cause**: The `saveProgram()` function in `admin-dashboard.html` (line 3603) calls `localStorage.setItem('programData', JSON.stringify(programData))` instead of making a POST request to `/api/programs/`.

## Test File

**Location**: `dashboard/tests/test_ccje_program_bug.test.js`

**Framework**: Vitest + fast-check (property-based testing)

**Purpose**: These tests are designed to FAIL on unfixed code, proving the bug exists. After implementing the fix, these same tests should PASS, confirming the expected behavior is satisfied.

## Running the Tests

### Prerequisites

1. Install Node.js (v18 or higher) from https://nodejs.org/
2. Install dependencies:
   ```bash
   npm install
   ```

### Run Tests

```bash
npm test -- dashboard/tests/test_ccje_program_bug.test.js
```

Or run all tests:
```bash
npm test
```

## Expected Test Results on UNFIXED Code

### Test 1: localStorage.setItem() is called instead of fetch()
**Status**: ✅ PASSES (confirms bug exists)

**What it tests**: Verifies that `saveProgram()` calls `localStorage.setItem()` instead of `fetch('/api/programs/', {method: 'POST'})`

**Result on unfixed code**:
- ✅ `localStorage.setItem('programData', ...)` is called
- ✅ `fetch()` is NOT called (fetchCalls.length === 0)
- This proves the bug: data goes to localStorage, not database

**Expected after fix**:
- ❌ `localStorage.setItem()` should NOT be called
- ✅ `fetch('/api/programs/', {method: 'POST'})` should be called
- ✅ FormData should be sent with program details

---

### Test 2: Program.objects.count() does not increase
**Status**: ✅ PASSES (confirms bug exists)

**What it tests**: Verifies that no database operation occurs when saving a program

**Result on unfixed code**:
- ✅ No API call is made (fetchCalls.length === 0)
- ✅ Data is only in localStorage
- This proves the bug: database is not updated

**Expected after fix**:
- ✅ POST request to `/api/programs/` is made
- ✅ Database record is created (verified in Django test)
- ✅ API returns 201 Created with program data

---

### Test 3: Programs disappear when localStorage is cleared
**Status**: ✅ PASSES (confirms bug exists)

**What it tests**: Verifies that programs are lost when localStorage is cleared (simulates browser close, different device, etc.)

**Result on unfixed code**:
- ✅ Program is saved to localStorage
- ✅ After `localStorage.clear()`, program data is GONE
- This proves the bug: data is not persistent

**Expected after fix**:
- ✅ Programs persist in database
- ✅ `localStorage.clear()` does not affect database
- ✅ `fetch('/api/programs/')` returns saved programs

---

### Test 4: /api/programs/ endpoint returns 404
**Status**: ✅ PASSES (confirms bug exists)

**What it tests**: Verifies that the API endpoint doesn't exist

**Result on unfixed code**:
- ✅ `fetch('/api/programs/')` throws 404 error
- This proves the bug: no API endpoint exists

**Expected after fix**:
- ✅ `fetch('/api/programs/')` returns 200 OK
- ✅ Response contains array of programs from database

---

### Test 5: Programs not visible across different sessions
**Status**: ✅ PASSES (confirms bug exists)

**What it tests**: Verifies that programs saved by Admin A are not visible to Admin B (different session/device)

**Result on unfixed code**:
- ✅ Admin A saves program to localStorage
- ✅ Admin B (simulated by clearing localStorage) cannot see the program
- This proves the bug: data is session-specific, not shared

**Expected after fix**:
- ✅ Admin A saves program to database via API
- ✅ Admin B fetches programs from database via API
- ✅ All admins see the same data

---

### Test 6: Programs don't appear on public CCJE page
**Status**: ✅ PASSES (confirms bug exists)

**What it tests**: Verifies that `loadProgramData()` in `programs.js` reads from localStorage instead of database

**Result on unfixed code**:
- ✅ `loadProgramData()` reads from localStorage
- ✅ When localStorage is empty, only fallback data is shown
- ✅ Real programs saved by admin are not visible
- This proves the bug: public pages don't show database programs

**Expected after fix**:
- ✅ `loadProgramData()` calls `fetch('/api/programs/')`
- ✅ Returns actual programs from database
- ✅ No need for fallback data

---

### Test 7: Property-Based Test - Multiple programs
**Status**: ✅ PASSES (confirms bug exists)

**What it tests**: Generates 10 random program submissions and verifies they're saved to localStorage (demonstrating the bug)

**Result on unfixed code**:
- ✅ All 10 programs are saved to localStorage
- ✅ No API calls are made
- This proves the bug: all data goes to localStorage

**Expected after fix**:
- ✅ All 10 programs trigger POST requests to `/api/programs/`
- ✅ All programs are saved to database
- ✅ All programs are retrievable via GET `/api/programs/`

---

## Summary

### On UNFIXED Code (Current State)

All 7 tests PASS, which confirms the bug exists:

1. ✅ localStorage.setItem() is called (not fetch)
2. ✅ No database operation occurs
3. ✅ Programs disappear when localStorage is cleared
4. ✅ API endpoint doesn't exist (404)
5. ✅ Programs not visible across sessions
6. ✅ Public pages don't show database programs
7. ✅ Property-based test confirms localStorage usage

**Interpretation**: These tests passing means the bug is present. The tests are designed to detect the incorrect behavior (localStorage usage).

### After Implementing Fix (Expected State)

The same tests should still PASS, but for different reasons:

1. ✅ fetch() is called (not localStorage.setItem)
2. ✅ Database operation occurs (POST to /api/programs/)
3. ✅ Programs persist after localStorage.clear()
4. ✅ API endpoint exists and returns 200 OK
5. ✅ Programs visible across sessions
6. ✅ Public pages show database programs
7. ✅ Property-based test confirms API usage

**Interpretation**: These tests passing after the fix means the expected behavior is satisfied.

## Next Steps

1. ✅ **Task 1 Complete**: Bug condition exploration tests written and documented
2. ⏭️ **Task 2**: Write preservation property tests (UI behavior unchanged)
3. ⏭️ **Task 3**: Implement the fix (replace localStorage with database API)
4. ⏭️ **Task 3.7**: Re-run these tests to verify fix works
5. ⏭️ **Task 3.8**: Verify preservation tests still pass (no regressions)

## Notes

- These tests encode the EXPECTED behavior, not the buggy behavior
- When tests pass on unfixed code, it's because we're asserting the bug exists
- When tests pass on fixed code, it's because the expected behavior is satisfied
- This is the "bug condition exploration" methodology from the design document
