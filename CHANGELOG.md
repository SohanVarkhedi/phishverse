
## [Phase 10] — 2026-05-23 — ML Risk Engine + Behaviour Analytics

### Added
- analytics/behaviour_tracker.py — BehaviourTracker class (clicked_link, credential_submit, reported_attack, ignored_attack, click_rate, report_rate, attack_history)
- ai/risk_model.py — DecisionTreeClassifier (sklearn); train_model(), predict(), rule fallback
- ai/datasets/risk_dataset.csv — 255-row synthetic training dataset
- ai/ai_models/ — artifact directory for trained .pkl
- ML_ARCHITECTURE.md — full ML design doc
- backend/app.py — GET /api/dept-stats endpoint
- employee.html — ML Risk Prediction card, Behaviour Metrics card with progress bars
- admin.html — Department Vulnerability real-data table (#deptStatsBody); Click Rate + Report Rate columns in employee table

### Changed
- event_manager.py — EventManager.set_behaviour_tracker(); _handle_choice() calls tracker.record()
- main.py — BehaviourTracker instantiated; wired to EventManager; passed to ResultStore.save() and run_ai_analysis()
- analytics/result_store.py — ResultStore.save() now accepts behaviour: dict; 8 behaviour fields written to JSON
- ai/__init__.py — uses RiskModel (ML Decision Tree) instead of RiskPredictor; behaviour dict merged into features; ai JSON includes ml_source + behaviour summary
- backend/app.py — /api/employees now includes click_rate, report_rate, clicked_link, credential_submit, reported_attack, ignored_attack
- app.js — PV.loadEmployees() updated for 8 columns with coloured click/report rate cells; PV.loadDeptStats() added; heatmap screen wired via PV.onScreenShow

### Architecture
- Rule engine (RiskEngine) remains source of truth for game score and pass/fail
- ML model augments: predicts risk label with confidence, identifies weakness
- BehaviourTracker classifies each event choice into link-click / credential-submit / report / vishing-fall

---

# PHISHVERSE — Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased] — v1.9 — AI Layer v1

### Added
- `ai/__init__.py` — `run_ai_analysis(employee_id, risk_summary) → dict`
  - Orchestrates all three AI modules; saves `ai_results/{id}_ai.json`
  - `load_ai_result(employee_id)` for future semester report integration
- `ai/risk_predictor.py` — `RiskPredictor`
  - Rule-based classification: HIGH / MEDIUM / LOW
  - Confidence score (0.50–0.95) derived from score + bias distance to band boundary
  - `train_model()` no-op placeholder (future: sklearn RandomForest)
  - `_extract_features()` isolated for ML swap without touching `predict()`
  - `self._model = None` reserved for trained classifier
- `ai/recommendation_engine.py` — `RecommendationEngine`
  - `generate_plan(bias_profile)` → ranked lectures + plain-text training plan
  - Priority labels: CRITICAL ≥3, HIGH ≥2, MEDIUM ≥1, LOW =0
- `ai/exam_generator.py` — `ExamGenerator`
  - `generate_profile(bias_profile, employee_id)` → topic distribution + topic list
  - BASE_PER_AXIS=2, TOTAL_QUESTIONS=10; extra slots allocated by bias proportion
- `ai/ai_models/.gitkeep` — future trained model storage
- `ai/datasets/.gitkeep` — future training data (risk_labels.csv)
- `ai_results/.gitkeep` — per-employee AI output directory

### Changed
- `main.py`: `from ai import run_ai_analysis` import added
- `main.py`: `_end_game()` calls `run_ai_analysis(emp_id, risk_summary)` after
  `LectureEngine.assign_lectures()` — AI runs last, augments without gating

### ai_results schema
```json
{
  "employee": "EMP01",
  "risk": "HIGH",
  "confidence": 0.84,
  "weakness": "authority",
  "recommendation": "Immediate training required: CEO Fraud & HR Impersonation.",
  "generated_topics": ["authority", "authority", "urgency", ...]
}
```

### Design constraints
- `RiskEngine` score unchanged — rule-based score is source of truth
- `LectureEngine.assign_lectures()` unchanged — AI does not gate lecture assignment
- No external APIs, no heavy ML training
- ML-ready: architecture supports sklearn swap with no interface changes

---

## [Unreleased] — v1.8 — Final Exam + Certificate

### Added
- `exam/question_bank.json` — adaptive question bank keyed to 4 bias axes
  - Fields per question: `question_id`, `bias_target`, `topic`, `difficulty`,
    `question`, `options` (A–D), `correct`, `explanation`, `campaign_tags`
- `exam/question_engine.py` — adaptive question distributor
  - Weights question selection by employee's entrance exam bias profile
  - Scales difficulty to entrance exam score
- `exam/final_exam.py` — exam UI, scoring, and certificate issuance
  - Presents MCQ drawn from question engine
  - Issues certificate on pass: name, campaign, score, date, UUID `certificate_id`

### Flow
```
SEMESTER REPORT (exam readiness gate) → FINAL EXAM → CERTIFICATE
```

---

## [Unreleased] — v1.7 — Semester Report

### Added
- `employee_reports/` — output directory for generated semester reports
- Semester report content:
  - Employee profile (name, ID, department, role)
  - Entrance exam score (from `analytics/results/{id}.json`)
  - Risk level + bias breakdown (urgency / authority / reward / fear)
  - Learning progress — assigned vs completed lectures
  - Cyber maturity rating (derived from score + bias + completion)
  - Per-bias recommendations
  - Exam readiness score (lectures 25pt + entrance 25pt + bias 50pt = 100)

### Flow
```
LECTURES COMPLETE → SEMESTER REPORT → FINAL EXAM (gated by readiness)
```

---

## [Unreleased] — v1.6 — Lecture System

### Added
- `training/__init__.py` — makes `training/` a Python package
- `training/lectures.json` — 4 lecture modules keyed to the 4 bias axes:
  - `email_awareness` (urgency) — 3 sections on urgency attacks, password scams,
    verification methods
  - `ceo_fraud_awareness` (authority) — 3 sections on BEC, authority manipulation,
    verification workflows
  - `qr_awareness` (reward) — 3 sections on reward baiting, QR code risks,
    scam indicators
  - `vishing_awareness` (fear) — 3 sections on OTP scams, threat manipulation,
    phone verification
- `training/lecture_engine.py` — `LectureEngine` static class
  - `assign_lectures(employee_id, risk_summary)` — rule-based; bias > 0 → assign;
    perfect run → all 4; idempotent (skips if record exists);
    writes `employee_training/{id}.json`
  - `load_training(employee_id)` — returns training record or None
  - `mark_complete(employee_id, lecture_id)` — marks lecture done; sets
    `completed=True` and `completed_at` when all assigned are done
  - `all_complete(employee_id)` — True if all assigned lectures completed
  - `load_lectures(lecture_ids)` — full content from JSON, order preserved
- `employee_training/.gitkeep` — directory placeholder
- `STATE_LECTURES = "lectures"` in `constants.py`
- `LectureScreen` in `ui.py`
  - List mode: animated header, lecture cards (bias-colour border, tag pill,
    status circle, title/topic), CONTINUE button when all done
  - Detail mode: heading + bullet scroll view, Mark as Complete footer button
  - `set_employee(employee_id)` — loads training record + lecture content
  - `handle_key()` — returns `"CONTINUE"` when all modules complete

### Changed
- `main.py`: imported `LectureScreen` and `LectureEngine`
- `main.py`: `lecture_screen` instantiated in `__init__` with `set_fonts()`
- `main.py`: `_end_game()` — calls `LectureEngine.assign_lectures()` after
  ResultStore save; calls `lecture_screen.set_employee()` to pre-load modules
- `main.py`: `STATE_REPORT` → `"DASHBOARD"` now routes to `STATE_LECTURES`
  (was: straight to `STATE_DASHBOARD`)
- `main.py`: `STATE_LECTURES` handler — `"CONTINUE"` → `dashboard.load_data()`
  then `STATE_DASHBOARD`
- `main.py`: `_update()` and `_draw()` handle `STATE_LECTURES`

### Flow after change
```
REPORT (ENTER) → LECTURES (complete all modules) → ANALYTICS DASHBOARD → QUIT
```

---

## [Unreleased] — v1.5 — Registration Dropdown Fix + Analytics Dashboard

### Added
- `STATE_DASHBOARD = "dashboard"` in `constants.py`
- `DashboardScreen` class in `ui.py`
  - Reads all `analytics/results/*.json` via `ResultStore.load_all()`
  - Overview panel: total employees, avg score, pass rate
  - Department risk bars — animated fill, colour-coded by score band
  - Behaviour bias bars — Urgency / Authority / Reward / Fear averages
  - Campaign stats: count + pass percentage per campaign
  - Bottom insight strip: most vulnerable department + most exploited attack type
  - No-data fallback when results/ is empty
- `_draw_dept_dropdown()` in `RegistrationScreen` — open dropdown overlay
  - Coloured dot + name for each option; `◀  selected` indicator
  - Rendered after all form fields so it overlays subsequent inputs

### Changed
- `RegistrationScreen.handle_key()`:
  - ENTER on dept field opens dropdown (was: advance to next field)
  - Keys fully absorbed while dropdown open (TAB/DOWN cannot escape)
  - ESC in dropdown closes list without changing selection
- `RegistrationScreen._draw_dept()`: redesigned as closed dropdown
  - Coloured dot + selected name + `▼` arrow (was: coloured block with `◀▶` cycler)
- `RegistrationScreen.reset()`: clears `_dept_open = False`
- Controls strip hint updated: `"</> on Dept  Change"` → `"ENTER  Open dept list"`
- `CyberResilienceReport.handle_key()`:
  - Return type: `bool` → `str | None`
  - ENTER/E → `"DASHBOARD"`, Q/ESC → `"QUIT"`
  - Dismiss hint: `"ENTER — view Analytics Dashboard  ·  ESC / Q — quit"`
- `main.py` — `STATE_REPORT` handler routes to dashboard or quit based on returned action
- `main.py` — `STATE_DASHBOARD` handler: `handle_key()` True → game exits

### Removed
- `RegistrationScreen._dept_input()` — LEFT/RIGHT cycling replaced by dropdown
- Hardcoded `◀▶` arrows from department field

---

## [Unreleased] — v1.4 — Employee Registration

### Added
- `STATE_REGISTRATION` game state — inserted between `STATE_TITLE` and `STATE_CAMPAIGN_SELECT`
- `RegistrationScreen` (in `ui.py`) — already implemented; now wired into game loop
  - Fields: Employee Name (required), Employee ID (required), Department (select),
    Role (optional) + CONFIRM button
  - Department selector: HR / Finance / IT / General with colour-coded pills
  - TAB/UP/DOWN navigate fields; LEFT/RIGHT cycle departments; ESC → back to title
  - Validates required fields; shows inline error messages
- Employee identity strip in `CyberResilienceReport` header
  - Shows: `Name: X  ·  ID: X  ·  Dept: X  ·  Campaign: X`
- Certificate banner now addresses employee by name

### Changed
- `main.py`: Title screen Enter key → `STATE_REGISTRATION` (was: `STATE_CAMPAIGN_SELECT`)
- `main.py`: `Game._key()` now accepts `unicode_char` parameter for text input
- `main.py`: `_end_game()` merges employee data into report_data and ResultStore call
- `report.py`: `header_h` 70 → 98; identity strip added at y=46
- `analytics/result_store.py`: `save()` signature extended with
  `employee_name`, `employee_department`, `employee_role` keyword args
- `analytics/result_store.py`: filename `{employee_id}.json` (was: `{id}_{camp}_{date}.json`)
- `analytics/result_store.py`: result schema — bias fields renamed to `urgency`, `authority`,
  `reward`, `fear`; risk level field renamed to `risk`; added `employee_name`, `role`

### Backward Compatibility
- `python main.py` still launches; registration is the first screen
- `ResultStore.save()` old positional args still work; new employee args are keyword-optional

---

## [Unreleased] — v1.3 — Campaign System

### Added
- `campaigns/` directory with 3 department-targeted campaign JSON files:
  - `hr_campaign.json` — `email_phishing`, `hr_message`, `voice_phishing` | pass=80
  - `finance_campaign.json` — `ceo_fraud`, `email_phishing` | pass=85
  - `employee_campaign.json` — all 6 events | pass=70
- `analytics/__init__.py` — package initialiser
- `analytics/campaign_loader.py` — `Campaign` data class + `CampaignLoader`
  - Loads from `campaigns/*.json`, validates required fields and event IDs
  - `load()`, `load_all()`, `list_available()`
- `analytics/result_store.py` — `ResultStore` persistence layer
  - `save()` — writes timestamped JSON to `analytics/results/`
  - `load()`, `load_all_for_campaign()`, `load_all()`, `list_results()`
  - `campaign_summary()` — aggregated pass rate, avg score, per-bias averages
- `analytics/results/emp01.json` — example result file documenting the schema
- `run_campaign.py` — CLI entry point
  - `--campaign CAMPAIGN_ID` / `-c`
  - `--employee EMPLOYEE_ID` / `-e`
  - `--list` / `-l` — tabular campaign listing

### Changed
- `events.py` — added `set_enabled_events(ids)` to `EventDatabase`
  - `get_by_tile()`, `all_events()`, `total` all respect the campaign filter
  - `_enabled = None` (default) → all events active (backward compatible)
- `main.py` — `Game.__init__` now accepts `campaign=None, employee_id=""`
  - Applies campaign filter to `EventDatabase` on init if campaign provided
  - `_end_game()` saves result via `ResultStore` if campaign is active
  - `from analytics.result_store import ResultStore` import added

### Backward Compatibility
- `python main.py` unchanged — free-play mode, campaign=None, no filter, no save

---

## [Unreleased] — v1.2 — Project Restructure

### Added
- `DEVLOG.md` — persistent developer log (updated after every change)
- `STATUS.md` — live project status tracker (DONE / IN PROGRESS / BLOCKED / PLANNED)
- `ROADMAP.md` — versioned product roadmap through v3.x enterprise
- `CHANGELOG.md` — this file
- Target folder structure: `game/`, `analytics/`, `dashboard/`, `training/`, `ai/`, `docs/`
- Module reuse analysis identifying `risk_engine.py`, `story.py`, `events.py`, and
  `data/events.json` as high-value reusable components

### Changed
- Nothing — structural documentation only, no file migrations yet

---

## [1.1.0] — 2026-05-21 — Story Progression Expansion

### Added
- `story.py` — `StoryManager` class driving 4-act RPG narrative
  - Acts 1–4 with automatic progression based on room visits and event completions
  - 14 room-entry cutscenes keyed to `(act, room)` pairs — each fires once
  - Act-keyed objectives list (3–4 items per act)
  - `alert_mode` property → True in acts 3 & 4
- `NPC_ACT_DIALOGS` in `npc.py` — 28 unique dialogue pairs across 4 acts and 7 NPCs
- `NPC.set_act(n)` and `NPC.get_dialog()` methods
- `NPC.dialog` backward-compatible property
- `_on_act_change(act, name)` in `main.py` — fires act banner, switches all NPC dialogue
- Alert-mode red atmospheric pulse overlay (alpha 18–28) during acts 3 & 4

### Changed
- `main.py`: replaced static `OBJECTIVES` list with `StoryManager`-driven objectives
- `main.py`: room-transition block now checks for cutscenes and opens dialog
- `main.py`: `_npc_interact()` now calls `npc.get_dialog()` explicitly
- `npc.py`: `NPC_DIALOG_SETS` replaced by `NPC_ACT_DIALOGS` (4-act pools)

### Removed
- Static 7-item `OBJECTIVES` list from `main.py` (replaced by `StoryManager`)
- Static `NPC_DIALOG_SETS` flat list from `npc.py` (replaced by `NPC_ACT_DIALOGS`)

---

## [1.0.1] — 2026-05-21 — Dialog UI Bug Fix

### Fixed
- **CRITICAL UI BUG:** Long message text overlapped and rendered over/behind
  the choice options menu in event dialog screens
- Root cause: choice menu anchored to box bottom; text rendered freely from top
  with no boundary between the two regions

### Changed — `dialogue.py`
- Added `MSG_MARGIN_BOT = 25` class constant — guaranteed pixel gap
- Dynamic `bh = max(BOX_HEIGHT, msg_lines_h + choice_block_h)` — box auto-expands
- `screen.set_clip(text_clip)` applied before text rendering — hard boundary
  prevents text from entering the choice area
- `choice_y = max(text_end_y + MSG_MARGIN_BOT, msg_region_bottom + PAD)` — choices
  always anchored dynamically below last rendered text line
- All box surface draws updated to use dynamic `bh` instead of hardcoded `BOX_HEIGHT`

---

## [1.0.0] — 2026-05-21 — Initial Release

### Added — Core RPG
- `main.py` — pygame game loop; title / explore / dialog / pause / report states
- `constants.py` — screen dimensions, colour palette, game state strings
- `dialogue.py` — `DialogBox` with typewriter reveal, animated choice menu,
  speaker name tags, scanline overlay, auto word-wrap
- `event_manager.py` — `EventManager` orchestrating full event lifecycle
  with score-change and game-end callbacks
- `events.py` — `EventDatabase` loading events from JSON; tile-based lookup
- `map.py` — `GameMap` with 40×28 office grid; 7 named rooms; door detection
- `npc.py` — Pixel-art NPC sprites; idle animation; speech bubbles; wander timer
- `player.py` — `Player` with WASD/arrow movement; direction facing; step animation
- `raycaster.py` — 3D raycaster (future mode; not active in 2D build)
- `report.py` — `CyberResilienceReport` — animated full-screen end-game report
- `risk_engine.py` — `RiskEngine` — score, bias tracking, risk assessment,
  `summary_dict()` output
- `tiles.py` — `TileRenderer` — pixel-art tile surfaces for all 15 tile types
- `ui.py` — `HUD`, `PauseMenu`, `TitleScreen`

### Added — Game Data
- `data/events.json` — 6 phishing scenario events:
  1. `email_phishing` — Password reset urgency attack (Work Area computers)
  2. `qr_phishing` — Fake hackathon QR poster (Cafeteria)
  3. `usb_drop` — Baited USB drive on floor (Work Area)
  4. `hr_message` — Authority phishing via fake HR portal link (HR Room)
  5. `voice_phishing` — Vishing call requesting OTP (HR Room phone)
  6. `ceo_fraud` — Business Email Compromise wire transfer (Meeting Room)
- `data/events3d.json` — Event definitions for 3D raycaster mode

### Added — Assets
- `assets/audio/` — Audio directory (placeholder)
- `assets/sprites/` — Sprite directory (placeholder)
- `assets/tiles/` — Tile directory (placeholder)

---

## Version Roadmap Summary

| Version | Description | Status |
|---------|-------------|--------|
| **v1.0** | Initial RPG prototype | ✅ Released |
| **v1.0.1** | Dialog overlap UI fix | ✅ Released |
| **v1.1** | 4-act story expansion | ✅ Released |
| **v1.2** | Project restructure + docs | 🔄 In Progress |
| **v1.3** | Import cleanup + packaging | 📋 Planned |
| **v1.6** | Lecture system (rule-based) | ✅ Done |
| **v1.7** | Semester report | ✅ Done |
| **v1.8** | Final exam + certificate | ✅ Done |
| **v1.9** | AI Layer v1 (rule-based, ML-ready) | ✅ Done |
| **v2.0** | Web platform — Employee + Manager portals | 📋 Planned |
| **v2.1** | Analytics REST API | 📋 Planned |
| **v2.2** | Manager dashboard web UI | 📋 Planned |
| **v2.3** | Scenario library (50+ events) | 📋 Planned |
| **v2.4** | User accounts + sessions | 📋 Planned |
| **v3.0** | Adaptive AI learning engine | 📋 Planned |
| **v3.1** | LLM scenario generator | 📋 Planned |
| **v3.2** | Department analytics | 📋 Planned |

---

*Last updated: 2026-05-22*

## [v1.5] - 2026-05-22

### Added
- Phase 5: Employee Registration screen (TITLE -> REGISTRATION -> CAMPAIGN_SELECT)
- Phase 8: Semester Report System (8-section comprehensive report card)
- reporting/ package: SemesterReport data class + SemesterReportScreen
- reporting/employee_reports/ - per-employee JSON report storage
- Cyber Maturity Index (Beginner/Aware/Secure/Cyber Guardian)
- Weakness Detection (primary + secondary attack vector vulnerability)
- Learning Progress section (stub - Phase 9 integration pending)
- STATE_REGISTRATION and STATE_SEMESTER_REPORT in constants.py

### Changed
- result_store.py: save() accepts employee:dict, filename now {employee_id}.json
- Game flow: REPORT -> SEMESTER_REPORT -> LECTURES (added semester report step)
- _end_game: generates + saves semester report on every game completion

## [v1.6] - 2026-05-22

### Added
- Phase 9: Final Exam system (adaptive 10-question MCQ from question_bank.json)
- Adaptive question selection: primary weakness category gets 4/10 questions
- FinalExamScreen: QUIZ/REVEALING/RESULTS phases with animated correct/wrong feedback
- CertificateScreen: animated gold cyber certificate with UUID cert ID + PV seal
- ExamEngine: exam result persistence to exam_results/{EMPID}_exam.json
- Certificate: JSON cert persistence to certificates/{EMPID}_certificate.json
- Exam retake system: FAIL returns to lectures, attempt counter increments
- STATE_FINAL_EXAM, STATE_CERTIFICATE in constants.py

### Changed
- STATE_SEMESTER_REPORT ENTER now routes to Final Exam (if unlocked) or Lectures (if locked)
- Complete employee lifecycle: Registration->Campaign->RPG->Report->Semester->Exam->Certificate

## [2026-05-22] v2.1 — Flask Web Bridge

### Added
- `backend/app.py` — Flask + Flask-CORS backend
  - POST `/api/launch-game` — spawns `main.py` via `subprocess.Popen`
  - GET  `/api/game-status` — returns running/idle + PID
  - GET  `/api/results/<employee_id>` — reads `analytics/results/{id}.json`
  - GET  `/api/ai-results/<employee_id>` — reads `ai_results/{id}_ai.json`
- `backend/requirements.txt` — flask>=3.0, flask-cors>=4.0
- `WEB_BACKEND_SETUP.md` — setup and architecture documentation

### Changed
- `employee.html` — `confirmLaunch` handler replaced: `alert()` → real `fetch` to Flask backend
  - Shows "Launching…" state while request is in flight
  - On success: unlocks subsequent stages + toast
  - On backend offline: toast with fix instruction (python backend/app.py)
