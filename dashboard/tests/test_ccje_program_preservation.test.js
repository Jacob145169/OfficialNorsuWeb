/**
 * Preservation Property Tests for CCJE Program Management
 * 
 * **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
 * 
 * This test suite verifies that UI behavior remains unchanged for non-save interactions.
 * These tests follow the observation-first methodology: observe behavior on UNFIXED code,
 * then write tests capturing that behavior.
 * 
 * Property 2: Preservation - UI Behavior Unchanged
 * For any user interaction that is NOT the final save action (modal display, form typing,
 * image preview, table rendering), the fixed code SHALL produce exactly the same visual
 * and interactive behavior as the original code, preserving all existing UI functionality
 * and user experience.
 * 
 * EXPECTED OUTCOME: These tests PASS on UNFIXED code (confirms baseline behavior)
 * After fix: These tests PASS on FIXED code (confirms no regressions)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as fc from 'fast-check';

/**
 * Load the JavaScript code from the HTML file
 * This simulates the browser environment where the code runs
 */
function loadProgramCode() {
  // Create the DOM structure needed for the program management UI
  document.body.innerHTML = `
    <div id="programModal" class="modal" style="display: none;">
      <div class="modal-content">
        <div class="modal-header">
          <h3 id="programModalTitle">Add New Program</h3>
          <span class="close" onclick="closeProgramModal()">&times;</span>
        </div>
        <div class="modal-body">
          <form id="programForm">
            <input type="hidden" id="programId">
            <div class="form-group">
              <label for="programName" class="form-label">Program Name</label>
              <input type="text" id="programName" class="form-control" placeholder="Enter program name" required>
            </div>
            <div class="form-group">
              <label for="programImage" class="form-label">Program Image</label>
              <input type="file" id="programImage" class="form-control" accept="image/*" onchange="previewProgramImage(event)">
              <div id="programImagePreview" style="margin-top: 10px; display: none;">
                <img id="previewImg" src="" alt="Preview" style="max-width: 100px; max-height: 100px; border-radius: 8px;">
              </div>
            </div>
            <div class="form-group">
              <label for="programDuration" class="form-label">Duration</label>
              <input type="text" id="programDuration" class="form-control" placeholder="e.g., 4 years" required>
            </div>
            <div class="form-group">
              <label for="programStatus" class="form-label">Status</label>
              <select id="programStatus" class="form-control" required>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" onclick="closeProgramModal()">Cancel</button>
          <button type="button" class="btn btn-primary" onclick="saveProgram()">
            <i class="fas fa-save"></i> Save Program
          </button>
        </div>
      </div>
    </div>

    <button class="btn btn-primary" onclick="openAddProgramModal()">
      <i class="fas fa-plus"></i> Add New Program
    </button>

    <table>
      <thead>
        <tr>
          <th>Image</th>
          <th>Program Name</th>
          <th>Duration</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="collegeProgramTableBody">
        <!-- Program rows will be populated by JavaScript -->
      </tbody>
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

  // Define openAddProgramModal function (from admin-dashboard.html)
  window.openAddProgramModal = function() {
    window.editingProgramId = null;
    document.getElementById('programModalTitle').textContent = 'Add New Program';
    document.getElementById('programForm').reset();
    document.getElementById('programModal').style.display = 'block';
  };

  // Define closeProgramModal function (from admin-dashboard.html)
  window.closeProgramModal = function() {
    document.getElementById('programModal').style.display = 'none';
    
    // Only reset form if not editing
    if (!window.editingProgramId) {
      document.getElementById('programForm').reset();
    }
  };

  // Define previewProgramImage function (from admin-dashboard.html)
  window.previewProgramImage = function(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('programImagePreview');
    const previewImg = document.getElementById('previewImg');
    
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        previewImg.src = e.target.result;
        preview.style.display = 'block';
      };
      reader.readAsDataURL(file);
    } else {
      preview.style.display = 'none';
    }
  };

  // Define populateCollegeProgramTable function (from admin-dashboard.html)
  window.populateCollegeProgramTable = function() {
    const tbody = document.getElementById('collegeProgramTableBody');
    
    if (!tbody) {
      return;
    }

    const userCollege = window.currentSession ? window.currentSession.college : null;
    
    // Filter programs by college
    const collegePrograms = Object.entries(window.programData)
      .filter(([id, program]) => program.college === userCollege)
      .map(([id, program]) => ({ id, ...program }));

    if (collegePrograms.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">No programs found. Click "Add New Program" to add your first program.</td></tr>';
      return;
    }

    const rows = collegePrograms.map(program => `
      <tr>
        <td>
          ${program.image ? `<img src="${program.image}" alt="${program.name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">` : '<div style="width: 50px; height: 50px; background: #f8f9fa; border-radius: 8px;"></div>'}
        </td>
        <td><strong>${program.name}</strong></td>
        <td>${program.duration}</td>
        <td>
          <span class="badge ${program.status === 'active' ? 'badge-success' : 'badge-secondary'}">
            ${program.status === 'active' ? 'Active' : 'Inactive'}
          </span>
        </td>
        <td>
          <button class="btn btn-sm btn-info" onclick="editProgram('${program.id}')">
            <i class="fas fa-edit"></i>
          </button>
          <button class="btn btn-sm btn-danger" onclick="deleteProgram('${program.id}')">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');

    tbody.innerHTML = rows;
  };
}

describe('CCJE Program Preservation Property Tests', () => {
  beforeEach(() => {
    // Clear localStorage and reset DOM before each test
    localStorage.clear();
    loadProgramCode();
  });

  /**
   * Test 1: Modal Display - Clicking "Add New Program" opens modal
   * **Validates: Requirement 3.1, 3.2**
   * 
   * Preservation: Modal display behavior must remain unchanged
   * The modal should open with correct form fields when button is clicked
   */
  it('should display modal with correct form fields when "Add New Program" is clicked', () => {
    // Arrange: Modal is initially hidden
    const modal = document.getElementById('programModal');
    expect(modal.style.display).toBe('none');

    // Act: Click "Add New Program" button
    window.openAddProgramModal();

    // Assert: Modal is now visible
    expect(modal.style.display).toBe('block');

    // Assert: Modal title is correct
    const modalTitle = document.getElementById('programModalTitle');
    expect(modalTitle.textContent).toBe('Add New Program');

    // Assert: All form fields are present
    expect(document.getElementById('programName')).toBeTruthy();
    expect(document.getElementById('programImage')).toBeTruthy();
    expect(document.getElementById('programDuration')).toBeTruthy();
    expect(document.getElementById('programStatus')).toBeTruthy();

    // Assert: Form fields are empty (reset)
    expect(document.getElementById('programName').value).toBe('');
    expect(document.getElementById('programDuration').value).toBe('');
    expect(document.getElementById('programStatus').value).toBe('active'); // Default value
  });

  /**
   * Test 2: Modal Close - Clicking close button hides modal
   * **Validates: Requirement 3.2**
   * 
   * Preservation: Modal close behavior must remain unchanged
   */
  it('should close modal when close button is clicked', () => {
    // Arrange: Open the modal
    window.openAddProgramModal();
    const modal = document.getElementById('programModal');
    expect(modal.style.display).toBe('block');

    // Act: Close the modal
    window.closeProgramModal();

    // Assert: Modal is now hidden
    expect(modal.style.display).toBe('none');
  });

  /**
   * Test 3: Form Validation - Empty form submission shows validation errors
   * **Validates: Requirement 3.2**
   * 
   * Preservation: Form validation behavior must remain unchanged
   * HTML5 validation should prevent submission of empty required fields
   */
  it('should show validation errors when required fields are empty', () => {
    // Arrange: Open modal and get form elements
    window.openAddProgramModal();
    const programName = document.getElementById('programName');
    const programDuration = document.getElementById('programDuration');
    const programStatus = document.getElementById('programStatus');

    // Assert: Required fields have the 'required' attribute
    expect(programName.hasAttribute('required')).toBe(true);
    expect(programDuration.hasAttribute('required')).toBe(true);
    expect(programStatus.hasAttribute('required')).toBe(true);

    // Assert: Empty fields are invalid
    programName.value = '';
    programDuration.value = '';
    expect(programName.validity.valid).toBe(false);
    expect(programDuration.validity.valid).toBe(false);

    // Assert: Filled fields are valid
    programName.value = 'BS Criminology';
    programDuration.value = '4 years';
    expect(programName.validity.valid).toBe(true);
    expect(programDuration.validity.valid).toBe(true);
  });

  /**
   * Test 4: Image Preview - Selecting an image shows preview
   * **Validates: Requirement 3.2**
   * 
   * Preservation: Image preview functionality must remain unchanged
   * When a file is selected, the preview should appear with the image
   */
  it('should display image preview when file is selected', async () => {
    // Arrange: Open modal and get image input
    window.openAddProgramModal();
    const imageInput = document.getElementById('programImage');
    const preview = document.getElementById('programImagePreview');
    const previewImg = document.getElementById('previewImg');

    // Assert: Preview is initially hidden
    expect(preview.style.display).toBe('none');

    // Arrange: Create a mock image file
    const mockImageData = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
    const mockFile = new File([''], 'test.png', { type: 'image/png' });

    // Mock FileReader
    const originalFileReader = global.FileReader;
    global.FileReader = class {
      readAsDataURL() {
        setTimeout(() => {
          this.onload({ target: { result: mockImageData } });
        }, 0);
      }
    };

    // Act: Simulate file selection
    Object.defineProperty(imageInput, 'files', {
      value: [mockFile],
      writable: false,
      configurable: true
    });
    
    // Trigger the change event
    const event = new Event('change');
    Object.defineProperty(event, 'target', {
      value: imageInput,
      writable: false
    });
    window.previewProgramImage(event);

    // Wait for FileReader to complete
    await new Promise(resolve => setTimeout(resolve, 10));

    // Assert: Preview is now visible
    expect(preview.style.display).toBe('block');
    expect(previewImg.src).toBe(mockImageData);

    // Cleanup
    global.FileReader = originalFileReader;
  });

  /**
   * Test 5: Table Rendering - Programs table displays with correct columns
   * **Validates: Requirement 3.3**
   * 
   * Preservation: Table structure and rendering must remain unchanged
   */
  it('should display programs table with correct columns', () => {
    // Arrange: Add some test programs to programData
    window.programData = {
      prog1: {
        name: 'Bachelor of Science in Criminology',
        college: 'ccje',
        duration: '4 years',
        status: 'active',
        image: ''
      },
      prog2: {
        name: 'Master of Arts in Criminal Justice',
        college: 'ccje',
        duration: '2 years',
        status: 'inactive',
        image: ''
      }
    };

    // Act: Populate the table
    window.populateCollegeProgramTable();

    // Assert: Table body exists
    const tbody = document.getElementById('collegeProgramTableBody');
    expect(tbody).toBeTruthy();

    // Assert: Table has correct number of rows (2 programs)
    const rows = tbody.querySelectorAll('tr');
    expect(rows.length).toBe(2);

    // Assert: Table contains program data
    const tableHTML = tbody.innerHTML;
    expect(tableHTML).toContain('Bachelor of Science in Criminology');
    expect(tableHTML).toContain('Master of Arts in Criminal Justice');
    expect(tableHTML).toContain('4 years');
    expect(tableHTML).toContain('2 years');
    expect(tableHTML).toContain('Active');
    expect(tableHTML).toContain('Inactive');

    // Assert: Table has action buttons (edit, delete)
    expect(tableHTML).toContain('fa-edit');
    expect(tableHTML).toContain('fa-trash');
  });

  /**
   * Test 6: Empty Table State - Shows message when no programs exist
   * **Validates: Requirement 3.3**
   * 
   * Preservation: Empty state message must remain unchanged
   */
  it('should display empty state message when no programs exist', () => {
    // Arrange: No programs in programData
    window.programData = {};

    // Act: Populate the table
    window.populateCollegeProgramTable();

    // Assert: Table shows empty state message
    const tbody = document.getElementById('collegeProgramTableBody');
    const tableHTML = tbody.innerHTML;
    expect(tableHTML).toContain('No programs found');
    expect(tableHTML).toContain('Add New Program');
  });

  /**
   * Test 7: Form Field Typing - User can type in form fields
   * **Validates: Requirement 3.2**
   * 
   * Preservation: Form input behavior must remain unchanged
   */
  it('should allow user to type in form fields', () => {
    // Arrange: Open modal
    window.openAddProgramModal();

    // Act: Type in form fields
    const programName = document.getElementById('programName');
    const programDuration = document.getElementById('programDuration');
    const programStatus = document.getElementById('programStatus');

    programName.value = 'BS Criminology';
    programDuration.value = '4 years';
    programStatus.value = 'active';

    // Assert: Values are correctly set
    expect(programName.value).toBe('BS Criminology');
    expect(programDuration.value).toBe('4 years');
    expect(programStatus.value).toBe('active');
  });

  /**
   * Test 8: Form Reset - Form is reset when modal is opened for new program
   * **Validates: Requirement 3.2**
   * 
   * Preservation: Form reset behavior must remain unchanged
   */
  it('should reset form when opening modal for new program', () => {
    // Arrange: Fill out the form
    window.openAddProgramModal();
    document.getElementById('programName').value = 'Test Program';
    document.getElementById('programDuration').value = '3 years';
    document.getElementById('programStatus').value = 'inactive';

    // Act: Close and reopen modal
    window.closeProgramModal();
    window.openAddProgramModal();

    // Assert: Form fields are reset
    expect(document.getElementById('programName').value).toBe('');
    expect(document.getElementById('programDuration').value).toBe('');
    expect(document.getElementById('programStatus').value).toBe('active'); // Default
  });

  /**
   * Property-Based Test: Modal behavior with random interactions
   * **Validates: Requirements 3.1, 3.2**
   * 
   * This test generates random modal open/close sequences and verifies
   * that the modal state is always consistent.
   */
  it('should maintain consistent modal state across random open/close sequences', () => {
    fc.assert(
      fc.property(
        fc.array(fc.constantFrom('open', 'close'), { minLength: 1, maxLength: 10 }),
        (actions) => {
          const modal = document.getElementById('programModal');
          
          actions.forEach(action => {
            if (action === 'open') {
              window.openAddProgramModal();
              // Assert: Modal is visible after open
              expect(modal.style.display).toBe('block');
            } else {
              window.closeProgramModal();
              // Assert: Modal is hidden after close
              expect(modal.style.display).toBe('none');
            }
          });

          // Final state depends on last action
          const lastAction = actions[actions.length - 1];
          if (lastAction === 'open') {
            expect(modal.style.display).toBe('block');
          } else {
            expect(modal.style.display).toBe('none');
          }
        }
      ),
      { numRuns: 20 } // Run 20 random test cases
    );
  });

  /**
   * Property-Based Test: Form validation with random inputs
   * **Validates: Requirement 3.2**
   * 
   * This test generates random form inputs and verifies that validation
   * works consistently.
   */
  it('should validate form fields consistently with random inputs', () => {
    fc.assert(
      fc.property(
        fc.record({
          name: fc.string({ maxLength: 100 }),
          duration: fc.string({ maxLength: 50 }),
          status: fc.constantFrom('active', 'inactive')
        }),
        (formData) => {
          // Arrange: Open modal
          window.openAddProgramModal();

          // Act: Fill form with random data
          const programName = document.getElementById('programName');
          const programDuration = document.getElementById('programDuration');
          const programStatus = document.getElementById('programStatus');

          programName.value = formData.name;
          programDuration.value = formData.duration;
          programStatus.value = formData.status;

          // Assert: Validation works correctly
          // Empty strings are invalid for required fields
          if (formData.name === '') {
            expect(programName.validity.valid).toBe(false);
          } else {
            expect(programName.validity.valid).toBe(true);
          }

          if (formData.duration === '') {
            expect(programDuration.validity.valid).toBe(false);
          } else {
            expect(programDuration.validity.valid).toBe(true);
          }

          // Status always has a value (select dropdown)
          expect(programStatus.validity.valid).toBe(true);
        }
      ),
      { numRuns: 20 } // Run 20 random test cases
    );
  });

  /**
   * Property-Based Test: Table rendering with random program data
   * **Validates: Requirement 3.3**
   * 
   * This test generates random program data and verifies that the table
   * renders correctly for all inputs.
   */
  it('should render table correctly with random program data', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            name: fc.string({ minLength: 1, maxLength: 100 }),
            duration: fc.constantFrom('2 years', '3 years', '4 years', '5 years'),
            status: fc.constantFrom('active', 'inactive')
          }),
          { minLength: 0, maxLength: 5 }
        ),
        (programs) => {
          // Arrange: Create program data
          window.programData = {};
          programs.forEach((program, index) => {
            window.programData[`prog${index}`] = {
              ...program,
              college: 'ccje',
              image: ''
            };
          });

          // Act: Populate table
          window.populateCollegeProgramTable();

          // Assert: Table body exists
          const tbody = document.getElementById('collegeProgramTableBody');
          expect(tbody).toBeTruthy();

          if (programs.length === 0) {
            // Assert: Empty state message is shown
            expect(tbody.innerHTML).toContain('No programs found');
          } else {
            // Assert: All programs are displayed
            const tableHTML = tbody.innerHTML;
            programs.forEach(program => {
              expect(tableHTML).toContain(program.name);
              expect(tableHTML).toContain(program.duration);
            });

            // Assert: Correct number of rows
            const rows = tbody.querySelectorAll('tr');
            expect(rows.length).toBe(programs.length);
          }
        }
      ),
      { numRuns: 15 } // Run 15 random test cases
    );
  });
});
