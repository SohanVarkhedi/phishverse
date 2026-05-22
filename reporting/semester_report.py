"""
PHISHVERSE – reporting/semester_report.py
Generates, stores and loads comprehensive employee semester reports.

A SemesterReport aggregates:
  • Employee identity (from RegistrationScreen)
  • Entrance exam result (score, risk, pass/fail)
  • Behaviour bias analysis (urgency / authority / reward / fear)
  • Weakness detection (highest-bias attack vectors)
  • Cyber Maturity Index (Beginner → Aware → Secure → Cyber Guardian)
  • Training progress (events completed vs total)
  • Learning progress (lectures assigned/completed — stub for Phase 8)
  • Recommendations (next lecture, focus topic, exam readiness)
  • Final Exam status (LOCKED / UNLOCKED)

Storage: reporting/employee_reports/{EMPID}_report.json
"""

import json
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path(__file__).parent / "employee_reports"

# ── Maturity level thresholds ─────────────────────────────────────────────────
# (min_score, max_score, level_name, description)
MATURITY_LEVELS = [
    (0,  40,  "Beginner",       "You are starting your cybersecurity journey."),
    (41, 60,  "Aware",          "You have foundational cybersecurity awareness."),
    (61, 80,  "Secure",         "You demonstrate solid security instincts."),
    (81, 100, "Cyber Guardian", "You are a cybersecurity champion."),
]

# ── Bias label mapping ────────────────────────────────────────────────────────
BIAS_LABELS = {
    "urgency_bias":   "Urgency Manipulation",
    "authority_bias": "Authority Phishing",
    "reward_bias":    "Reward Lures",
    "fear_bias":      "Fear Tactics",
}

# ── Recommended lectures per primary weakness ─────────────────────────────────
LECTURE_MAP = {
    "Urgency Manipulation": "Phishing Under Pressure",
    "Authority Phishing":   "Executive Impersonation & BEC",
    "Reward Lures":         "Too Good To Be True",
    "Fear Tactics":         "Ransomware & Threat Awareness",
}


class SemesterReport:
    """
    Static helper — no instantiation needed.
    Call SemesterReport.generate() to produce a report dict,
    then SemesterReport.save() to persist it.
    """

    # ── Maturity ──────────────────────────────────────────────────────────────

    @staticmethod
    def maturity_level(score: int) -> dict:
        """Map a 0-100 score to a Cyber Maturity level descriptor dict."""
        for lo, hi, level, desc in MATURITY_LEVELS:
            if lo <= score <= hi:
                return {"level": level, "description": desc, "score": score}
        # Fallback (score out of expected range)
        return {"level": "Beginner", "description": MATURITY_LEVELS[0][3], "score": score}

    # ── Weakness detection ────────────────────────────────────────────────────

    @staticmethod
    def detect_weaknesses(risk_summary: dict) -> dict:
        """
        Return the top-2 attack-vector weaknesses ranked by bias score.
        Primary = highest bias, Secondary = second highest.
        """
        biases = {
            "Urgency Manipulation": risk_summary.get("urgency_bias",   0),
            "Authority Phishing":   risk_summary.get("authority_bias", 0),
            "Reward Lures":         risk_summary.get("reward_bias",    0),
            "Fear Tactics":         risk_summary.get("fear_bias",      0),
        }
        ranked    = sorted(biases.items(), key=lambda kv: kv[1], reverse=True)
        primary   = ranked[0][0] if ranked else "None"
        secondary = ranked[1][0] if len(ranked) > 1 else "None"
        return {"primary": primary, "secondary": secondary}

    # ── Report generation ─────────────────────────────────────────────────────

    @staticmethod
    def generate(
        employee: dict,
        campaign,                    # Campaign object or None (free-play)
        risk_summary: dict,
        completed_events: list,
    ) -> dict:
        """
        Build a full semester report dict from game-session data.
        This is the canonical schema stored to disk and read by SemesterReportScreen.
        """
        score    = risk_summary.get("score", 0)
        maturity = SemesterReport.maturity_level(score)
        weakness = SemesterReport.detect_weaknesses(risk_summary)

        events_total     = len(campaign.enabled_events) if campaign else 0
        events_completed = len(completed_events)
        progress_pct     = (
            round(events_completed / events_total * 100) if events_total else 0
        )

        # Final exam unlocks once all campaign events are attempted
        exam_status = (
            "UNLOCKED" if events_completed >= events_total and events_total > 0
            else "LOCKED"
        )

        primary_weakness = weakness["primary"]
        next_lecture     = LECTURE_MAP.get(primary_weakness, "Cybersecurity Fundamentals")

        return {
            # ── Identity ──────────────────────────────────────────────────
            "employee": {
                "employee_name": employee.get("employee_name", ""),
                "employee_id":   employee.get("employee_id",   ""),
                "department":    employee.get("department",    ""),
                "role":          employee.get("role",          ""),
            },

            # ── Campaign ──────────────────────────────────────────────────
            "campaign":       campaign.campaign_id if campaign else "",
            "campaign_name":  campaign.name        if campaign else "Free Play",
            "date":           datetime.now(timezone.utc).strftime("%Y-%m-%d"),

            # ── Entrance exam ─────────────────────────────────────────────
            "score":      score,
            "pass_score": campaign.pass_score if campaign else 0,
            "passed":     score >= (campaign.pass_score if campaign else 0),
            "risk":       risk_summary.get("risk_level", "MEDIUM"),

            # ── Bias breakdown ────────────────────────────────────────────
            "biases": {
                "urgency":   risk_summary.get("urgency_bias",   0),
                "authority": risk_summary.get("authority_bias", 0),
                "reward":    risk_summary.get("reward_bias",    0),
                "fear":      risk_summary.get("fear_bias",      0),
            },

            # ── Weakness ──────────────────────────────────────────────────
            "weakness": weakness,

            # ── Training progress ─────────────────────────────────────────
            "training_progress": {
                "events_total":     events_total,
                "events_completed": events_completed,
                "progress_pct":     progress_pct,
                "completed_events": list(completed_events),
            },

            # ── Maturity ──────────────────────────────────────────────────
            "maturity": maturity,

            # ── Lectures (stub — Phase 9 will populate) ───────────────────
            "lectures": {
                "assigned":    0,
                "completed":   0,
                "pending":     0,
                "progress_pct": 0,
                "items":       [],
            },

            # ── Recommendations ───────────────────────────────────────────
            "recommendation": {
                "next_lecture":    next_lecture,
                "suggested_topic": primary_weakness,
                "exam_ready":      exam_status == "UNLOCKED",
            },

            # ── Exam status ───────────────────────────────────────────────
            "exam_status": exam_status,

            # ── Meta ──────────────────────────────────────────────────────
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── Persistence ───────────────────────────────────────────────────────────

    @staticmethod
    def save(report: dict, employee_id: str) -> Path:
        """
        Save report to reporting/employee_reports/{EMPID}_report.json.
        Overwrites on replay (latest session always wins).
        """
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        emp_id   = str(employee_id).upper().replace(" ", "_")
        filename = f"{emp_id}_report.json"
        path     = REPORTS_DIR / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[SemesterReport] Saved -> {path}")
        return path

    @staticmethod
    def load(employee_id: str) -> dict | None:
        """Load the latest semester report for an employee. Returns None if not found."""
        emp_id = str(employee_id).upper().replace(" ", "_")
        path   = REPORTS_DIR / f"{emp_id}_report.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_all() -> list[dict]:
        """Load every semester report on disk."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        results = []
        for p in sorted(REPORTS_DIR.glob("*_report.json")):
            with open(p, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        return results
