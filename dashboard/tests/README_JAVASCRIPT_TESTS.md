# JavaScript Testing for NORSU Dashboard

## Overview

This directory contains JavaScript tests for the NORSU Dashboard, specifically for testing client-side functionality like the achievements management feature.

## Test Files

- `test_achievements_bug.test.js` - Bug condition exploration tests for achievements management
- `setup.js` - Test environment setup (localStorage mock, DOM reset)
- `TEST_RESULTS_UNFIXED.md` - Documentation of expected test results on unfixed code

## Setup

### Prerequisites

1. **Node.js and npm**: Download and install from https://nodejs.org/
   - Recommended version: Node.js 18.x or higher
   - npm comes bundled with Node.js

2. **Verify installation**:
   ```bash
   node --version
   npm --version
   ```

### Installation

From the project root directory:

```bash
npm install
```

This will install:
- `vitest` - Modern JavaScript testing framework
- `fast-check` - Property-based testing library
- `happy-dom` - Lightweight DOM implementation for testing
- `@vitest/ui` - Optional UI for viewing test results

## Running Tests

### Run all tests once
```bash
npm test
```

### Run tests in watch mode (re-runs on file changes)
```bash
npm run test:watch
```

### Run tests with UI
```bash
npm run test:ui
```

## Test Structure

### Bug Condition Exploration Tests

The `test_achievements_bug.test.js` file contains tests that:

1. **Demonstrate the bug on unfixed code** - Tests are designed to fail, proving the bug exists
2. **Validate the fix** - After implementing the fix, tests should pass
3. **Use property-based testing** - Generates random test cases for stronger guarantees

### Test Cases

1. ✅ **Save to localStorage** - Verifies achievements are saved
2. ✅ **Display in table** - Verifies achievements appear in the table
3. ❌ **Image preview** - Verifies image preview works (FAILS on unfixed code)
4. ✅ **Clear form fields** - Verifies form is cleared after submission
5. ✅ **Close modal** - Verifies modal closes after submission
6. ✅ **Show notification** - Verifies success notification is displayed
7. ✅ **Sync to dashboards** - Verifies sync function is called
8. ✅ **Property-based test** - Tests with random data (10 runs)

## Understanding Test Results

### On UNFIXED Code

Most tests will PASS because the core functionality works. However:

- **Test 3 (Image preview)** will FAIL - This is the primary bug
- The failure proves that `setupFileUpload` is not called for 'achievementImage'

### After Implementing Fix

All tests should PASS, confirming:
- Image preview functionality works
- Image data is correctly captured and saved
- All other functionality continues to work (preservation)

## Test Configuration

### vitest.config.js

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'happy-dom',  // Simulates browser DOM
    globals: true,              // Makes test functions globally available
    setupFiles: ['./dashboard/tests/setup.js'],  // Runs before each test
  },
});
```

### setup.js

- Mocks `localStorage` for testing
- Resets DOM before each test
- Ensures clean test environment

## Writing New Tests

### Example Test Structure

```javascript
import { describe, it, expect, beforeEach } from 'vitest';

describe('Feature Name', () => {
  beforeEach(() => {
    // Setup code runs before each test
    localStorage.clear();
    document.body.innerHTML = '...';
  });

  it('should do something', () => {
    // Arrange: Set up test data
    const input = 'test';
    
    // Act: Perform the action
    const result = someFunction(input);
    
    // Assert: Verify the result
    expect(result).toBe('expected');
  });
});
```

### Property-Based Testing Example

```javascript
import * as fc from 'fast-check';

it('should work for all valid inputs', () => {
  fc.assert(
    fc.property(
      fc.string({ minLength: 1, maxLength: 100 }),
      (randomString) => {
        // Test with randomly generated string
        const result = processString(randomString);
        expect(result).toBeDefined();
      }
    ),
    { numRuns: 100 } // Run 100 random test cases
  );
});
```

## Troubleshooting

### npm not found

If you get "npm is not recognized":
1. Install Node.js from https://nodejs.org/
2. Restart your terminal/command prompt
3. Verify with `npm --version`

### Tests fail to run

1. Make sure dependencies are installed: `npm install`
2. Check that `vitest.config.js` exists in the project root
3. Check that `setup.js` exists in `dashboard/tests/`

### DOM-related errors

If you get errors about `document` or `window`:
1. Verify `vitest.config.js` has `environment: 'happy-dom'`
2. Check that `setup.js` is properly configured in `setupFiles`

## Integration with Django Tests

These JavaScript tests complement the existing Django tests:

- **Django tests** (`test_*.py`) - Test server-side Python code
- **JavaScript tests** (`test_*.test.js`) - Test client-side JavaScript code

Run both test suites to ensure full coverage:

```bash
# Django tests
python manage.py test

# JavaScript tests
npm test
```

## CI/CD Integration

To run tests in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Setup Node.js
  uses: actions/setup-node@v3
  with:
    node-version: '18'

- name: Install dependencies
  run: npm install

- name: Run JavaScript tests
  run: npm test
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [fast-check Documentation](https://fast-check.dev/)
- [happy-dom Documentation](https://github.com/capricorn86/happy-dom)

## Questions?

If you have questions about the JavaScript tests, refer to:
1. `TEST_RESULTS_UNFIXED.md` - Detailed test results and analysis
2. Test file comments - Each test has detailed documentation
3. Design document - `.kiro/specs/achievements-management-fix/design.md`
