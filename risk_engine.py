"""
PHISHVERSE – risk_engine.py
Tracks player stats and computes cybersecurity risk profile.
"""

from constants import MAX_SCORE, MIN_SCORE


class RiskEngine:
    """
    Maintains all player statistics and applies penalties / rewards.
    Also generates qualitative risk assessment for the final report.
    """

    def __init__(self):
        self.score             = 100
        self.urgency_bias      = 0
        self.authority_bias    = 0
        self.reward_bias       = 0
        self.fear_bias         = 0
        self.mistakes          = 0
        self.successful_reports = 0
        self.threats_completed  = 0
        self.total_threats      = 6    # total events in game
        self._history: list[dict] = []  # audit log

    # ── Mutation ─────────────────────────────────────────────────────────────

    def apply_penalty(self, event_id: str, choice: str, penalty: dict):
        delta = {
            "event":           event_id,
            "choice":          choice,
            "score_delta":     penalty.get("score", 0),
            "urgency_delta":   penalty.get("urgency_bias", 0),
            "authority_delta": penalty.get("authority_bias", 0),
            "reward_delta":    penalty.get("reward_bias", 0),
            "fear_delta":      penalty.get("fear_bias", 0),
        }
        self.score          = max(MIN_SCORE, min(MAX_SCORE, self.score + delta["score_delta"]))
        self.urgency_bias   += delta["urgency_delta"]
        self.authority_bias += delta["authority_delta"]
        self.reward_bias    += delta["reward_delta"]
        self.fear_bias      += delta["fear_delta"]
        self.mistakes       += penalty.get("mistakes", 0)
        self._history.append(delta)

    def record_success(self, event_id: str, choice: str):
        self.successful_reports += 1
        self.threats_completed  += 1
        self._history.append({
            "event": event_id,
            "choice": choice,
            "outcome": "SUCCESS",
        })

    def record_wrong(self, event_id: str, choice: str):
        self.threats_completed += 1
        self._history.append({
            "event": event_id,
            "choice": choice,
            "outcome": "FAIL",
        })

    # ── Assessment ───────────────────────────────────────────────────────────

    @property
    def risk_level(self) -> str:
        if self.score >= 80:
            return "LOW"
        elif self.score >= 55:
            return "MEDIUM"
        else:
            return "HIGH"

    @property
    def weakest_area(self) -> str:
        biases = {
            "Urgency Attacks":    self.urgency_bias,
            "Authority Phishing": self.authority_bias,
            "Reward Manipulation": self.reward_bias,
            "Fear-Based Attacks": self.fear_bias,
        }
        return max(biases, key=biases.get)

    @property
    def recommendation(self) -> str:
        level = self.risk_level
        if level == "LOW":
            return "Excellent awareness! Keep up regular cyber training."
        elif level == "MEDIUM":
            return f"Moderate risk. Focus on: {self.weakest_area}."
        else:
            return "High risk! Immediate cyber-awareness training recommended."

    def summary_dict(self) -> dict:
        return {
            "score":              self.score,
            "urgency_bias":       self.urgency_bias,
            "authority_bias":     self.authority_bias,
            "reward_bias":        self.reward_bias,
            "fear_bias":          self.fear_bias,
            "mistakes":           self.mistakes,
            "successful_reports": self.successful_reports,
            "threats_completed":  self.threats_completed,
            "total_threats":      self.total_threats,
            "risk_level":         self.risk_level,
            "weakest_area":       self.weakest_area,
            "recommendation":     self.recommendation,
        }
