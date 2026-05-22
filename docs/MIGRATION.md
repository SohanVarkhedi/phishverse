# PHISHVERSE — Migration Plan

> **Status:** PLANNED — no files have been moved yet.
> This document defines the target layout and migration steps for v1.2.
> Approved by: pending
> Last updated: 2026-05-22

---

## Target Folder Structure

```
PHISHVERSE/
│
├── game/                          ← All pygame RPG modules
│   ├── __init__.py
│   ├── main.py
│   ├── constants.py
│   ├── dialogue.py
│   ├── event_manager.py
│   ├── events.py
│   ├── map.py
│   ├── npc.py
│   ├── player.py
│   ├── raycaster.py
│   ├── story.py
│   ├── tiles.py
│   ├── ui.py
│   └── assets/                   ← moved from root assets/
│       ├── audio/
│       ├── sprites/
│       └── tiles/
│
├── analytics/                     ← Risk scoring + reporting API
│   ├── __init__.py
│   ├── risk_engine.py            ← copied from root (import updated)
│   ├── report_generator.py       ← extracted from report.py (non-pygame logic)
│   └── api.py                    ← NEW: FastAPI wrapper (v2.0)
│
├── dashboard/                     ← Admin web interface (v2.1)
│   ├── app.py                    ← Flask / FastAPI entry point
│   ├── templates/
│   ├── static/
│   └── README.md
│
├── training/                      ← Scenario library and campaign runner
│   ├── __init__.py
│   ├── scenarios/
│   │   ├── events.json           ← moved from data/events.json
│   │   └── events3d.json
│   ├── loader.py                 ← extracted from events.py (non-tile logic)
│   └── campaigns/                ← NEW: campaign definitions (v2.2)
│
├── ai/                            ← Adaptive learning engine (v3.0)
│   ├── __init__.py
│   ├── adaptive.py
│   ├── generator.py
│   └── fingerprint.py
│
├── docs/                          ← All documentation
│   ├── MIGRATION.md              ← this file
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── run_game.py                    ← NEW: root-level launcher (replaces running game/main.py directly)
├── requirements.txt
├── README.md
├── DEVLOG.md
├── STATUS.md
├── ROADMAP.md
└── CHANGELOG.md
```

---

## Module Reuse Analysis

### 🟢 HIGH REUSE — Move as-is, update imports

| Module | From | To | Notes |
|--------|------|----|-------|
| `risk_engine.py` | root | `analytics/` | Zero pygame dependency. Pure Python. No import changes needed internally. |
| `story.py` | root | `game/` | Zero pygame dependency. Pure Python state machine. |
| `constants.py` | root | `game/` | May become a shared config if analytics/ needs screen dims (unlikely). |
| `data/events.json` | `data/` | `training/scenarios/` | Update `EVENT_FILE` path in `constants.py`. |

### 🟡 MEDIUM REUSE — Move with minor refactoring

| Module | From | To | Notes |
|--------|------|----|-------|
| `events.py` | root | `game/` | `EventDatabase` has tile-based lookup that's game-specific. Extract pure JSON loader to `training/loader.py` for reuse. |
| `report.py` | root | Split | Pygame render logic → `game/report.py`. Pure data formatting → `analytics/report_generator.py`. |
| `event_manager.py` | root | `game/` | Tightly coupled to `DialogBox` and `RiskEngine` — stays in game/ but imports will need updating. |

### 🔴 GAME-ONLY — Move to `game/`, no reuse outside

| Module | Notes |
|--------|-------|
| `main.py` | Game loop — game/ only |
| `dialogue.py` | pygame dialog rendering |
| `map.py` | pygame tile map |
| `npc.py` | pygame NPC sprites |
| `player.py` | pygame player movement |
| `raycaster.py` | pygame 3D renderer |
| `tiles.py` | pygame tile surfaces |
| `ui.py` | pygame HUD/menus |

---

## Migration Steps (v1.2 — Pending)

> ⚠️ Do NOT proceed until this plan is approved and tests are in place.

### Step 1 — Game folder migration
```
1. Create game/__init__.py (empty)
2. Move all game-only modules to game/
3. Move assets/ to game/assets/
4. Update all imports within game/ to relative: from . import constants
5. Create run_game.py at root: import game.main; game.main.Game().run()
6. Test: python run_game.py — must launch identically to python main.py
```

### Step 2 — Analytics folder
```
1. Copy risk_engine.py to analytics/risk_engine.py
2. Update game/ imports: from analytics.risk_engine import RiskEngine
3. Create analytics/__init__.py
4. Extract non-pygame report logic to analytics/report_generator.py
5. Test: python -c "from analytics.risk_engine import RiskEngine; print('OK')"
```

### Step 3 — Training folder
```
1. Move data/ to training/scenarios/
2. Update EVENT_FILE constant: "training/scenarios/events.json"
3. Create training/loader.py (pure JSON scenario loader, no tile logic)
4. Test: python -c "from training.loader import load_scenarios; print(load_scenarios())"
```

### Step 4 — Root cleanup
```
1. Remove old flat .py files from root (after all imports verified)
2. Update README.md with new launch instructions
3. Update DEVLOG.md with migration completion entry
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Circular imports after restructure | Medium | High | Use absolute imports throughout; no `from . import *` |
| `EVENT_FILE` path breaks | High | Medium | Update constant immediately in Step 3 |
| `pygame.font.match_font` path changes | Low | Low | Font lookup is OS-level, unaffected by folder structure |
| Asset path references break | Medium | Medium | Use `Path(__file__).parent` for relative asset loading |

---

*Last updated: 2026-05-22 | Status: PLANNED — awaiting approval*
