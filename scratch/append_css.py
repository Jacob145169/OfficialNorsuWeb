
import os

css_path = r'c:\Users\USER\OneDrive\Desktop\NORSUWESITE\dashboard\static\dashboard\css\super-admin-dashboard.css'

new_styles = """
/* ============================================================
   Settings Tab Styles
   ============================================================ */
.settings-container {
    padding: 10px;
}

.settings-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
    margin-bottom: 32px;
}

.settings-section {
    background: var(--white);
    padding: 30px;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    transition: var(--transition);
}

.settings-section:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-sm);
}

.settings-section-title {
    font-family: var(--font-serif);
    font-size: 18px;
    font-weight: 700;
    color: var(--crimson);
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--crimson-tint);
    display: flex;
    align-items: center;
    gap: 10px;
}

.settings-group {
    margin-bottom: 20px;
}

.settings-group:last-child {
    margin-bottom: 0;
}

.settings-label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.settings-input {
    width: 100%;
    padding: 11px 14px;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    font-family: var(--font-sans);
    font-size: 14px;
    transition: var(--transition);
}

.settings-input:focus {
    outline: none;
    border-color: var(--crimson);
    box-shadow: 0 0 0 3px var(--crimson-muted);
}

.settings-toggle-group {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: var(--off-white);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: var(--transition);
}

.settings-toggle-group:hover {
    background: var(--crimson-tint);
}

.settings-toggle-group input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--crimson);
}

.settings-toggle-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    cursor: pointer;
}

.branding-preview {
    display: flex;
    gap: 24px;
    align-items: center;
}

.color-picker-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.color-input-wrapper {
    position: relative;
    width: 64px;
    height: 64px;
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 2px solid var(--border-strong);
    transition: var(--transition);
}

.color-input-wrapper:hover {
    border-color: var(--crimson);
    transform: scale(1.05);
}

.color-input-wrapper input[type="color"] {
    position: absolute;
    top: -10px;
    left: -10px;
    width: 150%;
    height: 150%;
    cursor: pointer;
    border: none;
}

.settings-footer {
    padding-top: 24px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: flex-end;
}

@media (max-width: 992px) {
    .settings-grid {
        grid-template-columns: 1fr;
    }
}
"""

with open(css_path, 'a') as f:
    f.write(new_styles)

print("Successfully appended settings styles.")
