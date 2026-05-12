# CCJE Program Preservation Property Test Results (UNFIXED CODE)

## Overview

This document describes the preservation property tests for the CCJE Program Save/Display bug and the expected results when running these tests on UNFIXED code.

## Purpose

These tests verify that UI behavior remains unchanged for non-save interactions. They follow the observation-first methodology: observe behavior on UNFIXED code, then write tests capturing that behavior.

**Property 2: Preservation - UI Behavior Unchanged**

For any user interaction that is NOT the final save action (modal display, form typing, image preview, table rendering), the fixed code SHALL produce exactly the same visual and interactive behavior as the original code, preserving all existing UI functionality and user experience.

## Test File

**Location**: `dashboard/tests/test_ccje_program_preservation.test.js`

**Framework**: Vitest + fast-check (property-based testing)

**Purpose**: These tests are designed to PASS on unfixed code (confirming baseline behavior). After implementing the fix, these same tests should PASS, confirming no regressions occurred.

## Running the Tests

### Prerequisites

1. Install Node.js (v18 or higher) from https://nodejs.org/
2. Install dependencies:
   ```bash
   npm install
   ```

### Run Tests

```bash
npm test -- dashboard/tests/test_ccje_program_preservation.test.js
```

Or run all tests:
```bash
npm test
```

## Expected Test Results on UNFIXED Code

All tests should PASS on unfixed code, confirming the baseline UI behavior that must be preserved.

### Test 1: Modal Display - Clicking "Add New Program" opens modal
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that clicking "Add New Program" button opens the modal with correct form fields

**Result on unfixed code**:
- ✅ Modal opens (display: block)
- ✅ Modal title is "Add New Program"
- ✅ All form fields are present (Program Name, Program Image, Duration, Status)
- ✅ Form fields are empty/reset

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 2: Modal Close - Clicking close button hides modal
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that clicking the close button hides the modal

**Result on unfixed code**:
- ✅ Modal closes (display: none)

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 3: Form Validation - Empty form submission shows validation errors
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that HTML5 validation prevents submission of empty required fields

**Result on unfixed code**:
- ✅ Required fields have 'required' attribute
- ✅ Empty fields are invalid (validity.valid = false)
- ✅ Filled fields are valid (validity.valid = true)

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 4: Image Preview - Selecting an image shows preview
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that selecting an image file shows a preview before saving

**Result on unfixed code**:
- ✅ Preview is initially hidden
- ✅ After file selection, preview becomes visible (display: block)
- ✅ Preview image src is set to the file data URL

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 5: Table Rendering - Programs table displays with correct columns
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that the programs table renders correctly with all columns

**Result on unfixed code**:
- ✅ Table displays with correct columns: Image, Program Name, Duration, Status, Actions
- ✅ Program data is displayed correctly
- ✅ Action buttons (edit, delete) are present

**Expected after fix**:
- ✅ Same behavior (no changes expected)
- Note: Data source will change from localStorage to API, but table structure remains the same

---

### Test 6: Empty Table State - Shows message when no programs exist
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that an empty state message is shown when no programs exist

**Result on unfixed code**:
- ✅ Empty state message is displayed: "No programs found. Click 'Add New Program' to add your first program."

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 7: Form Field Typing - User can type in form fields
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that users can type in form fields and values are correctly set

**Result on unfixed code**:
- ✅ User can type in Program Name field
- ✅ User can type in Duration field
- ✅ User can select Status from dropdown
- ✅ Values are correctly stored in the input elements

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 8: Form Reset - Form is reset when modal is opened for new program
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Verifies that the form is reset when opening the modal for a new program

**Result on unfixed code**:
- ✅ After closing and reopening modal, form fields are empty
- ✅ Status field returns to default value ('active')

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 9: Property-Based Test - Modal behavior with random interactions
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Generates random sequences of modal open/close actions and verifies consistent state

**Result on unfixed code**:
- ✅ Modal state is always consistent after each action
- ✅ Open action always results in display: block
- ✅ Close action always results in display: none
- ✅ Final state matches the last action

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 10: Property-Based Test - Form validation with random inputs
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Generates random form inputs and verifies validation works consistently

**Result on unfixed code**:
- ✅ Empty strings are invalid for required fields
- ✅ Non-empty strings are valid for required fields
- ✅ Status field is always valid (has default value)

**Expected after fix**:
- ✅ Same behavior (no changes expected)

---

### Test 11: Property-Based Test - Table rendering with random program data
**Status**: ✅ EXPECTED TO PASS

**What it tests**: Generates random program data and verifies table renders correctly

**Result on unfixed code**:
- ✅ Empty program list shows empty state message
- ✅ Non-empty program list shows all programs in table
- ✅ Table has correct number of rows
- ✅ All program data is displayed correctly

**Expected after fix**:
- ✅ Same behavior (no changes expected)
- Note: Data will come from API instead of localStorage, but rendering logic is the same

---

## Summary

### On UNFIXED Code (Current State)

All 11 tests should PASS, confirming the baseline UI behavior:

1. ✅ Modal opens with correct form fields
2. ✅ Modal closes when close button is clicked
3. ✅ Form validation works for required fields
4. ✅ Image preview appears when file is selected
5. ✅ Table renders with correct columns and data
6. ✅ Empty state message shows when no programs exist
7. ✅ User can type in form fields
8. ✅ Form resets when modal is reopened
9. ✅ Modal state is consistent across random interactions (20 test cases)
10. ✅ Form validation works with random inputs (20 test cases)
11. ✅ Table renders correctly with random data (15 test cases)

**Total Property-Based Test Cases**: 55 (20 + 20 + 15)

**Interpretation**: These tests passing means the baseline UI behavior is correctly captured. This is the behavior we must preserve when implementing the fix.

### After Implementing Fix (Expected State)

All 11 tests should still PASS, confirming no regressions:

1. ✅ Modal behavior unchanged
2. ✅ Form validation unchanged
3. ✅ Image preview unchanged
4. ✅ Table rendering unchanged (structure, not data source)
5. ✅ All UI interactions work the same way

**Interpretation**: These tests passing after the fix means we successfully preserved all existing UI functionality while fixing the localStorage bug.

## Test Coverage

### UI Interactions Covered

- ✅ Modal open/close
- ✅ Form field input
- ✅ Form validation
- ✅ Image file selection and preview
- ✅ Table rendering with data
- ✅ Empty state handling

### UI Interactions NOT Covered (Out of Scope)

These are covered by the bug condition exploration tests (Task 1):
- ❌ Save button click (this is the bug condition)
- ❌ Edit button click (will be updated to use API)
- ❌ Delete button click (will be updated to use API)
- ❌ Data persistence (localStorage vs database)

## Next Steps

1. ✅ **Task 2 Complete**: Preservation property tests written and documented
2. ⏭️ **Task 3**: Implement the fix (replace localStorage with database API)
3. ⏭️ **Task 3.7**: Re-run bug condition exploration tests to verify fix works
4. ⏭️ **Task 3.8**: Re-run these preservation tests to verify no regressions

## Notes

- These tests encode the BASELINE behavior that must be preserved
- When tests pass on unfixed code, it confirms we've correctly captured the UI behavior
- When tests pass on fixed code, it confirms we haven't introduced regressions
- This is the "preservation checking" methodology from the design document
- Property-based testing provides stronger guarantees by testing many random scenarios

## Validation Requirements

**Requirements Validated**:
- 3.1: Programs management interface displays with existing table layout
- 3.2: "Add New Program" modal displays with correct form fields
- 3.3: Programs table displays with correct columns (Image, Program Name, Duration, Status, Actions)
- 3.4: Program cards on public pages maintain same visual layout (tested separately)
- 3.5: Existing program management features continue to function (edit, delete tested separately)

## Manual Verification (Optional)

While the automated tests provide strong guarantees, you can also manually verify:

1. Open the admin dashboard in a browser
2. Click "Programs Offered" from the sidebar
3. Click "Add New Program" button
4. Verify modal opens with all form fields
5. Try typing in the fields
6. Select an image and verify preview appears
7. Close the modal without saving
8. Verify the table displays correctly

All of these interactions should work the same way before and after the fix.
