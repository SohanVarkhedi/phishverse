# PHISHVERSE — Architecture

> System design for the full PHISHVERSE platform: pygame RPG + Flask bridge + web portals.

---

## Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  Manager Portal  (admin.html)                                    │
│  · Create campaigns (Finance / HR / General domain)              │
│  · View real employee results from analytics/results/            │
│  · POST /api/campaigns → writes campaigns/<slug>.json            │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼  Flask API (backend/app.py, port 5000)
                          │
┌──────────────────────────────────────────────────────────────────┐
│  Employee Portal  (employee.html)                                │
│  · Fetches latest campaign_id from /api/campaigns                │
│  · POSTs to /api/launch-game → spawns game subprocess            │
│  · After game: "Load Results" fetches /api/results/{id}          │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼  subprocess.Popen([python, main.py, --campaign, id])
                          │
┌──────────────────────────────────────────────────────────────────┐
│  Game  (main.py — pygame RPG)  ← SOURCE OF TRUTH                │
│                                                                  │
│  Screens (state machine):                                        │
│    TITLE → REGISTRATION → (CAMPAIGN_SELECT) → EXPLORE           │
│    → REPORT → SEMESTER_REPORT → LECTURES → FINAL_EXAM → CERT    │
│                                                                  │
│  If --campaign arg present:                                      │
│    TITLE → REGISTRATION → EXPLORE  (skips CAMPAIGN_SELECT)      │
│                                                                  │
│  Employee registers IN game (Name / ID / Department / Role)      │
│  Domain-restricted events loaded from campaign JSON              │
│  Analytics saved on game end:                                    │
│    analytics/results/{employee_id}.json                          │
│    employee_reports/{employee_id}_report.json                    │
│    ai_results/{employee_id}_ai.json                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Domain → Events Mapping

| Domain  | Campaign JSON | Enabled Events |
|---------|--------------|----------------|
| Finance | `finance_campaign.json` | `ceo_fraud`, `email_phishing` |
| HR      | `hr_campaign.json`      | `hr_message`, `voice_phishing` |
| General | `general_campaign.json` | All 6 events |

---

## Flask API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/launch-game` | Launch `main.py` subprocess. Accepts optional `campaign_id`. |
| GET  | `/api/game-status` | Returns `{status: running\|idle\|exited}`. |
| GET  | `/api/employees`   | Returns all result JSONs from `analytics/results/`. |
| GET  | `/api/results/<id>` | Single employee result JSON. |
| GET  | `/api/ai-results/<id>` | AI analysis JSON for employee. |
| GET  | `/api/campaigns`   | Lists all campaign JSONs from `campaigns/`. |
| POST | `/api/campaigns`   | Create new campaign: `{name, domain, duration_days}`. |

---

## File Structure

```
PHISHVERSE/
├── main.py               — Game entry point (pygame RPG)
├── constants.py          — Shared constants + state names
├── events.py             — Event definitions + campaign filter
├── risk_engine.py        — Bias tracking (urgency/authority/reward/fear)
├── ui.py                 — All game screens (Registration, HUD, Report, etc.)
│
├── analytics/
│   ├── campaign_loader.py — Loads + validates campaign JSON
│   └── result_store.py    — Saves/loads employee results
│
├── analytics/results/    — One JSON per employee (source of truth for portals)
├── campaigns/            — Campaign definitions (Finance/HR/General)
├── ai_results/           — AI analysis output per employee
├── employee_reports/     — Semester report JSONs
│
├── backend/
│   ├── app.py            — Flask bridge (7 endpoints)
│   └── requirements.txt  — flask>=3.0, flask-cors>=4.0
│
├── index.html            — Public landing page
├── employee.html         — Employee training portal
├── admin.html            — Manager dashboard
├── styles.css            — Shared stylesheet
└── app.js                — Shared JS utilities (PV namespace)
```

---

## Data Flow Summary

1. **Manager** creates campaign in admin.html → POST `/api/campaigns` → `campaigns/<slug>.json` written
2. **Employee** opens employee.html → clicks "Launch PHISHVERSE"
3. **Portal** fetches latest campaign from `/api/campaigns` → POST `/api/launch-game {campaign_id}`
4. **Flask** spawns `python main.py --campaign finance_campaign`
5. **Game** shows: Title → Registration (employee enters own data) → Explore (domain-restricted)
6. **Game** ends → writes `analytics/results/{employee_id}.json`
7. **Employee portal** Report screen: enter Employee ID → fetch `/api/results/{id}` → populate results
8. **Manager portal** Employees screen: fetch `/api/employees` → render real roster table

---

*Last updated: 2026-05-23*
