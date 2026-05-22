"""
PHISHVERSE – ai/recommendation_engine.py
Generates adaptive lecture recommendations from an employee bias profile.

Bias → lecture mapping mirrors training/lecture_engine.py.
Recommendations are ranked by bias severity and labelled CRITICAL / HIGH /
MEDIUM / LOW so the semester report can surface the most urgent modules first.

Priority thresholds:
  CRITICAL  bias >= 3   (repeated failures — immediate intervention)
  HIGH      bias >= 2   (clear vulnerability — priority training)
  MEDIUM    bias >= 1   (one mistake — standard module assignment)
  LOW       bias == 0   (refresher / preventive)
"""

_BIAS_KEYS = ("urgency", "authority", "reward", "fear")

_BIAS_TO_LECTURE = {
    "urgency":   ("email_awareness",     "Email Phishing Awareness"),
    "authority": ("ceo_fraud_awareness", "CEO Fraud & HR Impersonation"),
    "reward":    ("qr_awareness",        "QR Phishing & Reward Baiting"),
    "fear":      ("vishing_awareness",   "Vishing & Fear Manipulation"),
}


def _bias(data: dict, key: str) -> int:
    return int(data.get(f"{key}_bias", data.get(key, 0)))


class RecommendationEngine:
    """
    Produces a ranked, prioritised training plan from an employee bias profile.
    """

    def generate_plan(self, bias_profile: dict) -> dict:
        """
        Input:  bias_profile — RiskEngine.summary_dict() or ResultStore schema
        Output:
        {
            "primary_weakness": str,
            "ranked_lectures": [
                {"lecture_id": str, "title": str, "priority": str, "bias_score": int}
            ],
            "training_plan": str,
        }
        """
        biases = {k: _bias(bias_profile, k) for k in _BIAS_KEYS}
        ranked = sorted(biases.items(), key=lambda kv: kv[1], reverse=True)

        # Primary weakness = highest-bias axis; fall back to urgency on a clean run
        primary = ranked[0][0] if ranked and ranked[0][1] > 0 else "urgency"

        ranked_lectures = []
        for bias, score in ranked:
            lecture_id, title = _BIAS_TO_LECTURE[bias]
            if   score >= 3: priority = "CRITICAL"
            elif score >= 2: priority = "HIGH"
            elif score >= 1: priority = "MEDIUM"
            else:            priority = "LOW"
            ranked_lectures.append({
                "lecture_id":  lecture_id,
                "title":       title,
                "priority":    priority,
                "bias_score":  score,
            })

        # Plain-text training plan for report display ────────────────────────
        critical = [l["title"] for l in ranked_lectures if l["priority"] == "CRITICAL"]
        high     = [l["title"] for l in ranked_lectures if l["priority"] == "HIGH"]
        if critical:
            plan = f"Immediate training required: {', '.join(critical)}."
        elif high:
            plan = f"Priority training recommended: {', '.join(high)}."
        else:
            plan = "Comprehensive cybersecurity awareness training recommended."

        return {
            "primary_weakness": primary,
            "ranked_lectures":  ranked_lectures,
            "training_plan":    plan,
        }
