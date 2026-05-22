# PHISHVERSE — Web Integration Map

> Maps each front-end file to its responsibility within the PHISHVERSE web platform.
> The pygame RPG (`main.py`) is the Entrance Exam module, launched as a subprocess.
> All portal files are static HTML/CSS/JS — no framework, no build step required.

---

## File Responsibilities

### `index.html` — Marketing / Landing Page

Public-facing home page. Links to both portals.

| Section | ID | Purpose |
|---------|----|---------|
| Hero | — | Video background, particles, brand entry |
| Stats | `.stats` | Problem framing (91% attack stat, $4.9M breach cost, etc.) |
| Platform | `#platform` | AI copilot + cinematic training feature strip |
| Lifecycle | `#journey` | 8-step training timeline (Registration → Certificate) |
| Attack vectors | `#attacks` | 6 phishing type cards (Email, CEO Fraud, Vishing, QR, USB, HR) |
| Portal Access | `#portals` | Dual cards linking to employee.html and admin.html |
| Console Preview | `#console` | Risk heatmap + AI briefing live preview |
| CTA | `#pricing` | Enroll CTA |
| Footer | `#trust` | Links, compliance tags |

---

### `employee.html` — Employee Training Portal

Single-page portal. One sidebar, 7 screens hidden/shown via `PV.showScreen()`.

| Screen ID | Route Stage | Python Module |
|-----------|-------------|---------------|
| `screen-registration` | `#registration` | `events.py` (employee dict) |
| `screen-campaigns` | `#campaign` | `campaigns/` |
| `screen-exam` | `#entrance` | `main.py` subprocess launch |
| `screen-lectures` | `#training` | `training/lecture_engine.py` |
| `screen-report` | `#report` | `reporting/semester_report.py` |
| `screen-final` | `#exam` | `exam/final_exam.py` |
| `screen-certificate` | `#certificate` | `exam/final_exam.py Certificate` |

**Lifecycle state** is tracked in `sessionStorage` via `PV.completeStep(stepName)`.
Results are read from `analytics/results/{id}.json` and `ai_results/{id}_ai.json`.

Sidebar links must use `data-screen="{name}"` (short form, without `screen-` prefix) for `PV.showScreen()` to wire automatically.

---

### `admin.html` — Manager Portal

Single-page dashboard. One sidebar, N screens hidden/shown via `PV.showAdminPage()`.

| Page ID | Screen | Data Source |
|---------|--------|-------------|
| `screen-overview` | KPI grid + campaign chart + threat feed | `PV.MOCK.*` |
| `screen-employees` | Employee roster table | `analytics/results/` |
| `screen-campaigns` | Campaign list + analytics | `campaigns/` |
| `screen-heatmap` | Department risk heatmap | `risk_engine.py` aggregated |
| `screen-reports` | AI report cards | `ai_results/` |
| `screen-mcq` | MCQ results + pass/fail | `exam/` |
| `screen-new` | Campaign builder form | POST → `/api/campaigns` |
| `screen-settings` | Org + user settings | config |

Sidebar links must use `data-screen="{name}"` (short form). `PV.showAdminPage` is an alias for `PV.showScreen` — both portals use the same convention.

---

### `styles.css` — Shared Stylesheet

Single stylesheet used by all three HTML files. No framework, all custom.

| Class group | Purpose |
|-------------|---------|
| `:root` variables | Design tokens (colors, fonts, radii) |
| `.topnav` | Public landing nav with scroll state |
| `.hero` | Full-screen hero with video + particles |
| `.stats-grid` | 4-column stat bar |
| `.section` | Page section wrapper with max-width |
| `.journey` / `.journey-wide` | 6-col (default) / 4×2 grid training timeline |
| `.attack-card` | Phishing type cards with mouse glow |
| `.portal-access-grid` | 2-column portal card layout |
| `.portal-card` | Individual portal card (cyan / gold variants) |
| `.portal-shell` | Sidebar + main content grid |
| `.sidebar` | Fixed sidebar with active link state |
| `.card` / `.glass` | Content card variants |
| `.bar` / `.bar-fill` | Animated progress bars (cyan/gold/red/green) |
| `.bias-bars` / `.bias-row` | Bias score visualization rows |
| `.report-widget` / `.ring-fill` | Score ring + report card |
| `.v-timeline` / `.v-step` | Vertical progress timeline |
| `.heat-cell` + risk modifiers | Heatmap cells with risk-level coloring |
| `.data-table` | Employee roster / results table |
| `.ai-report-card` | Purple AI briefing card |
| `.modal-backdrop` / `.modal` | Dialog overlay |
| `.toast` | Bottom-right notification |
| `.tag` | Inline label chips |
| `.reveal` | Scroll-triggered fade-in |

---

### `app.js` — Shared JS Utilities

Single JS file loaded by all pages. Exposes everything on `window.PV`.

| Function | Description |
|----------|-------------|
| `PV.showScreen(id)` | Employee portal — show a screen, sync sidebar, animate bars/rings |
| `PV.showAdminPage(id)` | Admin portal — show a page, sync sidebar, animate bars |
| `PV.completeStep(step)` | Mark a training step done, persist to sessionStorage, re-sync progress UI |
| `PV.getProgress()` | Return current step completion state |
| `PV.renderBiasBar(el, data)` | Render 4-axis bias bar visualization into a container |
| `PV.renderRing(el, pct, label)` | Render an SVG score ring |
| `PV.renderHeatmap(el)` | Render department risk bars from mock data |
| `PV.MOCK` | Mock analytics dataset (departments, employees, bias, AI summary) |
| `PV.openModal(id)` | Open a modal by ID |
| `PV.closeModal(id)` | Close a modal |
| `PV.toast(msg)` | Show a bottom-right toast notification |
| `PV.mockPost(endpoint, body)` | Simulated async POST for demo flows |
| `PV.toggleSidebar()` | Mobile sidebar toggle |

**Auto-wiring on DOMContentLoaded:**
- `.sidebar-link[data-screen]` → calls `PV.showScreen` on click
- `.sidebar-link[data-page]` → calls `PV.showAdminPage` on click
- `.modal-backdrop` → closes on backdrop click and Escape key

---

## Data Flow: Real Data Architecture (Phase 11+)

```
Manager Portal (admin.html)
    │
    ├── [New Campaign screen]  →  POST /api/campaigns {name, domain}
    │                              domain Finance → [ceo_fraud, email_phishing]
    │                              domain HR      → [hr_message, voice_phishing]
    │                              domain General → all 6 events
    │                              writes campaigns/<slug>.json
    │
    ▼
Employee Portal (employee.html)
    │
    ├── [Entrance Exam screen] →  GET /api/campaigns (fetch latest campaign_id)
    │                          →  POST /api/launch-game {campaign_id}
    │                          →  Flask: subprocess.Popen(main.py --campaign campaign_id)
    │
    ▼
Game (main.py — source of truth)
    │
    ├── Employee Registration screen  (Name, ID, Department, Role)
    ├── Domain auto-loaded (skips campaign select if --campaign arg present)
    ├── Plays only events for assigned domain
    └── On game end → writes analytics/results/{employee_id}.json
                    → writes employee_reports/{id}_report.json
                    → writes ai_results/{id}_ai.json
    │
    ▼
Flask backend (backend/app.py)
    │
    ├── GET /api/employees      →  reads all analytics/results/*.json
    ├── GET /api/results/<id>   →  reads analytics/results/{id}.json
    ├── GET /api/ai-results/<id>→  reads ai_results/{id}_ai.json
    │
    ▼
Employee Portal (employee.html — Report screen)
    │
    └── "Load Results" form → enter Employee ID → fetch /api/results/{id}
                            → populates score gauge, bias bars, AI debrief, certificate

Manager Portal (admin.html — Employees screen)
    │
    └── PV.loadEmployees() → fetch /api/employees → renders real records in table
```

---

## app.js API (Phase 11+)

| Function | Description |
|----------|-------------|
| `PV.loadEmployees()` | Fetch `/api/employees`, render real records into `#empBody` |
| `PV.loadOverviewEmployees()` | Fetch `/api/employees`, render top-5 into `#overviewEmpBody` |
| `PV.onScreenShow(key, fn)` | Register a data-load callback that fires when a screen is shown |
| `PV._screenHandlers` | Registry of screen-key → callback mappings |

`PV.MOCK.employees` has been **removed**. All employee data comes from the Flask API.

---

## Domain → Events Mapping

| Domain  | enabled_events |
|---------|---------------|
| Finance | `ceo_fraud`, `email_phishing` |
| HR      | `hr_message`, `voice_phishing` |
| General | `email_phishing`, `qr_phishing`, `usb_drop`, `hr_message`, `voice_phishing`, `ceo_fraud` |

---

## Adding a New Screen (Employee Portal)

1. Add a `<div id="screen-{name}" class="screen">` block in `employee.html`
2. Add a `<a class="sidebar-link" data-screen="screen-{name}">` link in the sidebar
3. Add the step key to `_STEPS` array in `app.js` (if it contributes to progress tracking)
4. Call `PV.completeStep('{name}')` when the user finishes that screen
5. Optionally register a data loader: `PV.onScreenShow('{name}', myLoadFn)`

## Adding a New Admin Page

1. Add a `<div id="screen-{name}" class="admin-page">` block in `admin.html`
2. Add a `<a class="sidebar-link" data-screen="screen-{name}">` link in the sidebar
3. Optionally register a data loader: `PV.onScreenShow('{name}', myLoadFn)`
4. The auto-wiring in `app.js` DOMContentLoaded handles the rest

---

*Last updated: 2026-05-23*
