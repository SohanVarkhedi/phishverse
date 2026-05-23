# PHISHVERSE — Developer Log

> **Rule:** This file is updated after every change, no matter how small.
> Format: date · files · reason · issues · fixes · next steps.

---

## [2026-05-21] — Session 1: Initial RPG Build

**Files Created (all):**
`main.py`, `constants.py`, `dialogue.py`, `event_manager.py`, `events.py`,
`map.py`, `npc.py`, `player.py`, `raycaster.py`, `report.py`,
`risk_engine.py`, `tiles.py`, `ui.py`, `data/events.json`, `data/events3d.json`

**Reason:**
Initial implementation of PHISHVERSE — a 2D top-down cybersecurity awareness RPG
built in pygame. Includes full office map, 6 phishing scenarios, score system,
NPC sprites, dialog box, and a final Cyber Resilience Report screen.

**What Works:**
- Full pygame game loop with title, explore, dialog, pause, report states
- 6 event scenarios: email phishing, QR code, USB drop, HR message, vishing, CEO fraud
- Risk engine tracking urgency/authority/reward/fear bias scores
- Typewriter-style dialog box with choice menus
- Animated NPCs with speech bubbles
- Room flash transitions, score popups, camera shake
- Cyber Resilience Report with bias bars and certificate

**Issues Found:**
- None at initial build — game runs cleanly on Python 3.13.1 + pygame 2.6.1

**Next Steps:**
- Fix dialog overlap bug (text rendering over choices)
- Add story progression and 4-act narrative

---

## [2026-05-21] — Session 2: Dialog UI Bug Fix

**Files Modified:** `dialogue.py`

**Reason:**
Long message text was expanding downward and rendering behind/over the choice
options menu. Message area and choices area had no enforced separation.

**Root Cause:**
Choice menu was anchored to bottom of the box (`menu_y = by + BOX_HEIGHT - menu_h`)
while text rendered freely downward from the top — two independent regions
with no boundary enforcement.

**Fix Applied:**
1. Added `MSG_MARGIN_BOT = 25` class constant (guaranteed text-to-choice gap)
2. Pre-compute `choice_block_h` first (bottom-up layout)
3. Compute dynamic `bh = max(BOX_HEIGHT, msg_lines_h + choice_block_h)` — box
   auto-expands to fit all content
4. Applied `screen.set_clip(text_clip)` to hard-clip text rendering to message
   region — text physically cannot bleed into the choice area
5. `choice_y = max(text_end_y + MSG_MARGIN_BOT, msg_region_bottom + PAD)` —
   choices always anchored below last text line with guaranteed margin
6. Updated all box surface draws to use dynamic `bh` instead of `BOX_HEIGHT`

**Issues Found:** None after fix — tested with long and short messages.

**Next Steps:** Story expansion (4-act narrative)

---

## [2026-05-21] — Session 3: Story Progression Expansion (4-Act Narrative)

**Files Created:** `story.py`
**Files Modified:** `npc.py`, `main.py`

**Reason:**
Game lacked narrative structure. Single-session event loop felt disconnected.
Added 4-act RPG story progression without rewriting any existing system.

**Changes:**

### `story.py` (NEW)
- `StoryManager` class — tracks act (1–4) and phase
- Act transitions:
  - Act 1→2: player enters Work Area for first time
  - Act 2→3: 3 events completed
  - Act 3→4: 5 events completed
- 14 room-entry cutscenes keyed by `(act, room)` — each fires exactly once
- Act-keyed objectives list (3–4 lines per act)
- `alert_mode` property — True in acts 3 & 4

### `npc.py`
- Replaced 7 flat `NPC_DIALOG_SETS` with `NPC_ACT_DIALOGS` — 4 pools × 7 NPCs
- Added `set_act(n)` method — switches dialogue pool
- Added `get_dialog()` method — returns current-act lines
- Added `.dialog` property as backward-compat shim

### `main.py`
- Import `StoryManager`
- Replaced static `OBJECTIVES` list with `StoryManager`-driven objectives
- Added `_on_act_change(act, name)` — updates NPCs, HUD, fires act banner
- Room-transition block now checks `story.get_cutscene(room)` and opens dialog
- `story.advance()` called each tick — automatic act progression
- Alert-mode red pulse atmospheric overlay in acts 3 & 4 (alpha ~18–28)

**Issues Found:**
- Windows CP1252 terminal encoding rejects emoji in print() calls — not a game
  issue (pygame uses its own renderer). Logic verified via UTF-8 forced test.

**Fixes:** Used `os.environ['PYTHONIOENCODING'] = 'utf-8'` in test scripts only.

**Tests Run:**
- `story.py` unit logic: act transitions, cutscene-fires-once, alert_mode ✓
- Full `Game()` init: 14 NPCs, act 1, correct objective ✓
- `python main.py`: game window opens, no exceptions ✓

**Next Steps:** Phase 2 — project restructuring, documentation, roadmap

---

## [2026-05-22] — Session 4: Phase 2 — Documentation & Project Structure

**Files Created:**
`DEVLOG.md` (this file), `STATUS.md`, `ROADMAP.md`, `CHANGELOG.md`

**Folders Created (empty — migration pending):**
`game/`, `analytics/`, `dashboard/`, `training/`, `ai/`, `docs/`
(all contain `.gitkeep` placeholder; no files moved)

**Reason:**
PHISHVERSE is transitioning from a single-module RPG prototype to a structured
enterprise platform. Phase 2 establishes persistent documentation and the target
folder architecture BEFORE any file migration begins.

**Module Inventory & Reuse Analysis:**

| Current File       | Target Folder | Reusability Notes |
|--------------------|---------------|-------------------|
| `main.py`          | `game/`       | Game loop only — stays in game/ |
| `constants.py`     | `game/`       | Could become shared config |
| `dialogue.py`      | `game/`       | Purely game UI |
| `event_manager.py` | `game/`       | Orchestrates event lifecycle |
| `events.py`        | `game/`       | JSON loader/wrapper |
| `map.py`           | `game/`       | 2D office map |
| `npc.py`           | `game/`       | NPC sprites + dialogue |
| `player.py`        | `game/`       | Player movement |
| `raycaster.py`     | `game/`       | 3D perspective (future use) |
| `story.py`         | `game/`       | Story state machine |
| `tiles.py`         | `game/`       | Tile renderer |
| `ui.py`            | `game/`       | HUD, title, pause |
| `risk_engine.py`   | `analytics/`  | **HIGH REUSE** — pure Python, zero pygame, outputs `summary_dict()` |
| `report.py`        | `analytics/`  | Pygame render only — logic extractable |
| `data/events.json` | `training/`   | **HIGH REUSE** — JSON scenario library |

**Key Reusable Modules Identified:**

1. **`risk_engine.py`** — Zero pygame dependency. Pure Python scoring engine
   with bias tracking and `summary_dict()` output. Directly usable by the
   analytics dashboard and AI layer with no changes.

2. **`data/events.json`** — Self-contained JSON scenario library. Can be loaded
   by training workflows, admin campaign manager, and AI adaptive engine.

3. **`story.py`** — Pure Python state machine. Zero pygame dependency.
   Can drive training workflows and learning path sequencing.

4. **`events.py`** (EventDatabase class) — JSON loader with tile-based lookup.
   Loader is reusable; tile lookup is game-specific and can be separated.

**Issues Found:** None — structural work only, no code changes.

**Next Steps:**
- File migration (game/ folder) — pending user approval
- analytics/ scaffold (risk_engine adapter)
- dashboard/ scaffold (Flask/FastAPI or Next.js)
- training/ scaffold (scenario JSON schema + loader)

---

## [2026-05-22] — Session 5: Phase 3 — Campaign System

**Files Created:**
`campaigns/hr_campaign.json`, `campaigns/finance_campaign.json`,
`campaigns/employee_campaign.json`,
`analytics/__init__.py`, `analytics/campaign_loader.py`,
`analytics/result_store.py`, `analytics/results/emp01.json`,
`run_campaign.py`

**Files Modified:** `events.py`, `main.py`

**Reason:**
Implement the campaign layer — the bridge between the RPG game and the future
enterprise dashboard. Goal: campaign selected → events filtered → game runs →
result persisted. No game rewrite, no dashboard, no AI.

---

### `campaigns/` — 3 Campaign JSON files

**Schema:**
```json
{
  "campaign_id": "",
  "name": "",
  "department": "",
  "employees": [],
  "enabled_events": [],
  "pass_score": 80,
  "duration_days": 7
}
```

**HR Campaign** (`hr_campaign.json`)
- Target: HR department (emp01–03)
- Events: `email_phishing`, `hr_message`, `voice_phishing`
- Pass score: 80 | Duration: 7 days
- Rationale: HR staff face authority phishing and vishing most frequently

**Finance Campaign** (`finance_campaign.json`)
- Target: Finance department (emp04–06)
- Events: `ceo_fraud`, `email_phishing`
- Pass score: 85 (higher bar — finance approves payments) | Duration: 14 days
- Rationale: CEO fraud (BEC) is the primary financial attack vector

**Employee Campaign** (`employee_campaign.json`)
- Target: ALL staff (emp01–10)
- Events: all 6 scenarios
- Pass score: 70 | Duration: 30 days
- Rationale: Baseline org-wide awareness training

---

### `events.py` — Campaign event filter (minimal addition)

Added to `EventDatabase`:
- `self._enabled: set[str] | None = None` — filter state (None = all active)
- `set_enabled_events(event_ids)` — called by campaign runner before game start
- Updated `get_by_tile()` — returns None for events outside the enabled set
- Updated `all_events()` — returns only enabled events (respects filter)
- Updated `total` property — counts only enabled events

Zero changes to EventManager, RiskEngine, or any other system.

---

### `analytics/campaign_loader.py`

- `Campaign` class — immutable wrapper around campaign JSON
  - `has_employee(id)`, `is_passing(score)`, `to_dict()`
- `CampaignLoader` — static methods only
  - `load(campaign_id)` — validates & loads single campaign
  - `load_all()` — loads all campaigns from campaigns/
  - `list_available()` — returns list of IDs
  - `_validate(data)` — checks required fields + valid event IDs

---

### `analytics/result_store.py`

- `ResultStore` — static methods only
  - `save(employee_id, campaign, risk_summary, completed_events)` — writes
    `analytics/results/{employee_id}_{campaign_id}_{date}.json`
  - `load(employee_id, campaign_id)` — reads all results for one employee/campaign
  - `load_all_for_campaign(campaign_id)` — aggregate for dashboard
  - `load_all()` — all results
  - `list_results()` — filenames
  - `campaign_summary(campaign_id)` — aggregated stats (avg score, pass rate,
    per-bias averages) — ready for dashboard consumption

**Result schema stored:**
```json
{
  "employee_id", "campaign", "campaign_name", "department",
  "score", "pass_score", "passed",
  "urgency_bias", "authority_bias", "reward_bias", "fear_bias",
  "risk_level", "weakest_area", "recommendation", "mistakes",
  "successful_reports", "completed_events", "events_total",
  "events_completed", "timestamp"
}
```

---

### `main.py` — Campaign hook (minimal wiring)

- Added `campaign=None, employee_id=""` to `Game.__init__`
- Calls `self.db.set_enabled_events()` if campaign is provided
- In `_end_game()`: calls `ResultStore.save()` if campaign is active
- `from analytics.result_store import ResultStore` import added

`python main.py` still works identically — campaign=None = free play, no filter.

---

### `run_campaign.py` — CLI entry point

```
python run_campaign.py --campaign hr_campaign --employee emp01
python run_campaign.py --campaign finance_campaign --employee emp04
python run_campaign.py --list
python run_campaign.py        # free play
```

**Issues Found:** None

**Tests Run:**
- `CampaignLoader.list_available()` returns 3 campaigns ✓
- HR filter: `db.total` drops 6 → 3 ✓
- `ceo_fraud` tile returns None under HR filter ✓
- `email_phishing` tile passes HR filter ✓
- `ResultStore.save()` writes JSON correctly ✓
- `run_campaign.py --list` prints formatted table ✓
- `python main.py` still boots cleanly ✓

**Next Steps:**
- Phase 4: Admin dashboard (analytics/api.py + dashboard/app.py)
- Phase 5: Scenario library expansion (50+ events)

---

*Last updated: 2026-05-22*


---

## [2026-05-22] — Session 6: Phase 4 — Campaign Gameplay Integration

**Files Modified:**
`constants.py`, `ui.py`, `main.py`, `analytics/campaign_loader.py`,
`campaigns/hr_campaign.json`, `campaigns/finance_campaign.json`,
`campaigns/employee_campaign.json`

**Reason:**
Campaigns existed as data-only files with no in-game visibility. Phase 4 makes
campaign selection a playable, animated game state inserted between the title
screen and gameplay. Players see campaign cards, navigate with keyboard,
select a campaign, and the game loads only those events.

---

### `constants.py`
- Added `STATE_CAMPAIGN_SELECT = "campaign_select"` — new state between title and explore

---

### Campaign JSONs — all 3 updated
- Added `"description"` field (full sentence, shown word-wrapped on campaign cards)

| Campaign | description excerpt |
|----------|---------------------|
| hr_campaign | "Targeted training for HR staff. Covers authority-based phishing..." |
| finance_campaign | "High-stakes training for finance staff who authorise payments..." |
| employee_campaign | "Full cybersecurity awareness suite for all staff. Covers every..." |

---

### `analytics/campaign_loader.py`
- Added `self.description = data.get("description", "")` to `Campaign.__init__`
- Added `"description"` to `to_dict()` output

---

### `ui.py` — `CampaignSelectScreen` (NEW class, ~200 lines)

Full-screen animated campaign picker:

**Visual design:**
- Animated gradient background (slow sine-wave colour shift, matching title screen palette)
- Scanline overlay for CRT aesthetic
- Fixed header panel: "SELECT TRAINING CAMPAIGN" with pulsing subtitle
- 3 campaign cards, vertically centred, slide-in from left on screen entry
  (cubic ease-out animation over ~17 frames)
- Bottom controls strip with keyboard hint bar

**Each card shows:**
- Campaign name (gold when selected, white otherwise)
- Department badge — coloured pill (blue=HR, amber=Finance, green=ALL)
- Description text, word-wrapped to 2 lines
- Stats row: event count · pass score · duration

**Selected card effects:**
- Blue border glow (animated alpha pulse)
- Outer glow rect around card
- Gold `▶` cursor arrow that bobs vertically
- Brighter background tint

**Controls (returned from `handle_key()`):**
- `W` / `↑` → prev card
- `S` / `↓` → next card
- `ENTER` / `E` → return Campaign object
- `F` → return `"FREE_PLAY"`
- `ESC` → return `"BACK"`

---

### `main.py` — State machine wiring

**Imports added:**
- `CampaignSelectScreen` from `ui`
- `CampaignLoader` from `analytics.campaign_loader`

**`__init__` changes:**
- `camp_select = CampaignSelectScreen(...)` — initialised with fonts + all campaigns
- `CampaignLoader.load_all()` called once at startup

**New method `_apply_campaign(campaign)`:**
- Sets `self._campaign` and `self._employee_id`
- Calls `self.db.set_enabled_events(campaign.enabled_events)`
- Used by both in-game campaign select and CLI path

**`_key()` changes:**
- `STATE_TITLE`: pressing Enter now goes to `STATE_CAMPAIGN_SELECT` (not directly to explore)
  — `_slide_in` reset to 0.0 so animation replays on re-entry
- `STATE_CAMPAIGN_SELECT` handler added:
  - `BACK` → `STATE_TITLE`
  - `FREE_PLAY` → `STATE_EXPLORE` + room flash "FREE PLAY"
  - Campaign selected → `_apply_campaign()` + `STATE_EXPLORE` + campaign name banner

**`_update()` change:**
- `STATE_CAMPAIGN_SELECT` → `camp_select.update()` and early return

**`_draw()` change:**
- `STATE_CAMPAIGN_SELECT` → `camp_select.draw(screen)` + flip + early return

**End-game result:**
- `_end_game()` saves result via `ResultStore` using campaign name
  and `employee_id="player"` when coming from in-game campaign select

---

### New Game Flow

```
python main.py
  ↓
TITLE SCREEN  (press Enter)
  ↓
CAMPAIGN SELECT  (animated card picker)
  ├─ Select campaign → filter events → EXPLORE → result saved
  └─ Press F        → free play, all events, no result saved
  └─ ESC            → back to TITLE
```

**`run_campaign.py` CLI path unchanged** — bypasses campaign select entirely.

---

**Issues Found:** None

**Tests Run:**
- All 6 modules compile cleanly (`py_compile`) ✓
- `CampaignSelectScreen` loads 3 campaigns from disk ✓
- `K_DOWN` navigation: `sel` increments, returns `None` ✓
- `K_RETURN` returns `Campaign` object ✓
- `K_f` returns `"FREE_PLAY"` ✓
- `STATE_CAMPAIGN_SELECT` constant present ✓
- `python main.py` launches (RUNNING status, no crash) ✓

**Next Steps:**
- Phase 5: Employee Registration (see Session 7 below)

---

## [2026-05-22] — Session 7: Phase 5 — Employee Registration

**Files Modified:**
`main.py`, `report.py`, `analytics/result_store.py`
(`ui.py` and `constants.py` already had the required code — just wired up)

**Reason:**
Before gameplay began the game collected no employee identity. Results were saved
as anonymous "player" records. Phase 5 inserts a mandatory employee registration
form between the title screen and campaign select so every training session is
tied to a named employee, department, and role.

---

### New Game Flow

```
TITLE SCREEN  (Enter)
  ↓
EMPLOYEE REGISTRATION  (name, ID, dept, role)
  ↓
CAMPAIGN SELECT
  ↓
GAMEPLAY
  ↓
CYBER RESILIENCE REPORT  (shows employee identity + campaign)
```

---

### `main.py` — State machine wiring

- Imported `RegistrationScreen` from `ui` (class was already implemented there)
- Added `self._employee: dict = {}` to store registration data
- Instantiated `self.reg_screen = RegistrationScreen(...)` with fonts
- **TITLE** `handle_key()` → `STATE_REGISTRATION` (was: directly to `STATE_CAMPAIGN_SELECT`)
  - `reg_screen.reset()` called on entry to clear previous session data
- **STATE_REGISTRATION** handler added to `_key()`:
  - `ESC` → `STATE_TITLE`
  - `dict` returned → store in `self._employee`, set `self._employee_id`, go to `STATE_CAMPAIGN_SELECT`
- `_update()` and `_draw()` updated to call `reg_screen.update()` / `reg_screen.draw()`
- Event loop updated: `_key(ev.key, running, ev.unicode)` — passes unicode char for text input
- `_key()` signature updated to `_key(self, key, running, unicode_char="")`
- `_end_game()` now builds `report_data` merging `risk.summary_dict()` with employee fields
  (employee_name, employee_id, department, role, campaign_name) before passing to report
- `ResultStore.save()` call updated with new keyword args: `employee_name`,
  `employee_department`, `employee_role`
- `_apply_campaign()` updated to read `employee_id` from `self._employee` dict

---

### `report.py` — Employee identity strip

- `header_h` increased 70 → 98 to accommodate identity strip
- Title text shifted to y=10
- New identity bar at y=46: renders `Name · ID · Dept · Campaign`
  as a single small-font line, dimly coloured (160, 175, 220)
- Thin horizontal rule at y=70 separates identity from score content
- Certificate banner now addresses the employee by name:
  `"{employee_name} demonstrated {risk_level} risk resilience. Score: {score}/100"`
  Falls back to employee_id, then "This employee" if neither set

---

### `analytics/result_store.py` — Schema update

**`save()` new signature:**
```python
ResultStore.save(
    employee_id, campaign, risk_summary, completed_events,
    employee_name="", employee_department="", employee_role=""
)
```

**Filename:** `analytics/results/{employee_id}.json`
(simplified from `{employee_id}_{campaign_id}_{date}.json` — latest run overwrites)

**New result schema stored:**
```json
{
  "employee_name", "employee_id", "department", "role",
  "campaign", "campaign_id",
  "score", "pass_score", "passed",
  "urgency", "authority", "reward", "fear",
  "risk", "weakest_area", "recommendation",
  "mistakes", "successful_reports",
  "completed_events", "events_total", "events_completed",
  "timestamp"
}
```

Bias fields renamed: `urgency_bias` → `urgency`, `authority_bias` → `authority`,
`reward_bias` → `reward`, `fear_bias` → `fear` (matches spec analytics schema).
Risk level renamed: `risk_level` → `risk`.

---

**Issues Found:** None

**Tests Run:**
- All modified files pass `py_compile` ✓
- `STATE_REGISTRATION` constant was already in `constants.py` ✓
- `RegistrationScreen` class was already fully implemented in `ui.py` ✓
- `_key()` correctly receives `ev.unicode` for text entry ✓
- Flow: TITLE → REGISTRATION → CAMPAIGN_SELECT → EXPLORE → REPORT ✓

**Next Steps:**
- Phase 6: UI fix + Analytics Dashboard (see Session 8 below)

---

## [2026-05-22] — Session 8: Phase 6 — Registration Dropdown Fix + Analytics Dashboard

**Files Modified:**
`constants.py`, `ui.py`, `report.py`, `main.py`

---

### Part A — Department Dropdown Fix (`ui.py` → `RegistrationScreen`)

**Problem:** Department used a coloured-block left/right cycler. Selected value was
hard to read at a glance and the interaction model was inconsistent with the other fields.

**Change:** Replaced with a standard dropdown.

**Closed state:**
- Shows a coloured dot + selected department name + `▼` arrow
- Pressing ENTER (while dept field is focused) opens the dropdown

**Open state:**
- Overlay list panel drawn on top of all subsequent form fields (rendered last)
- UP/DOWN navigate options, each with coloured dot + department name
- Active selection shows `◀  selected` indicator on the right
- ENTER confirms selection and closes; ESC closes without change
- All navigation keys are absorbed while dropdown is open — TAB/DOWN cannot
  escape to the next field accidentally

**Code changes:**
- Added `_dept_open = False` and `_dept_box_pos = None` to `__init__` and `reset()`
- `handle_key()`: rewrote to check `_dept_open` first and consume all keys when open;
  ENTER on dept field opens dropdown (not advance to next field)
- Removed `_dept_input()` — LEFT/RIGHT cycling removed in favour of dropdown only
- Replaced `_draw_dept()`: shows closed state (dot + name + ▼)
- Added `_draw_dept_dropdown()`: open state overlay with coloured items
- `draw()`: records `_dept_box_pos` during field loop; draws dropdown overlay after
  all other fields so it renders on top
- Updated controls strip: `"</> on Dept  Change"` → `"ENTER  Open dept list"` +
  `"↑↓ in list  Navigate"`

---

### Part B — Analytics Dashboard (`ui.py` + `constants.py` + `report.py` + `main.py`)

**New game flow:**
```
TITLE → REGISTRATION → CAMPAIGN SELECT → GAME → REPORT → ANALYTICS DASHBOARD → QUIT
```

**`constants.py`:**
- Added `STATE_DASHBOARD = "dashboard"`

**`ui.py` — `DashboardScreen` (new class, ~200 lines):**

Reads `analytics/results/*.json` via `ResultStore.load_all()` on entry.

Layout (960×640):
- Header: "ANALYTICS DASHBOARD" + animated gradient bg
- Col 1 (x=24, w=240): Overview (employees / avg score / pass rate) + Campaign stats
- Col 2 (x=284, w=356): Department risk bars (animated fill, colour-coded by score)
- Col 3 (x=660, w=276): Behaviour bias bars (Urgency / Authority / Reward / Fear)
- Bottom strip (y=sh-110): "Most Vulnerable Department" card + "Most Exploited Attack" card
- Blink hint: "Press ENTER or ESC to quit"
- No-data fallback: shows message if results/ is empty

Aggregation (`_aggregate()`):
- Total employees, average score, pass rate
- Per-department: count + average score (sorted descending)
- Per-campaign: count + pass percentage
- Per-bias averages across all employees
- `most_vulnerable` = dept with lowest avg score
- `most_failed` = bias axis with highest average value

**`report.py` — `CyberResilienceReport.handle_key()`:**
- Return type changed `bool` → `str | None`
- ENTER/E → returns `"DASHBOARD"` (proceed to dashboard)
- Q/ESC   → returns `"QUIT"` (exit immediately)
- Dismiss hint updated: `"ENTER — view Analytics Dashboard  ·  ESC / Q — quit"`

**`main.py`:**
- Imported `DashboardScreen`
- Instantiated `self.dashboard = DashboardScreen(...)` with fonts in `__init__`
- `STATE_REPORT` handler: routes to `STATE_DASHBOARD` (loads data) or exits
- `STATE_DASHBOARD` handler added: `handle_key()` returns True → `running = False`
- `_update()` and `_draw()` updated for `STATE_DASHBOARD`

---

**Issues Found:** None

**Tests Run:**
- All 4 modified files pass `py_compile` ✓
- `STATE_DASHBOARD` constant present ✓
- `DashboardScreen._aggregate([])` returns `{}` (no-data path) ✓
- Dropdown: `_dept_open` absorbed keys without leaking to outer handler ✓
- Flow: TITLE → REGISTRATION → CAMPAIGN SELECT → EXPLORE → REPORT → DASHBOARD ✓

**Next Steps:**
- Phase 6.5: Employee Portal architecture docs (see Session 9 below)

---

## [2026-05-22] — Session 9: Phase 6.5 — Employee Portal Architecture

**Files Created:**
`docs/EMPLOYEE_PORTAL.md`, `docs/DB_SCHEMA.md`, `docs/ROUTES.md`

**No code changes.** Documentation and architecture planning only.

---

### Reason

PHISHVERSE is evolving from a standalone RPG into a structured cybersecurity
learning pipeline. Before implementation begins, the full architecture needs to
be defined so the database, routes, and stage logic can be built consistently
without rework.

---

### What was designed

#### `docs/EMPLOYEE_PORTAL.md` — Full pipeline architecture

Defines 8 pipeline stages:

```
LOGIN → REGISTRATION → CAMPAIGN ASSIGNMENT → ENTRANCE EXAM (RPG)
→ AI LECTURES → SEMESTER REPORT → FINAL EXAM → CERTIFICATE
```

Key design decisions:
- Existing RPG engine becomes Stage 4 (Entrance Exam) — **zero changes** to `main.py`
- RPG launched via `subprocess.Popen()` from portal; result read from `analytics/results/{id}.json`
- 4 lecture modules, one per bias axis: urgency / authority / reward / fear
- All 4 lectures must be completed before final exam unlocks
- Exam readiness score computed from lectures + entrance score + bias profile
- Certificate issued automatically on final exam pass with UUID `certificate_id`
- Technology stack planned: Flask + SQLite/PostgreSQL + Jinja2 + JWT

#### `docs/DB_SCHEMA.md` — Full relational schema

Tables defined:

| Table | Purpose |
|-------|---------|
| `employees` | Identity, department, campaign assignment, bcrypt password |
| `campaigns` | Campaign definitions (seeded from JSON) |
| `entrance_results` | RPG session results: score, bias, risk, events |
| `lectures` | Module definitions (4 rows, seeded once) |
| `lecture_progress` | Per-employee per-lecture completion state |
| `final_exam_attempts` | Each MCQ attempt with score, status, question snapshot |
| `certificates` | Issued certificate with UUID + level |

Also defines `training/exam_questions.json` question bank schema:
- Fields: `question_id`, `bias_target`, `topic`, `difficulty`, `question`,
  `options` (A–D), `correct`, `explanation`, `campaign_tags`
- Bias targets: urgency / authority / reward / fear
- Minimum 5 questions per bias (target: 15)

Semester report is a computed view (no dedicated table) assembled from all tables.

Exam readiness score formula:
```
+25  all 4 lectures complete
+25  entrance exam score ≥ campaign pass_score
+50  all bias values < 15
```

#### `docs/ROUTES.md` — REST route specifications

17 routes defined under `/employee/` prefix.
Each route includes: method, auth requirement, request schema, success response,
error codes, and guard conditions.

Key routes:
- `POST /employee/login` — returns JWT + `stage` field for redirect routing
- `POST /employee/register` — creates employee + auto-assigns campaign
- `POST /employee/entrance_exam/start` — launches RPG subprocess
- `GET  /employee/entrance_exam/result` — reads JSON result, persists to DB
- `POST /employee/lectures/{id}/complete` — marks lecture done (idempotent)
- `GET  /employee/semester_report` — full consolidated view
- `POST /employee/final_exam/submit` — scores attempt, issues certificate if passed
- `GET  /employee/certificate/{cert_id}` — public verification endpoint (no auth)

Pipeline stage guard logic defined: each route blocks access if the employee
has not yet reached that stage in the pipeline.

---

**Issues Found:** None — documentation only.

**Next Steps:**
- Phase 7: `portal/` Flask app scaffold (db.py, models.py, app factory)
- Phase 8: `training/exam_questions.json` — populate question bank (20+ questions)
- Phase 9: AI lecture content + AI exam generation (Claude API)

---

## [2026-05-22] — Session 10: Phase 7 — Lecture System

**Files Created:**
`training/__init__.py`, `training/lectures.json`, `training/lecture_engine.py`,
`employee_training/.gitkeep`

**Files Modified:**
`constants.py`, `ui.py`, `main.py`

**Reason:**
After completing the entrance exam (RPG gameplay), employees receive personalised
lecture assignments based on which bias axes showed weaknesses. Phase 7 implements
the full in-game lecture layer: assignment engine, content store, and interactive
lecture UI screen, with the flow gated so the analytics dashboard is only reached
after all assigned lectures are complete.

---

### New Game Flow

```
TITLE → REGISTRATION → CAMPAIGN SELECT → GAMEPLAY (entrance exam)
  ↓
CYBER RESILIENCE REPORT  (ENTER to continue)
  ↓
LECTURES SCREEN  (complete all assigned modules)
  ↓
ANALYTICS DASHBOARD → QUIT
```

---

### `training/__init__.py` (NEW)
Empty package initialiser — makes `training/` importable.

---

### `training/lectures.json` (NEW)
4 lecture modules, one per bias axis:

| lecture_id | bias_target | title |
|---|---|---|
| `email_awareness` | urgency | Email Phishing Awareness |
| `ceo_fraud_awareness` | authority | CEO Fraud & HR Impersonation |
| `qr_awareness` | reward | QR Phishing & Reward Baiting |
| `vishing_awareness` | fear | Vishing & Fear Manipulation |

Each module has 3 sections with 4–5 bullet points of specific, actionable guidance.
Content covers: trigger phrases, domain spoofing, verification workflows, OTP scams,
QR code risks, authority manipulation, caller ID spoofing, and phone verification.

---

### `training/lecture_engine.py` (NEW) — `LectureEngine` static class

**`BIAS_TO_LECTURE` mapping:**
```python
urgency   → email_awareness
authority → ceo_fraud_awareness
reward    → qr_awareness
fear      → vishing_awareness
```

**Assignment rule:** `BIAS_THRESHOLD = 0` — any bias > 0 triggers the lecture.
Perfect run (all biases = 0) → all 4 modules assigned as a refresher.

**Methods:**
- `assign_lectures(employee_id, risk_summary)` — idempotent; skips if record exists;
  handles both `urgency_bias` and `urgency` field name conventions; writes
  `employee_training/{id}.json`
- `load_training(employee_id)` — returns existing record or None
- `mark_complete(employee_id, lecture_id)` — marks one lecture done; updates
  `completed` and `completed_at` when all assigned lectures are done
- `all_complete(employee_id)` — returns True if all assigned lectures finished
- `load_lectures(lecture_ids)` — reads full content from `lectures.json`,
  preserves caller order

**Training record schema:**
```json
{
  "employee": "EMP01",
  "assigned_lectures": ["email_awareness", "vishing_awareness"],
  "completed_lectures": [],
  "completed": false,
  "assigned_at": "2026-05-22T...",
  "completed_at": null
}
```

---

### `employee_training/.gitkeep` (NEW)
Empty placeholder so the directory is tracked in git before any training records
are written at runtime.

---

### `constants.py`
- Added `STATE_LECTURES = "lectures"` to the state constants list

---

### `ui.py` — `LectureScreen` (new class, appended)

**Two modes:**
- `"list"` — card grid of assigned modules, status indicator, CONTINUE button when all done
- `"detail"` — scrollable reading view for a single module

**`set_employee(employee_id)`:**
- Loads `employee_training/{id}.json` via `LectureEngine`
- Calls `LectureEngine.load_lectures()` to populate full content
- Resets to list mode

**`handle_key()`:**
- List mode: UP/DOWN navigate cards; ENTER opens detail view; ENTER on CONTINUE
  (when all done) returns `"CONTINUE"` to caller
- Detail mode: UP/DOWN/W/S scroll; ENTER marks current lecture complete;
  ESC returns to list
- Returns `"CONTINUE"` only when `LectureEngine.all_complete()` confirms all done

**Visual design:**
- BIAS_COLORS: urgency=(230,80,80), authority=(200,120,50), reward=(60,160,220),
  fear=(180,60,200)
- Lecture cards: bias-coloured left border, bias tag pill, status circle
  (green filled = done, grey outline = pending), title + topic text
- CONTINUE button: only appears when all modules complete; gold-bordered
- Detail view: heading lines in white, bullet points in light grey with `•` glyph,
  scrollable with pixel-level offset; footer bar with Mark as Complete button

---

### `main.py` — State machine wiring

**Imports added:**
- `LectureScreen` from `ui`
- `LectureEngine` from `training.lecture_engine`

**`__init__`:**
- `self.lecture_screen = LectureScreen(SCREEN_WIDTH, SCREEN_HEIGHT)` instantiated
  with `set_fonts()` called

**`_end_game()` additions:**
- `emp_id` extracted to local variable (shared by ResultStore and LectureEngine)
- `LectureEngine.assign_lectures(emp_id, risk)` called after ResultStore save
- `self.lecture_screen.set_employee(emp_id)` called to load assigned modules

**`_key()` changes:**
- `STATE_REPORT` "DASHBOARD" action now routes to `STATE_LECTURES`
  (no longer jumps straight to dashboard)
- New `STATE_LECTURES` handler: `handle_key()` → if `"CONTINUE"`:
  `dashboard.load_data()` then `STATE_DASHBOARD`

**`_update()` change:**
- `STATE_LECTURES` → `lecture_screen.update()` early return

**`_draw()` change:**
- `STATE_LECTURES` → `lecture_screen.draw(screen)` + flip + early return

---

**Issues Found:** None

**Tests Run:**
- All modified files pass `python -m py_compile` ✓
- `training/` importable as a package ✓
- `LectureEngine.assign_lectures()` idempotent ✓
- `LectureEngine.load_lectures()` preserves order ✓
- `STATE_LECTURES` constant present ✓
- Full flow: REPORT → LECTURES → DASHBOARD ✓

**Next Steps:**
- Phase 8: Semester Report
- Phase 9: Final Exam + Certificate

---

## [2026-05-22] — Session 11: Phase 8 — Semester Report

**Files Created:**
`employee_reports/` (directory), semester report engine

**Reason:**
After completing all assigned lectures, employees need a consolidated view of their
full learning journey before being permitted to sit the final exam. The Semester
Report aggregates all data from the entrance exam, lecture completion, and bias
analysis into a single structured document.

---

### Semester Report Contents

| Section | Data Source |
|---|---|
| Employee profile | Registration data |
| Entrance exam score | `analytics/results/{id}.json` |
| Risk level | `risk_engine.summary_dict()` |
| Bias analysis | urgency / authority / reward / fear scores |
| Learning progress | `employee_training/{id}.json` — assigned vs completed |
| Cyber maturity rating | Derived from score + bias + lecture completion |
| Recommendations | Per-bias remediation guidance |
| Exam readiness score | Formula: lectures + entrance score + bias values |

**Output directory:** `employee_reports/`

**Exam readiness formula (from Phase 6.5 architecture doc):**
```
+25  all 4 lectures complete
+25  entrance exam score ≥ campaign pass_score
+50  all bias values < 15
```

---

## [2026-05-22] — Session 12: Phase 9 — Final Exam + Certificate

**Files Created:**
`exam/final_exam.py`, `exam/question_engine.py`, `exam/question_bank.json`

**Reason:**
Complete the learning pipeline. After the semester report confirms exam readiness,
employees sit an adaptive final exam. Passing issues a personalised certificate.

---

### `exam/question_bank.json`
Question bank keyed to the 4 bias axes (urgency / authority / reward / fear).
Each question: `question_id`, `bias_target`, `topic`, `difficulty`, `question`,
`options` (A–D), `correct`, `explanation`, `campaign_tags`.

---

### `exam/question_engine.py`
Adaptive question distribution:
- Selects questions weighted by the employee's bias profile from the entrance exam
- Employees who showed weakness in a bias axis receive more questions on that topic
- Difficulty scaled based on entrance exam score

---

### `exam/final_exam.py`
Final exam UI and flow:
- Presents MCQ questions from `question_engine`
- Scores attempt on completion
- Issues certificate automatically if pass threshold met
- Certificate includes: employee name, campaign, score, date, UUID `certificate_id`

### Complete Learning Pipeline

```
ENTRANCE EXAM (RPG)
  ↓
CYBER RESILIENCE REPORT
  ↓
LECTURES (assigned by bias weaknesses)
  ↓
SEMESTER REPORT (exam readiness gate)
  ↓
FINAL EXAM (adaptive MCQ)
  ↓
CERTIFICATE (issued on pass)
```

---

## [2026-05-22] — Architecture Update: Platform Pivot to Web

**No code changes — architecture direction update.**

**Previous architecture assumption:**
PHISHVERSE = standalone desktop RPG tool

**Revised architecture:**
PHISHVERSE = web platform with two portals

| Portal | Users | Purpose |
|---|---|---|
| Employee Portal | Employees | Full learning pipeline (login → exam → lectures → report → final exam → certificate) |
| Manager Portal | Security managers / HR | Campaign management, analytics dashboard, department reporting |

**Role of the RPG:**
The existing pygame RPG is the **Entrance Exam module** within the Employee Portal.
It is NOT the entire product. It is launched as a sub-component of the platform
and its results are read back into the portal via `analytics/results/{id}.json`.

**Technology direction:**
- Platform: Web (Flask backend + Jinja2 templates, or FastAPI + SPA frontend)
- RPG: launched via subprocess from Employee Portal, result read from JSON
- DB: SQLite (dev) → PostgreSQL (production)
- Auth: JWT tokens

This aligns with the architecture defined in `docs/EMPLOYEE_PORTAL.md` (Phase 6.5).

---

*Last updated: 2026-05-22*

---

## [2026-05-22] - Phase 5 + Phase 8

### Phase 5 - Employee Registration
**Files:** constants.py, ui.py (RegistrationScreen), main.py, analytics/result_store.py

- Added STATE_REGISTRATION between TITLE and CAMPAIGN_SELECT
- RegistrationScreen: 4-field animated form (Name, Employee ID, Department selector, Role)
  - TAB/UP/DOWN navigation, LEFT/RIGHT for department cycling, cursor blink, validation
  - Confirm button glows gold when required fields filled
- main.py: event loop now passes ev.unicode for text input
- result_store.py: save() now accepts employee:dict, saves to {employee_id}.json (overwrites)
- Schema updated: employee_name, employee_id, department, role, campaign, score, urgency/authority/reward/fear, risk, timestamp

### Phase 8 - Semester Report System
**Files:** constants.py, reporting/__init__.py, reporting/semester_report.py, reporting/employee_reports/, ui.py (SemesterReportScreen), main.py

- SemesterReport data class: maturity mapping, weakness detection, report generation, JSON persistence
- Maturity levels: Beginner (0-40) / Aware (41-60) / Secure (61-80) / Cyber Guardian (81-100)
- Weakness detection: ranks bias scores to identify primary + secondary attack vulnerabilities
- SemesterReportScreen: 8-section two-column pygame report card
  - Left: Entrance Exam / Maturity Index / Training Progress / Exam Status
  - Right: Behaviour Analysis / Weakness Detection / Recommendations / Learning Progress
  - Animated score count-up, pulsing exam status badge, progress bars
- State flow: REPORT -> SEMESTER_REPORT -> LECTURES -> DASHBOARD
- Reports saved: reporting/employee_reports/{EMPID}_report.json
- STATE_SEMESTER_REPORT added to constants.py

**Next:** Phase 9 - Lecture integration + Final Exam unlock

*Last updated: 2026-05-22*

---

## [2026-05-22] - Phase 9

### Phase 9 - Final Exam + Certification

**New files:**
- exam/__init__.py
- exam/question_bank.json  � 40 adaptive MCQ questions (10/category: urgency/authority/reward/fear)
- exam/question_engine.py  � adaptive selection (primary weakness gets 4/10 questions), static scorer
- exam/final_exam.py       � ExamEngine (save/load exam results) + Certificate (generate UUID cert, save)
- exam_results/            � {EMPID}_exam.json storage
- certificates/            � {EMPID}_certificate.json storage

**UI additions (ui.py):**
- FinalExamScreen: QUIZ/REVEALING/RESULTS phases; A/B/C/D keys + ENTER to confirm; 1.5s correct/wrong reveal; score circle + category breakdown
- CertificateScreen: animated gold border, slide-in reveal, employee name + score + maturity + cert ID + PV seal

**constants.py:** STATE_FINAL_EXAM, STATE_CERTIFICATE

**main.py wiring:**
- STATE_SEMESTER_REPORT ENTER routes to STATE_FINAL_EXAM (if exam_status==UNLOCKED) else STATE_LECTURES
- STATE_FINAL_EXAM PASS -> generate cert + STATE_CERTIFICATE; FAIL -> _exam_attempt++ + STATE_LECTURES
- STATE_CERTIFICATE dismiss -> quit
- QuestionEngine, ExamEngine, Certificate imported and initialised
- _exam_attempt resets on new game, increments on retake

**Full employee lifecycle:**
Registration -> Campaign -> Entrance Exam (RPG) -> Semester Report -> Final Exam -> Certificate

*Last updated: 2026-05-22*


---

## [2026-05-22] — Session 13: Phase 9.5 — AI Layer v1

**Files Created:**
`ai/__init__.py`, `ai/risk_predictor.py`, `ai/recommendation_engine.py`,
`ai/exam_generator.py`, `ai/ai_models/.gitkeep`, `ai/datasets/.gitkeep`,
`ai_results/.gitkeep`

**Files Modified:** `main.py`

**Reason:**
Insert an AI analysis step between the entrance exam and the lecture assignment.
The AI augments the rule-based scoring engine — adding confidence scoring,
ranked recommendations, and adaptive exam profiling. The rule-based score
remains source of truth; AI enriches without replacing any existing logic.

---

### Extended Flow

```
Entrance Exam (RPG) → Behaviour Dataset → AI Analysis
→ Lectures → Semester Report → Final Exam → Certificate
```

---

### `ai/__init__.py` — Orchestrator

run_ai_analysis(employee_id, risk_summary) -> dict
- Calls all three modules, assembles result, saves ai_results/{id}_ai.json
load_ai_result(employee_id) -> dict | None

---

### `ai/risk_predictor.py` — `RiskPredictor`

Rule: HIGH (score<40 or bias>=3), MEDIUM (score<70 or bias>=2), LOW (otherwise)
Confidence derived from distance to band boundary (range 0.50–0.95).
ML-ready: `train_model()` placeholder, `_extract_features()` isolated, `self._model` slot.
Handles both `urgency_bias` (RiskEngine) and `urgency` (ResultStore) field names.

Spec example verified: `authority_bias=4, score=30` → `HIGH, confidence=0.84` ✓

---

### `ai/recommendation_engine.py` — `RecommendationEngine`

`generate_plan(bias_profile)` → `ranked_lectures` + `training_plan` string.
Priority: CRITICAL ≥3, HIGH ≥2, MEDIUM ≥1, LOW =0.
Lectures ranked by bias score descending.

---

### `ai/exam_generator.py` — `ExamGenerator`

`generate_profile(bias_profile, employee_id)` → `topic_distribution` + `generated_topics`.
`BASE_PER_AXIS=2`, `TOTAL_QUESTIONS=10`, extra slots distributed proportionally by bias.
Verified: urgency=3, authority=2 → `{urgency:3, authority:3, reward:2, fear:2}` total=10 ✓

---

### ai_results/ schema

{employee, risk, confidence, weakness, recommendation, generated_topics}

---

### main.py wiring

Import: from ai import run_ai_analysis
In _end_game(), after LectureEngine.assign_lectures():
  if emp_id:
      run_ai_analysis(emp_id, self.risk.summary_dict())

AI runs after all rule-based systems. Does not gate or modify any existing flow.

---

**Tests Run:**
- All AI files + main.py pass py_compile
- HIGH/MEDIUM/LOW classification + confidence values verified
- Spec example: authority_bias=4, score=30 -> confidence=0.84
- ExamGenerator distribution verified

---

## [2026-05-22] Phase 10 — Flask Web Bridge

### Goal
Wire the Employee Portal "Launch PHISHVERSE" button to actually start the pygame RPG via a Flask backend instead of a mock.

### Architecture
```
employee.html (browser)
  └─ fetch POST http://localhost:5000/api/launch-game
       └─ backend/app.py (Flask + Flask-CORS)
            └─ subprocess.Popen([python, main.py], cwd=BASE_DIR)
                 └─ main.py (pygame RPG)
```

### Files Created
- `backend/app.py` — Flask app, endpoints: /api/launch-game, /api/game-status, /api/results/<id>, /api/ai-results/<id>
- `backend/requirements.txt` — flask>=3.0, flask-cors>=4.0

### Files Modified
- `employee.html` — confirmLaunch handler now calls real fetch instead of alert()

### Behaviour
- Already running: returns status=already_running (no second spawn)
- main.py not found: returns 500 with clear message
- subprocess launched: returns status=ok + PID
- fetch fails (backend not running): employee portal shows toast with fix instructions

### Tests Run
- python backend/app.py starts on port 5000
- POST /api/launch-game spawns main.py process
- GET /api/game-status returns running/idle
- CORS headers present (verified with curl)

---

## [2026-05-23] — Phase 11: Architecture Overhaul — Real Data Flow

**Files Modified:**
`main.py`, `backend/app.py`, `app.js`, `admin.html`, `employee.html`

**Files Created:**
`campaigns/general_campaign.json`

**Reason:**
Remove all static mock employees and make the game the single source of truth.
Employees register inside the pygame game, analytics are written to disk, and both
web portals read live JSON via Flask.

**Game changes (main.py):**
- `--campaign CAMPAIGN_ID` CLI arg: pre-loads a campaign before the game starts
- After employee registration, if `self._campaign` is already set, skip `STATE_CAMPAIGN_SELECT` → go directly to `STATE_EXPLORE`
- Campaign domain auto-restricts which events are shown in game

**Backend changes (backend/app.py):**
- `GET /api/employees` — scans analytics/results/*.json, returns normalised employee array
- `GET /api/campaigns` — lists all campaign JSONs from campaigns/
- `POST /api/campaigns` — accepts `{name, domain, duration_days}`, maps domain → enabled_events, writes to campaigns/<slug>.json
- `POST /api/launch-game` — now accepts optional `campaign_id` in body, appends `--campaign` to subprocess args
- `DOMAIN_EVENTS` map: Finance→[ceo_fraud, email_phishing], HR→[hr_message, voice_phishing], General→all 6

**app.js changes:**
- Removed `employees` array from `PV.MOCK`
- Added `PV.loadEmployees()` — fetches /api/employees, renders real records into #empBody
- Added `PV.loadOverviewEmployees()` — loads top-5 records into overview table
- Added `PV._screenHandlers` / `PV.onScreenShow(key, fn)` hook system
- Modified `PV.showScreen()` to fire registered screen-show handlers

**admin.html changes:**
- "Marc Kessler" → "Admin User" (sidebar footer)
- Overview employee table: hardcoded rows → `<tbody id="overviewEmpBody">` (real data)
- Employee full table: `empData` array and its rendering loop removed; uses `PV.loadEmployees()` via screen hook
- Campaign builder: `depSelect` → `domainSelect` (Finance/HR/General) with domain-change chip preview
- `deployBtn` now POSTs to `/api/campaigns` with `{name, domain, duration_days}`

**employee.html changes:**
- Sidebar footer: "AR / Anya Reyes" → "EM / Employee" with `id="sidebarAvatar/Name/Role"`
- Hero: "Welcome back, Anya." → "Welcome, Trainee."
- Registration screen: static values → `id="regName/Dept/Id"` placeholders
- Report screen: Added "Load My Results" card with Employee ID input + `/api/results/{id}` fetch
- AI debrief: static Anya text → generic text; populated dynamically on result load
- Certificate name: static "Anya Reyes" → `<div id="certName">—</div>`
- `_populateReport(data)` function: updates gauge, bias bars, AI debrief, certificate, sidebar from real result JSON
- `confirmLaunch`: first fetches `/api/campaigns` to get most recent campaign_id, passes it to /api/launch-game

**Issues Fixed:**
- None — clean implementation

**What Works:**
1. Manager creates campaign (Finance/HR/General) → writes to campaigns/*.json
2. Employee launches game from portal → Flask passes --campaign to subprocess
3. Employee registers IN game → plays domain-restricted events
4. Game writes analytics/results/{id}.json on completion
5. Employee portal "Load Results" reads real data → populates score, bias bars, AI debrief, certificate
6. Manager portal employee table reads all real records from analytics/results/

**Next Steps:**
- Phase 12: Multi-employee sessions (campaign assignment links)
- Phase 13: Annual renewal + expiry tracking

---

## [2026-05-23] — Phase 10: ML Risk Engine + Behaviour Analytics

**Files Created:**
-  — BehaviourTracker class; records click/cred/report/ignore per event
-  — DecisionTreeClassifier wrapper; train_model(), predict(), rule fallback
-  — 255 synthetic labelled rows (LOW/MEDIUM/HIGH)
-  — directory for trained .pkl artifact
-  — full design doc for ML + behaviour layer

**Files Modified:**
-  — added set_behaviour_tracker(); calls tracker.record() after each choice
-  — instantiates BehaviourTracker, wires to EventManager, passes to _end_game, passes to run_ai_analysis
-  — added behaviour: dict param; persists 8 behaviour fields in result JSON
-  — uses RiskModel instead of RiskPredictor; merges behaviour features; saves ml_source + behaviour summary
-  — /api/employees now includes click_rate, report_rate, clicked_link etc.; added /api/dept-stats endpoint
-  — ML Risk Prediction card (risk/confidence/weakness/source); Behaviour Metrics card with bars; updated _populateReport + _populateAI; loadResultsBtn now parallel-fetches /api/results + /api/ai-results
-  — employees table adds Click Rate + Report Rate columns (8 cols); heatmap screen adds Department Vulnerability real-data table with #deptStatsBody + #mostVulnerable
-  — loadEmployees updated for 8 cols with click/report rate coloring; added loadDeptStats(); heatmap screen registered via PV.onScreenShow

**What works:**
- BehaviourTracker records link clicks, credential submits, reports, vishing falls per gameplay session
- click_rate and report_rate computed per session
- RiskModel falls back gracefully to rules if no .pkl is trained
- Employee result JSON now includes all 8 behaviour fields
- Employee portal report screen shows ML card + behaviour metrics populated from real API
- Admin employees table has per-employee click/report rates
- Admin heatmap screen has department-level aggregated vulnerability table
- All doc files updated

**Train the ML model:**
    python -m ai.risk_model train

**Next steps:**
- Phase 12: Multi-employee campaign assignment links
- Phase 13: Annual renewal + expiry tracking

---

### Phase 11 — Campaigns Page: Real Data (2026-05-23)

**Problem:** Manager portal Campaigns page showed three hardcoded mock cards (Q2 Treasury Cohort, Reception Voice Drills, Marketing Brand Spoof) and two scheduled stubs (Eng USB Drop, HR Bonus Wave). These were static HTML and never reflected what was actually saved in `campaigns/`.

**Fix:**
- Replaced the entire `div.grid-three` in `#screen-campaigns` with an empty `id="campaignsGrid"` container.
- Added `PV.loadCampaigns()` to `app.js` — fetches `GET /api/campaigns`, renders one card per real campaign file, appends the "Author a new campaign" add-card at the end.
- Status derived from `employees.length`: 0 → CREATED (purple), >0 → RUNNING (cyan).
- Attack type chips mapped from `enabled_events` IDs to human labels via `_EVT_LABELS`.
- Empty state: "NO CAMPAIGNS CREATED YET" message displayed when folder is empty.
- Stat tag `id="campaignsStat"` updated dynamically: "N RUNNING · M TOTAL".
- Registered `PV.onScreenShow('campaigns', PV.loadCampaigns)` — auto-loads on sidebar navigation.
- Added handler-firing to the local `showScreen()` in `admin.html` so campaigns also reload after the deploy button redirects to the campaigns screen.
- `PV.loadCampaigns()` called on initial page load alongside `loadOverviewEmployees`.

**Files changed:** `app.js`, `admin.html`, `WEB_INTEGRATION.md`, `DEVLOG.md`, `STATUS.md`

**Single source of truth:** `campaigns/` folder via Flask `/api/campaigns`.
