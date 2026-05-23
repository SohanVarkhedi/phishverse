# PHISHVERSE — AI-Driven Cybersecurity Awareness Platform

PHISHVERSE is an **AI-driven phishing simulation and cybersecurity awareness platform** that transforms traditional awareness training into **experiential learning**.

Instead of static slides and seminars, employees experience phishing attacks through a **Pokémon-inspired RPG simulation**, behavioural analytics, adaptive learning and enterprise dashboards.

> We do not teach cybersecurity through reading.  
> We teach it through simulation.

---

# Architecture Overview

```text
Manager Portal
      ↓
Campaign Creation
      ↓
Employee Assignment
      ↓
PHISHVERSE RPG (Entrance Exam)
      ↓
Behaviour Analytics
      ↓
AI + ML Risk Analysis
      ↓
Adaptive Training
      ↓
Semester Report
      ↓
Final Exam
      ↓
Certification
```

---

# Features

## Employee Portal

Employee lifecycle:

```text
Registration
↓
Campaign Selection
↓
Entrance Exam (PHISHVERSE RPG)
↓
AI Analysis
↓
Lectures
↓
Semester Report
↓
Final MCQ
↓
Cyber Resilience Certificate
```

### Modules

- Employee Registration
- Campaign Assignment
- RPG Simulation
- AI Training Engine
- Semester Report
- Final Assessment
- Certification

---

## Manager Portal

Organization dashboard for monitoring awareness cycles.

Features:

- Campaign Management
- Employee Monitoring
- Department Risk Heatmaps
- AI Reports
- MCQ Analytics
- Threat Intelligence
- Campaign Analytics
- Organizational Vulnerability Tracking

---

# PHISHVERSE RPG — Entrance Exam

The RPG acts as the **behaviour assessment engine**.

Employees enter an office environment and experience realistic phishing simulations.

Map:

```text
┌─────────────────────────────────────────┐
│ ENTRY / OUTSIDE                         │
├─────────────────────────────────────────┤
│ RECEPTION                               │
├─────────────────┬───────────────────────┤
│ WORK AREA       │ HR ROOM               │
├─────────────────┼───────────────────────┤
│ CAFETERIA       │ MEETING ROOM          │
├─────────────────┴───────────────────────┤
│ IT SUPPORT DESK                         │
└─────────────────────────────────────────┘
```

---

# Attack Simulations

| Event | Attack Type | Behaviour Target |
|--------|------------|------------------|
| Email Phishing | Urgency Manipulation | Urgency Bias |
| QR Phishing | Reward Manipulation | Reward Bias |
| USB Drop Attack | Curiosity Bait | Reward / Curiosity |
| HR Authority Attack | Fake Authority | Authority Bias |
| Vishing | Fear + Authority | Fear Bias |
| CEO Fraud / BEC | Executive Manipulation | Authority Bias |

---

# Behaviour Analytics

PHISHVERSE tracks employee behaviour rather than only correctness.

Metrics:

```text
score

urgency_bias

authority_bias

reward_bias

fear_bias

clicked_link

credential_submit

reported_attack

ignored_attack
```

---

# AI + ML Layer

Current AI stack:

## Rule-Based Behaviour Engine

Adaptive recommendations:

```text
reward high
↓
QR awareness

authority high
↓
CEO fraud awareness
```

---

## ML Risk Prediction

Model:

```python
DecisionTreeClassifier
```

Input:

```text
score

urgency

authority

reward

fear

clicked_link

credential_submit

reported_attack

campaign

department
```

Output:

```text
LOW

MEDIUM

HIGH
```

Example:

```json
{
 "risk":"HIGH",
 "confidence":0.84,
 "weakness":"authority"
}
```

---

# Semester Report

Generated after training cycle completion.

Contains:

- Cyber Score
- Behaviour Profile
- Risk Level
- Weakness Detection
- AI Recommendation
- Training Progress
- Cyber Maturity Index

---

# Final Exam + Certification

Employees undergo adaptive MCQ assessment.

Pass:

Cyber Resilience Certificate generated.

Fail:

Training cycle repeats.

---

# Project Structure

```text
PHISHVERSE/

game/

ai/
 └── risk_model.py

analytics/
 └── behaviour_tracker.py

training/

exam/

reporting/

backend/

manager/

campaigns/

employee_reports/

exam_results/

ai_results/

website/
 ├── index.html
 ├── employee.html
 ├── admin.html
 ├── styles.css
 └── app.js

docs/

README.md
requirements.txt
```

---

# Tech Stack

Frontend:

- HTML
- CSS
- JavaScript

Game Engine:

- Python
- Pygame

Backend:

- Flask

AI / ML:

- Scikit-learn
- Decision Trees

Data:

- JSON
- CSV

---

# Installation

Clone:

```bash
git clone https://github.com/<username>/phishverse.git

cd phishverse
```

Install:

```bash
pip install -r requirements.txt
```

Run backend:

```bash
python backend/app.py
```

Run website:

```bash
python -m http.server 8000
```

Launch:

```text
http://localhost:8000
```

---

# Problem Statement Coverage

✅ Configurable phishing campaigns

✅ AI-powered analytics

✅ Department risk dashboards

✅ Automated awareness workflows

✅ Secure campaign monitoring

✅ Adaptive training engine

✅ ML risk prediction

---

# Future Roadmap

- Live Campaign Assignment
- Game → Portal Synchronization
- Department Intelligence
- Multi-Cycle Learning
- Cloud Deployment
- Advanced ML Models
- Enterprise Integration

---

# Team

PHISHVERSE Team

Track:

Cybersecurity & Blockchain

Problem Statement:

AI-Driven Phishing Attack Simulation and Cyber Awareness Training Platform
