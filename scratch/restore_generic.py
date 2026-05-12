"""Restore dashbordgeneric.html JS section to original pre-edit state."""
import os

SRC = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'templates', 'dashboard', 'dashbordgeneric.html')

# Read the current file
with open(SRC, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where the JS block starts ({% block extra_js %})
js_start = None
for i, line in enumerate(lines):
    if '{% block extra_js %}' in line:
        js_start = i
        break

if js_start is None:
    print("ERROR: Could not find {% block extra_js %}")
    exit(1)

print(f"Found JS block at line {js_start + 1}")

# Keep HTML portion (lines 0 to js_start inclusive)
html_part = lines[:js_start + 1]

# The original JS block (matching the pattern from before edits)
js_block = """
<script>
  /* ════════════════════════════════════════════════
     INIT
  ════════════════════════════════════════════════ */
  const CURRENT_COLLEGE_ABBR = "{{ college.abbreviation|lower|default:'cas' }}";

  document.addEventListener('DOMContentLoaded', async function () {
    await Promise.all([
      loadCollegeInfo(),
      loadCASPrograms(),
      loadCASFaculty(),
      loadCasLatestPosts(),
      loadCasAlumni(),
      loadCasAwards(),
      loadCasFacilities()
    ]);
    initScrollReveal();
    initSubnav();

    window.addEventListener('storage', function (e) {
      if (e.key && (e.key.includes('Updated') || e.key.includes('Posts'))) {
        loadCASPrograms(); loadCASFaculty(); loadCasLatestPosts();
        loadCasAlumni(); loadCasAwards(); loadCasFacilities();
      }
    });
  });

  /* ─── SUB-NAV ACTIVE STATE ─── */
  function initSubnav() {
    const sections = ['about-section', 'programs-section', 'news-section',
      'alumni-section', 'awards-section', 'facilities-section', 'administration-section'];
    const links = document.querySelectorAll('.snav-link');

    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const id = e.target.id;
          links.forEach(l => l.classList.remove('active'));
          const active = [...links].find(l => l.getAttribute('onclick')?.includes(id));
          if (active) active.classList.add('active');
        }
      });
    }, { threshold: 0.3 });

    sections.forEach(id => {
      const el = document.getElementById(id);
      if (el) obs.observe(el);
    });
  }

  function scrollToSec(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  }

  /* ─── COLLEGE INFO ─── */
  async function loadCollegeInfo() {
    try {
      const res = await fetch(`/api/colleges/?t=${Date.now()}`, { cache: 'no-store' });
      const data = await res.json();
      if (data.success && data.colleges) {
        const info = data.colleges.find(c => (c.abbreviation || '').toLowerCase() === CURRENT_COLLEGE_ABBR);
        if (info) {
          // Update Hero
          if (info.hero_description) {
            const heroDesc = document.querySelector('.hero-desc');
            if (heroDesc) heroDesc.innerHTML = info.hero_description;
          }
          // Update About
          if (info.about) {
            const aboutBody = document.querySelector('.about-body');
            if (aboutBody) aboutBody.innerHTML = info.about;
          }
          // Update Goals
          if (info.goals && Array.isArray(info.goals) && info.goals.length > 0) {
            const goalsList = document.getElementById('cas-goals-list');
            if (goalsList) {
              goalsList.innerHTML = info.goals.map(g => `
                <div class="cas-goal">
                  <span class="goal-letter gl-${(g.letter || 'C').toLowerCase()}">${g.letter || ''}</span>
                  <div class="goal-text">
                    <div class="goal-content">${g.english || ''}</div>
                    ${g.translated ? `<div class="goal-translation">${g.translated}</div>` : ''}
                  </div>
                </div>
              `).join('');
            }
          }
        }
      }
    } catch (e) {
      console.error('College Info error:', e);
    }
  }

  /* ─── GOALS TOGGLE ─── */
  function toggleGoals() {
    const list = document.getElementById('cas-goals-list');
    const btn = document.getElementById('goals-toggle-btn');
    if (!list) return;
    const hidden = list.style.display === 'none';
    list.style.display = hidden ? 'flex' : 'none';
    btn.innerHTML = hidden
      ? '<i class="fas fa-times"></i> Hide Goals'
      : `<i class="fas fa-bullseye"></i> View ${CURRENT_COLLEGE_ABBR.toUpperCase()} Goals`;
  }

  /* ─── PROGRAMS ─── */
  async function loadCASPrograms() {
    const container = document.getElementById('cas-programs');
    if (!container) return;
    try {
      const res = await fetch(`/api/programs/?college=${CURRENT_COLLEGE_ABBR}&t=${Date.now()}`);
      const data = await res.json();
      if (data.success && data.programs) {
        const progs = data.programs.filter(p => (p.college || '').toLowerCase() === CURRENT_COLLEGE_ABBR);
        const el = document.getElementById('prog-count-display');
        if (el) el.textContent = progs.length || '\\u2014';
        ['hero-program-count', 'stat-programs'].forEach(id => {
          const e = document.getElementById(id);
          if (e) e.textContent = progs.length || '\\u2014';
        });
        if (!progs.length) {
          container.innerHTML = `<div style="color:rgba(255,255,255,.5);padding:60px 0;font-size:18px;grid-column:1/-1">No programs listed yet.</div>`;
          return;
        }
        container.innerHTML = progs.map(p => `
        <div class="prog-card">
          <div class="prog-img">
            <img src="${p.image || '/static/dashboard/images/logo1.png'}"
                 onerror="this.src='/static/dashboard/images/logo1.png'" loading="lazy" alt="${p.title}">
            <span class="prog-duration-badge">${(p.duration || 'Duration TBA').toUpperCase()}</span>
          </div>
          <div class="prog-body">
            <div class="prog-name">${p.title}</div>
            <div class="prog-desc">${p.description || 'Program details will be published soon.'}</div>
            <a href="javascript:void(0)" class="prog-link" onclick="navigateToProgram('${p.title}')">
              Learn More <i class="fas fa-arrow-right"></i>
            </a>
          </div>
        </div>
      `).join('');
      }
    } catch (e) { console.error('Programs error:', e); }
  }

  function navigateToProgram(title) {
    window.location.href = '/programs/';
  }

  /* ─── FACULTY / ORG CHART ─── */
  async function loadCASFaculty() {
    try {
      const res = await fetch(`/api/faculty/?college=${CURRENT_COLLEGE_ABBR}`);
      const data = await res.json();
      if (data.success && data.faculty) {
        updateOrganizationalChart(data.faculty);
        ['hero-faculty-count', 'stat-faculty'].forEach(id => {
          const e = document.getElementById(id);
          if (e) e.textContent = data.faculty.length || '\\u2014';
        });
      }
    } catch (e) { console.error('Faculty error:', e); }
  }

  function updateOrganizationalChart(faculty) {
    const container = document.getElementById('cas-organizational-chart');
    if (!container) return;
    if (!faculty || !faculty.length) {
      container.innerHTML = '<p style="text-align:center;color:rgba(255,255,255,.5);padding:40px">No faculty data available.</p>';
      return;
    }
    const rank = pos => {
      pos = (pos || '').toLowerCase();
      if (pos.includes('dean') && !pos.includes('assistant')) return 1;
      if (pos.includes('assistant dean')) return 2;
      return 3;
    };
    const sorted = [...faculty].sort((a, b) => rank(a.position) - rank(b.position));
    const dean = sorted.find(f => rank(f.position) === 1);
    const assts = sorted.filter(f => rank(f.position) === 2);
    const others = sorted.filter(f => rank(f.position) === 3);
    const fallback = '/static/dashboard/images/silhouette.png';
    const cardHTML = (f, cls) => `
    <div class="org-box ${cls}">
      <img src="${f.image || fallback}" class="org-avatar" loading="lazy"
           onerror="this.src='${fallback}'" alt="${f.name}">
      <div class="org-info">
        <h3>${f.name}</h3>
        <p>${f.position}</p>
      </div>
    </div>`;

    let html = '';
    if (dean) {
      html += `<div class="org-level"><div class="org-row">${cardHTML(dean, 'dean-box')}</div></div>
             <div class="org-connector"></div>`;
    }
    if (assts.length) {
      html += `<div class="org-level"><div class="org-row">${assts.map(a => cardHTML(a, 'assistant-box')).join('')}</div></div>
             <div class="org-connector"></div>`;
    }
    if (others.length) {
      html += `<div class="org-level"><div class="org-grid">${others.map(f => cardHTML(f, 'faculty-box')).join('')}</div></div>`;
    }
    container.innerHTML = html;
  }

  /* ─── NEWS / LATEST POSTS ─── */
  async function loadCasLatestPosts() {
    const container = document.getElementById('cas-latest');
    if (!container) return;
    try {
      const res = await fetch(`/api/posts/get/?college=${CURRENT_COLLEGE_ABBR}`);
      const data = await res.json();
      if (!data.success || !data.posts?.length) {
        container.innerHTML = '<p style="color:var(--gray-500);padding:40px 0;font-size:18px">No news available.</p>';
        return;
      }
      const posts = data.posts.filter(p => !['alumni', 'award'].includes((p.post_type || p.type || '').toLowerCase()));
      if (!posts.length) {
        container.innerHTML = '<p style="color:var(--gray-500);padding:40px 0">No news available.</p>';
        return;
      }
      const fmt = d => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
      const isNew = d => (new Date() - new Date(d)) / 3600000 <= 72;
      const fallback = '/static/dashboard/images/news.jpg';

      let html = '';
      posts.slice(0, 5).forEach(p => {
        html += `
        <a href="/news/${p.id}/" class="news-card-sm news-card-link">
          <div class="news-sm-img">
            <img src="${p.image || fallback}" onerror="this.src='${fallback}'" loading="lazy" alt="${p.title}">
          </div>
          <div class="news-sm-body">
            <div style="display:flex;gap:6px;flex-wrap:wrap">
              ${isNew(p.date_posted || p.date) ? '<span class="news-tag news-is-new">New</span>' : ''}
            <span class="news-tag">${(p.post_type || p.type || 'Announcement').toUpperCase()}</span>
          </div>
          <div class="news-date">${fmt(p.date_posted || p.date)}</div>
          <h4 class="news-title-sm">${p.title}</h4>
          <p class="news-excerpt-sm">${(p.content || '').substring(0, 100)}\\u2026</p>
          <span class="news-read">Read More <i class="fas fa-arrow-right"></i></span>
          </div>
        </a>`;
      });

      container.innerHTML = html;
    } catch (e) { console.error('Posts error:', e); }
  }

  /* ─── ALUMNI ─── */
  async function loadCasAlumni() {
    const featContainer = document.getElementById('alumni-featured');
    const listContainer = document.getElementById('alumni-scrollable');
    if (!featContainer || !listContainer) return;

    try {
      const res = await fetch(`/api/posts/get/?college=${CURRENT_COLLEGE_ABBR}&type=alumni`);
      const data = await res.json();
      if (!data.success || !data.posts?.length) {
        featContainer.innerHTML = '<p style="color:rgba(255,255,255,.5)">No alumni stories listed.</p>';
        listContainer.innerHTML = '';
        return;
      }

      const stories = data.posts.filter(post => (post.college || '').toLowerCase() === CURRENT_COLLEGE_ABBR);
      if (!stories.length) {
        featContainer.innerHTML = '<p style="color:rgba(255,255,255,.5)">No alumni stories listed.</p>';
        listContainer.innerHTML = '';
        return;
      }

      const fallback = '/static/dashboard/images/silhouette.png';
      const lead = stories[0];
      const rest = stories.slice(1);

      featContainer.innerHTML = `
        <div class="master-card">
          <div class="alumni-photo">
            <img src="${lead.image || fallback}" onerror="this.src='${fallback}'" loading="lazy" alt="${lead.title || 'Alumni'}">
          </div>
          <div class="alumni-name">${lead.title || 'Alumni Story'}</div>
          <div class="alumni-meta">${CURRENT_COLLEGE_ABBR.toUpperCase()}</div>
          <div class="alumni-quote">${lead.content || ''}</div>
        </div>
      `;

      listContainer.innerHTML = `
        <div class="small-grid">
          ${rest.map(story => `
            <div class="mini-card">
              <div class="alumni-photo">
                <img src="${story.image || fallback}" onerror="this.src='${fallback}'" loading="lazy" alt="${story.title || 'Alumni'}">
              </div>
              <div class="alumni-name">${story.title || 'Alumni Story'}</div>
              <div class="alumni-meta">${CURRENT_COLLEGE_ABBR.toUpperCase()}</div>
              <div class="alumni-quote">${story.content || ''}</div>
            </div>
          `).join('')}
        </div>
      `;

    } catch (e) { console.error('Alumni error:', e); }
  }
  /* ─── AWARDS ─── */
  async function loadCasAwards() {
    const container = document.getElementById('cas-awards');
    if (!container) return;
    try {
      const res = await fetch(`/api/posts/get/?college=${CURRENT_COLLEGE_ABBR}&type=award`);
      const data = await res.json();
      if (!data.success || !data.posts?.length) {
        container.innerHTML = '<p style="color:var(--gray-500);padding:40px 0">No awards listed.</p>';
        return;
      }
      const unique = data.posts.filter((a, i, arr) =>
        arr.findIndex(b => b.id === a.id) === i
      );
      const fallback = '/static/dashboard/images/logo1.png';
      container.innerHTML = unique.map(post => `
      <a href="/news/${post.id}/" class="award-card award-card-link">
        <div class="award-img">
          <div class="award-trophy"><i class="fas fa-trophy"></i></div>
          <img src="${post.image || fallback}"
               onerror="this.src='${fallback}'" loading="lazy" alt="${post.title}">
        </div>
        <div class="award-body">
          <h3 class="award-title">${post.title}</h3>
          <p class="award-desc">${(post.content || 'No description available.').substring(0, 160)}${post.content?.length > 160 ? '\\u2026' : ''}</p>
          <span class="award-link">
            Read More <i class="fas fa-arrow-right"></i>
          </span>
        </div>
      </a>
    `).join('');
    } catch (e) { console.error('Awards error:', e); }
  }

  /* ─── FACILITIES ─── */
  async function loadCasFacilities() {
    const container = document.getElementById('cas-facilities');
    if (!container) return;
    try {
      const res = await fetch(`/api/facilities/?college=${CURRENT_COLLEGE_ABBR}`);
      const data = await res.json();
      if (!data.success || !data.facilities?.length) {
        container.innerHTML = '<p style="color:var(--gray-500);padding:40px 0">No facilities listed.</p>';
        return;
      }
      const fallback = '/static/dashboard/images/logo1.png';
      container.innerHTML = data.facilities.map(f => `
      <div class="fac-card">
        <div class="fac-label">${f.name}</div>
        <img src="${f.image || fallback}"
             onerror="this.src='${fallback}'" loading="lazy" alt="${f.name}">
      </div>
    `).join('');
    } catch (e) { console.error('Facilities error:', e); }
  }

  /* ─── SCROLL REVEAL ─── */
  function initScrollReveal() {
    const SEL = [
      '.astat-card', '.cas-goal', '.prog-card',
      '.news-card-feat', '.news-card-sm',
      '.alumni-card', '.award-card', '.fac-card',
      '.org-box', '.sec-label', '.sec-title', '.about-label', '.about-title'
    ].join(',');

    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

    document.querySelectorAll(SEL).forEach((el, i) => {
      el.classList.add('reveal');
      const siblings = [...el.parentElement.children].filter(c => c.classList.contains('reveal'));
      el.style.transitionDelay = `${Math.min(siblings.indexOf(el) * 0.08, 0.4)}s`;
      obs.observe(el);
    });
  }

  /* ─── SCROLL EFFECTS ─── */
  const floatingArrow = document.getElementById('floatingArrow');
  const scrollProgress = document.getElementById('scrollProgress');

  window.addEventListener('scroll', () => {
    // Arrow Visibility
    floatingArrow.classList.toggle('visible', window.scrollY > 600);

    // Progress Bar
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    if (scrollProgress) {
      scrollProgress.style.width = scrolled + "%";
    }
  });

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
</script>
{% endblock %}
"""

# Write the restored file
with open(SRC, 'w', encoding='utf-8') as f:
    for line in html_part:
        f.write(line)
    f.write(js_block)

print(f"Restored {SRC}")
print(f"HTML lines kept: {len(html_part)}")
# Verify
with open(SRC, 'r', encoding='utf-8') as f:
    total = len(f.readlines())
print(f"Total lines in restored file: {total}")
