// PHISHVERSE — shared utilities

(function () {
  'use strict';

  // ────────── Custom cursor ──────────
  function initCursor() {
    if (window.matchMedia('(hover: none)').matches) return;
    const dot = document.createElement('div');
    const ring = document.createElement('div');
    dot.className = 'cursor-dot';
    ring.className = 'cursor-ring';
    document.body.append(dot, ring);

    let mx = -100, my = -100, rx = -100, ry = -100;
    window.addEventListener('mousemove', (e) => { mx = e.clientX; my = e.clientY; });

    function tick() {
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      dot.style.transform = `translate(${mx}px, ${my}px) translate(-50%, -50%)`;
      ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%, -50%)`;
      requestAnimationFrame(tick);
    }
    tick();

    document.addEventListener('mouseover', (e) => {
      if (e.target.closest('a, button, .interactive, [role="button"], .sidebar-link')) {
        ring.classList.add('hover');
      }
    });
    document.addEventListener('mouseout', (e) => {
      if (e.target.closest && e.target.closest('a, button, .interactive, [role="button"], .sidebar-link')) {
        ring.classList.remove('hover');
      }
    });
  }

  // ────────── Floating particles ──────────
  function initParticles(container, count = 50) {
    if (!container) return;
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;';
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    let W = 0, H = 0, particles = [];

    function resize() {
      const dpr = window.devicePixelRatio || 1;
      W = canvas.clientWidth;
      H = canvas.clientHeight;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);

    const colors = ['rgba(24,232,255,', 'rgba(245,197,24,', 'rgba(168,85,247,', 'rgba(0,245,196,'];
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.6 + 0.4,
        vx: (Math.random() - 0.5) * 0.18,
        vy: (Math.random() - 0.5) * 0.18,
        c: colors[(Math.random() * colors.length) | 0],
        a: Math.random() * 0.5 + 0.2,
        ph: Math.random() * Math.PI * 2,
      });
    }

    let mouseX = -1000, mouseY = -1000;
    container.addEventListener('mousemove', (e) => {
      const r = container.getBoundingClientRect();
      mouseX = e.clientX - r.left;
      mouseY = e.clientY - r.top;
    });
    container.addEventListener('mouseleave', () => { mouseX = -1000; mouseY = -1000; });

    function frame(t) {
      ctx.clearRect(0, 0, W, H);
      for (const p of particles) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
        // gentle repel from cursor
        const dx = p.x - mouseX, dy = p.y - mouseY;
        const d2 = dx*dx + dy*dy;
        if (d2 < 14400) {
          const f = (14400 - d2) / 14400 * 0.6;
          p.x += (dx / Math.sqrt(d2 || 1)) * f;
          p.y += (dy / Math.sqrt(d2 || 1)) * f;
        }
        const flicker = (Math.sin(t * 0.001 + p.ph) + 1) * 0.5;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.c + (p.a * (0.4 + 0.6 * flicker)) + ')';
        ctx.fill();
      }
      // soft connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i], b = particles[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx*dx + dy*dy;
          if (d2 < 11000) {
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = `rgba(24,232,255,${(1 - d2/11000) * 0.08})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  // ────────── Scroll reveal ──────────
  function initReveal() {
    const els = document.querySelectorAll('.reveal');
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      }
    }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
    els.forEach(el => io.observe(el));
  }

  // ────────── Animated counter ──────────
  function animateCounter(el) {
    const target = parseFloat(el.dataset.target);
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    const dur = parseInt(el.dataset.dur || '1600', 10);
    const start = performance.now();
    function step(now) {
      const t = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const val = target * eased;
      el.textContent = prefix + (decimals > 0 ? val.toFixed(decimals) : Math.round(val).toLocaleString()) + suffix;
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function initCounters() {
    const els = document.querySelectorAll('[data-counter]');
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          animateCounter(e.target);
          io.unobserve(e.target);
        }
      }
    }, { threshold: 0.5 });
    els.forEach(el => io.observe(el));
  }

  // ────────── Bar fill animation ──────────
  function initBars() {
    const bars = document.querySelectorAll('.bar-fill[data-w]');
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          requestAnimationFrame(() => { e.target.style.width = e.target.dataset.w + '%'; });
          io.unobserve(e.target);
        }
      }
    }, { threshold: 0.4 });
    bars.forEach(b => io.observe(b));
  }

  // ────────── Topnav scroll ──────────
  function initNav() {
    const nav = document.querySelector('.topnav');
    if (!nav) return;
    function check() {
      if (window.scrollY > 24) nav.classList.add('scrolled');
      else nav.classList.remove('scrolled');
    }
    check();
    window.addEventListener('scroll', check, { passive: true });
  }

  // ────────── Parallax for hero ──────────
  function initParallax() {
    const layers = document.querySelectorAll('[data-parallax]');
    if (!layers.length) return;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      layers.forEach(l => {
        const f = parseFloat(l.dataset.parallax) || 0.2;
        l.style.transform = `translateY(${y * f}px)`;
      });
    }, { passive: true });
  }

  // ────────── Attack card mouse glow ──────────
  function initCardGlow() {
    document.querySelectorAll('.attack-card, .glow-card').forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${e.clientX - r.left}px`);
        card.style.setProperty('--my', `${e.clientY - r.top}px`);
      });
    });
  }

  // ────────── Modal ──────────
  window.PV = window.PV || {};
  window.PV.openModal = function (id) {
    const m = document.getElementById(id);
    if (m) m.classList.add('open');
  };
  window.PV.closeModal = function (id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove('open');
  };
  window.PV.toast = function (msg) {
    let t = document.querySelector('.toast');
    if (!t) {
      t = document.createElement('div');
      t.className = 'toast';
      t.innerHTML = `<span class="dot"></span><span class="msg"></span>`;
      document.body.appendChild(t);
    }
    t.querySelector('.msg').textContent = msg;
    requestAnimationFrame(() => t.classList.add('show'));
    clearTimeout(t._h);
    t._h = setTimeout(() => t.classList.remove('show'), 3200);
  };

  // ────────── Mock POST ──────────
  window.PV.mockPost = async function (endpoint, body = {}) {
    console.log('[PHISHVERSE mock POST]', endpoint, body);
    await new Promise(r => setTimeout(r, 600));
    if (endpoint === '/api/launch-game') {
      return { ok: true, sessionId: 'PV-' + Math.random().toString(36).slice(2, 10).toUpperCase(), launchUrl: '#demo' };
    }
    if (endpoint === '/api/cycle/report') {
      return { ok: true, cycleId: 'C-2026Q2', score: 78 };
    }
    if (endpoint === '/api/cycle/complete') {
      return { ok: true, certificate: 'CERT-PV-' + Date.now() };
    }
    return { ok: true };
  };

  // ────────── Sidebar toggle (mobile) ──────────
  window.PV.toggleSidebar = function () {
    document.querySelector('.sidebar')?.classList.toggle('open');
  };

  // ────────── Screen-show hooks (registered by page-specific code) ──────────
  window.PV._screenHandlers = {};
  window.PV.onScreenShow = function (screenKey, fn) {
    PV._screenHandlers[screenKey] = fn;
  };

  // ────────── Portal section navigation ──────────
  // Accepts either the full element id ("screen-registration") or the short key ("registration").
  window.PV.showScreen = function (idOrKey) {
    const id = idOrKey.startsWith('screen-') ? idOrKey : 'screen-' + idOrKey;
    const shortKey = id.replace(/^screen-/, '');

    document.querySelectorAll('.screen').forEach(s => s.classList.remove('show'));
    const target = document.getElementById(id);
    if (target) target.classList.add('show');

    // sync sidebar active state
    document.querySelectorAll('.sidebar-link[data-screen]').forEach(l => {
      l.classList.toggle('active', l.dataset.screen === shortKey);
    });

    // update breadcrumb if present
    const cur = document.querySelector('.crumbs .cur');
    if (cur) {
      const link = document.querySelector(`.sidebar-link[data-screen="${shortKey}"]`);
      if (link) cur.textContent = link.textContent.trim();
    }

    // animate bars in the newly visible screen
    target?.querySelectorAll('.bar-fill[data-w]').forEach(b => {
      requestAnimationFrame(() => { b.style.width = b.dataset.w + '%'; });
    });

    // animate ring fills
    target?.querySelectorAll('.ring-fill[data-pct]').forEach(r => {
      const pct = parseFloat(r.dataset.pct) / 100;
      const circ = 251.2;
      requestAnimationFrame(() => { r.style.strokeDashoffset = circ - circ * pct; });
    });

    // fire registered data-load handler for this screen
    const handler = PV._screenHandlers[shortKey];
    if (handler) handler();
  };

  // ────────── Progress tracker ──────────
  const _STEPS = ['registration','campaigns','exam','lectures','report','final','certificate'];
  let _progress = JSON.parse(sessionStorage.getItem('pv_progress') || '{}');

  window.PV.completeStep = function (step) {
    _progress[step] = true;
    sessionStorage.setItem('pv_progress', JSON.stringify(_progress));
    _syncProgress();
  };

  window.PV.getProgress = function () { return Object.assign({}, _progress); };

  function _syncProgress() {
    _STEPS.forEach((step, i) => {
      const dot = document.querySelector(`.cycle-progress .step:nth-child(${i + 1}) .dot`);
      const link = document.querySelector(`.sidebar-link[data-screen="screen-${step}"]`);
      const badge = link?.querySelector('.badge');
      if (_progress[step]) {
        dot?.closest('.step')?.classList.add('done');
        dot?.closest('.step')?.classList.remove('active');
        if (badge) { badge.textContent = 'DONE'; badge.className = 'badge done'; }
      }
    });

    // mark current step active
    const first_incomplete = _STEPS.find(s => !_progress[s]);
    if (first_incomplete) {
      const idx = _STEPS.indexOf(first_incomplete);
      const dot = document.querySelector(`.cycle-progress .step:nth-child(${idx + 1}) .dot`);
      dot?.closest('.step')?.classList.add('active');
    }
  }

  // ────────── Bias bar renderer ──────────
  window.PV.renderBiasBar = function (container, biasData) {
    /* biasData: { urgency: 0-4, authority: 0-4, reward: 0-4, fear: 0-4 } */
    const labels = { urgency: 'Urgency', authority: 'Authority', reward: 'Reward', fear: 'Fear' };
    const colorClass = (v) => v >= 3 ? 'crit' : v >= 2 ? 'high' : v >= 1 ? 'med' : 'low';
    const pct = (v) => Math.round((v / 4) * 100);
    const barClass = (v) => v >= 3 ? 'red' : v >= 2 ? 'gold' : v >= 1 ? '' : 'green';

    let html = '<div class="bias-bars">';
    for (const [key, label] of Object.entries(labels)) {
      const v = biasData[key] || 0;
      html += `
        <div class="bias-row">
          <div class="bias-row-head">
            <span class="label">${label}</span>
            <span class="val ${colorClass(v)}">${v} / 4</span>
          </div>
          <div class="bar"><div class="bar-fill ${barClass(v)}" data-w="${pct(v)}"></div></div>
        </div>`;
    }
    html += '</div>';
    container.innerHTML = html;
    container.querySelectorAll('.bar-fill[data-w]').forEach(b => {
      requestAnimationFrame(() => { b.style.width = b.dataset.w + '%'; });
    });
  };

  // ────────── Score ring renderer ──────────
  window.PV.renderRing = function (container, pct, label) {
    const circ = 251.2;
    const offset = circ - circ * (pct / 100);
    const colorClass = pct >= 75 ? 'green' : pct >= 50 ? '' : 'red';
    container.innerHTML = `
      <div class="report-score-ring">
        <svg viewBox="0 0 90 90">
          <circle class="ring-track" cx="45" cy="45" r="40"/>
          <circle class="ring-fill ${colorClass}" cx="45" cy="45" r="40"
            style="stroke-dashoffset:${offset}" data-pct="${pct}"/>
        </svg>
        <span class="ring-val">${pct}<small style="font-size:.5em;color:var(--muted)">%</small></span>
        <span class="ring-label">${label}</span>
      </div>`;
  };

  // ────────── Static reference data (no mock employees) ──────────
  window.PV.MOCK = {
    departments: [
      { name: 'Reception',  risk: 91, level: 'risk-critical' },
      { name: 'Finance',    risk: 88, level: 'risk-critical' },
      { name: 'Marketing',  risk: 74, level: 'risk-high'     },
      { name: 'HR',         risk: 62, level: 'risk-high'     },
      { name: 'Operations', risk: 54, level: 'risk-medium'   },
      { name: 'IT',         risk: 35, level: 'risk-low'      },
    ],
    biasProfile: { urgency: 3, authority: 2, reward: 1, fear: 2 },
  };

  const BACKEND = 'http://localhost:5000';

  // ────────── Real employee loader ──────────
  // Fetches from Flask /api/employees and renders into #empBody.
  window.PV.loadEmployees = async function () {
    const tbody = document.getElementById('empBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:32px;font-family:var(--font-mono);font-size:12px;letter-spacing:0.14em;">LOADING…</td></tr>`;
    try {
      const res  = await fetch(`${BACKEND}/api/employees`);
      const json = await res.json();
      const emps = json.employees || [];
      if (!emps.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:32px;font-family:var(--font-mono);font-size:12px;letter-spacing:0.14em;">NO RECORDS YET — run the game to generate results</td></tr>`;
        return;
      }
      tbody.innerHTML = '';
      emps.forEach(e => {
        const ini     = (e.employee_name || e.employee_id || '?').split(' ').map(p => p[0]).join('').slice(0,2).toUpperCase();
        const prog    = e.events_total ? Math.round((e.events_completed / e.events_total) * 100) : 0;
        const barColor = prog < 50 ? 'var(--red)' : prog < 75 ? 'var(--gold)' : prog === 100 ? 'var(--green)' : 'var(--cyan)';
        const riskTag  = e.risk === 'LOW' ? 'green' : e.risk === 'MEDIUM' ? 'gold' : e.risk === 'HIGH' || e.risk === 'CRITICAL' ? 'red' : 'muted';
        const stage    = e.passed ? 'PASSED' : 'IN PROGRESS';
        const stageTag = e.passed ? 'green' : 'cyan';
        const bias     = [
          e.urgency   >= 3 ? 'Urgency'   : null,
          e.authority >= 3 ? 'Authority' : null,
          e.reward    >= 3 ? 'Reward'    : null,
          e.fear      >= 3 ? 'Fear'      : null,
        ].filter(Boolean).join(' · ') || 'Balanced';
        const row = document.createElement('tr');
        row.innerHTML = `
          <td style="padding-left:28px;"><div class="uname"><div class="av" style="background:linear-gradient(135deg,var(--cyan),var(--purple));">${ini}</div><div class="name-block"><div class="nm">${e.employee_name || e.employee_id}</div><div class="em mono" style="font-size:11px;">${e.employee_id}</div></div></div></td>
          <td style="color:var(--muted);">${e.department || '—'}</td>
          <td><span class="mono" style="font-size:11px;color:#C7D0E8;">${bias}</span></td>
          <td><span class="mini-bar"><i style="width:${prog}%;background:${barColor};"></i></span>${prog}%</td>
          <td><strong>${e.score}</strong></td>
          <td><span class="tag ${stageTag}">${stage}</span></td>
          <td style="padding-right:28px;"><span class="tag ${riskTag}">${e.risk}</span></td>
        `;
        tbody.appendChild(row);
      });
    } catch {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:32px;font-family:var(--font-mono);font-size:12px;letter-spacing:0.14em;">BACKEND OFFLINE — start python backend/app.py</td></tr>`;
    }
  };

  // ────────── Overview employee loader (top movers strip) ──────────
  window.PV.loadOverviewEmployees = async function () {
    const tbody = document.getElementById('overviewEmpBody');
    if (!tbody) return;
    try {
      const res  = await fetch(`${BACKEND}/api/employees`);
      const json = await res.json();
      const emps = (json.employees || []).slice(0, 5);
      if (!emps.length) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:24px;font-family:var(--font-mono);font-size:12px;">NO RECORDS YET</td></tr>`;
        return;
      }
      tbody.innerHTML = '';
      emps.forEach(e => {
        const ini  = (e.employee_name || e.employee_id || '?').split(' ').map(p => p[0]).join('').slice(0,2).toUpperCase();
        const prog = e.events_total ? Math.round((e.events_completed / e.events_total) * 100) : 0;
        const barColor = prog < 50 ? 'var(--red)' : prog < 75 ? 'var(--gold)' : 'var(--cyan)';
        const stageTag = e.passed ? 'green' : 'cyan';
        const stage    = e.passed ? 'CERTIFIED' : 'IN PROGRESS';
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><div class="uname"><div class="av" style="background:linear-gradient(135deg,var(--cyan),var(--purple));">${ini}</div><div class="name-block"><div class="nm">${e.employee_name || e.employee_id}</div><div class="em mono" style="font-size:11px;">${e.employee_id}</div></div></div></td>
          <td>${e.department || '—'}</td>
          <td><span class="mini-bar"><i style="width:${prog}%;background:${barColor};"></i></span>${prog}%</td>
          <td>${e.score}</td>
          <td><span class="tag ${stageTag}">${stage}</span></td>
        `;
        tbody.appendChild(row);
      });
    } catch { /* backend offline — table stays empty */ }
  };

  window.PV.renderHeatmap = function (container) {
    const rows = window.PV.MOCK.departments;
    let html = '';
    rows.forEach(d => {
      const barClass = d.risk >= 75 ? 'red' : d.risk >= 50 ? 'gold' : 'green';
      html += `
        <div>
          <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:8px;">
            <span>${d.name}</span>
            <span class="mono" style="color:var(--${barClass === 'red' ? 'red' : barClass === 'gold' ? 'gold' : 'green'})">${d.risk}%</span>
          </div>
          <div class="bar"><div class="bar-fill ${barClass}" data-w="${d.risk}"></div></div>
        </div>`;
    });
    container.innerHTML = html;
    container.querySelectorAll('.bar-fill[data-w]').forEach(b => {
      requestAnimationFrame(() => { b.style.width = b.dataset.w + '%'; });
    });
  };

  // ────────── Admin page routing ──────────
  // Admin uses the same data-screen convention as the employee portal.
  window.PV.showAdminPage = window.PV.showScreen;

  // ────────── Glow card mouse tracking ──────────
  function initGlowCards() {
    document.querySelectorAll('.portal-card.glow-card').forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${e.clientX - r.left}px`);
        card.style.setProperty('--my', `${e.clientY - r.top}px`);
      });
    });
  }

  // ────────── Init ──────────
  document.addEventListener('DOMContentLoaded', () => {
    initCursor();
    initNav();
    initReveal();
    initCounters();
    initBars();
    initParallax();
    initCardGlow();
    initGlowCards();
    _syncProgress();

    const hp = document.querySelector('.hero-particles');
    if (hp) initParticles(hp, 60);

    // Close modals via backdrop click & Esc
    document.querySelectorAll('.modal-backdrop').forEach(b => {
      b.addEventListener('click', (e) => { if (e.target === b) b.classList.remove('open'); });
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') document.querySelectorAll('.modal-backdrop.open').forEach(m => m.classList.remove('open'));
    });

    // Sidebar links with data-screen (employee + admin portals)
    document.querySelectorAll('.sidebar-link[data-screen]').forEach(l => {
      l.addEventListener('click', (e) => {
        e.preventDefault();
        window.PV.showScreen(l.dataset.screen);
      });
    });
  });
})();
