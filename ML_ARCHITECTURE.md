# PHISHVERSE — ML Architecture (Phase 10)

> ML Risk Engine + Behaviour Analytics layer.
> Rule engine (RiskEngine) remains source of truth for the game score.
> ML prediction augments — adds confidence, weakness context, and behaviour telemetry.

---

## Data Flow

```
Game (main.py)
    │
    ├── EventManager._handle_choice()
    │       │
    │       └── BehaviourTracker.record(event_id, trigger_type, choice, is_correct)
    │               clicked_link / credential_submit / reported_attack
    │               ignored_attack / correct_actions / wrong_actions
    │
    ├── Game._end_game()
    │       │
    │       ├── RiskEngine.summary_dict()          ← rule-based score + bias (SOURCE OF TRUTH)
    │       ├── BehaviourTracker.to_dict()          ← telemetry from gameplay
    │       │
    │       ├── ResultStore.save(behaviour=...)     → analytics/results/{id}.json  (merged)
    │       ├── BehaviourTracker.save(id)           → analytics/results/{id}_behavior.json
    │       └── run_ai_analysis(id, risk_summary, behaviour=...)
    │               │
    │               └── RiskModel.predict(features)
    │                       │
    │                       ├── [if trained]  sklearn DecisionTreeClassifier.predict_proba()
    │                       │                 → risk: HIGH/MEDIUM/LOW, confidence: 0.0–1.0
    │                       └── [fallback]    Rule-based bounds check
    │
    └── Saves → ai_results/{id}_ai.json
```

---

## Feature Set

| Feature             | Source                    | Role              |
|---------------------|---------------------------|-------------------|
| `score`             | RiskEngine.score          | Primary signal    |
| `urgency`           | RiskEngine.urgency_bias   | Bias dimension    |
| `authority`         | RiskEngine.authority_bias | Bias dimension    |
| `reward`            | RiskEngine.reward_bias    | Bias dimension    |
| `fear`              | RiskEngine.fear_bias      | Bias dimension    |
| `clicked_link`      | BehaviourTracker          | Action telemetry  |
| `credential_submit` | BehaviourTracker          | Action telemetry  |
| `reported_attack`   | BehaviourTracker          | Action telemetry  |

**Target:** `risk` — `LOW` | `MEDIUM` | `HIGH`

---

## ML Model (ai/risk_model.py)

```
Classifier:  sklearn.tree.DecisionTreeClassifier
  max_depth      = 6
  min_samples_leaf = 3
  random_state   = 42

Training data: ai/datasets/risk_dataset.csv
  255 labelled rows (75 LOW / 75 MEDIUM / 75 HIGH + 30 edge cases)

Trained model: ai/ai_models/risk_model.pkl

Train from CLI:
  python -m ai.risk_model train
```

**Output:**
```json
{
  "risk":       "HIGH",
  "confidence": 0.84,
  "weakness":   "authority",
  "source":     "ml_decision_tree"
}
```

**Fallback** (no .pkl): rule-based bounds — same boundaries as legacy RiskPredictor:
- `HIGH`   if score < 40 OR any bias >= 3
- `MEDIUM` if score < 70 OR any bias >= 2
- `LOW`    otherwise

---

## Behaviour Tracker (analytics/behaviour_tracker.py)

Classifies each event choice into a behaviour category:

| Event / trigger_type | Wrong choice → behaviour     |
|----------------------|------------------------------|
| `email_phishing`     | `clicked_link`               |
| `qr_phishing`        | `clicked_link`               |
| `ceo_fraud`          | `credential_submit`          |
| `voice_phishing`     | `vishing_fall` (ignored_attack) |
| `usb_drop` / others  | `wrong_action`               |
| Any correct choice   | `reported_attack`            |

**Derived rates:**
- `click_rate`  = clicked_link / (clicked_link + reported_attack)
- `report_rate` = correct_actions / (correct_actions + wrong_actions)

---

## Output Files

| File                                       | Content                                    |
|--------------------------------------------|--------------------------------------------|
| `analytics/results/{id}.json`              | Full result including behaviour fields     |
| `analytics/results/{id}_behavior.json`     | Granular behaviour + attack_history log    |
| `ai_results/{id}_ai.json`                  | ML risk, confidence, weakness, behaviour   |

---

## API Endpoints (Phase 10 additions)

| Method | Path              | Description                                          |
|--------|-------------------|------------------------------------------------------|
| GET    | `/api/employees`  | Now includes `click_rate`, `report_rate`, `clicked_link`, etc. |
| GET    | `/api/dept-stats` | Department aggregates: avg click rate, report rate, high-risk count, most vulnerable |

---

## Dashboard Additions

**Employee Portal — Report screen:**
- ML Risk Prediction card: predicted risk, confidence %, weakness axis
- Behaviour Metrics card: link clicks, cred submits, reports, click rate bar, report rate bar

**Manager Portal — Heatmap screen:**
- Department Vulnerability table (real data via `/api/dept-stats`)
- "Most Vulnerable" department chip (auto-identified)

**Manager Portal — Employees table:**
- Click Rate column (colour-coded: red ≥50%, amber ≥25%, green <25%)
- Report Rate column (colour-coded: green ≥75%, amber ≥40%, red <40%)

---

## Rule Engine vs ML — Responsibility Split

| Concern                    | Rule Engine (RiskEngine) | ML (RiskModel)       |
|----------------------------|--------------------------|----------------------|
| Game score                 | ✅ Source of truth        | ❌ Not used           |
| Pass/fail decision         | ✅ score ≥ pass_score     | ❌ Not used           |
| Bias tracking              | ✅ Exact counts           | Input feature only   |
| Risk label (game report)   | ✅ Primary                | Augments             |
| Risk label (AI result)     | Input only               | ✅ Predicted          |
| Confidence score           | ❌                        | ✅                    |
| Behaviour classification   | ❌                        | ✅ (BehaviourTracker) |
| Department aggregation     | ❌                        | ✅ (/api/dept-stats)  |

---

*Last updated: 2026-05-23*
