"""
PHISHVERSE – training/lecture_engine.py
Rule-based lecture assignment driven by entrance exam bias profile.

Flow:
    1. Entrance exam completes → risk_summary contains bias values
    2. LectureEngine.assign_lectures(employee_id, risk_summary)
       → detects which biases are elevated
       → assigns the corresponding lecture module(s)
       → writes employee_training/{employee_id}.json
    3. LectureScreen reads the training record and displays assigned modules
    4. LectureEngine.mark_complete() updates the record when employee finishes a module
    5. LectureEngine.all_complete() gates transition to the analytics dashboard

Assignment rules (BIAS_THRESHOLD = 0):
    Any bias > 0 (i.e. the employee made at least one mistake in that category)
    → the corresponding lecture is assigned.
    If no biases are elevated (perfect run), all 4 modules are assigned as a refresher.
"""

import json
from datetime import datetime, timezone
from pathlib  import Path

TRAINING_DIR    = Path("employee_training")
LECTURES_FILE   = Path("training") / "lectures.json"
BIAS_THRESHOLD  = 0   # assign lecture if bias strictly greater than this

BIAS_TO_LECTURE = {
    "urgency":   "email_awareness",
    "authority": "ceo_fraud_awareness",
    "reward":    "qr_awareness",
    "fear":      "vishing_awareness",
}


class LectureEngine:
    """Static helper — no instantiation required."""

    @staticmethod
    def assign_lectures(employee_id: str, risk_summary: dict) -> dict:
        """
        Detect weaknesses from risk_summary and assign lecture modules.
        Accepts both 'urgency_bias' (RiskEngine format) and 'urgency' (ResultStore format).
        Idempotent: returns existing record if one already exists for this employee.
        Writes to employee_training/{employee_id}.json.
        """
        TRAINING_DIR.mkdir(parents=True, exist_ok=True)
        path = TRAINING_DIR / f"{employee_id}.json"

        # Idempotent — don't overwrite an existing training record
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Read bias values — handle both field name conventions
        def _bias(key_long, key_short):
            return risk_summary.get(key_long, risk_summary.get(key_short, 0))

        biases = {
            "urgency":   _bias("urgency_bias",   "urgency"),
            "authority": _bias("authority_bias",  "authority"),
            "reward":    _bias("reward_bias",     "reward"),
            "fear":      _bias("fear_bias",       "fear"),
        }

        assigned = [
            BIAS_TO_LECTURE[axis]
            for axis, val in biases.items()
            if val > BIAS_THRESHOLD
        ]

        # Perfect run → assign all modules as a refresher
        if not assigned:
            assigned = list(BIAS_TO_LECTURE.values())

        record = {
            "employee":           employee_id,
            "assigned_lectures":  assigned,
            "completed_lectures": [],
            "completed":          False,
            "assigned_at":        datetime.now(timezone.utc).isoformat(),
            "completed_at":       None,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        print(f"[LectureEngine] Assigned {len(assigned)} lecture(s) to {employee_id}: {assigned}")
        return record

    @staticmethod
    def load_training(employee_id: str) -> dict | None:
        """Load the training record for an employee. Returns None if not found."""
        path = TRAINING_DIR / f"{employee_id}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def mark_complete(employee_id: str, lecture_id: str) -> dict:
        """
        Mark a single lecture as complete for the employee.
        Updates 'completed' and 'completed_at' when all assigned lectures are done.
        Returns the updated training record.
        """
        path = TRAINING_DIR / f"{employee_id}.json"
        with open(path, "r", encoding="utf-8") as f:
            record = json.load(f)

        if lecture_id not in record["completed_lectures"]:
            record["completed_lectures"].append(lecture_id)

        # Check if all assigned are now done
        if set(record["assigned_lectures"]) <= set(record["completed_lectures"]):
            record["completed"]    = True
            record["completed_at"] = datetime.now(timezone.utc).isoformat()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        return record

    @staticmethod
    def all_complete(employee_id: str) -> bool:
        """Return True if all assigned lectures are marked complete."""
        record = LectureEngine.load_training(employee_id)
        if record is None:
            return True   # no record → don't gate the flow
        return record.get("completed", False)

    @staticmethod
    def load_lectures(lecture_ids: list[str]) -> list[dict]:
        """
        Load full lecture content for the given IDs from training/lectures.json.
        Preserves the order of lecture_ids.
        Returns only lectures that exist in the JSON file.
        """
        if not LECTURES_FILE.exists():
            return []
        with open(LECTURES_FILE, "r", encoding="utf-8") as f:
            all_lecs = json.load(f).get("lectures", [])
        lec_map = {l["lecture_id"]: l for l in all_lecs}
        return [lec_map[lid] for lid in lecture_ids if lid in lec_map]
