# PHISHVERSE — Portal Route Structure

> **Status:** Planning / Documentation only — no implementation yet.
> **Phase:** 6.5
> **Last updated:** 2026-05-22
> **Base URL:** `/employee/`

---

## Overview

All employee-facing routes live under the `/employee/` prefix.
Admin routes (future) live under `/admin/`.
All routes require authentication except `/employee/login` and `/employee/register`.

---

## Authentication

- **Method:** JWT Bearer token in `Authorization` header, or session cookie for
  browser-rendered pages.
- **Token lifetime:** 8 hours (configurable).
- **Unauthenticated requests:** Redirect to `/employee/login` (browser) or
  return `401 Unauthorized` (API).

---

## Route Table

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/POST | `/employee/login` | ✗ | Login form / authenticate |
| POST | `/employee/logout` | ✓ | Invalidate session |
| GET/POST | `/employee/register` | ✗ | Registration form / create account |
| GET | `/employee/campaigns` | ✓ | View assigned campaign |
| GET | `/employee/campaigns/{campaign_id}` | ✓ | Campaign detail view |
| GET | `/employee/entrance_exam` | ✓ | Entrance exam landing page |
| POST | `/employee/entrance_exam/start` | ✓ | Launch RPG subprocess |
| GET | `/employee/entrance_exam/result` | ✓ | Read + persist RPG result |
| GET | `/employee/lectures` | ✓ | All lecture modules + progress |
| GET | `/employee/lectures/{lecture_id}` | ✓ | Single lecture content view |
| POST | `/employee/lectures/{lecture_id}/complete` | ✓ | Mark lecture complete |
| GET | `/employee/semester_report` | ✓ | Full semester report view |
| GET | `/employee/final_exam` | ✓ | Final exam landing page |
| POST | `/employee/final_exam/start` | ✓ | Begin new exam attempt |
| POST | `/employee/final_exam/submit` | ✓ | Submit answers, calculate score |
| GET | `/employee/certificate` | ✓ | Certificate view (if earned) |
| GET | `/employee/certificate/{certificate_id}` | ✗ | Public certificate verification |

---

## Route Specifications

---

### `GET /employee/login`

Returns the login HTML page.

**Response:** `200 OK` — HTML form with `employee_id` + `password` fields.

---

### `POST /employee/login`

Authenticates the employee.

**Request body (form or JSON):**
```json
{
  "employee_id": "EMP001",
  "password":    "plain_text_password"
}
```

**Success response:** `200 OK`
```json
{
  "token":       "eyJ...",
  "employee_id": "EMP001",
  "name":        "Alice Smith",
  "stage":       "lectures"
}
```

The `stage` field tells the frontend which pipeline stage the employee is currently
at so the UI can redirect to the correct page:

| `stage` value | Redirect |
|--------------|----------|
| `registration` | `/employee/register` |
| `campaigns` | `/employee/campaigns` |
| `entrance_exam` | `/employee/entrance_exam` |
| `lectures` | `/employee/lectures` |
| `semester_report` | `/employee/semester_report` |
| `final_exam` | `/employee/final_exam` |
| `certificate` | `/employee/certificate` |

**Error responses:**
- `401 Unauthorized` — wrong credentials
- `403 Forbidden` — account locked (future)

---

### `POST /employee/logout`

Invalidates the session token.

**Response:** `200 OK` `{ "message": "Logged out." }`

---

### `GET /employee/register`

Returns the registration HTML page (mirrors the pygame registration screen).

---

### `POST /employee/register`

Creates a new employee record.

**Request body:**
```json
{
  "employee_id": "EMP001",
  "name":        "Alice Smith",
  "department":  "HR",
  "role":        "HR Coordinator",
  "email":       "alice@company.com",
  "password":    "plain_text_password"
}
```

**Validation rules:**
- `employee_id` — required, unique, alphanumeric + underscores, max 32 chars
- `name` — required, max 64 chars
- `department` — required, must be one of: `HR`, `Finance`, `IT`, `General`
- `role` — optional, max 64 chars
- `email` — optional, must be valid email format if provided
- `password` — required, min 8 chars

**Success:** `201 Created`
```json
{
  "employee_id":  "EMP001",
  "campaign_id":  "hr_campaign",
  "next_stage":   "campaigns"
}
```

Campaign assignment is automatic based on department (see `EMPLOYEE_PORTAL.md`
§ Stage 3 — Campaign Assignment).

**Error:** `422 Unprocessable Entity` — validation errors
```json
{
  "errors": {
    "employee_id": "Employee ID already exists.",
    "password":    "Password must be at least 8 characters."
  }
}
```

---

### `GET /employee/campaigns`

Shows the employee's assigned campaign details.

**Response:** `200 OK`
```json
{
  "campaign_id":     "hr_campaign",
  "name":            "HR Phishing Awareness",
  "department":      "HR",
  "description":     "Targeted training for HR staff...",
  "enabled_events":  ["email_phishing", "hr_message", "voice_phishing"],
  "pass_score":      80,
  "duration_days":   7,
  "entrance_exam_available": true,
  "entrance_exam_completed": false
}
```

---

### `GET /employee/campaigns/{campaign_id}`

Detail view of a specific campaign (used to confirm before starting exam).

**Response:** Same as above, plus:
```json
{
  "events_detail": [
    { "id": "email_phishing", "title": "Password Reset Alert", "location": "Work Area" }
  ]
}
```

---

### `GET /employee/entrance_exam`

Landing page for the entrance exam. Shows instructions and a "Start Exam" button.

**Guard:** If `entrance_results` row already exists for this employee + campaign,
return `{ "completed": true, "score": 82, "redirect": "/employee/lectures" }`.

---

### `POST /employee/entrance_exam/start`

Launches the PHISHVERSE RPG as a subprocess for the employee's campaign.

**Guard:** Returns `409 Conflict` if entrance exam already completed.

**Implementation note (not yet built):**
```python
subprocess.Popen([
    "python", "main.py",
    "--employee", employee_id,
    "--campaign", campaign_id,
])
```

**Response:** `202 Accepted` `{ "message": "Exam started. Complete the game to record your result." }`

The portal polls `/employee/entrance_exam/result` to detect completion.

---

### `GET /employee/entrance_exam/result`

Reads the RPG result file and persists it to `entrance_results`.

**Logic:**
1. Check `analytics/results/{employee_id}.json` exists and is newer than exam start time.
2. Parse JSON; validate required fields.
3. INSERT into `entrance_results` (or return existing row if already persisted).
4. Return result summary.

**Response:** `200 OK`
```json
{
  "score":     78,
  "passed":    false,
  "risk":      "MEDIUM",
  "urgency":   12,
  "authority": 18,
  "reward":    5,
  "fear":      8,
  "next_stage": "lectures"
}
```

**Not ready:** `202 Accepted` `{ "message": "Result not yet available." }`

---

### `GET /employee/lectures`

Returns all 4 lecture modules with the employee's completion status.

**Response:** `200 OK`
```json
{
  "lectures": [
    {
      "lecture_id":    "LEC_URG",
      "topic":         "Email Awareness & Urgency Attacks",
      "bias_target":   "urgency",
      "completed":     true,
      "completed_at":  "2026-05-22T10:14:00Z"
    },
    {
      "lecture_id":    "LEC_AUT",
      "topic":         "HR Fraud & CEO Impersonation",
      "bias_target":   "authority",
      "completed":     false,
      "completed_at":  null
    }
  ],
  "all_completed": false,
  "final_exam_unlocked": false
}
```

---

### `GET /employee/lectures/{lecture_id}`

Returns the content of a specific lecture module.

**Response:** `200 OK`
```json
{
  "lecture_id":  "LEC_URG",
  "topic":       "Email Awareness & Urgency Attacks",
  "bias_target": "urgency",
  "content":     "...(HTML or markdown string)...",
  "self_check":  [
    {
      "question": "What is a common sign of a phishing email?",
      "options":  ["Urgent deadline", "Company logo", "Signed by CEO", "All of the above"],
      "correct":  3
    }
  ],
  "completed": false
}
```

---

### `POST /employee/lectures/{lecture_id}/complete`

Marks a lecture module as complete for the authenticated employee.

**Guard:** Returns `200 OK` (idempotent) if already marked complete.

**Response:** `200 OK`
```json
{
  "lecture_id":    "LEC_URG",
  "completed_at":  "2026-05-22T10:14:00Z",
  "all_completed": false,
  "remaining":     3
}
```

---

### `GET /employee/semester_report`

Returns the full semester report for the employee.

**Response:** `200 OK`
```json
{
  "employee": {
    "employee_id": "EMP001",
    "name":        "Alice Smith",
    "department":  "HR",
    "role":        "HR Coordinator",
    "campaign":    "HR Phishing Awareness"
  },
  "entrance_exam": {
    "score":     78,
    "passed":    false,
    "risk":      "MEDIUM",
    "urgency":   12,
    "authority": 18,
    "reward":    5,
    "fear":      8,
    "weakest_area":   "Authority Phishing",
    "recommendation": "Focus on verifying HR requests directly..."
  },
  "lecture_progress": {
    "completed": 2,
    "total":     4,
    "modules": [
      { "lecture_id": "LEC_URG", "completed": true },
      { "lecture_id": "LEC_AUT", "completed": true },
      { "lecture_id": "LEC_REW", "completed": false },
      { "lecture_id": "LEC_FEA", "completed": false }
    ]
  },
  "exam_readiness": {
    "score":       50,
    "breakdown": {
      "lectures_complete": 0,
      "entrance_passed":   25,
      "bias_under_threshold": 25
    }
  },
  "final_exam": {
    "attempts":     0,
    "max_attempts": 3,
    "best_score":   null,
    "status":       "NOT_STARTED"
  },
  "certificate": null
}
```

---

### `GET /employee/final_exam`

Landing page showing exam rules, attempt count, and a "Start Exam" button.

**Guard:** Returns `403 Forbidden` if not all lectures are completed.

**Response:** `200 OK`
```json
{
  "unlocked":     true,
  "attempts_used": 1,
  "max_attempts":  3,
  "pass_score":    80,
  "question_count": 10,
  "best_score":    72,
  "status":        "FAILED"
}
```

---

### `POST /employee/final_exam/start`

Begins a new exam attempt. Samples 10 questions from the question bank.

**Guard:**
- `403 Forbidden` if lectures not all completed.
- `409 Conflict` if max attempts exhausted.
- `409 Conflict` if an attempt is already in progress.

**Response:** `200 OK`
```json
{
  "attempt_no":   2,
  "question_count": 10,
  "questions": [
    {
      "question_id": "q_urg_001",
      "question":    "An email says your account will be locked in 1 hour...",
      "options": {
        "A": "Click the link immediately.",
        "B": "Forward to your team.",
        "C": "Verify through official portal.",
        "D": "Reply to ask for more info."
      }
    }
  ]
}
```

Note: `correct` and `explanation` fields are **not** returned in this response —
they are revealed after submission.

---

### `POST /employee/final_exam/submit`

Submits answers for the current attempt and calculates the score.

**Request body:**
```json
{
  "attempt_no": 2,
  "answers": {
    "q_urg_001": "C",
    "q_aut_003": "B"
  }
}
```

**Response:** `200 OK`
```json
{
  "attempt_no":  2,
  "score":       90,
  "passed":      true,
  "status":      "PASSED",
  "results": [
    {
      "question_id": "q_urg_001",
      "chosen":      "C",
      "correct":     "C",
      "is_correct":  true,
      "explanation": "Always verify through official channels..."
    }
  ],
  "certificate_issued": true,
  "certificate_id":     "a3f9c2d1-..."
}
```

If `passed = true`, a `certificates` row is automatically created.

---

### `GET /employee/certificate`

Returns the employee's certificate (if earned).

**Response (earned):** `200 OK`
```json
{
  "certificate_id": "a3f9c2d1-4b5e-4f9a-8c2d-1e3f5a7b9c0d",
  "employee_name":  "Alice Smith",
  "employee_id":    "EMP001",
  "department":     "HR",
  "campaign":       "HR Phishing Awareness",
  "final_score":    90,
  "level":          "ADVANCED DEFENDER",
  "issued_at":      "2026-05-22T14:30:00Z"
}
```

**Response (not earned):** `404 Not Found`
```json
{ "error": "Certificate not yet issued. Complete the final exam to earn your certificate." }
```

---

### `GET /employee/certificate/{certificate_id}`

Public endpoint — no authentication required.
Used for certificate verification (e.g., employer scans a QR code).

**Response (valid):** `200 OK` — same structure as `GET /employee/certificate`

**Response (invalid):** `404 Not Found`
```json
{ "error": "Certificate not found." }
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error":   "Short error description.",
  "detail":  "Optional longer explanation.",
  "code":    "MACHINE_READABLE_CODE"
}
```

**Common error codes:**

| Code | HTTP Status | Meaning |
|------|------------|---------|
| `UNAUTHENTICATED` | 401 | No valid session token |
| `FORBIDDEN` | 403 | Action not allowed at current pipeline stage |
| `NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | Resource already exists / duplicate action |
| `VALIDATION_ERROR` | 422 | Request body failed validation |
| `EXAM_LOCKED` | 403 | Lectures not complete; exam is locked |
| `MAX_ATTEMPTS` | 409 | No more exam attempts available |
| `ALREADY_COMPLETED` | 409 | Stage already completed; cannot re-do |

---

## Pipeline Stage Guard Logic

Each route checks which stage the employee is currently at and blocks access
to stages they have not yet reached.

```
Stage order:  registration → campaigns → entrance_exam → lectures
              → semester_report → final_exam → certificate

Guard rule: if requested_stage > current_stage → 403 FORBIDDEN
```

The `current_stage` is derived at request time by querying the database:

```python
def get_current_stage(employee_id):
    if not employee_registered(employee_id):        return "registration"
    if not entrance_result_exists(employee_id):     return "entrance_exam"
    if not all_lectures_complete(employee_id):      return "lectures"
    if not final_exam_passed(employee_id):          return "final_exam"
    return "certificate"
```

---

## Future Routes (Not Phase 6.5)

| Path | Description |
|------|-------------|
| `GET  /admin/employees` | List all employees and their pipeline stage |
| `GET  /admin/campaigns` | Manage campaign assignments |
| `POST /admin/employees/{id}/reset` | Reset a stage for re-attempt |
| `GET  /admin/analytics` | Aggregate dashboard (replaces pygame dashboard) |
| `POST /employee/lectures/{id}/generate` | AI-generate lecture content (Phase 8+) |
| `POST /employee/final_exam/generate` | AI-generate questions from bias profile (Phase 8+) |
