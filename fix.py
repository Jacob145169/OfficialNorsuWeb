import re

with open('dashboard/templates/dashboard/aboutnorsu.html', 'r', encoding='utf-8') as f:
    content = f.read()

body = """<div class="about-page">

    <!-- Hero Section -->
    <header class="hero-section">
        <div class="hero-content">
            <span class="hero-subtitle">University Overview</span>
            <h1 class="hero-title">About NORSU</h1>
            <p class="hero-desc">Advancing progressive leadership, excellence in education, and impactful research since
                our founding.</p>
        </div>
    </header>

    <!-- Leadership Section -->
    <section class="leadership-section" aria-labelledby="president-heading">
        <div class="leadership-grid">
            <div class="leadership-image-wrap">
                <div class="leadership-image">
                    <img id="presidentPhotoImg" src="{% static 'dashboard/images/pres.png' %}"
                        data-default-src="{% static 'dashboard/images/pres.png' %}" alt="University President">
                </div>
            </div>
            <div class="leadership-info">
                <span class="leadership-role" id="presidentRole">Loading...</span>
                <h2 class="leadership-name" id="president-heading">
                    <span id="presidentName">Loading...</span>
                </h2>
                <div class="leadership-quote" id="presidentCaption">Loading caption...</div>
                <div class="text-module-content" style="max-width: 600px;">
                    Information will be updated soon.
                </div>
            </div>
        </div>
    </section>

    <!-- Core Grid -->
    <section class="core-section" id="contentArea" aria-live="polite">
        <div class="core-container">
            <span class="section-label">Founding Principles</span>

            <div class="vision-mission-grid">
                <div class="editorial-block" id="mission" data-type="mission">
                    <h2 class="editorial-title">Our Mission</h2>
                    <div class="editorial-content" data-field="mission"></div>
                </div>

                <div class="editorial-block" id="vision" data-type="vision">
                    <h2 class="editorial-title">Our Vision</h2>
                    <div class="editorial-content" data-field="vision"></div>
                </div>
            </div>

            <div class="text-module"
                style="background: var(--h-white); padding: 3rem; border: 2px solid var(--h-border);">
                <h3 class="text-module-title">General Mandate</h3>
                <div class="text-module-content" data-field="generalMandate"></div>
            </div>
        </div>
    </section>

    <!-- Details Section -->
    <section class="details-section">
        <span class="section-label">Strategic Priorities</span>
        <div class="details-grid">
            <div class="text-module" id="strategic-goals">
                <h3 class="text-module-title">Strategic Goals</h3>
                <div class="text-module-content" data-field="strategicGoals"></div>
            </div>
            <div class="text-module" id="core-values">
                <h3 class="text-module-title">Core Values</h3>
                <div class="text-module-content" data-field="coreValues"></div>
            </div>
            <div class="text-module" id="quality-policy">
                <h3 class="text-module-title">Quality Policy</h3>
                <div class="text-module-content" data-field="qualityPolicy"></div>
            </div>
        </div>
    </section>

    <!-- History Section -->
    <section class="history-section" id="norsu-history">
        <div class="history-inner">
            <span class="history-pretitle">The Origins</span>
            <h2 class="history-title">Institutional History</h2>
            <div class="history-content">
                <p id="norsu-history-content">
                    Loading history...
                </p>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
        <div class="cta-container">
            <span class="section-label">Official Documentation</span>
            <h2 class="cta-title">University Profile</h2>
            <p class="cta-desc">For a formalized and comprehensive overview of Negros Oriental State University's
                institutional information, including our policy, mandate, and history, please retrieve the official
                document.</p>
            <button onclick="downloadNORSUPDF();" class="btn-editorial">
                <i class="fas fa-file-pdf"></i>
                Download Document
            </button>
        </div>
    </section>

</div>"""

pattern = re.compile(r'<div class="about-page">.*?</section>\s*</div>', re.DOTALL)
new_content = pattern.sub(body, content)

with open('dashboard/templates/dashboard/aboutnorsu.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
