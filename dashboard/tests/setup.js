/**
 * Test setup file for Vitest
 * Configures the test environment with necessary globals and utilities
 */

// Mock localStorage for testing
class LocalStorageMock {
  constructor() {
    this.store = {};
  }

  clear() {
    this.store = {};
  }

  getItem(key) {
    return this.store[key] || null;
  }

  setItem(key, value) {
    this.store[key] = String(value);
  }

  removeItem(key) {
    delete this.store[key];
  }

  get length() {
    return Object.keys(this.store).length;
  }

  key(index) {
    const keys = Object.keys(this.store);
    return keys[index] || null;
  }
}

global.localStorage = new LocalStorageMock();

// Setup DOM before each test
beforeEach(() => {
  // Clear localStorage before each test
  localStorage.clear();
  
  // Reset document body
  document.body.innerHTML = '';
});
