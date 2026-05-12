import glob
import os

print("Starting mobile menu synchronization...")

# 1. Update all college style.css files to ensure the navbar toggle remains visible and on top
css_files = [
    'dashboard/static/dashboard/css/casstyle.css',
    'dashboard/static/dashboard/css/citstyle.css',
    'dashboard/static/dashboard/css/cbastyle.css',
    'dashboard/static/dashboard/css/ccjestyle.css',
    'dashboard/static/dashboard/css/cafstyle.css',
    'dashboard/static/dashboard/css/ctedstyle.css'
]

patch = """
/* ================================================================
   MOBILE MENU SYNC PATCH (v2)
   Ensures the centralized navbar.html logic is never overridden 
   by college-specific grid layers.
   ================================================================ */
.mobile-nav-menu, .mobile-menu-overlay { 
    z-index: 99999 !important; 
    display: block !important;
}
.mobile-menu-toggle { 
    z-index: 100000 !important; 
    display: flex !important;
}

@media (min-width: 1025px) {
    .mobile-menu-toggle { display: none !important; }
    .mobile-nav-menu { display: none !important; }
}
"""

for fpath in css_files:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "MOBILE MENU SYNC PATCH (v2)" not in content:
            with open(fpath, 'a', encoding='utf-8') as f:
                f.write("\n" + patch)
            print(f"Patched {fpath}")

# 2. Verify all dashboards have navbar.html included
dashboards = ['dashbordcas.html', 'dashbordcit.html', 'dashbordccje.html', 'dashbordcba.html', 'dashbordcaf.html', 'dashbordcted.html']
for d in dashboards:
    fpath = os.path.join('dashboard/templates/dashboard/', d)
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()
        if '{% include \'dashboard/navbar.html\' %}' not in html:
            print(f"CRITICAL: {d} is missing the navbar inclusion!")

print("Synchronization complete.")
