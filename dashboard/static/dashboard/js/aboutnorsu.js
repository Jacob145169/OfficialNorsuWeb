/**
 * About NORSU Page JavaScript
 * Handles dynamic loading of NORSU information from the backend API
 * with a localStorage fallback for older browser-saved content.
 */

class NORSUAboutPage {
    constructor() {
        this.apiUrl = '/api/university-info/';
        this.storageKey = 'superAdminNORSUInfo';
        this.presidentStorageKey = 'superAdminPresidentInfo';
        this.historyStorageKey = 'superAdminHistoryInfo';
        this.contentArea = null;
        this.refreshInterval = null;
        this.navEl = null;
        this.lastUpdatedEl = null;
        this.observer = null;
        this.currentInfo = null;
        this.defaultPresident = {
            role: 'University President',
            name: 'Information will be updated soon.',
            caption: 'Information will be updated soon.'
        };
        this.defaultInfo = {
            generalMandate: 'University information for this section will appear here once it is published by the administrator.',
            vision: 'Information will be updated soon.',
            mission: 'Information will be updated soon.',
            visionImage: '',
            missionImage: '',
            strategicGoals: 'Information will be updated soon.',
            coreValues: 'Information will be updated soon.',
            qualityPolicy: 'Information will be updated soon.'
        };
        this.defaultHistory = {
            title: 'Institutional History',
            body: 'Information will be updated soon.'
        };
        this.init();
    }

    /**
     * Initialize the About NORSU page
     */
    init() {
        console.log('About NORSU page initialized');
        this.contentArea = document.getElementById('contentArea');
        this.navEl = document.getElementById('aboutNav');
        this.lastUpdatedEl = document.getElementById('aboutLastUpdated');

        this.applyPresidentProfile();
        this.applyHistorySection();

        if (this.contentArea) {
            this.loadNORSUInformation();
            this.setupActions();
            this.setupSectionNav();
            // Keep auto-refresh, but avoid being too aggressive.
            this.setupAutoRefresh();
            this.setupStorageListener();
            this.setupKeyboardShortcuts();
        } else {
            console.error('Content area not found');
        }
    }

    getFieldElements() {
        return Array.from(document.querySelectorAll('[data-field]'));
    }

    setupActions() {
        const refreshBtn = document.getElementById('aboutRefreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadNORSUInformation());
        }

        const copyBtn = document.getElementById('aboutCopyLinkBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', async () => {
                const url = window.location.href;
                try {
                    if (navigator.clipboard?.writeText) {
                        await navigator.clipboard.writeText(url);
                    } else {
                        const temp = document.createElement('textarea');
                        temp.value = url;
                        document.body.appendChild(temp);
                        temp.select();
                        document.execCommand('copy');
                        temp.remove();
                    }
                    copyBtn.blur();
                } catch (e) {
                    console.warn('Copy failed:', e);
                }
            });
        }

        // Smooth scrolling for pills
        if (this.navEl) {
            this.navEl.addEventListener('click', (e) => {
                const a = e.target.closest('a[href^="#"]');
                if (!a) return;
                const id = a.getAttribute('href');
                const el = document.querySelector(id);
                if (!el) return;
                e.preventDefault();
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        }
    }

    /**
     * Load NORSU information from localStorage
     */
    async loadNORSUInformation() {
        if (!this.contentArea) return;

        try {
            this.showLoadingState();

            const [infoData] = await Promise.all([
                this.fetchNORSUInformation(),
                this.delay(250)
            ]);

            if (infoData.length === 0) {
                this.showNoDataState();
            } else {
                const latestInfo = this.getLatestInfoRecord(infoData);
                this.displayNORSUInfo(latestInfo);
            }
        } catch (error) {
            console.error('Error loading NORSU information:', error);
            this.showErrorState();
        }
    }

    async fetchNORSUInformation() {
        try {
            const response = await fetch(this.apiUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Unable to load university information');
            }

            const infoData = Array.isArray(data.info) ? data.info : [];
            if (infoData.length > 0) {
                localStorage.setItem(this.storageKey, JSON.stringify(infoData));
                return infoData;
            }
        } catch (error) {
            console.warn('Falling back to localStorage for NORSU information:', error);
        }

        return this.getStoredNORSUInformation();
    }

    getStoredNORSUInformation() {
        try {
            const rawInfoData = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
            return Array.isArray(rawInfoData) ? rawInfoData : (rawInfoData ? [rawInfoData] : []);
        } catch (error) {
            console.error('Error reading localStorage NORSU information:', error);
            return [];
        }
    }

    /**
     * Display loading state
     */
    showLoadingState() {
        // If the template already has section cards, just set placeholders.
        const fields = this.getFieldElements();
        if (fields.length > 0) {
            fields.forEach(el => {
                el.textContent = 'Loading...';
            });
        } else {
            this.contentArea.innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <h2>Loading NORSU Information...</h2>
                    <p>Please wait while we fetch the latest information.</p>
                </div>
            `;
        }

        if (this.lastUpdatedEl) {
            this.lastUpdatedEl.hidden = true;
            this.lastUpdatedEl.textContent = '';
        }
    }

    /**
     * Display NORSU information
     */
    displayNORSUInfo(info) {
        if (!this.contentArea || !info) return;

        this.currentInfo = info;
        const data = {
            generalMandate: this.toDisplayHtml(info.generalMandate, this.defaultInfo.generalMandate),
            vision: this.toDisplayHtml(info.vision, this.defaultInfo.vision),
            mission: this.toDisplayHtml(info.mission, this.defaultInfo.mission),
            strategicGoals: this.toDisplayHtml(info.strategicGoals, this.defaultInfo.strategicGoals),
            coreValues: this.toDisplayHtml(info.coreValues, this.defaultInfo.coreValues),
            qualityPolicy: this.toDisplayHtml(info.qualityPolicy, this.defaultInfo.qualityPolicy)
        };

        const fields = this.getFieldElements();
        if (fields.length > 0) {
            fields.forEach(el => {
                const key = el.getAttribute('data-field');
                if (!key) return;
                el.innerHTML = data[key] || '';
            });
        } else {
            // Fallback for older markup if this template gets swapped.
            this.contentArea.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h2>Page needs an update</h2>
                    <p>The About page template was updated but could not be detected. Please refresh.</p>
                    <button class="refresh-btn" onclick="window.location.reload()">Reload</button>
                </div>
            `;
        }

        this.applyEditorialImages(info);

        if (this.lastUpdatedEl) {
            const timestamp = info.updatedAt || info.createdDate || info.updated_at || info.created_at;
            const when = timestamp ? new Date(timestamp).toLocaleString() : 'Unknown';
            this.lastUpdatedEl.hidden = false;
            this.lastUpdatedEl.innerHTML = `<i class="fa-solid fa-clock"></i> Last updated: <strong>${this.escapeHtml(String(when))}</strong>`;
        }
    }

    applyEditorialImages(info = {}) {
        const blocks = [
            {
                key: 'missionImage',
                selector: '.editorial-block[data-type="mission"]',
                overlay: 'linear-gradient(135deg, rgba(0, 0, 0, 0.82), rgba(0, 0, 0, 0.58))'
            },
            {
                key: 'visionImage',
                selector: '.editorial-block[data-type="vision"]',
                overlay: 'linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.82))'
            }
        ];

        blocks.forEach(({ key, selector, overlay }) => {
            const block = document.querySelector(selector);
            if (!block) return;

            const imageUrl = (info[key] || '').trim();
            if (imageUrl) {
                const safeUrl = imageUrl.replace(/"/g, '\\"');
                block.style.background = `${overlay}, url("${safeUrl}") center / cover no-repeat`;
                block.classList.add('editorial-block--has-image');
            } else {
                block.style.background = '';
                block.classList.remove('editorial-block--has-image');
            }
        });
    }

    /**
     * Show no data state
     */
    showNoDataState() {
        if (!this.contentArea) return;

        this.currentInfo = { ...this.defaultInfo };
        const fields = this.getFieldElements();
        if (fields.length > 0) {
            fields.forEach(el => {
                const key = el.getAttribute('data-field');
                el.innerHTML = this.toDisplayHtml(this.defaultInfo[key], this.defaultInfo[key]);
            });
        } else {
            this.contentArea.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-info-circle"></i>
                    <h2>No Information Available</h2>
                    <p>NORSU information has not been added yet. Please contact the administrator to update the institutional information.</p>
                    <button class="refresh-btn" onclick="window.norsuAboutPage.loadNORSUInformation()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
            `;
        }

        this.applyEditorialImages(this.defaultInfo);

        if (this.lastUpdatedEl) {
            this.lastUpdatedEl.hidden = false;
            this.lastUpdatedEl.innerHTML = `<i class="fa-solid fa-circle-info"></i> Showing default content (admin data not yet published).`;
        }
    }

    /**
     * Show error state
     */
    showErrorState() {
        if (!this.contentArea) return;

        this.showNoDataState();

        if (this.lastUpdatedEl) {
            this.lastUpdatedEl.hidden = false;
            this.lastUpdatedEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Unable to load admin data, so default content is being shown.`;
        }
    }

    /**
     * Setup auto-refresh functionality
     */
    setupAutoRefresh() {
        // Check for updates periodically (avoid overly frequent refresh).
        this.refreshInterval = setInterval(() => {
            this.loadNORSUInformation();
        }, 120000);
    }

    /**
     * Setup storage event listener for cross-tab updates
     */
    setupStorageListener() {
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey) {
                console.log('NORSU information updated in another tab, refreshing...');
                this.loadNORSUInformation();
            }
            if (e.key === this.presidentStorageKey) {
                console.log('President profile updated in another tab, refreshing...');
                this.applyPresidentProfile();
            }
            if (e.key === this.historyStorageKey) {
                console.log('History info updated in another tab, refreshing...');
                this.applyHistorySection();
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+R or F5 to refresh
            if ((e.ctrlKey && e.key === 'r') || e.key === 'F5') {
                e.preventDefault();
                this.loadNORSUInformation();
            }
            // Escape to stop auto-refresh
            if (e.key === 'Escape') {
                this.stopAutoRefresh();
            }
        });
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh stopped');
        }
    }

    setupSectionNav() {
        if (!this.navEl) return;

        const pills = Array.from(this.navEl.querySelectorAll('a[href^="#"]'));
        const targets = pills
            .map(a => document.querySelector(a.getAttribute('href')))
            .filter(Boolean);

        if (targets.length === 0) return;

        const setActive = (id) => {
            pills.forEach(a => {
                const href = a.getAttribute('href');
                a.classList.toggle('active', href === id);
            });
        };

        // Initial state
        setActive(pills[0]?.getAttribute('href') || '#mission');

        try {
            this.observer = new IntersectionObserver((entries) => {
                const visible = entries
                    .filter(e => e.isIntersecting)
                    .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
                if (visible?.target?.id) {
                    setActive(`#${visible.target.id}`);
                }
            }, { root: null, threshold: [0.25, 0.4, 0.6], rootMargin: '-20% 0px -65% 0px' });

            targets.forEach(t => this.observer.observe(t));
        } catch (e) {
            console.warn('IntersectionObserver not available:', e);
        }
    }

    /**
     * Restart auto-refresh
     */
    restartAutoRefresh() {
        this.stopAutoRefresh();
        this.setupAutoRefresh();
        console.log('Auto-refresh restarted');
    }

    /**
     * Apply University President profile from the database to the About page section.
     */
    async applyPresidentProfile() {
        const imgEl = document.getElementById('presidentPhotoImg');
        const roleEl = document.getElementById('presidentRole');
        const nameEl = document.getElementById('presidentName');
        const captionEl = document.getElementById('presidentCaption');

        if (!imgEl && !roleEl && !nameEl && !captionEl) {
            return;
        }

        let data = null;
        try {
            const response = await fetch('/api/president-profile/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const payload = await response.json();
            if (!response.ok || !payload.success) {
                throw new Error(payload.error || 'Unable to load president profile');
            }
            data = payload.profile || null;
            if (data) {
                localStorage.setItem(this.presidentStorageKey, JSON.stringify(data));
            }
        } catch (error) {
            console.warn('Falling back to localStorage for president profile:', error);
            data = this.readStorageData(this.presidentStorageKey);
        }

        const role = this.hasMeaningfulContent(data?.role) ? data.role : this.defaultPresident.role;
        const name = this.hasMeaningfulContent(data?.name) ? data.name : this.defaultPresident.name;
        const caption = this.hasMeaningfulContent(data?.caption) ? data.caption : this.defaultPresident.caption;
        const photo = this.hasMeaningfulContent(data?.photo) ? data.photo : (this.hasMeaningfulContent(data?.image) ? data.image : null);

        if (roleEl) {
            roleEl.textContent = role;
        }
        if (nameEl) {
            nameEl.textContent = name;
        }
        if (captionEl) {
            captionEl.textContent = caption;
        }
        if (imgEl) {
            const defaultSrc = imgEl.getAttribute('data-default-src') || imgEl.src;
            imgEl.onerror = () => {
                imgEl.onerror = null;
                imgEl.src = defaultSrc;
            };
            imgEl.src = photo || defaultSrc;
        }
    }

    /**
     * Apply NORSU History text from localStorage to the About page section
     */
    applyHistorySection() {
        const section = document.getElementById('norsu-history');
        if (!section) return;

        const titleEl = section.querySelector('.history-title');
        const bodyEl = section.querySelector('#norsu-history-content');
        const data = this.readStorageData(this.historyStorageKey);

        const title = this.hasMeaningfulContent(data?.title) && data.title !== 'NORSU HISTORY'
            ? data.title
            : this.defaultHistory.title;
        const body = this.hasMeaningfulContent(data?.body)
            ? data.body
            : this.defaultHistory.body;

        if (titleEl) {
            titleEl.textContent = title;
        }
        if (bodyEl) {
            bodyEl.innerHTML = this.toDisplayHtml(body, this.defaultHistory.body);
        }
    }

    getLatestInfoRecord(infoData) {
        if (!Array.isArray(infoData) || infoData.length === 0) {
            return null;
        }

        return infoData
            .filter(Boolean)
            .slice()
            .sort((a, b) => this.getRecordTimestamp(b) - this.getRecordTimestamp(a))[0] || null;
    }

    getRecordTimestamp(record) {
        if (!record) return 0;

        const candidates = [record.updatedAt, record.createdDate, record.created_at, record.id];
        for (const value of candidates) {
            if (!value) continue;

            const asDate = Date.parse(value);
            if (!Number.isNaN(asDate)) {
                return asDate;
            }

            const asNumber = Number(value);
            if (!Number.isNaN(asNumber)) {
                return asNumber;
            }
        }

        return 0;
    }

    readStorageData(key) {
        try {
            const raw = localStorage.getItem(key);
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            console.warn(`Invalid localStorage data for ${key}:`, e);
            return null;
        }
    }

    hasMeaningfulContent(value) {
        if (typeof value !== 'string') {
            return value !== null && value !== undefined;
        }

        return value.replace(/<[^>]*>/g, '').trim().length > 0;
    }

    toDisplayHtml(value, fallback = '') {
        const source = this.hasMeaningfulContent(value) ? String(value) : String(fallback || '');
        const decoded = this.decodeHtmlEntities(source);

        if (!decoded) return '';
        if (/<[a-z][\s\S]*>/i.test(decoded)) {
            return decoded;
        }

        return this.escapeHtml(decoded).replace(/\r?\n/g, '<br>');
    }

    decodeHtmlEntities(text) {
        if (!text || typeof document === 'undefined') {
            return text || '';
        }

        let decoded = String(text);
        for (let i = 0; i < 2; i += 1) {
            const textarea = document.createElement('textarea');
            textarea.innerHTML = decoded;
            const nextValue = textarea.value;
            if (nextValue === decoded) {
                break;
            }
            decoded = nextValue;
        }

        return decoded;
    }

    /**
     * Utility function to escape HTML
     */
    escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Utility function to create delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get information count from localStorage
     */
    getInfoCount() {
        try {
            const infoData = this.getStoredNORSUInformation();
            return infoData.length;
        } catch (error) {
            console.error('Error getting info count:', error);
            return 0;
        }
    }

    /**
     * Get latest information without displaying
     */
    getLatestInfo() {
        try {
            const infoData = this.getStoredNORSUInformation();
            return this.getLatestInfoRecord(Array.isArray(infoData) ? infoData : [infoData]);
        } catch (error) {
            console.error('Error getting latest info:', error);
            return null;
        }
    }

    /**
     * Export data for backup
     */
    exportData() {
        try {
            const infoData = this.getStoredNORSUInformation();
            const dataStr = JSON.stringify(infoData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);

            const link = document.createElement('a');
            link.href = url;
            link.download = `norsu_info_backup_${new Date().toISOString().split('T')[0]}.json`;
            link.click();

            URL.revokeObjectURL(url);
            console.log('Data exported successfully');
        } catch (error) {
            console.error('Error exporting data:', error);
        }
    }

    /**
     * Cleanup method
     */
    destroy() {
        this.stopAutoRefresh();
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        console.log('About NORSU page destroyed');
    }
}

// Global functions for backward compatibility
window.loadNORSUInformation = function() {
    if (window.norsuAboutPage) {
        window.norsuAboutPage.loadNORSUInformation();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.norsuAboutPage = new NORSUAboutPage();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.norsuAboutPage) {
        window.norsuAboutPage.destroy();
    }
});
