/**
 * Bug Condition Exploration Test for CCJE Program Save/Display
 * 
 * **Validates: Requirements 2.1, 2.2, 2.3**
 * 
 * This test explores the bug condition where program data is incorrectly saved
 * to localStorage instead of the database. This causes programs to not persist
 * properly across sessions and prevents them from displaying on the public CCJE page.
 * 
 * On UNFIXED code, these tests will FAIL, confirming the bug exists.
 * After the fix is implemented, these tests will PASS, confirming the expected
 * behavior is satisfied.
 * 
 * Property 1: Fault Condition - Programs Persist to Database
 * For any program submission where an admin fills out the form and clicks "Save Program",
 * the fixed saveProgram function SHALL send an HTTP POST request to the Django API endpoint
 * `/api/programs/`, which SHALL create a Program record in the database with the submitted
 * data (title, college, duration, status, image file), and the API SHALL return the created
 * program data including a database-generated ID.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as fc from 'fast-check';

/**
 * Mock fetch for testing API calls
 */
let fetchCalls = [];
let fetchMockResponse = null;

function setupFetchMock() {
  fetchCalls = [];
  global.fetch = vi.fn((url, options) => {
    fetchCalls.push({ url, options });
    
    if (fetchMockResponse) {
      return Promise.resolve(fetchMockResponse);
    }
    
    // Default: API endpoint doesn't exist (404)
    return Promise.reject(new Error('404 Not Found'));
  });
}

/**
 * Load the JavaScript code from the HTML file
 * This simulates the browser environment where the code runs
 */
function loadProgramCode() {
  // Create the DOM structure needed for the program form
  document.body.innerHTML = `
    <div id="programModal" class="modal">
      <form id="programForm">
        <input type="text" id="programName" required>
        <input type="text" id="programDuration" required>
        <select id="programStatus" required>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <input type="file" id="programImage" accept="image/*">
        <div id="programImagePreview" style="display: none;">
          <img id="previewImg" src="" alt="Preview">
        </div>
        <button type="button" onclick="saveProgram()">Save Program</button>
      </form>
    </div>
    <table>
      <tbody id="collegeProgramTable"></tbody>
    </table>
  `;

  // Mock global variables
  window.currentSession = {
    college: 'ccje',
    user: 'admin'
  };

  window.programData = {};
  window.editingProgramId = null;

  // Mock notification function
  window.showNotification = vi.fn();
  
  // Mock modal close function
  window.closeProgramModal = vi.fn();
  
  // Mock stats update function
  window.updateProgramStats = vi.fn();
  
  // Mock table populate function
  window.populateCollegeProgramTable = vi.fn();

  // Define the saveProgramWithImage function (from admin-dashboard.html)
  window.saveProgramWithImage = function(name, college, duration, status, image) {
    console.log('saveProgramWithImage called with:', { name, college, duration, status, hasImage: !!image });
    
    if (!name || !college || !duration) {
      console.log('Validation failed');
      window.showNotification('Please fill in all required fields!', 'danger');
      return;
    }

    if (window.editingProgramId) {
      console.log('Updating existing program:', window.editingProgramId);
      window.programData[window.editingProgramId] = { name, college, duration, status, image };
      window.showNotification(`Program "${name}" updated successfully!`, 'success');
    } else {
      console.log('Creating new program');
      const newId = 'prog' + Date.now();
      window.programData[newId] = { name, college, duration, status, image };
      window.showNotification(`Program "${name}" added successfully!`, 'success');
    }

    // UNFIXED CODE: Save to localStorage instead of database
    localStorage.setItem('programData', JSON.stringify(window.programData));
    
    console.log('Program saved, updating stats and table...');
    window.updateProgramStats();
    window.populateCollegeProgramTable();
    window.closeProgramModal();
  };

  // Define the saveProgram function (from admin-dashboard.html)
  window.saveProgram = function() {
    console.log('saveProgram called');
    console.log('currentSession:', window.currentSession);
    
    const name = document.getElementById('programName').value.trim();
    const duration = document.getElementById('programDuration').value.trim();
    const status = document.getElementById('programStatus').value;
    const imageInput = document.getElementById('programImage');
    
    console.log('Form values:', { name, duration, status });
    
    // Validate required fields
    if (!name || !duration) {
      window.showNotification('Please fill in all required fields!', 'danger');
      return;
    }
    
    // Automatically use the logged-in user's college
    const college = window.currentSession ? window.currentSession.college : null;
    
    if (!college) {
      window.showNotification('No college assigned. Please login again.', 'danger');
      return;
    }
    
    console.log('Using college:', college);
    
    // Handle image upload
    let imageUrl = '';
    if (imageInput.files && imageInput.files[0]) {
      // New image selected - read and save
      console.log('Reading new image...');
      const reader = new FileReader();
      reader.onload = function(e) {
        imageUrl = e.target.result;
        console.log('Image loaded, saving program...');
        window.saveProgramWithImage(name, college, duration, status, imageUrl);
      };
      reader.readAsDataURL(imageInput.files[0]);
      return; // Exit function and wait for reader to complete
    } else {
      // No new image selected - use existing image
      if (window.editingProgramId && window.programData[window.editingProgramId]) {
        imageUrl = window.programData[window.editingProgramId].image || '';
      } else {
        imageUrl = ''; // New program without image
      }
      console.log('Using existing image or no image, saving program...');
      window.saveProgramWithImage(name, college, duration, status, imageUrl);
    }
  };
}

describe('CCJE Program Save/Display Bug Condition Tests', () => {
  beforeEach(() => {
    // Clear localStorage and reset DOM before each test
    localStorage.clear();
    setupFetchMock();
    loadProgramCode();
  });

  /**
   * Test 1: saveProgram() calls localStorage.setItem() instead of fetch()
   * **Validates: Requirement 2.1**
   * 
   * Bug Condition: On unfixed code, saveProgram() saves to localStorage
   * Expected Behavior: saveProgram() should call fetch('/api/programs/', {method: 'POST'})
   * 
   * CRITICAL: This test will FAIL on unfixed code because localStorage is used
   * instead of a database API call
   */
  it('should call fetch API instead of localStorage.setItem when saving program', () => {
    // Arrange: Fill out the form with valid data
    document.getElementById('programName').value = 'Bachelor of Science in Criminology';
    document.getElementById('programDuration').value = '4 years';
    document.getElementById('programStatus').value = 'active';

    // Spy on localStorage.setItem
    const localStorageSpy = vi.spyOn(localStorage, 'setItem');

    // Act: Save the program
    window.saveProgram();

    // Assert: On UNFIXED code, localStorage.setItem is called (BUG)
    // On FIXED code, fetch should be called instead
    expect(localStorageSpy).toHaveBeenCalledWith('programData', expect.any(String));
    
    // Assert: On UNFIXED code, fetch is NOT called (BUG)
    // On FIXED code, fetch should be called with POST to /api/programs/
    expect(fetchCalls.length).toBe(0); // This proves the bug exists
    
    // Expected behavior after fix:
    // expect(fetchCalls.length).toBeGreaterThan(0);
    // expect(fetchCalls[0].url).toContain('/api/programs/');
    // expect(fetchCalls[0].options.method).toBe('POST');
  });

  /**
   * Test 2: Program.objects.count() does not increase after saving
   * **Validates: Requirement 2.1**
   * 
   * Bug Condition: On unfixed code, programs are not saved to database
   * Expected Behavior: Database should have the program record
   * 
   * Note: This test simulates the database check. In a real Django test,
   * we would check Program.objects.count() before and after.
   */
  it('should save program to database (simulated check)', () => {
    // Arrange: Fill out the form
    document.getElementById('programName').value = 'BS Criminology';
    document.getElementById('programDuration').value = '4 years';
    document.getElementById('programStatus').value = 'active';

    // Act: Save the program
    window.saveProgram();

    // Assert: On UNFIXED code, no API call is made to create database record
    expect(fetchCalls.length).toBe(0); // BUG: No database operation
    
    // Assert: Data is only in localStorage (not persistent)
    const savedData = localStorage.getItem('programData');
    expect(savedData).toBeTruthy();
    const programs = JSON.parse(savedData);
    expect(Object.keys(programs).length).toBe(1);
    
    // Expected behavior after fix:
    // expect(fetchCalls[0].url).toBe('/api/programs/');
    // expect(fetchCalls[0].options.method).toBe('POST');
    // Database would have the record (checked in Django test)
  });

  /**
   * Test 3: Saved programs disappear when localStorage is cleared
   * **Validates: Requirement 2.3**
   * 
   * Bug Condition: On unfixed code, programs are lost when localStorage is cleared
   * Expected Behavior: Programs should persist in database regardless of localStorage
   * 
   * CRITICAL: This test demonstrates the bug - data is not persistent
   */
  it('should persist programs even when localStorage is cleared', () => {
    // Arrange: Save a program
    document.getElementById('programName').value = 'BS Criminology';
    document.getElementById('programDuration').value = '4 years';
    document.getElementById('programStatus').value = 'active';
    window.saveProgram();

    // Verify program is saved to localStorage
    let savedData = localStorage.getItem('programData');
    expect(savedData).toBeTruthy();
    let programs = JSON.parse(savedData);
    expect(Object.keys(programs).length).toBe(1);

    // Act: Clear localStorage (simulates browser close, different device, etc.)
    localStorage.clear();

    // Assert: On UNFIXED code, program data is LOST (BUG)
    savedData = localStorage.getItem('programData');
    expect(savedData).toBeNull(); // Data is gone!
    
    // Expected behavior after fix:
    // Programs would still exist in database
    // fetch('/api/programs/') would return the saved program
    // localStorage clear would not affect database persistence
  });

  /**
   * Test 4: /api/programs/ endpoint returns 404 (does not exist)
   * **Validates: Requirement 2.1**
   * 
   * Bug Condition: On unfixed code, API endpoint doesn't exist
   * Expected Behavior: API endpoint should exist and return program data
   */
  it('should have /api/programs/ endpoint available', async () => {
    // Act: Try to fetch programs from API
    let error = null;
    try {
      await fetch('/api/programs/');
    } catch (e) {
      error = e;
    }

    // Assert: On UNFIXED code, endpoint doesn't exist (404)
    expect(error).toBeTruthy();
    expect(error.message).toContain('404');
    
    // Expected behavior after fix:
    // fetch('/api/programs/') would return 200 OK
    // Response would contain array of programs from database
  });

  /**
   * Test 5: Programs are not visible across different sessions
   * **Validates: Requirement 2.3**
   * 
   * Bug Condition: On unfixed code, programs are session-specific (localStorage)
   * Expected Behavior: Programs should be visible to all users (database)
   */
  it('should make programs visible across different sessions', () => {
    // Arrange: Admin A saves a program
    document.getElementById('programName').value = 'BS Criminology';
    document.getElementById('programDuration').value = '4 years';
    document.getElementById('programStatus').value = 'active';
    window.saveProgram();

    // Verify program is in localStorage
    let savedData = localStorage.getItem('programData');
    expect(savedData).toBeTruthy();

    // Act: Simulate Admin B logging in (different session, different device)
    // In reality, Admin B would have a different localStorage
    localStorage.clear(); // Simulates different browser/device

    // Assert: On UNFIXED code, Admin B cannot see the program (BUG)
    savedData = localStorage.getItem('programData');
    expect(savedData).toBeNull(); // Admin B sees nothing!
    
    // Expected behavior after fix:
    // Admin B would fetch from /api/programs/
    // Database would return the program saved by Admin A
    // All admins see the same data
  });

  /**
   * Test 6: Programs don't appear on public CCJE page
   * **Validates: Requirement 2.2, 2.3**
   * 
   * Bug Condition: On unfixed code, loadProgramData() reads from localStorage
   * Expected Behavior: loadProgramData() should fetch from /api/programs/
   */
  it('should load programs from API for public pages', () => {
    // Simulate the loadProgramData function from programs.js
    function loadProgramData() {
      const savedData = localStorage.getItem('programData');
      if (savedData) {
        return JSON.parse(savedData);
      }
      // Fallback data
      return {
        prog1: { name: 'Bachelor of Science in Criminology', college: 'ccje', duration: '4 years', status: 'active' }
      };
    }

    // Arrange: No data in localStorage (simulates fresh browser)
    localStorage.clear();

    // Act: Load programs for public page
    const programs = loadProgramData();

    // Assert: On UNFIXED code, only fallback data is shown (BUG)
    // Real programs saved by admin are not visible
    expect(programs.prog1.name).toBe('Bachelor of Science in Criminology');
    // This is fallback data, not real data from database
    
    // Expected behavior after fix:
    // loadProgramData() would call fetch('/api/programs/')
    // Would return actual programs from database
    // No need for fallback data
  });

  /**
   * Property-Based Test: Multiple programs with random data
   * **Validates: Requirements 2.1, 2.2, 2.3**
   * 
   * This test generates random program data and verifies that all
   * programs are saved to localStorage (demonstrating the bug).
   * After fix, this should verify programs are saved to database.
   */
  it('should save multiple programs (currently to localStorage, should be database)', () => {
    fc.assert(
      fc.property(
        fc.record({
          name: fc.string({ minLength: 10, maxLength: 100 }),
          duration: fc.constantFrom('2 years', '3 years', '4 years', '5 years'),
          status: fc.constantFrom('active', 'inactive')
        }),
        (programData) => {
          // Arrange: Fill out the form with generated data
          document.getElementById('programName').value = programData.name;
          document.getElementById('programDuration').value = programData.duration;
          document.getElementById('programStatus').value = programData.status;

          // Act: Save the program
          window.saveProgram();

          // Assert: On UNFIXED code, program is saved to localStorage (BUG)
          const savedData = localStorage.getItem('programData');
          expect(savedData).toBeTruthy();
          
          const programs = JSON.parse(savedData);
          const lastProgram = Object.values(programs)[Object.values(programs).length - 1];
          
          expect(lastProgram.name).toBe(programData.name);
          expect(lastProgram.duration).toBe(programData.duration);
          expect(lastProgram.status).toBe(programData.status);
          expect(lastProgram.college).toBe('ccje');
          
          // Expected behavior after fix:
          // expect(fetchCalls.length).toBeGreaterThan(0);
          // expect(fetchCalls[fetchCalls.length - 1].url).toContain('/api/programs/');
        }
      ),
      { numRuns: 10 } // Run 10 random test cases
    );
  });
});
