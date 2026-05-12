// College Facilities Management System
let collegeFacilities = {};

// Initialize facilities from localStorage
function initializeCollegeFacilities() {
    const savedData = localStorage.getItem('collegeFacilities');
    if (savedData) {
        collegeFacilities = JSON.parse(savedData);
    } else {
        // Initialize with default CIT facilities
        collegeFacilities = {
            cit: [
                { id: 'cit_office', name: 'CIT OFFICE', image: '/static/dashboard/images/citoff.jpg' },
                { id: 'cit_1', name: 'CIT 1', image: '/static/dashboard/images/cit1.jpg' },
                { id: 'cit_2', name: 'CIT 2', image: '/static/dashboard/images/cit2.jpg' },
                { id: 'cit_3', name: 'CIT 3', image: '/static/dashboard/images/cit8.jpg' },
                { id: 'cit_4', name: 'CIT 4', image: '/static/dashboard/images/cit4.jpg' },
                { id: 'cit_5', name: 'CIT 5', image: '/static/dashboard/images/cit2.jpg' },
                { id: 'cit_6', name: 'CIT 6', image: '/static/dashboard/images/cit6.jpg' },
                { id: 'cit_7', name: 'CIT 7', image: '/static/dashboard/images/cit8.jpg' },
                { id: 'cit_8', name: 'CIT 8', image: '/static/dashboard/images/cit8.jpg' },
                { id: 'cit_9', name: 'CIT 9', image: '/static/dashboard/images/cit9.jpg' },
                { id: 'cit_10', name: 'CIT 10', image: '/static/dashboard/images/cit10.jpg' },
                { id: 'cit_11', name: 'CIT 11', image: '/static/dashboard/images/cit11.jpg' }
            ]
        };
        localStorage.setItem('collegeFacilities', JSON.stringify(collegeFacilities));
    }
}

// Get facilities for a specific college
function getFacilitiesByCollege(collegeCode) {
    return collegeFacilities[collegeCode] || [];
}

// Generate facility cards for a college
function generateFacilityCards(collegeCode) {
    const facilities = getFacilitiesByCollege(collegeCode);
    
    if (facilities.length === 0) {
        // Show empty state when no facilities exist
        return `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-building"></i>
                </div>
                <h3>No Facilities Available</h3>
                <p>Facilities for this college will appear here once added in the admin dashboard.</p>
            </div>
        `;
    }
    
    let html = '';
    facilities.forEach(facility => {
        html += `
            <div class="facility-card">
                <img src="${facility.image}" alt="${facility.name}" onerror="this.src='/static/dashboard/images/default-facility.jpg'">
                <span class="label">${facility.name}</span>
            </div>
        `;
    });
    
    return html;
}

// Add new facility to a college
function addFacilityToCollege(collegeCode, facilityData) {
    if (!collegeFacilities[collegeCode]) {
        collegeFacilities[collegeCode] = [];
    }
    
    const newFacility = {
        id: facilityData.id || `${collegeCode}_${Date.now()}`,
        name: facilityData.name,
        image: facilityData.image || '/static/dashboard/images/default-facility.jpg'
    };
    
    collegeFacilities[collegeCode].push(newFacility);
    localStorage.setItem('collegeFacilities', JSON.stringify(collegeFacilities));
    
    return newFacility;
}

// Update facility in a college
function updateFacilityInCollege(collegeCode, facilityId, facilityData) {
    if (!collegeFacilities[collegeCode]) return false;
    
    const facilityIndex = collegeFacilities[collegeCode].findIndex(f => f.id === facilityId);
    if (facilityIndex === -1) return false;
    
    collegeFacilities[collegeCode][facilityIndex] = {
        ...collegeFacilities[collegeCode][facilityIndex],
        ...facilityData
    };
    
    localStorage.setItem('collegeFacilities', JSON.stringify(collegeFacilities));
    return true;
}

// Delete facility from a college
function deleteFacilityFromCollege(collegeCode, facilityId) {
    if (!collegeFacilities[collegeCode]) return false;
    
    const facilityIndex = collegeFacilities[collegeCode].findIndex(f => f.id === facilityId);
    if (facilityIndex === -1) return false;
    
    collegeFacilities[collegeCode].splice(facilityIndex, 1);
    localStorage.setItem('collegeFacilities', JSON.stringify(collegeFacilities));
    
    return true;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeCollegeFacilities();
});
