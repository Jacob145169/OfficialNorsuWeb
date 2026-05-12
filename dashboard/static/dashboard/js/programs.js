// Program Data for Website
// This file loads program data from admin dashboard and makes it available to all college pages

// Load program data from localStorage (set by admin dashboard)
function loadProgramData() {
    const savedData = localStorage.getItem('programData');
    console.log('Loading program data from localStorage...');
    console.log('Saved data found:', !!savedData);
    
    if (savedData) {
        try {
            const parsedData = JSON.parse(savedData);
            console.log('Parsed data:', parsedData);
            
            // Check if any programs have images
            const hasImages = Object.values(parsedData).some(program => program.image);
            console.log('Any programs have images:', hasImages);
            
            return parsedData;
        } catch (error) {
            console.error('Error parsing program data:', error);
        }
    }
    
    console.log('No saved data found, using fallback');
    // Fallback data if localStorage is empty
    return {
        prog1: { name: 'Bachelor of Science in Computer Science', college: 'cas', duration: '4 years', status: 'active' },
        prog2: { name: 'Bachelor of Business Administration', college: 'cba', duration: '4 years', status: 'active' },
        prog3: { name: 'Bachelor of Science in Criminology', college: 'ccje', duration: '4 years', status: 'active' },
        prog4: { name: 'Bachelor of Industrial Technology', college: 'cit', duration: '4 years', status: 'active' },
        prog5: { name: 'Bachelor of Elementary Education', college: 'cted', duration: '4 years', status: 'active' },
        prog6: { name: 'Bachelor of Science in Agriculture', college: 'caf', duration: '4 years', status: 'active' }
    };
}

// Get programs for a specific college
function getProgramsByCollege(collegeCode) {
    const allPrograms = loadProgramData();
    const collegePrograms = {};
    
    Object.keys(allPrograms).forEach(id => {
        const program = allPrograms[id];
        if (program.college === collegeCode) {
            collegePrograms[id] = program;
        }
    });
    
    return collegePrograms;
}

// Test function to verify images are working
function testImageLoading() {
    console.log('Testing image loading...');
    
    // Test 1: Check if default image loads
    const testImg = new Image();
    testImg.onload = function() {
        console.log('✅ Default image loads successfully');
    };
    testImg.onerror = function() {
        console.log('❌ Default image failed to load');
    };
    testImg.src = '/static/dashboard/images/pulis.jpg';
    
    // Test 2: Check localStorage data
    const savedData = localStorage.getItem('programData');
    if (savedData) {
        const programs = JSON.parse(savedData);
        Object.keys(programs).forEach(id => {
            const program = programs[id];
            if (program.image) {
                console.log(`Program ${program.name} has image:`, program.image.substring(0, 50) + '...');
            } else {
                console.log(`Program ${program.name} has no image`);
            }
        });
    } else {
        console.log('No programs in localStorage');
    }
}

// Generate program cards HTML for a college
function generateProgramCards(collegeCode) {
    const programs = getProgramsByCollege(collegeCode);
    let html = '';
    
    console.log('Generating cards for college:', collegeCode);
    console.log('Programs found:', programs);
    
    if (Object.keys(programs).length === 0) {
        // Show empty state when no programs exist
        html = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <h3>No Programs Available</h3>
                <p>Programs for this college will appear here once added in the admin dashboard.</p>
            </div>
        `;
    } else {
        // Generate dynamic cards with exact same structure
        Object.values(programs).forEach(program => {
            const isHighlighted = program.status === 'active';
            const statusText = program.status === 'active' ? 'Available' : 'Not Available';
            
            console.log('Processing program:', program);
            
            // Use uploaded image or default fallback
            let programImage = program.image || "/static/dashboard/images/pulis.jpg";
            
            // Debug the image source
            console.log('Image source:', programImage);
            console.log('Has image property:', !!program.image);
            
            html += `
                <div class="card">
                    <img src="${programImage}" alt="${program.name}" onerror="console.log('Image failed to load, using fallback'); this.src='/static/dashboard/images/pulis.jpg'" onload="console.log('Image loaded successfully:', this.src)">
                    <div class="card-body ${isHighlighted ? 'highlighted' : ''}">
                        <h3>${program.name}</h3>
                        <div class="program-info">
                            <div class="info-item">
                                <i class="fas fa-clock"></i>
                                <span>${program.duration}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-info-circle"></i>
                                <span>${statusText}</span>
                            </div>
                        </div>
                        <a href="/programs/#${program.name.toLowerCase().replace(/\s+/g, '-')}" class="learn-btn">Learn More</a>
                    </div>
                </div>
            `;
        });
    }
    
    return html;
}

// Get full college name from code
function getCollegeFullName(collegeCode) {
    const colleges = {
        'cas': 'College of Arts & Sciences',
        'cba': 'College of Business Administration',
        'ccje': 'College of Criminal Justice Education',
        'cit': 'College of Industrial Technology',
        'cted': 'College of Teacher Education',
        'caf': 'College of Agriculture & Forestry'
    };
    return colleges[collegeCode] || collegeCode;
}

// Show program details (placeholder function)
function showProgramDetails(programName) {
    alert(`Program Details: ${programName}\n\nThis would typically open a detailed program page with curriculum, admission requirements, and more information.`);
}

// Initialize program cards when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Run tests to debug image issues
    testImageLoading();
    
    // This will be called from individual college pages
    if (typeof initializeCollegePrograms === 'function') {
        initializeCollegePrograms();
    }
});
