"""
PHISHVERSE – ai/risk_model.py
Decision Tree ML risk predictor.  Augments the rule engine; does not replace it.

Train from CLI:
    python -m ai.risk_model train

Predict (programmatic):
    model = RiskModel()
    result = model.predict({"score": 55, "urgency": 2, ..., "clicked_link": 1})
    # {"risk": "MEDIUM", "confidence": 0.78, "weakness": "urgency", "source": "ml_decision_tree"}

Features used:
    score, urgency, authority, reward, fear,
    clicked_link, credential_submit, reported_attack

Target: risk  (LOW | MEDIUM | HIGH)
"""

import csv
import pickle
from pathlib import Path

_DATASETS_DIR = Path(__file__).parent / "datasets"
_MODELS_DIR   = Path(__file__).parent / "ai_models"
_MODEL_PATH   = _MODELS_DIR / "risk_model.pkl"

_FEATURE_KEYS = [
    "score", "urgency", "authority", "reward", "fear",
    "clicked_link", "credential_submit", "reported_attack",
]
_BIAS_KEYS = ["urgency", "authority", "reward", "fear"]


class RiskModel:
    """
    sklearn DecisionTreeClassifier wrapper.
    Auto-loads a persisted model on construction; falls back to rule-based
    prediction if no trained model is found.
    """

    def __init__(self):
        self._clf = self._load_model()

    # ── Model lifecycle ───────────────────────────────────────────────────────

    @classmethod
    def train_model(cls) -> "RiskModel":
        """
        Train from ai/datasets/risk_dataset.csv and persist to ai/ai_models/risk_model.pkl.
        Returns a ready-to-use RiskModel instance with the trained classifier loaded.
        """
        try:
            from sklearn.tree import DecisionTreeClassifier
        except ImportError as exc:
            raise ImportError("scikit-learn required: pip install scikit-learn") from exc

        dataset_path = _DATASETS_DIR / "risk_dataset.csv"
        if not dataset_path.exists():
            raise FileNotFoundError(f"Training dataset not found: {dataset_path}")

        rows: list[dict] = []
        with open(dataset_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)

        if not rows:
            raise ValueError("Dataset is empty.")

        X = [[int(float(r.get(k, 0))) for k in _FEATURE_KEYS] for r in rows]
        y = [r["risk"].strip().upper()                          for r in rows]

        clf = DecisionTreeClassifier(max_depth=6, min_samples_leaf=3, random_state=42)
        clf.fit(X, y)

        _MODELS_DIR.mkdir(parents=True, exist_ok=True)
        with open(_MODEL_PATH, "wb") as f:
            pickle.dump(clf, f)

        print(f"[RiskModel] Trained on {len(X)} samples -> {_MODEL_PATH}")
        m = cls()
        m._clf = clf
        return m

    @staticmethod
    def _load_model():
        if not _MODEL_PATH.exists():
            return None
        try:
            with open(_MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"[RiskModel] Could not load model: {e}")
            return None

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict(self, features: dict) -> dict:
        """
        Predict risk from a feature dict.
        Accepts RiskEngine.summary_dict() extended with behaviour fields.

        Returns:
            {risk, confidence, weakness, source}
        """
        vec = [int(features.get(k, 0)) for k in _FEATURE_KEYS]

        if self._clf is not None:
            try:
                proba  = self._clf.predict_proba([vec])[0]
                label  = self._clf.classes_[proba.argmax()]
                conf   = round(float(proba.max()), 2)
                source = "ml_decision_tree"
            except Exception:
                return self._rule_fallback(features)
        else:
            return self._rule_fallback(features)

        biases   = {k: int(features.get(k, 0)) for k in _BIAS_KEYS}
        weakness = max(biases, key=biases.get) if any(v > 0 for v in biases.values()) else "none"

        return {"risk": str(label), "confidence": conf, "weakness": weakness, "source": source}

    # ── Rule fallback ─────────────────────────────────────────────────────────

    @staticmethod
    def _rule_fallback(features: dict) -> dict:
        """Rule-based prediction used when no trained model is available."""
        score   = int(features.get("score", 0))
        biases  = {k: int(features.get(k, 0)) for k in _BIAS_KEYS}
        max_b   = max(biases.values())
        total_b = sum(biases.values())
        weakness = max(biases, key=biases.get) if any(v > 0 for v in biases.values()) else "none"

        if score < 40 or max_b >= 3:
            risk = "HIGH"
            conf = round(min(0.92, 0.60 + total_b * 0.05 + max(0, (40 - score) * 0.004)), 2)
        elif score < 70 or max_b >= 2:
            risk = "MEDIUM"
            conf = round(min(0.85, 0.55 + total_b * 0.04 + max(0, (70 - score) * 0.002)), 2)
        else:
            risk = "LOW"
            conf = round(min(0.90, 0.65 + (score - 70) * 0.006), 2)

        return {"risk": risk, "confidence": conf, "weakness": weakness, "source": "rule_fallback"}


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        RiskModel.train_model()
        print("[RiskModel] Training complete.")
    else:
        print("Usage: python -m ai.risk_model train")
