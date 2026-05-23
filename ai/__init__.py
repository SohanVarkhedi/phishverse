"""
PHISHVERSE – ai package
Public interface: run_ai_analysis(employee_id, risk_summary, behaviour) -> dict

Pipeline:
  1. RiskModel (ML Decision Tree — falls back to rules if not trained)
  2. RecommendationEngine  (training plan)
  3. ExamGenerator         (topic profile)

Saves result to ai_results/{employee_id}_ai.json.
Rule engine (RiskEngine) remains source of truth for the main game score.
ML prediction augments — it adds confidence, weakness, and behaviour context.
"""

import json
from pathlib import Path

from ai.risk_model            import RiskModel
from ai.recommendation_engine import RecommendationEngine
from ai.exam_generator        import ExamGenerator

_RESULTS_DIR = Path("ai_results")
_ml_model    = RiskModel()   # loaded once at import; falls back to rules if no .pkl


def run_ai_analysis(employee_id: str, risk_summary: dict, behaviour: dict | None = None) -> dict:
    """
    Run the full AI analysis pipeline for one employee session.
    risk_summary  – from RiskEngine.summary_dict()
    behaviour     – from BehaviourTracker.to_dict() (optional)
    Saves ai_results/{employee_id}_ai.json and returns the result dict.
    """
    rec_engine = RecommendationEngine()
    exam_gen   = ExamGenerator()

    # Build feature dict: rule features + behaviour features
    features = dict(risk_summary)
    if behaviour:
        features.update({
            "clicked_link":      behaviour.get("clicked_link",      0),
            "credential_submit": behaviour.get("credential_submit",  0),
            "reported_attack":   behaviour.get("reported_attack",    0),
        })

    ml_pred = _ml_model.predict(features)
    rec     = rec_engine.generate_plan(risk_summary)
    exam_pr = exam_gen.generate_profile(risk_summary, employee_id)

    result = {
        "employee":    employee_id,
        # ML prediction
        "risk":        ml_pred["risk"],
        "confidence":  ml_pred["confidence"],
        "weakness":    ml_pred["weakness"],
        "ml_source":   ml_pred["source"],
        # Behaviour summary
        "behaviour": {
            "clicked_link":      (behaviour or {}).get("clicked_link",      0),
            "credential_submit": (behaviour or {}).get("credential_submit",  0),
            "reported_attack":   (behaviour or {}).get("reported_attack",    0),
            "ignored_attack":    (behaviour or {}).get("ignored_attack",     0),
            "click_rate":        (behaviour or {}).get("click_rate",         0.0),
            "report_rate":       (behaviour or {}).get("report_rate",        0.0),
        },
        # Recommendations
        "recommendation":   rec["training_plan"],
        "generated_topics": exam_pr["generated_topics"],
    }

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = _RESULTS_DIR / f"{employee_id}_ai.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[AI] Analysis saved → {path}  (source: {ml_pred['source']})")
    return result


def load_ai_result(employee_id: str) -> dict | None:
    """Load a previously saved AI result. Returns None if not found."""
    path = _RESULTS_DIR / f"{employee_id}_ai.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
