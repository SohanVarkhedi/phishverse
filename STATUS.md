# PHISHVERSE — Project Status

> **Rule:** Update this file whenever work items change state.
> States: ✅ DONE · 🔄 IN PROGRESS · 🚧 BLOCKED · 📋 PLANNED

---

## ✅ DONE

### Core RPG (v1.0)
- [x] pygame game loop — title / explore / dialog / pause / report states
- [x] 40×28 tile office map with 7 rooms
- [x] Animated NPC sprites with speech bubbles and idle wander
- [x] Typewriter dialog box with animated choice menu
- [x] 6 phishing scenario events (email, QR, USB, HR, vishing, CEO fraud)
- [x] Risk engine — urgency / authority / reward / fear bias tracking
- [x] Cyber Resilience Report screen with animated bias bars
- [x] Score popups, camera shake, screen flash effects
- [x] Room-transition flash banners

### UI Bug Fix (v1.0.1)
- [x] Dialog text / choice overlap eliminated
- [x] Dynamic box height — auto-expands to fit content
- [x] Hard clip region — text cannot bleed into choices
- [x] `choice_y` dynamically anchored below last text line + 25 px margin

### Story Expansion (v1.1)
- [x] `story.py` — `StoryManager` 4-act state machine
- [x] 14 room-entry cutscenes (fires once per act+room)
- [x] NPC act-aware dialogue pools (4 acts × 7 NPCs = 28 dialogue pairs)
- [x] Automatic act progression (room entry + event-count triggers)
- [x] Alert-mode red atmospheric overlay (acts 3 & 4)
- [x] Act-change banner animations

### Documentation & Structure (Phase 2)
- [x] `DEVLOG.md`, `STATUS.md`, `ROADMAP.md`, `CHANGELOG.md` created
- [x] Target folder structure: `game/`, `analytics/`, `dashboard/`, `training/`, `ai/`, `docs/`
- [x] Module reuse analysis in DEVLOG.md + docs/MIGRATION.md

### Campaign System (Phase 3)
- [x] `campaigns/hr_campaign.json` — HR-targeted events (email, authority, vishing)
- [x] `campaigns/finance_campaign.json` — Finance-targeted events (CEO fraud, email)
- [x] `campaigns/employee_campaign.json` — All 6 events, general staff
- [x] `analytics/campaign_loader.py` — `Campaign` + `CampaignLoader` with validation
- [x] `analytics/result_store.py` — `ResultStore` with save/load/aggregate methods
- [x] `analytics/results/emp01.json` — Example result file (schema reference)
- [x] `run_campaign.py` — CLI launcher (`--campaign`, `--employee`, `--list`)
- [x] `events.py` — `set_enabled_events()` added to `EventDatabase` (campaign filter)
- [x] `main.py` — Campaign hook: filter on init, save result on game end
- [x] Integration tests: all campaign/filter/save/load assertions pass

### Registration Dropdown + Analytics Dashboard (Phase 6)
- [x] Department field replaced with proper dropdown (open/close, UP/DOWN navigate, ENTER select)
- [x] `_dept_open` state — absorbs all keys while open; ESC closes without change
- [x] `_draw_dept_dropdown()` — overlay drawn last, renders above subsequent form fields
- [x] Controls strip updated to reflect new dropdown interaction model
- [x] `STATE_DASHBOARD = "dashboard"` added to `constants.py`
- [x] `DashboardScreen` class in `ui.py` (~200 lines)
  - Overview panel: employees, avg score, pass rate
  - Department risk bars (animated, colour-coded)
  - Behaviour bias bars (Urgency / Authority / Reward / Fear)
  - Campaign stats table
  - Bottom insight strip: most vulnerable dept + most exploited attack type
  - No-data fallback message
- [x] `report.py` — `handle_key()` returns `"DASHBOARD"` or `"QUIT"` (was bool)
- [x] `main.py` — full STATE_DASHBOARD wiring (key / update / draw)
- [x] Full flow: TITLE → REGISTRATION → CAMPAIGN SELECT → GAME → REPORT → DASHBOARD → QUIT

### Employee Registration (Phase 5)
- [x] `STATE_REGISTRATION` game state — TITLE → REGISTRATION → CAMPAIGN_SELECT → GAME
- [x] `RegistrationScreen` — full form: Name, Employee ID, Department (select), Role (optional)
- [x] `main.py` — wired registration state into game loop (key/update/draw)
- [x] `main.py` — employee dict stored globally, passed to report + ResultStore
- [x] `report.py` — identity strip: Name, ID, Dept, Campaign in report header
- [x] `report.py` — certificate banner addresses employee by name
- [x] `analytics/result_store.py` — `save()` accepts employee_name / department / role
- [x] `analytics/results/{employee_id}.json` — per-employee filename (overwrites on re-run)
- [x] Analytics schema includes: employee_name, employee_id, department, role,
      campaign, score, urgency, authority, reward, fear, risk, recommendation, timestamp

---

### Employee Portal Architecture (Phase 6.5)
- [x] `docs/EMPLOYEE_PORTAL.md` — full 8-stage pipeline architecture
- [x] `docs/DB_SCHEMA.md` — full relational schema (7 tables + question bank JSON)
- [x] `docs/ROUTES.md` — 17 REST routes with request/response specs and guard logic
- [x] Lecture module structure: 4 modules keyed to urgency / authority / reward / fear
- [x] Semester report data model (computed view, no separate table)
- [x] Exam readiness score formula defined
- [x] Certificate issuance logic + `certificate_id` UUID design
- [x] Pipeline stage guard logic defined
- [x] `training/exam_questions.json` schema defined (question bank, not yet populated)

### Lecture System (Phase 7)
- [x] `training/__init__.py` — package initialiser
- [x] `training/lectures.json` — 4 lecture modules (email / CEO fraud / QR / vishing)
  - Each module: 3 sections × 4–5 actionable bullet points
- [x] `training/lecture_engine.py` — `LectureEngine` static class
  - Rule-based assignment: bias > 0 → assign corresponding lecture
  - Perfect run → all 4 modules assigned as refresher
  - Idempotent — existing record not overwritten on replay
  - Handles both `urgency_bias` and `urgency` field name conventions
  - Methods: assign / load / mark_complete / all_complete / load_lectures
- [x] `employee_training/.gitkeep` — directory tracked in git
- [x] `STATE_LECTURES = "lectures"` added to `constants.py`
- [x] `LectureScreen` class in `ui.py`
  - List mode: lecture cards with bias tag pill, status circle, CONTINUE button
  - Detail mode: scrollable sections/bullets, Mark as Complete footer button
  - `set_employee()`: loads training record + full lecture content
  - `handle_key()`: returns `"CONTINUE"` only when all modules complete
- [x] `main.py` — full `STATE_LECTURES` wiring
  - `LectureEngine` and `LectureScreen` imported
  - `lecture_screen` instantiated with fonts in `__init__`
  - `_end_game()`: assigns lectures after save; loads into lecture screen
  - REPORT → LECTURES (was: REPORT → DASHBOARD directly)
  - LECTURES `"CONTINUE"` → `dashboard.load_data()` → DASHBOARD
  - `_update()` and `_draw()` handle `STATE_LECTURES`

### Semester Report (Phase 8)
- [x] `employee_reports/` — output directory for semester reports
- [x] Employee profile section (name, ID, department, role)
- [x] Entrance exam score from `analytics/results/{id}.json`
- [x] Risk level and bias analysis (urgency / authority / reward / fear)
- [x] Learning progress: assigned vs completed lectures
- [x] Cyber maturity rating derived from score + bias + completion
- [x] Recommendations — per-bias remediation guidance
- [x] Exam readiness score (lectures 25 + entrance 25 + bias 50)

### Final Exam + Certificate (Phase 9)
- [x] `exam/question_bank.json` — question bank keyed to 4 bias axes
  - Fields: question_id, bias_target, topic, difficulty, question, options (A–D),
    correct, explanation, campaign_tags
- [x] `exam/question_engine.py` — adaptive question distribution
  - Questions weighted by employee bias profile from entrance exam
  - Difficulty scaled to entrance exam score
- [x] `exam/final_exam.py` — exam UI + scoring + certificate issuance
  - Issues certificate on pass: employee name, campaign, score, date, UUID cert ID

### AI Layer v1 (Phase 9.5)
- [x] `ai/__init__.py` — package + `run_ai_analysis()` orchestrator
- [x] `ai/risk_predictor.py` — `RiskPredictor` (rule-based, ML-ready)
  - HIGH / MEDIUM / LOW classification with confidence score
  - `train_model()` placeholder, `_extract_features()` isolation, `self._model` slot
  - Handles `urgency_bias` and `urgency` field name conventions
- [x] `ai/recommendation_engine.py` — `RecommendationEngine`
  - Ranked lecture list with CRITICAL / HIGH / MEDIUM / LOW priority labels
  - Plain-text `training_plan` for report display
- [x] `ai/exam_generator.py` — `ExamGenerator`
  - `BASE_PER_AXIS=2`, `TOTAL_QUESTIONS=10`
  - Proportional extra-question allocation by bias weight
  - `generated_topics` list consumed by `QuestionEngine`
- [x] `ai/ai_models/.gitkeep` — placeholder for future trained model files
- [x] `ai/datasets/.gitkeep` — placeholder for future training CSV datasets
- [x] `ai_results/.gitkeep` — output directory for per-employee AI JSON
- [x] `main.py` — `run_ai_analysis(emp_id, risk_summary)` called in `_end_game()`
  after `LectureEngine.assign_lectures()` (rule systems unchanged)

### Full Learning Pipeline (current)
```
ENTRANCE EXAM (RPG) → [AI ANALYSIS] → REPORT → LECTURES
→ SEMESTER REPORT → FINAL EXAM → CERTIFICATE
```

---

## 🔄 IN PROGRESS

- [ ] File migration of game modules → `game/` subfolder (pending approval)

---

## 🚧 BLOCKED

- **File migration to `game/`** — blocked on: import strategy decision
  (`sys.path` vs `__init__.py` vs relative imports).

- **Web platform scaffold** — blocked on: tech stack confirmation
  (Flask + Jinja2 vs FastAPI + SPA). Architecture defined in docs/.

- **AI layer** — blocked on: web platform first.

---

## 📋 PLANNED

### Platform Architecture (Confirmed Direction)
- [ ] **Employee Portal** — web app; employees log in, take entrance exam (RPG),
      complete lectures, view semester report, sit final exam, receive certificate
- [ ] **Manager Portal** — web app; security/HR managers create campaigns,
      view department analytics, monitor completion, export reports

> The existing pygame RPG is the **Entrance Exam module** within the Employee Portal.
> It is launched as a subprocess and its results are read back via JSON.

### Web Platform (Next)
- [ ] `portal/` — Flask app factory (`db.py`, `models.py`, `routes/`)
- [ ] Employee Portal routes (login, exam start, lecture, report, exam submit)
- [ ] Manager Portal routes (campaigns, analytics, employee management)
- [ ] JWT authentication
- [ ] SQLite DB seeded from existing campaign/lecture JSON

### v2.0 — Enterprise Layer
- [ ] `analytics/` — REST API wrapping `risk_engine.py`
- [ ] Manager dashboard web UI (campaign management, department analytics)
- [ ] User session persistence (SQLite → PostgreSQL path)
- [ ] Multi-scenario campaign builder

### v3.0 — AI Analytics Layer
- [ ] `ai/` — Adaptive learning engine
- [ ] Per-user bias fingerprinting
- [ ] Scenario difficulty auto-adjustment
- [ ] Natural language phishing scenario generator
- [ ] Department-level risk analytics

### Future / Enterprise Deployment
- [ ] Multi-user support (user accounts, progress tracking)
- [ ] Cloud deployment (Docker → Kubernetes)
- [ ] LMS integration (SCORM export)
- [ ] Real-time admin monitoring dashboard

---

*Last updated: 2026-05-22*

---

## [2026-05-22] Status Update

### DONE
- Phase 1: Dialog UI bug fix
- Phase 2: 4-act story expansion
- Phase 3: Campaign system (JSONs + ResultStore)
- Phase 4: Campaign gameplay (CampaignSelectScreen)
- Phase 5: Employee Registration (RegistrationScreen, updated result schema)
- Phase 8: Semester Report System (SemesterReport + SemesterReportScreen)

### IN PROGRESS
- Integration testing Phase 5+8 flow end-to-end

### PLANNED
- Phase 9: Final Exam unlock (lecture completion check)
- Phase 6: Admin dashboard (analytics/api.py + dashboard/app.py)
- Phase 7: AI adaptive learning layer

### BLOCKED
- None

---

## [2026-05-22] Phase 9 Status

### DONE
- Phase 1-5: Registration, Campaign, RPG, Reports
- Phase 8: Semester Report System
- Phase 9: Final Exam + Certification

### COMPLETE: Employee Lifecycle
Registration -> Campaign Select -> Entrance Exam -> Cyber Resilience Report -> Semester Report -> Final Exam -> Certificate

### NEXT
- Phase 6: Manager/Admin Dashboard
- Phase 10: Annual renewal, expiry tracking

---

## [2026-05-22] Phase 10 Status

### DONE
- Flask backend bridge (`backend/app.py`) — POST /api/launch-game launches main.py via subprocess
- CORS enabled — browser fetch from employee.html to localhost:5000 works
- Additional endpoints: /api/game-status, /api/results/<id>, /api/ai-results/<id>
- Employee portal confirmLaunch now calls real Flask endpoint
- Error handling: already running, not found, backend offline — all produce clear user-facing toasts

### NEXT
- Phase 11: Manager Portal live data (Flask endpoints returning real analytics JSON)
- Phase 12: Session persistence (pass employee ID from portal to main.py args)

---

## [2026-05-23] Phase 11 Status

### DONE — Architecture Overhaul (Real Data Flow)

#### Game (source of truth)
- [x] `main.py` — `--campaign CAMPAIGN_ID` CLI arg: skips in-game campaign select, auto-applies pre-assigned domain
- [x] Employee registers INSIDE the game (RegistrationScreen) — no static employee in portal
- [x] Domain-based event filtering: Finance → CEO fraud + Email phishing; HR → Authority + Vishing; General → all 6
- [x] All analytics written to `analytics/results/{id}.json` on game end

#### Flask backend
- [x] `GET /api/employees` — scans `analytics/results/*.json`, returns real employee records
- [x] `GET /api/campaigns` — lists all campaign JSONs from `campaigns/`
- [x] `POST /api/campaigns` — creates new campaign JSON with domain-mapped events
- [x] `POST /api/launch-game` — now accepts `campaign_id` in body, passes `--campaign` to subprocess

#### Manager Portal (admin.html)
- [x] Removed Marc Kessler — sidebar now shows generic "Admin User"
- [x] Removed all hardcoded mock employees (Anya Reyes, Jonas Maier, Priya Kapoor, Liu Chen, Sara Okafor, etc.)
- [x] Employee tables (`#empBody`, `#overviewEmpBody`) load real data from `/api/employees`
- [x] Campaign builder: domain selector (Finance/HR/General) auto-sets enabled events
- [x] "Deploy campaign" button POSTs to `/api/campaigns` (real Flask endpoint)

#### Employee Portal (employee.html)
- [x] Removed all "Anya Reyes" hardcoding from sidebar, hero, registration, report, certificate
- [x] Sidebar footer is generic until results are loaded
- [x] Report screen: "Load Results" form — enter Employee ID → fetches `/api/results/{id}` → populates gauge, bias bars, AI debrief, certificate
- [x] Launch flow: fetches most recent campaign from `/api/campaigns`, passes `campaign_id` to game subprocess

#### app.js
- [x] `PV.MOCK.employees` removed — no mock employee array
- [x] `PV.loadEmployees()` — real fetch to `/api/employees`, renders into `#empBody`
- [x] `PV.loadOverviewEmployees()` — loads top 5 into overview table
- [x] `PV._screenHandlers` / `PV.onScreenShow` hook — screens auto-load data when navigated to
- [x] `general_campaign.json` created for General domain (all 6 events)

### Phase 11 — Campaigns Page: Real Data (2026-05-23)

- [x] admin.html — removed all hardcoded mock campaign cards (Treasury Cohort, Reception Voice Drills, Marketing Brand Spoof, USB Drop, HR Bonus Wave)
- [x] admin.html — campaigns section now uses `id="campaignsGrid"` container + dynamic `id="campaignsStat"` tag
- [x] admin.html — `showScreen()` now fires `PV._screenHandlers` (campaigns reload on deploy redirect)
- [x] app.js — `PV.loadCampaigns()` added: fetches `GET /api/campaigns`, renders real cards, empty state
- [x] app.js — `PV.onScreenShow('campaigns', PV.loadCampaigns)` registered
- [x] WEB_INTEGRATION.md — updated to remove mock dependency notes for campaigns

### NEXT
- Phase 12: Annual renewal, expiry tracking
- Phase 13: Multi-employee session (manager assigns campaign link per employee)

### Phase 10 — ML Risk Engine + Behaviour Analytics (2026-05-23)

- [x] analytics/behaviour_tracker.py — tracks clicked_link, credential_submit, reported_attack, ignored_attack per session
- [x] ai/risk_model.py — DecisionTreeClassifier with train/predict/fallback
- [x] ai/datasets/risk_dataset.csv — 255 synthetic labelled rows
- [x] ai/ai_models/ — model artifact directory
- [x] event_manager.py — BehaviourTracker hooked to _handle_choice()
- [x] main.py — BehaviourTracker instantiated, wired, passed to _end_game
- [x] analytics/result_store.py — 8 behaviour fields in result JSON
- [x] ai/__init__.py — RiskModel replaces RiskPredictor; behaviour passed to prediction
- [x] backend/app.py — /api/employees includes behaviour metrics; /api/dept-stats added
- [x] employee.html — ML Risk Prediction card + Behaviour Metrics card
- [x] admin.html — Click Rate / Report Rate columns in employee table; Dept Vulnerability table in heatmap
- [x] app.js — loadEmployees updated; loadDeptStats added; heatmap screen registered
- [x] ML_ARCHITECTURE.md created
