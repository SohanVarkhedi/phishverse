# PHISHVERSE — Product Roadmap

> This document tracks the full product vision from RPG prototype to
> enterprise cybersecurity training platform.

---

## 🎯 CURRENT — v1.x: RPG Entrance Exam Module

**Status:** Feature complete — awaiting web platform integration
**Platform:** Desktop (Windows/Linux/Mac) — Python + pygame

> **Architecture note:** The pygame RPG is the **Entrance Exam module** within
> the PHISHVERSE web platform. It is not the entire product — it is one stage
> in the employee learning pipeline, launched as a subprocess from the
> Employee Portal. Results are read back via `analytics/results/{id}.json`.

### What's Built (v1.x — complete)
- Full pygame RPG with 6 phishing scenario types
- 4-act narrative story progression
- Risk engine with bias-tracking analytics
- Employee registration (name, ID, department, role)
- Campaign system (HR / Finance / General staff)
- Cyber Resilience Report (entrance exam result)
- Lecture system: 4 modules assigned by bias weakness
- Semester report with exam readiness scoring
- Final exam with adaptive MCQ + certificate issuance

### v1.x Milestones
| Version | Description | Status |
|---------|-------------|--------|
| v1.0 | Initial RPG prototype | ✅ Done |
| v1.0.1 | Dialog layout bug fix | ✅ Done |
| v1.1 | 4-act story expansion | ✅ Done |
| v1.2 | Project restructure + docs | ✅ Done |
| v1.3 | Campaign system | ✅ Done |
| v1.4 | Employee registration | ✅ Done |
| v1.5 | Analytics dashboard + dropdown | ✅ Done |
| v1.6 | Lecture system | ✅ Done |
| v1.7 | Semester report | ✅ Done |
| v1.8 | Final exam + certificate | ✅ Done |
| v1.9 | AI Layer v1 — rule-based, ML-ready | ✅ Done |

---

## 🔜 NEXT — v2.0: Web Platform

**Status:** Planned
**Platform:** Web (Flask + SQLite/PostgreSQL)

Transform the completed RPG module into a full web-based cybersecurity training
platform with two separate portals.

### Platform Architecture

```
PHISHVERSE Web Platform
├── Employee Portal
│   ├── Login / Registration
│   ├── Campaign assignment
│   ├── Entrance Exam (launches pygame RPG as subprocess)
│   ├── Lectures (assigned by bias weakness)
│   ├── Semester Report
│   ├── Final Exam (adaptive MCQ)
│   └── Certificate
│
└── Manager Portal
    ├── Login (admin/manager role)
    ├── Campaign creation + management
    ├── Employee roster + progress tracking
    ├── Department risk analytics dashboard
    └── Export reports (CSV / PDF)
```

### Employee Portal (v2.0)
- Web app: Flask + Jinja2 templates (or FastAPI + SPA)
- Launches RPG via `subprocess.Popen()` from the exam stage
- Reads result from `analytics/results/{id}.json` on completion
- All 8 pipeline stages implemented as web routes
- JWT authentication, bcrypt passwords

### Manager Portal (v2.1)
- Campaign CRUD: create, assign to departments, set pass scores
- Live completion tracking per employee/campaign
- Department risk heatmap (aggregated bias scores)
- Analytics views wired to existing `ResultStore` + `RiskEngine`

### v2.x Milestones
| Version | Description |
|---------|-------------|
| v2.0 | Employee Portal (Flask scaffold + exam pipeline) |
| v2.1 | Manager Portal (campaigns + analytics) |
| v2.2 | Scenario library (50+ events, difficulty levels) |
| v2.3 | User accounts + session persistence |
| v2.4 | Email notifications + campaign scheduling |

---

## 🔮 FUTURE — v3.0: AI Analytics Layer

**Status:** Planned (post-v2)
**Platform:** Cloud-native

Adaptive intelligence layer that personalises training per user.

### Components

#### 3.1 Adaptive Learning Engine (`ai/`)
- Analyse each user's decision history to build a "vulnerability fingerprint"
- Auto-adjust scenario difficulty based on past performance
- Recommend specific training modules for identified weak areas
- Learning path sequencing (prerequisite-aware)

#### 3.2 Phishing Scenario Generator
- LLM-powered scenario generation (GPT-4 / open-source model)
- Generate novel phishing emails, QR campaigns, vishing scripts
- Localise scenarios to user's industry/role/region
- Red-team simulation mode (generate real-looking but sandboxed samples)

#### 3.3 Department Risk Analytics
- Heatmap: which departments are most vulnerable to which attack vectors
- Time-series risk trends (is awareness improving?)
- Peer benchmarking (how does your team compare to industry baseline?)
- Board-level executive report generation

### v3.x Milestones
| Version | Description |
|---------|-------------|
| v3.0 | Adaptive learning engine (bias-aware difficulty) |
| v3.1 | AI scenario generator (LLM integration) |
| v3.2 | Department analytics + heatmaps |
| v3.3 | Predictive risk scoring |

---

## 🌐 FUTURE — Enterprise Deployment

### Multi-User Infrastructure
- User authentication (OAuth2 / SAML for SSO)
- Role-based access control (Admin / Manager / Employee)
- Org hierarchy support (company → department → team → individual)
- Audit log for compliance (ISO 27001, NIST CSF)

### Cloud Deployment Path
```
Phase 1: Single-server Docker container
Phase 2: Docker Compose (app + db + cache)
Phase 3: Kubernetes cluster (HA, auto-scaling)
Phase 4: Managed cloud (AWS ECS / GCP Cloud Run)
```

### LMS Integration
- SCORM 1.2 / xAPI (Tin Can) export for existing LMS platforms
- Moodle plugin
- Microsoft Teams integration (training reminders, results in Teams)
- Slack bot for micro-training sessions

### Compliance & Certifications
- Generate ISO 27001 training evidence
- GDPR-compliant data handling (EU users)
- SOC 2 readiness reporting
- Custom certificate generation per completion

---

## Architecture Evolution

```
v1.x (RPG module — done)       v2.x (Web platform)            v3.x (AI)
─────────────────────          ──────────────────────         ──────────────────
  main.py  (RPG game)            portal/                        ai/
  risk_engine.py      ──────►    ├── employee/  (8 stages)      ├── adaptive.py
  training/           ──────►    ├── manager/   (dashboard)     ├── generator.py
  exam/               ──────►    ├── db.py                      └── fingerprint.py
  analytics/          ──────►    └── models.py
  campaigns/          ──────►    analytics/  (REST API)
                                 training/   (scenario library)
```

**The RPG (`main.py`) is unchanged in v2.x** — it becomes a subprocess called
from `portal/employee/routes.py` at the Entrance Exam stage.

---

*Last updated: 2026-05-22*

---

## Current Status (2026-05-22)

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Dialog UI fix | ✅ DONE |
| 2 | RPG story expansion | ✅ DONE |
| 3 | Campaign system | ✅ DONE |
| 4 | Campaign gameplay integration | ✅ DONE |
| 5 | Employee registration | ✅ DONE |
| 6 | Analytics dashboard + dropdown | ✅ DONE |
| 6.5 | Employee portal architecture docs | ✅ DONE |
| 7 | Lecture system | ✅ DONE |
| 8 | Semester report | ✅ DONE |
| 9 | Final exam + certificate | ✅ DONE |
| 9.5 | AI Layer v1 (rule-based + ML-ready) | ✅ DONE |
| 10 | Web platform — Employee Portal | 📋 NEXT |
| 11 | Web platform — Manager Portal | 📋 PLANNED |
| 12 | AI adaptive layer | 📋 PLANNED |
