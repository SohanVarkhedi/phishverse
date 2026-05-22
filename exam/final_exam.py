"""
PHISHVERSE – exam/final_exam.py
Exam result persistence and certificate generation.

Storage:
  exam_results/  {EMPID}_exam.json
  certificates/  {EMPID}_certificate.json
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

EXAM_DIR = Path(__file__).parent.parent / "exam_results"
CERT_DIR = Path(__file__).parent.parent / "certificates"

# Maturity level lookup (mirrors semester_report.py for consistency)
_MATURITY = [
    (0,  40,  "Beginner"),
    (41, 60,  "Aware"),
    (61, 80,  "Secure"),
    (81, 100, "Cyber Guardian"),
]


def _maturity_label(score: int) -> str:
    for lo, hi, level in _MATURITY:
        if lo <= score <= hi:
            return level
    return "Beginner"


# ── Exam result persistence ───────────────────────────────────────────────────

class ExamEngine:
    """Static helper — save and load exam result JSON files."""

    @staticmethod
    def save_result(employee_id: str, result: dict) -> Path:
        """Save exam result to exam_results/{EMPID}_exam.json."""
        EXAM_DIR.mkdir(parents=True, exist_ok=True)
        emp_id   = str(employee_id).upper().replace(" ", "_")
        filename = f"{emp_id}_exam.json"
        path     = EXAM_DIR / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[ExamEngine] Saved -> {path}")
        return path

    @staticmethod
    def load_result(employee_id: str) -> dict | None:
        """Load latest exam result for an employee. Returns None if not found."""
        emp_id = str(employee_id).upper().replace(" ", "_")
        path   = EXAM_DIR / f"{emp_id}_exam.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def build_result(
        employee: dict,
        exam_score: dict,
        semester_report: dict,
        attempt: int = 1,
    ) -> dict:
        """
        Build a serialisable exam result dict from game data.

        Args:
            employee:        dict from RegistrationScreen
            exam_score:      dict from QuestionEngine.score()
            semester_report: dict from SemesterReport.generate()
            attempt:         attempt number (increments on retake)
        """
        return {
            "employee_id":     employee.get("employee_id",   ""),
            "employee_name":   employee.get("employee_name", ""),
            "department":      employee.get("department",    ""),
            "role":            employee.get("role",          ""),
            "campaign":        semester_report.get("campaign_name", ""),

            "entrance_score":  semester_report.get("score",  0),
            "final_score":     exam_score.get("score",       0),
            "correct":         exam_score.get("correct",     0),
            "total_questions": exam_score.get("total",       10),
            "passed":          exam_score.get("passed",      False),
            "by_category":     exam_score.get("by_category", {}),

            "cyber_maturity":  _maturity_label(exam_score.get("score", 0)),
            "attempt":         attempt,
            "timestamp":       datetime.now(timezone.utc).isoformat(),
        }


# ── Certificate generation ────────────────────────────────────────────────────

class Certificate:
    """Generate and persist PHISHVERSE Cyber Awareness Certificates."""

    @staticmethod
    def generate(employee: dict, exam_result: dict) -> dict:
        """
        Build a certificate dict from employee and exam data.

        Returns a dict suitable for display and JSON storage.
        """
        cert_id = (
            f"PV-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
            f"-{str(uuid.uuid4())[:8].upper()}"
        )
        score   = exam_result.get("final_score", 0)

        return {
            "certificate_id": cert_id,
            "title":          "Cyber Awareness Certification",
            "issuer":         "PHISHVERSE Training Platform",

            # Employee identity
            "employee_name":  employee.get("employee_name", ""),
            "employee_id":    employee.get("employee_id",   ""),
            "department":     employee.get("department",    ""),
            "role":           employee.get("role",          ""),
            "campaign":       exam_result.get("campaign",   ""),

            # Scores
            "entrance_score": exam_result.get("entrance_score", 0),
            "final_score":    score,
            "cyber_maturity": _maturity_label(score),
            "risk_level":     exam_result.get("risk_level", ""),

            # Dates
            "issued_date":    datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "valid_until":    "",     # Phase 10: annual renewal

            "status":         "CERTIFIED",
        }

    @staticmethod
    def save(cert: dict, employee_id: str) -> Path:
        """Save certificate to certificates/{EMPID}_certificate.json."""
        CERT_DIR.mkdir(parents=True, exist_ok=True)
        emp_id   = str(employee_id).upper().replace(" ", "_")
        filename = f"{emp_id}_certificate.json"
        path     = CERT_DIR / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=2, ensure_ascii=False)
        print(f"[Certificate] Saved -> {path}")
        return path

    @staticmethod
    def load(employee_id: str) -> dict | None:
        """Load certificate for an employee. Returns None if not issued."""
        emp_id = str(employee_id).upper().replace(" ", "_")
        path   = CERT_DIR / f"{emp_id}_certificate.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
