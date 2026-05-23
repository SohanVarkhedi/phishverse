"""
PHISHVERSE – analytics/behaviour_tracker.py
Tracks granular player behaviour during event resolution.

Usage (wired into EventManager automatically):
    tracker = BehaviourTracker()
    tracker.record(event_id, trigger_type, choice, is_correct)
    tracker.save(employee_id)  # writes analytics/results/{id}_behavior.json
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

# Events where a wrong click maps to "clicked a link / scanned QR"
_LINK_CLICK_EVENTS = {"email_phishing", "qr_phishing"}
# Events where wrong choice = submitting credentials
_CRED_EVENTS       = {"ceo_fraud"}
# Events triggered via phone (voice/vishing)
_PHONE_EVENTS      = {"voice_phishing"}


class BehaviourTracker:
    """
    Accumulates behavioural signals during one gameplay session.
    Attach to EventManager; call record() after each choice resolves.
    """

    def __init__(self):
        self.clicked_link      = 0
        self.credential_submit = 0
        self.reported_attack   = 0
        self.ignored_attack    = 0
        self.correct_actions   = 0
        self.wrong_actions     = 0
        self.attack_history: list[dict] = []

    # ── Core record ──────────────────────────────────────────────────────────

    def record(self, event_id: str, trigger_type: str, choice: str, is_correct: bool):
        """
        Classify and record the outcome of one event choice.
        trigger_type: "computer" | "poster" | "usb" | "phone"
        """
        entry: dict = {
            "event_id":     event_id,
            "trigger_type": trigger_type,
            "choice":       choice,
            "outcome":      "CORRECT" if is_correct else "WRONG",
        }

        if is_correct:
            self.reported_attack += 1
            self.correct_actions += 1
            entry["behaviour"] = "reported"
        else:
            self.wrong_actions += 1
            if event_id in _LINK_CLICK_EVENTS or trigger_type in ("computer", "poster"):
                self.clicked_link += 1
                entry["behaviour"] = "clicked_link"
            elif event_id in _CRED_EVENTS:
                self.credential_submit += 1
                entry["behaviour"] = "credential_submit"
            elif event_id in _PHONE_EVENTS or trigger_type == "phone":
                self.ignored_attack += 1
                entry["behaviour"] = "vishing_fall"
            else:
                entry["behaviour"] = "wrong_action"

        self.attack_history.append(entry)

    # ── Derived rates ─────────────────────────────────────────────────────────

    @property
    def click_rate(self) -> float:
        """Proportion of events where user clicked the malicious link/QR."""
        total = self.clicked_link + self.reported_attack
        return round(self.clicked_link / total, 2) if total > 0 else 0.0

    @property
    def report_rate(self) -> float:
        """Proportion of events where user made the correct (safe) choice."""
        total = self.correct_actions + self.wrong_actions
        return round(self.correct_actions / total, 2) if total > 0 else 0.0

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "clicked_link":      self.clicked_link,
            "credential_submit": self.credential_submit,
            "reported_attack":   self.reported_attack,
            "ignored_attack":    self.ignored_attack,
            "correct_actions":   self.correct_actions,
            "wrong_actions":     self.wrong_actions,
            "click_rate":        self.click_rate,
            "report_rate":       self.report_rate,
            "attack_history":    self.attack_history,
        }

    def save(self, employee_id: str) -> Path:
        """Persist behaviour JSON to analytics/results/{employee_id}_behavior.json."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        path = RESULTS_DIR / f"{employee_id}_behavior.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"employee_id": employee_id, **self.to_dict()}, f, indent=2, ensure_ascii=False)
        print(f"[BehaviourTracker] Saved → {path}")
        return path
