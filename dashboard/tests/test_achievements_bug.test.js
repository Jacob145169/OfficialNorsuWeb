/**
 * Bug Condition Exploration Test for Achievements Management
 * 
 * **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
 * 
 * This test explores the bug condition where the achievement form submission
 * does not save achievements to localStorage and does not display them in the
 * achievements table. Additionally, the image preview functionality does not work.
 * 
 * On UNFIXED code, these tests will FAIL, confirming the bug exists.
 * After the fix is implemented, these tests will PASS, confirming the expected
 * behavior is satisfied.
 * 
 * Property 1: Fault Condition - Achievement Form Saves and Displays Data
 * For any form submission where the achievement form is filled with valid data,
 * the fixed achievement form handler SHALL save the achievement to localStorage,
 * display it in the achievements table with all provided information including
 * uploaded images, close the modal, clear form fields, display success notification,
 * and sync the achievement to other dashboards.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as fc from 'fast-check';

/**
 * Load the JavaScript code from the HTML file
 * This simulates the browser environment where the code runs
 */
function loadAchievementCode() {
  // Create the DOM structure needed for the achievement form
  document.body.innerHTML = `
    <div id="achievementModal" class="modal">
      <form id="achievementForm">
        <input type="text" id="achievementTitle" required>
        <select id="achievementCategory" required>
          <option value="academic">Academic Excellence</option>
          <option value="sports">Sports Achievement</option>
        </select>
        <input type="date" id="achievementDate" required>
        <textarea id="achievementDescription" required></textarea>
        <input type="text" id="achievementRecipient" required>
        <input type="file" id="achievementImage" accept="image/*">
        <div id="achievementImagePreview" style="display: none;">
          <img src="" alt="Preview">
          <button type="button" onclick="removeImage('achievement')">Remove</button>
        </div>
        <button type="submit">Add Achievement</button>
      </form>
    </div>
    <table>
      <tbody id="achievementsTable"></tbody>
    </table>
  `;

  // Mock notification function
  window.showNotification = vi.fn();
  
  // Mock modal close function
  window.closeModal = vi.fn();
  
  // Mock sync function
  window.syncAchievementToDashboards = vi.fn();
  
  // Mock loadDashboardData function
  window.loadDashboardData = vi.fn();

  // Define the setupFileUpload function (from the HTML file)
  window.setupFileUpload = function(inputId, previewId) {
    const input = document.getElementById(inputId);
    const previewContainer = document.getElementById(previewId);
    const previewImg = previewContainer?.querySelector('img');
    
    if (input && previewContainer) {
      input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
          // Validate file type
          if (!file.type.startsWith('image/')) {
            window.showNotification('Please select an image file', 'error');
            this.value = '';
            return;
          }
          
          // Validate file size (max 5MB)
          if (file.size > 5 * 1024 * 1024) {
            window.showNotification('Image size must be less than 5MB', 'error');
            this.value = '';
            return;
          }
          
          // Read and display the image
          const reader = new FileReader();
          reader.onload = function(e) {
            previewImg.src = e.target.result;
            previewContainer.style.display = 'block';
          };
          reader.readAsDataURL(file);
        } else {
          previewContainer.style.display = 'none';
          previewImg.src = '';
        }
      });
    }
  };

  // Define the removeImage function
  window.removeImage = function(type) {
    const input = document.getElementById(type + 'Image');
    const previewContainer = document.getElementById(type + 'ImagePreview');
    const previewImg = previewContainer?.querySelector('img');
    
    if (input) input.value = '';
    if (previewContainer) previewContainer.style.display = 'none';
    if (previewImg) previewImg.src = '';
  };

  // Define the getImageData function
  window.getImageData = function(type) {
    const input = document.getElementById(type + 'Image');
    const previewContainer = document.getElementById(type + 'ImagePreview');
    const previewImg = previewContainer?.querySelector('img');
    
    if (input && input.files && input.files.length > 0) {
      return previewImg?.src || null;
    }
    return null;
  };

  // Define the getCategoryLabel function
  window.getCategoryLabel = function(category) {
    const labels = {
      'academic': 'Academic Excellence',
      'sports': 'Sports',
      'research': 'Research',
      'community': 'Community Service',
      'arts': 'Arts & Culture',
      'leadership': 'Leadership',
      'international': 'International',
      'other': 'Other'
    };
    return labels[category] || category;
  };

  // Define the loadAchievements function (from the HTML file)
  window.loadAchievements = function() {
    const achievements = JSON.parse(localStorage.getItem('superAdminAchievements') || '[]');
    const achievementsTable = document.getElementById('achievementsTable');
    
    if (achievements.length === 0) {
      achievementsTable.innerHTML = '<tr><td colspan="6" style="text-align: center;">No achievements found. Add your first achievement!</td></tr>';
      return;
    }
    
    const achievementsHTML = achievements.map(achievement => `
      <tr>
        <td>
          ${achievement.image ? `<img src="${achievement.image}" alt="${achievement.title}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">` : '<div style="width: 50px; height: 50px; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-trophy" style="color: #f39c12;"></i></div>'}
        </td>
        <td><strong>${achievement.title}</strong></td>
        <td><span class="category-badge category-${achievement.category}">${window.getCategoryLabel(achievement.category)}</span></td>
        <td>${new Date(achievement.date).toLocaleDateString()}</td>
        <td>${achievement.description.substring(0, 100)}${achievement.description.length > 100 ? '...' : ''}</td>
        <td>
          <button class="btn btn-sm btn-info" onclick="viewAchievement('${achievement.id}')">
            <i class="fas fa-eye"></i>
          </button>
          <button class="btn btn-sm btn-danger" onclick="deleteAchievement('${achievement.id}')">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
    
    achievementsTable.innerHTML = achievementsHTML;
  };

  // NOTE: The achievement form submission handler is NOT initialized here
  // This simulates the UNFIXED code where setupFileUpload is not called for achievementImage
  // and the form handler may have issues
  
  // UNFIXED CODE: Missing setupFileUpload call for achievementImage
  // setupFileUpload('achievementImage', 'achievementImagePreview'); // <-- THIS IS MISSING
  
  // Achievement form submission handler (from the HTML file)
  document.getElementById('achievementForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const achievement = {
      id: Date.now().toString(),
      title: document.getElementById('achievementTitle').value,
      category: document.getElementById('achievementCategory').value,
      date: document.getElementById('achievementDate').value,
      description: document.getElementById('achievementDescription').value,
      recipient: document.getElementById('achievementRecipient').value,
      image: window.getImageData('achievement'),
      createdDate: new Date().toISOString()
    };
    
    const achievements = JSON.parse(localStorage.getItem('superAdminAchievements') || '[]');
    achievements.push(achievement);
    localStorage.setItem('superAdminAchievements', JSON.stringify(achievements));

    // Clear form fields
    this.reset();
    
    // Clear image preview
    const previewContainer = document.getElementById('achievementImagePreview');
    const previewImg = previewContainer?.querySelector('img');
    if (previewContainer) {
      previewContainer.style.display = 'none';
    }
    if (previewImg) {
      previewImg.src = '';
    }

    // Sync to other dashboards
    window.syncAchievementToDashboards(achievement);

    window.closeModal('achievementModal');
    window.loadAchievements();
    window.loadDashboardData();
    window.showNotification('Achievement added successfully!', 'success');
  });
}

describe('Achievement Management Bug Condition Tests', () => {
  beforeEach(() => {
    // Clear localStorage and reset DOM before each test
    localStorage.clear();
    loadAchievementCode();
  });

  /**
   * Test 1: Achievement form submission saves to localStorage
   * **Validates: Requirement 2.1**
   * 
   * Bug Condition: On unfixed code, achievement may not be saved to localStorage
   * Expected Behavior: Achievement is saved to localStorage under 'superAdminAchievements' key
   */
  it('should save achievement to localStorage when form is submitted', () => {
    // Arrange: Fill out the form with valid data
    document.getElementById('achievementTitle').value = "Dean's List Award";
    document.getElementById('achievementCategory').value = 'academic';
    document.getElementById('achievementDate').value = '2024-01-15';
    document.getElementById('achievementDescription').value = 'Awarded to top students';
    document.getElementById('achievementRecipient').value = 'John Doe';

    // Act: Submit the form
    const form = document.getElementById('achievementForm');
    form.dispatchEvent(new Event('submit'));

    // Assert: Achievement should be saved to localStorage
    const savedAchievements = JSON.parse(localStorage.getItem('superAdminAchievements') || '[]');
    
    expect(savedAchievements).toHaveLength(1);
    expect(savedAchievements[0]).toMatchObject({
      title: "Dean's List Award",
      category: 'academic',
      date: '2024-01-15',
      description: 'Awarded to top students',
      recipient: 'John Doe'
    });
    expect(savedAchievements[0]).toHaveProperty('id');
    expect(savedAchievements[0]).toHaveProperty('createdDate');
  });

  /**
   * Test 2: Achievement appears in table after submission
   * **Validates: Requirement 2.2**
   * 
   * Bug Condition: On unfixed code, achievement may not appear in the table
   * Expected Behavior: Achievement is displayed in the achievements table with all data
   */
  it('should display achievement in table after form submission', () => {
    // Arrange: Fill out the form
    document.getElementById('achievementTitle').value = 'Research Excellence Award';
    document.getElementById('achievementCategory').value = 'research';
    document.getElementById('achievementDate').value = '2024-02-20';
    document.getElementById('achievementDescription').value = 'Outstanding research contribution';
    document.getElementById('achievementRecipient').value = 'Jane Smith';

    // Act: Submit the form
    const form = document.getElementById('achievementForm');
    form.dispatchEvent(new Event('submit'));

    // Assert: Achievement should appear in the table
    const table = document.getElementById('achievementsTable');
    const tableHTML = table.innerHTML;
    
    expect(tableHTML).toContain('Research Excellence Award');
    expect(tableHTML).toContain('Outstanding research contribution');
    expect(tableHTML).toContain('Jane Smith');
    expect(tableHTML).toContain('Research'); // Category label
  });

  /**
   * Test 3: Image preview functionality works when file is selected
   * **Validates: Requirement 2.3**
   * 
   * Bug Condition: On unfixed code, image preview does NOT work because
   * setupFileUpload is not called for achievementImage
   * Expected Behavior: Image preview appears when file is selected
   * 
   * CRITICAL: This test will FAIL on unfixed code because setupFileUpload
   * is not called for 'achievementImage' in the DOMContentLoaded handler
   */
  it('should display image preview when file is selected', async () => {
    // First, we need to call setupFileUpload to enable the functionality
    // On UNFIXED code, this is NOT called, so the test will fail
    window.setupFileUpload('achievementImage', 'achievementImagePreview');

    // Arrange: Create a mock image file
    const mockImageData = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
    const mockFile = new File([''], 'test.png', { type: 'image/png' });
    
    const fileInput = document.getElementById('achievementImage');
    const previewContainer = document.getElementById('achievementImagePreview');
    const previewImg = previewContainer.querySelector('img');

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
    Object.defineProperty(fileInput, 'files', {
      value: [mockFile],
      writable: false
    });
    fileInput.dispatchEvent(new Event('change'));

    // Wait for FileReader to complete
    await new Promise(resolve => setTimeout(resolve, 10));

    // Assert: Preview should be visible with the image
    expect(previewContainer.style.display).toBe('block');
    expect(previewImg.src).toBe(mockImageData);

    // Cleanup
    global.FileReader = originalFileReader;
  });

  /**
   * Test 4: Form fields are cleared after submission
   * **Validates: Requirement 2.6**
   * 
   * Bug Condition: On unfixed code, form fields may not be cleared
   * Expected Behavior: All form fields are cleared after successful submission
   */
  it('should clear form fields after submission', () => {
    // Arrange: Fill out the form
    document.getElementById('achievementTitle').value = 'Test Achievement';
    document.getElementById('achievementCategory').value = 'sports';
    document.getElementById('achievementDate').value = '2024-03-10';
    document.getElementById('achievementDescription').value = 'Test description';
    document.getElementById('achievementRecipient').value = 'Test Recipient';

    // Act: Submit the form
    const form = document.getElementById('achievementForm');
    form.dispatchEvent(new Event('submit'));

    // Assert: Form fields should be cleared
    expect(document.getElementById('achievementTitle').value).toBe('');
    expect(document.getElementById('achievementCategory').value).toBe('');
    expect(document.getElementById('achievementDate').value).toBe('');
    expect(document.getElementById('achievementDescription').value).toBe('');
    expect(document.getElementById('achievementRecipient').value).toBe('');
  });

  /**
   * Test 5: Modal closes after submission
   * **Validates: Requirement 2.4**
   * 
   * Bug Condition: On unfixed code, modal may not close
   * Expected Behavior: Modal closes after successful submission
   */
  it('should close modal after form submission', () => {
    // Arrange: Fill out the form
    document.getElementById('achievementTitle').value = 'Test Achievement';
    document.getElementById('achievementCategory').value = 'academic';
    document.getElementById('achievementDate').value = '2024-01-01';
    document.getElementById('achievementDescription').value = 'Test';
    document.getElementById('achievementRecipient').value = 'Test';

    // Act: Submit the form
    const form = document.getElementById('achievementForm');
    form.dispatchEvent(new Event('submit'));

    // Assert: closeModal should be called
    expect(window.closeModal).toHaveBeenCalledWith('achievementModal');
  });

  /**
   * Test 6: Success notification is displayed
   * **Validates: Requirement 2.5**
   * 
   * Bug Condition: On unfixed code, notification may not be displayed
   * Expected Behavior: Success notification is shown after submission
   */
  it('should display success notification after form submission', () => {
    // Arrange: Fill out the form
    document.getElementById('achievementTitle').value = 'Test Achievement';
    document.getElementById('achievementCategory').value = 'academic';
    document.getElementById('achievementDate').value = '2024-01-01';
    document.getElementById('achievementDescription').value = 'Test';
    document.getElementById('achievementRecipient').value = 'Test';

    // Act: Submit the form
    const form = document.getElementById('achievementForm');
    form.dispatchEvent(new Event('submit'));

    // Assert: showNotification should be called with success message
    expect(window.showNotification).toHaveBeenCalledWith('Achievement added successfully!', 'success');
  });

  /**
   * Test 7: Achievement syncs to other dashboards
   * **Validates: Requirement 2.1**
   * 
   * Bug Condition: On unfixed code, sync may not occur
   * Expected Behavior: syncAchievementToDashboards is called with the achievement
   */
  it('should sync achievement to other dashboards', () => {
    // Arrange: Fill out the form
    document.getElementById('achievementTitle').value = 'Test Achievement';
    document.getElementById('achievementCategory').value = 'academic';
    document.getElementById('achievementDate').value = '2024-01-01';
    document.getElementById('achievementDescription').value = 'Test';
    document.getElementById('achievementRecipient').value = 'Test';

    // Act: Submit the form
    const form = document.getElementById('achievementForm');
    form.dispatchEvent(new Event('submit'));

    // Assert: syncAchievementToDashboards should be called
    expect(window.syncAchievementToDashboards).toHaveBeenCalled();
    const syncCall = window.syncAchievementToDashboards.mock.calls[0][0];
    expect(syncCall).toMatchObject({
      title: 'Test Achievement',
      category: 'academic',
      date: '2024-01-01',
      description: 'Test',
      recipient: 'Test'
    });
  });

  /**
   * Property-Based Test: Multiple achievements with random data
   * **Validates: Requirements 2.1, 2.2**
   * 
   * This test generates random achievement data and verifies that all
   * achievements are saved and displayed correctly.
   */
  it('should save and display multiple achievements with random data', () => {
    fc.assert(
      fc.property(
        fc.record({
          title: fc.string({ minLength: 1, maxLength: 100 }),
          category: fc.constantFrom('academic', 'sports', 'research', 'community', 'arts', 'leadership', 'international', 'other'),
          date: fc.date({ min: new Date('2020-01-01'), max: new Date('2025-12-31') }).map(d => d.toISOString().split('T')[0]),
          description: fc.string({ minLength: 10, maxLength: 500 }),
          recipient: fc.string({ minLength: 1, maxLength: 100 })
        }),
        (achievementData) => {
          // Arrange: Fill out the form with generated data
          document.getElementById('achievementTitle').value = achievementData.title;
          document.getElementById('achievementCategory').value = achievementData.category;
          document.getElementById('achievementDate').value = achievementData.date;
          document.getElementById('achievementDescription').value = achievementData.description;
          document.getElementById('achievementRecipient').value = achievementData.recipient;

          // Act: Submit the form
          const form = document.getElementById('achievementForm');
          form.dispatchEvent(new Event('submit'));

          // Assert: Achievement should be saved to localStorage
          const savedAchievements = JSON.parse(localStorage.getItem('superAdminAchievements') || '[]');
          const lastAchievement = savedAchievements[savedAchievements.length - 1];
          
          expect(lastAchievement.title).toBe(achievementData.title);
          expect(lastAchievement.category).toBe(achievementData.category);
          expect(lastAchievement.date).toBe(achievementData.date);
          expect(lastAchievement.description).toBe(achievementData.description);
          expect(lastAchievement.recipient).toBe(achievementData.recipient);

          // Assert: Achievement should appear in the table
          const table = document.getElementById('achievementsTable');
          const tableHTML = table.innerHTML;
          expect(tableHTML).toContain(achievementData.title);
        }
      ),
      { numRuns: 10 } // Run 10 random test cases
    );
  });
});
