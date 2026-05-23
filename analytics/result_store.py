"""
PHISHVERSE – analytics/result_store.py
Saves employee simulation results to analytics/results/.

Result filename: analytics/results/{employee_id}_{campaign_id}_{date}.json

Usage (called automatically by main.py on game end):
    ResultStore.save(
        employee_id="emp01",
        campaign=campaign_obj,
        risk_summary=risk_engine.summary_dict(),
        completed_events=["email_phishing", "hr_message"],
    )

Also provides:
    ResultStore.load(employee_id, campaign_id)
    ResultStore.load_all_for_campaign(campaign_id)
    ResultStore.list_results()
"""

import json
from datetime import datetime, timezone
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"


class ResultStore:
    """
    Static helper — no instantiation required.
    All results are stored as individual JSON files in analytics/results/.
    """

    @staticmethod
    def save(
        employee: dict,              # from RegistrationScreen or fallback dict
        campaign,                    # Campaign object from campaign_loader
        risk_summary: dict,
        completed_events: list[str],
        behaviour: dict | None = None,   # from BehaviourTracker.to_dict()
    ) -> Path:
        """
        Persist a simulation result to disk.
        Filename: analytics/results/{employee_id}.json   (overwrites on replay).
        Returns the path of the written file.
        """
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        employee_id   = employee.get("employee_id",   "unknown")
        employee_name = employee.get("employee_name", "")
        department    = employee.get("department",    "")
        role          = employee.get("role",          "")
        timestamp     = datetime.now(timezone.utc).isoformat()

        result = {
            # ── Employee identity ─────────────────────────────────────────
            "employee_name":  employee_name,
            "employee_id":    employee_id,
            "department":     department,
            "role":           role,

            # ── Campaign ──────────────────────────────────────────────────
            "campaign":       campaign.campaign_id,
            "campaign_name":  campaign.name,

            # ── Scores ────────────────────────────────────────────────────
            "score":          risk_summary.get("score", 0),
            "pass_score":     campaign.pass_score,
            "passed":         risk_summary.get("score", 0) >= campaign.pass_score,

            # ── Bias breakdown (user-spec keys) ───────────────────────────
            "urgency":        risk_summary.get("urgency_bias",   0),
            "authority":      risk_summary.get("authority_bias", 0),
            "reward":         risk_summary.get("reward_bias",    0),
            "fear":           risk_summary.get("fear_bias",      0),

            # ── Risk profile ──────────────────────────────────────────────
            "risk":           risk_summary.get("risk_level",     "UNKNOWN"),
            "weakest_area":   risk_summary.get("weakest_area",   "N/A"),
            "recommendation": risk_summary.get("recommendation", ""),
            "mistakes":       risk_summary.get("mistakes",        0),
            "successful_reports": risk_summary.get("successful_reports", 0),

            # ── Event completion ──────────────────────────────────────────
            "completed_events": completed_events,
            "events_total":     len(campaign.enabled_events),
            "events_completed": len(completed_events),

            # ── Behaviour metrics ─────────────────────────────────────────
            "clicked_link":      (behaviour or {}).get("clicked_link",      0),
            "credential_submit": (behaviour or {}).get("credential_submit",  0),
            "reported_attack":   (behaviour or {}).get("reported_attack",    0),
            "ignored_attack":    (behaviour or {}).get("ignored_attack",     0),
            "correct_actions":   (behaviour or {}).get("correct_actions",    0),
            "wrong_actions":     (behaviour or {}).get("wrong_actions",      0),
            "click_rate":        (behaviour or {}).get("click_rate",         0.0),
            "report_rate":       (behaviour or {}).get("report_rate",        0.0),

            # ── Meta ──────────────────────────────────────────────────────
            "timestamp":      timestamp,
        }

        filename = f"{employee_id}.json"
        out_path = RESULTS_DIR / filename

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[ResultStore] Saved result -> {out_path}")
        return out_path

    # ── Read helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def load(employee_id: str, campaign_id: str) -> list[dict]:
        """
        Load all results for a given employee + campaign combination.
        Returns a list of result dicts (may have multiple if replayed).
        """
        results = []
        for path in sorted(RESULTS_DIR.glob(f"{employee_id}_{campaign_id}_*.json")):
            with open(path, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        return results

    @staticmethod
    def load_all_for_campaign(campaign_id: str) -> list[dict]:
        """Load all employee results for a specific campaign."""
        results = []
        for path in sorted(RESULTS_DIR.glob(f"*_{campaign_id}_*.json")):
            with open(path, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        return results

    @staticmethod
    def load_all() -> list[dict]:
        """Load every result file in analytics/results/."""
        results = []
        for path in sorted(RESULTS_DIR.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        return results

    @staticmethod
    def list_results() -> list[str]:
        """Return filenames of all stored results."""
        return [p.name for p in sorted(RESULTS_DIR.glob("*.json"))]

    @staticmethod
    def campaign_summary(campaign_id: str) -> dict:
        """
        Aggregate statistics for a campaign across all employees.
        Returns a summary dict suitable for dashboard display.
        """
        results = ResultStore.load_all_for_campaign(campaign_id)
        if not results:
            return {"campaign": campaign_id, "total_employees": 0}

        scores      = [r["score"] for r in results]
        pass_count  = sum(1 for r in results if r.get("passed", False))
        avg_score   = round(sum(scores) / len(scores), 1)
        avg_urgency = round(sum(r.get("urgency_bias", 0)   for r in results) / len(results), 1)
        avg_auth    = round(sum(r.get("authority_bias", 0) for r in results) / len(results), 1)
        avg_reward  = round(sum(r.get("reward_bias", 0)    for r in results) / len(results), 1)
        avg_fear    = round(sum(r.get("fear_bias", 0)      for r in results) / len(results), 1)

        return {
            "campaign":         campaign_id,
            "total_employees":  len(results),
            "pass_count":       pass_count,
            "fail_count":       len(results) - pass_count,
            "pass_rate_pct":    round(pass_count / len(results) * 100, 1),
            "avg_score":        avg_score,
            "min_score":        min(scores),
            "max_score":        max(scores),
            "avg_urgency_bias": avg_urgency,
            "avg_authority_bias": avg_auth,
            "avg_reward_bias":  avg_reward,
            "avg_fear_bias":    avg_fear,
        }
