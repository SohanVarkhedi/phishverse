"""
PHISHVERSE – ai/risk_predictor.py
Rule-based risk predictor with ML-ready architecture.

Classification rules:
  HIGH:   score < 40  OR  any single bias >= 3
  MEDIUM: score < 70  OR  any single bias >= 2
  LOW:    otherwise

Confidence is derived from how firmly the score + bias values sit
inside one band. It rises when an employee is far from a boundary
(very low score, very high bias, or perfect run) and falls near
decision thresholds where genuine ambiguity exists.

ML upgrade path:
  1. Collect labelled rows in ai/datasets/risk_labels.csv
     (columns: score, urgency, authority, reward, fear, risk_label)
  2. Implement train_model() — load CSV, fit sklearn RandomForest,
     persist to ai/ai_models/risk_model.pkl
  3. Replace the rule block in predict() with:
       proba = self._model.predict_proba([features])[0]
       label = self._model.classes_[proba.argmax()]
       conf  = round(float(proba.max()), 2)

Example output:
  {"risk": "HIGH", "confidence": 0.84, "weakness": "authority"}
"""

_BIAS_KEYS = ("urgency", "authority", "reward", "fear")


def _bias(data: dict, key: str) -> int:
    """Read a bias count, handling both 'urgency_bias' and 'urgency' field names."""
    return int(data.get(f"{key}_bias", data.get(key, 0)))


class RiskPredictor:
    """
    Rule-based explainable risk predictor.
    Public interface: predict(employee_data) → {risk, confidence, weakness}
    self._model is reserved for a future trained classifier.
    """

    def __init__(self):
        self._model = None   # future: sklearn / torch model loaded by train_model()

    # ── ML-ready placeholder ──────────────────────────────────────────────────

    def train_model(self, dataset_path: str | None = None):
        """
        ML upgrade slot — currently a no-op.
        Future: load dataset_path CSV, train classifier, set self._model.
        """
        pass

    # ── Feature extraction ────────────────────────────────────────────────────

    def _extract_features(self, data: dict) -> dict:
        """Normalise raw input into a clean feature dict."""
        return {
            "score":     int(data.get("score", 0)),
            "urgency":   _bias(data, "urgency"),
            "authority": _bias(data, "authority"),
            "reward":    _bias(data, "reward"),
            "fear":      _bias(data, "fear"),
        }

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict(self, employee_data: dict) -> dict:
        """
        Predict risk level from employee data.
        Accepts RiskEngine.summary_dict() or ResultStore schema.
        Returns: {"risk": "LOW"|"MEDIUM"|"HIGH", "confidence": float, "weakness": str}
        """
        f       = self._extract_features(employee_data)
        score   = f["score"]
        biases  = {k: f[k] for k in _BIAS_KEYS}
        max_b   = max(biases.values())
        total_b = sum(biases.values())

        has_bias = any(v > 0 for v in biases.values())
        weakness = max(biases, key=biases.get) if has_bias else "none"

        # Rule-based classification ──────────────────────────────────────────
        if score < 40 or max_b >= 3:
            risk = "HIGH"
            # Confidence rises with lower score and higher accumulated bias
            conf = 0.60 + (total_b * 0.05) + max(0, (40 - score) * 0.004)
            confidence = round(min(0.95, conf), 2)

        elif score < 70 or max_b >= 2:
            risk = "MEDIUM"
            conf = 0.55 + (total_b * 0.04) + max(0, (70 - score) * 0.002)
            confidence = round(min(0.88, conf), 2)

        else:
            risk = "LOW"
            # Higher score above 70 → stronger confidence in LOW classification
            conf = 0.65 + (score - 70) * 0.006
            confidence = round(min(0.92, conf), 2)

        return {
            "risk":       risk,
            "confidence": confidence,
            "weakness":   weakness,
        }
