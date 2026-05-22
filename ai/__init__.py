"""
PHISHVERSE – ai package
Public interface: run_ai_analysis(employee_id, risk_summary) -> dict

Orchestrates all three AI modules and saves the result to
ai_results/{employee_id}_ai.json.
"""

import json
from pathlib import Path

from ai.risk_predictor        import RiskPredictor
from ai.recommendation_engine import RecommendationEngine
from ai.exam_generator        import ExamGenerator

_RESULTS_DIR = Path("ai_results")


def run_ai_analysis(employee_id: str, risk_summary: dict) -> dict:
    """
    Run the full AI analysis pipeline for one employee session.
    Accepts risk_summary from RiskEngine.summary_dict().
    Saves ai_results/{employee_id}_ai.json and returns the result dict.
    """
    predictor  = RiskPredictor()
    rec_engine = RecommendationEngine()
    exam_gen   = ExamGenerator()

    risk_pred  = predictor.predict(risk_summary)
    rec        = rec_engine.generate_plan(risk_summary)
    exam_prof  = exam_gen.generate_profile(risk_summary, employee_id)

    result = {
        "employee":         employee_id,
        "risk":             risk_pred["risk"],
        "confidence":       risk_pred["confidence"],
        "weakness":         risk_pred["weakness"],
        "recommendation":   rec["training_plan"],
        "generated_topics": exam_prof["generated_topics"],
    }

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = _RESULTS_DIR / f"{employee_id}_ai.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[AI] Analysis saved → {path}")
    return result


def load_ai_result(employee_id: str) -> dict | None:
    """Load a previously saved AI result. Returns None if not found."""
    path = _RESULTS_DIR / f"{employee_id}_ai.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
