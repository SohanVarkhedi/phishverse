# PHISHVERSE — Database Schema

> **Status:** Planning / Documentation only — no implementation yet.
> **Phase:** 6.5
> **Last updated:** 2026-05-22
> **Target DB:** SQLite (development) → PostgreSQL (production)

---

## Tables Overview

| Table | Purpose |
|-------|---------|
| `employees` | Core employee identity and campaign assignment |
| `campaigns` | Campaign definitions (mirrors `campaigns/*.json`) |
| `entrance_results` | RPG session results per employee per campaign |
| `lecture_progress` | Tracks which lecture modules each employee has completed |
| `lectures` | Lecture module definitions |
| `final_exam_attempts` | Each final exam attempt per employee |
| `certificates` | Issued certificates (one per employee per passed campaign) |

---

## Table Definitions

---

### `employees`

Stores every registered employee.

```sql
CREATE TABLE employees (
    employee_id   TEXT        PRIMARY KEY,       -- e.g. "EMP001", "hr_alice"
    name          TEXT        NOT NULL,
    department    TEXT        NOT NULL            -- "HR" | "Finance" | "IT" | "General"
                              CHECK (department IN ('HR','Finance','IT','General')),
    role          TEXT        DEFAULT '',         -- optional free-text job title
    email         TEXT        UNIQUE,             -- optional; used for certificate delivery
    campaign_id   TEXT        REFERENCES campaigns(campaign_id),
    password_hash TEXT        NOT NULL,           -- bcrypt hash
    created_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_campaign   ON employees(campaign_id);
```

**Notes:**
- `employee_id` is the primary key and is also used as the RPG session identifier.
- `campaign_id` is set at registration based on department; admins can override.
- `password_hash`: bcrypt with cost factor 12.
- `updated_at` should be maintained by an `ON UPDATE` trigger (or application layer).

---

### `campaigns`

Campaign definitions. Mirrors `campaigns/*.json` but persisted in the database
for relational integrity. Loaded from JSON on first run via a seed script.

```sql
CREATE TABLE campaigns (
    campaign_id    TEXT    PRIMARY KEY,           -- e.g. "hr_campaign"
    name           TEXT    NOT NULL,
    department     TEXT    NOT NULL,              -- target department
    description    TEXT    DEFAULT '',
    enabled_events TEXT    NOT NULL,              -- JSON array: ["email_phishing","hr_message"]
    pass_score     INTEGER NOT NULL DEFAULT 70,
    duration_days  INTEGER NOT NULL DEFAULT 7,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Notes:**
- `enabled_events` stored as a JSON string (SQLite compatible; use `JSONB` in PostgreSQL).
- This table is read-only from the portal; campaigns are managed via JSON files and a seed script.

---

### `entrance_results`

One row per employee per campaign attempt. Records the full RPG session result.

```sql
CREATE TABLE entrance_results (
    id             INTEGER   PRIMARY KEY AUTOINCREMENT,
    employee_id    TEXT      NOT NULL REFERENCES employees(employee_id),
    campaign_id    TEXT      NOT NULL REFERENCES campaigns(campaign_id),

    -- Scores
    score          INTEGER   NOT NULL DEFAULT 0,   -- 0–100
    passed         BOOLEAN   NOT NULL DEFAULT FALSE,

    -- Cognitive bias breakdown
    urgency        INTEGER   NOT NULL DEFAULT 0,
    authority      INTEGER   NOT NULL DEFAULT 0,
    reward         INTEGER   NOT NULL DEFAULT 0,
    fear           INTEGER   NOT NULL DEFAULT 0,

    -- Risk profile
    risk           TEXT      NOT NULL DEFAULT 'UNKNOWN'
                             CHECK (risk IN ('LOW','MEDIUM','HIGH','UNKNOWN')),
    weakest_area   TEXT      DEFAULT '',
    recommendation TEXT      DEFAULT '',

    -- Event completion
    mistakes              INTEGER NOT NULL DEFAULT 0,
    successful_reports    INTEGER NOT NULL DEFAULT 0,
    events_completed      INTEGER NOT NULL DEFAULT 0,
    events_total          INTEGER NOT NULL DEFAULT 0,

    -- Meta
    completed_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (employee_id, campaign_id)   -- one result per employee per campaign
);

CREATE INDEX idx_entrance_employee  ON entrance_results(employee_id);
CREATE INDEX idx_entrance_campaign  ON entrance_results(campaign_id);
CREATE INDEX idx_entrance_risk      ON entrance_results(risk);
```

**Notes:**
- The `UNIQUE (employee_id, campaign_id)` constraint enforces one entrance exam
  per campaign. Admin can delete the row to allow a re-attempt.
- Bias fields mirror the `analytics/results/{employee_id}.json` schema so the
  existing `ResultStore` output can be imported directly via a loader script.

---

### `lectures`

Defines the available lecture modules. Seeded once; not user-editable.

```sql
CREATE TABLE lectures (
    lecture_id    TEXT    PRIMARY KEY,       -- e.g. "LEC_URG"
    type          TEXT    NOT NULL,          -- "video" | "article" | "interactive"
    topic         TEXT    NOT NULL,          -- human-readable title
    bias_target   TEXT    NOT NULL           -- "urgency" | "authority" | "reward" | "fear"
                          CHECK (bias_target IN ('urgency','authority','reward','fear')),
    content_path  TEXT    DEFAULT '',        -- relative path to content file / URL
    order_index   INTEGER NOT NULL DEFAULT 0 -- display/recommended order
);
```

**Seed data:**

| lecture_id | type        | topic                           | bias_target |
|------------|-------------|----------------------------------|-------------|
| LEC_URG    | article     | Email Awareness & Urgency Attacks | urgency     |
| LEC_AUT    | article     | HR Fraud & CEO Impersonation      | authority   |
| LEC_REW    | article     | QR Phishing & Reward Baiting      | reward      |
| LEC_FEA    | article     | Vishing & Social Engineering      | fear        |

---

### `lecture_progress`

Tracks lecture completion per employee. One row per employee per lecture module.

```sql
CREATE TABLE lecture_progress (
    id           INTEGER   PRIMARY KEY AUTOINCREMENT,
    employee_id  TEXT      NOT NULL REFERENCES employees(employee_id),
    lecture_id   TEXT      NOT NULL REFERENCES lectures(lecture_id),
    completed    BOOLEAN   NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP,                         -- NULL until completed

    UNIQUE (employee_id, lecture_id)
);

CREATE INDEX idx_progress_employee ON lecture_progress(employee_id);
```

**Notes:**
- Rows are created (with `completed = FALSE`) when the employee is assigned their campaign.
- `completed_at` is set when the employee clicks "Mark as Complete."

---

### `final_exam_attempts`

Stores each attempt at the final MCQ exam. Multiple attempts are allowed up to
the campaign's configured maximum.

```sql
CREATE TABLE final_exam_attempts (
    id           INTEGER   PRIMARY KEY AUTOINCREMENT,
    employee_id  TEXT      NOT NULL REFERENCES employees(employee_id),
    campaign_id  TEXT      NOT NULL REFERENCES campaigns(campaign_id),

    attempt_no   INTEGER   NOT NULL DEFAULT 1,       -- 1, 2, 3 …
    score        INTEGER   NOT NULL DEFAULT 0,        -- 0–100
    status       TEXT      NOT NULL DEFAULT 'PENDING'
                           CHECK (status IN ('PENDING','PASSED','FAILED')),

    -- Question snapshot (which questions were asked, what was answered)
    questions_json TEXT    DEFAULT '[]',              -- JSON array of {question_id, chosen, correct}

    attempted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (employee_id, campaign_id, attempt_no)
);

CREATE INDEX idx_exam_employee ON final_exam_attempts(employee_id);
CREATE INDEX idx_exam_status   ON final_exam_attempts(status);
```

**Notes:**
- `questions_json` stores the full question snapshot so results are auditable
  even if the question bank is later updated.
- `attempt_no` is auto-incremented by the application before insert.

---

### `certificates`

One certificate per employee per passed campaign. Issued automatically when
`final_exam_attempts.status = 'PASSED'`.

```sql
CREATE TABLE certificates (
    id             INTEGER   PRIMARY KEY AUTOINCREMENT,
    employee_id    TEXT      NOT NULL REFERENCES employees(employee_id),
    campaign_id    TEXT      NOT NULL REFERENCES campaigns(campaign_id),
    certificate_id TEXT      NOT NULL UNIQUE,         -- UUID v4
    final_score    INTEGER   NOT NULL DEFAULT 0,
    level          TEXT      NOT NULL DEFAULT 'CYBER AWARE'
                             CHECK (level IN ('ADVANCED DEFENDER','CYBER AWARE','CYBER AWARE (Passed)')),
    issued_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (employee_id, campaign_id)   -- one certificate per employee per campaign
);

CREATE INDEX idx_cert_employee ON certificates(employee_id);
```

**Certification level logic:**

| Final Exam Score | Level |
|-----------------|-------|
| 90–100 | `ADVANCED DEFENDER` |
| 75–89  | `CYBER AWARE` |
| pass_score–74 | `CYBER AWARE (Passed)` |

---

## `training/exam_questions.json` — Question Bank Schema

The final exam draws questions from this file. It is not a database table —
it is a JSON file loaded at runtime and queried in memory.

**File location:** `training/exam_questions.json`

```json
{
  "version": "1.0",
  "questions": [
    {
      "question_id":  "q_urg_001",
      "bias_target":  "urgency",
      "topic":        "email_awareness",
      "difficulty":   "easy",
      "question":     "An email says your account will be locked in 1 hour unless you click a link. What should you do?",
      "options": {
        "A": "Click the link immediately to avoid being locked out.",
        "B": "Forward the email to your team.",
        "C": "Verify by logging into the official portal directly.",
        "D": "Reply to the email asking for more information."
      },
      "correct":      "C",
      "explanation":  "Urgency is a social engineering tactic. Always verify through official channels rather than clicking links in unsolicited emails.",
      "campaign_tags": ["hr_campaign", "employee_campaign"]
    }
  ]
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `question_id` | string | Unique ID — format: `q_{bias}_{nnn}` |
| `bias_target` | enum | `urgency` \| `authority` \| `reward` \| `fear` |
| `topic` | string | Maps to lecture module topic |
| `difficulty` | enum | `easy` \| `medium` \| `hard` |
| `question` | string | The question text |
| `options` | object | Keys A–D, each with answer text |
| `correct` | string | Correct option key (`"A"` – `"D"`) |
| `explanation` | string | Explanation shown after answering |
| `campaign_tags` | array | Which campaigns this question is relevant to |

**Minimum question bank sizes (recommendation):**

| Bias | Minimum | Target |
|------|---------|--------|
| urgency   | 5 | 15 |
| authority | 5 | 15 |
| reward    | 5 | 15 |
| fear      | 5 | 15 |

---

## Semester Report — Data Sources

The semester report screen pulls from multiple tables. No dedicated table needed —
it is a read-only view assembled at request time.

```
semester_report data = {
    employee         ← employees WHERE employee_id = ?
    campaign         ← campaigns WHERE campaign_id = employee.campaign_id
    entrance_result  ← entrance_results WHERE employee_id = ? AND campaign_id = ?
    lecture_progress ← lecture_progress WHERE employee_id = ?  (all 4 modules)
    exam_attempts    ← final_exam_attempts WHERE employee_id = ? ORDER BY attempt_no DESC
    certificate      ← certificates WHERE employee_id = ? (if exists)
}
```

**Exam readiness score (computed, not stored):**

```
readiness = 0
if all 4 lectures completed:              readiness += 25
if entrance_result.score >= pass_score:   readiness += 25
if all bias values < 15:                  readiness += 50
```

---

## Entity Relationship Summary

```
employees ──┬── entrance_results ── campaigns
            ├── lecture_progress ── lectures
            ├── final_exam_attempts ── campaigns
            └── certificates ── campaigns
```

---

## Migration Notes

- **Phase 6.5:** Schema defined; no tables created yet.
- **Phase 7 (implementation):** `portal/db.py` creates all tables via SQLAlchemy
  on first run; seed scripts populate `campaigns` and `lectures` from JSON files.
- **Production path:** SQLite → PostgreSQL. No schema changes needed; only the
  connection string and `enabled_events` column type (`TEXT` → `JSONB`) change.
