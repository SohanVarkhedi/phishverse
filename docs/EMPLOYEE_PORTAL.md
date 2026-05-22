# PHISHVERSE — Employee Portal Architecture

> **Status:** Planning / Documentation only — no implementation yet.
> **Phase:** 6.5
> **Last updated:** 2026-05-22

---

## Overview

The Employee Portal converts the PHISHVERSE RPG from a standalone game into a
structured cybersecurity learning pipeline. Each employee progresses through a
fixed sequence of stages: login → registration → campaign assignment → entrance
exam (the RPG) → AI lectures → semester report → final exam → certificate.

The existing RPG engine is **not modified**. It becomes the Entrance Exam stage.
All other stages are new layers built around it.

---

## Full Learning Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                  PHISHVERSE EMPLOYEE PORTAL                     │
└─────────────────────────────────────────────────────────────────┘

  LOGIN
  │  Authenticate with employee_id + password (or org SSO)
  ↓
  EMPLOYEE REGISTRATION
  │  Collect: name, department, role, email
  │  Assign campaign based on department
  ↓
  CAMPAIGN ASSIGNMENT
  │  Show assigned campaign details
  │  Employee reviews scope + objectives before starting
  ↓
  ENTRANCE EXAM  ←── PHISHVERSE RPG (existing engine, unchanged)
  │  Employee plays through campaign events
  │  Score, bias breakdown, and risk level recorded
  │  Results → entrance_results table
  ↓
  AI LECTURES  (4 targeted modules, served based on bias profile)
  │  urgency   → Email Awareness
  │  authority → HR & CEO Fraud Defence
  │  reward    → QR Phishing & Baiting
  │  fear      → Vishing & Social Engineering
  │  Progress tracked per lecture
  ↓
  SEMESTER REPORT
  │  Consolidated view: profile + bias chart + training progress
  │  Risk level + recommendation + exam readiness score
  ↓
  FINAL EXAM  (MCQ — question bank / AI-generated later)
  │  Tests knowledge from lecture modules
  │  Multiple attempts allowed (configurable per campaign)
  │  Pass/fail against campaign pass_score
  ↓
  CERTIFICATE
     Issued on final exam pass
     Contains: employee name, campaign, score, date, certificate_id
```

---

## Stage Descriptions

### Stage 1 — Login

- Employee authenticates with `employee_id` + password.
- Session token issued on success.
- Failed attempts logged.
- Future: SSO / SAML integration for enterprise deployments.

### Stage 2 — Employee Registration

- Collects: full name, department, role, email.
- If already registered, skip to current stage in pipeline.
- Department drives automatic campaign assignment (see Stage 3).

**Department → Default Campaign mapping:**

| Department | Default Campaign |
|------------|-----------------|
| HR         | hr_campaign     |
| Finance    | finance_campaign |
| IT         | employee_campaign (all events) |
| General    | employee_campaign |

### Stage 3 — Campaign Assignment

- Employee is shown their assigned campaign:
  - Name + description
  - Which threat scenarios are included
  - Pass score required
  - Estimated duration
- Employee confirms readiness before the entrance exam is unlocked.
- Admins can override the default campaign per employee.

### Stage 4 — Entrance Exam (PHISHVERSE RPG)

- Launches the existing PHISHVERSE pygame game engine.
- Campaign filter applied: only assigned campaign events are active.
- On game completion (`_end_game()` callback):
  - Score, bias breakdown (urgency/authority/reward/fear), risk level written
    to `entrance_results` table.
  - Result also written to `analytics/results/{employee_id}.json` (existing path).
- Entrance exam can only be taken once per campaign assignment.
  - Re-attempts only allowed if admin resets the record.

### Stage 5 — AI Lectures

Four lecture modules, each targeting a specific cognitive bias.
Module assignment is driven by the employee's bias profile from the entrance exam.

**Lecture Modules:**

| Module ID | Bias Target | Topic | Trigger Condition |
|-----------|-------------|-------|-------------------|
| `LEC_URG` | urgency   | Email Awareness & Urgency Attacks | Always shown |
| `LEC_AUT` | authority | HR Fraud & CEO Impersonation      | Always shown |
| `LEC_REW` | reward    | QR Phishing & Baiting             | Always shown |
| `LEC_FEA` | fear      | Vishing & Social Engineering      | Always shown |

All four modules are always assigned. In a future AI phase, high-bias modules
will be surfaced first and given extended content.

**Lecture content format (per module):**
- Explanation of the attack type
- Real-world examples
- Decision framework (how to recognise + respond)
- Short self-check quiz (3 questions, unscored)
- Mark-as-complete button

**Progress tracking:**
- Each module has a `completed` flag per employee.
- All 4 must be completed before the Final Exam is unlocked.

### Stage 6 — Semester Report

A read-only summary screen consolidating all pipeline data for the employee.

**Sections:**

1. **Employee Profile** — name, ID, department, role, campaign
2. **Entrance Exam Results** — score, pass/fail against campaign threshold
3. **Bias Chart** — bar chart: urgency / authority / reward / fear values
4. **Training Progress** — lecture completion status (0/4 → 4/4)
5. **Risk Level** — LOW / MEDIUM / HIGH with colour coding
6. **Recommendation** — personalised guidance based on bias profile
7. **Exam Readiness** — calculated score:
   - 25 pts: all lectures completed
   - 25 pts: entrance exam score ≥ pass_score
   - 50 pts: bias values all below threshold (< 15 each)
   - Max: 100 — shown as a readiness percentage

### Stage 7 — Final Exam

MCQ assessment drawn from `training/exam_questions.json`.

**Rules:**
- 10 questions per attempt (randomly sampled from question bank).
- Questions filtered to the employee's weak bias areas first (priority weighting).
- Pass mark = campaign `pass_score` (same threshold as entrance exam).
- Maximum 3 attempts per campaign assignment (configurable).
- Each attempt stored with timestamp, score, and pass/fail status.

**Question bank format:** see `training/exam_questions.json` (schema defined in `DB_SCHEMA.md`).

**Future (AI phase):** questions dynamically generated by Claude based on the
employee's specific wrong answers from the entrance exam.

### Stage 8 — Certificate

Issued automatically when the employee passes the final exam.

**Certificate contains:**
- Employee name + ID + department
- Campaign name
- Final exam score
- Issue date
- Unique `certificate_id` (UUID)
- PHISHVERSE certification level (LOW RISK / CYBER AWARE / ADVANCED DEFENDER)

**Certification levels (based on final exam score):**

| Score | Level |
|-------|-------|
| 90–100 | ADVANCED DEFENDER |
| 75–89  | CYBER AWARE |
| pass_score–74 | CYBER AWARE (Passed) |

---

## Technology Stack (Planned)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Portal backend | Flask (Python) | Lightweight; reuses existing Python ecosystem |
| Database | SQLite (dev) → PostgreSQL (prod) | SQLAlchemy ORM |
| Auth | JWT tokens | Simple session management |
| Frontend | Jinja2 templates + Tailwind CSS | Server-rendered; no React needed |
| RPG integration | subprocess / pygame embed | Launch RPG; read result from JSON |
| AI lectures | Claude API (future phase) | Prompt-based content generation |
| Final exam (AI) | Claude API (future phase) | MCQ generation from bias profile |
| Deployment | Docker → Gunicorn + Nginx | Standard Flask production stack |

---

## Integration with Existing RPG

The existing pygame RPG engine is launched as a **subprocess** from the portal.
When the game ends, it writes the result to `analytics/results/{employee_id}.json`.
The portal then reads this file and persists the data to the database.

```
Portal (Flask)
    │
    ├── POST /employee/entrance_exam/start
    │       └── subprocess.Popen(["python", "main.py", "--employee", emp_id, "--campaign", camp_id])
    │
    └── GET /employee/entrance_exam/result
            └── ResultStore.load(employee_id, campaign_id)  → reads JSON → saves to DB
```

No changes to `main.py` are required for this integration path.

---

## File Structure (Target)

```
PHISHVERSE/
├── portal/                     ← NEW: Flask portal application
│   ├── app.py                  ← Flask app factory
│   ├── auth.py                 ← Login / JWT
│   ├── routes/
│   │   ├── employee.py         ← All /employee/* routes
│   │   └── admin.py            ← Admin management routes
│   ├── models.py               ← SQLAlchemy models
│   ├── db.py                   ← Database connection + init
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── campaigns.html
│       ├── lectures.html
│       ├── semester_report.html
│       ├── final_exam.html
│       └── certificate.html
│
├── training/
│   └── exam_questions.json     ← Question bank (schema in DB_SCHEMA.md)
│
├── analytics/
│   ├── result_store.py         ← Existing (unchanged)
│   ├── campaign_loader.py      ← Existing (unchanged)
│   └── results/                ← Existing JSON output directory
│
└── docs/
    ├── EMPLOYEE_PORTAL.md      ← This file
    ├── DB_SCHEMA.md
    └── ROUTES.md
```

---

## Out of Scope (Phase 6.5)

The following are explicitly deferred:

- AI lecture content generation (Claude API)
- AI-generated final exam questions
- Admin web dashboard
- Multi-tenant / multi-organisation support
- SCORM export / LMS integration
- Real-time analytics streaming
- Email notifications
- Password reset flow
