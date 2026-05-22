"""
PHISHVERSE — Flask backend bridge
Launches the pygame RPG via subprocess and exposes results + campaign data to the web portal.
"""

import json
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR        = Path(__file__).resolve().parent.parent
MAIN_PY         = BASE_DIR / "main.py"
RESULTS_DIR     = BASE_DIR / "analytics" / "results"
AI_RESULTS_DIR  = BASE_DIR / "ai_results"
CAMPAIGNS_DIR   = BASE_DIR / "campaigns"

# Domain → enabled_events mapping (mirrors campaign JSON definitions)
DOMAIN_EVENTS = {
    "Finance":  ["ceo_fraud", "email_phishing"],
    "HR":       ["hr_message", "voice_phishing"],
    "General":  ["email_phishing", "qr_phishing", "usb_drop", "hr_message", "voice_phishing", "ceo_fraud"],
}

_game_process = None  # track the running subprocess


# ─────────────────────────────────────────
# POST /api/launch-game
# Body (optional): { "campaign_id": "finance_campaign" }
# ─────────────────────────────────────────
@app.route("/api/launch-game", methods=["POST"])
def launch_game():
    global _game_process

    if _game_process is not None and _game_process.poll() is None:
        return jsonify({
            "status":  "already_running",
            "message": "PHISHVERSE is already running.",
            "pid":     _game_process.pid,
        })

    if not MAIN_PY.exists():
        return jsonify({
            "status":  "error",
            "message": f"main.py not found at {MAIN_PY}",
        }), 500

    body        = request.get_json(silent=True) or {}
    campaign_id = body.get("campaign_id")

    cmd = [sys.executable, str(MAIN_PY)]
    if campaign_id:
        cmd += ["--campaign", campaign_id]

    try:
        _game_process = subprocess.Popen(cmd, cwd=str(BASE_DIR))
        return jsonify({
            "status":      "ok",
            "message":     "PHISHVERSE launched.",
            "pid":         _game_process.pid,
            "campaign_id": campaign_id,
        })
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


# ─────────────────────────────────────────
# GET /api/game-status
# ─────────────────────────────────────────
@app.route("/api/game-status", methods=["GET"])
def game_status():
    global _game_process
    if _game_process is None:
        return jsonify({"status": "idle", "running": False})
    running = _game_process.poll() is None
    return jsonify({
        "status":  "running" if running else "exited",
        "running": running,
        "pid":     _game_process.pid,
    })


# ─────────────────────────────────────────
# GET /api/results/<employee_id>
# ─────────────────────────────────────────
@app.route("/api/results/<employee_id>", methods=["GET"])
def get_results(employee_id):
    path = RESULTS_DIR / f"{employee_id}.json"
    if not path.exists():
        return jsonify({"status": "not_found"}), 404
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify({"status": "ok", "data": data})


# ─────────────────────────────────────────
# GET /api/ai-results/<employee_id>
# ─────────────────────────────────────────
@app.route("/api/ai-results/<employee_id>", methods=["GET"])
def get_ai_results(employee_id):
    path = AI_RESULTS_DIR / f"{employee_id}_ai.json"
    if not path.exists():
        return jsonify({"status": "not_found"}), 404
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify({"status": "ok", "data": data})


# ─────────────────────────────────────────
# GET /api/employees
# Returns all result JSONs from analytics/results/ (real employee records)
# ─────────────────────────────────────────
@app.route("/api/employees", methods=["GET"])
def list_employees():
    employees = []
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(RESULTS_DIR.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            employees.append({
                "employee_id":   data.get("employee_id", path.stem),
                "employee_name": data.get("employee_name", ""),
                "department":    data.get("department", ""),
                "campaign":      data.get("campaign", ""),
                "campaign_name": data.get("campaign_name", ""),
                "score":         data.get("score", 0),
                "risk":          data.get("risk", "UNKNOWN"),
                "passed":        data.get("passed", False),
                "timestamp":     data.get("timestamp", ""),
                "events_completed": data.get("events_completed", 0),
                "events_total":     data.get("events_total", 0),
                "urgency":       data.get("urgency", 0),
                "authority":     data.get("authority", 0),
                "reward":        data.get("reward", 0),
                "fear":          data.get("fear", 0),
            })
        except Exception:
            pass
    return jsonify({"status": "ok", "employees": employees, "total": len(employees)})


# ─────────────────────────────────────────
# GET /api/campaigns
# Returns all campaign JSON files from campaigns/
# ─────────────────────────────────────────
@app.route("/api/campaigns", methods=["GET"])
def list_campaigns():
    campaigns = []
    CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(CAMPAIGNS_DIR.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            campaigns.append(data)
        except Exception:
            pass
    return jsonify({"status": "ok", "campaigns": campaigns})


# ─────────────────────────────────────────
# POST /api/campaigns
# Body: { "name": "...", "domain": "Finance|HR|General", "duration_days": 14 }
# Creates a new campaign JSON in campaigns/
# ─────────────────────────────────────────
@app.route("/api/campaigns", methods=["POST"])
def create_campaign():
    body = request.get_json(silent=True) or {}
    name     = body.get("name", "").strip()
    domain   = body.get("domain", "General")
    duration = int(body.get("duration_days", 14))

    if not name:
        return jsonify({"status": "error", "message": "Campaign name is required"}), 400

    if domain not in DOMAIN_EVENTS:
        return jsonify({
            "status":  "error",
            "message": f"Unknown domain '{domain}'. Valid: {list(DOMAIN_EVENTS.keys())}",
        }), 400

    # Build a slug from the name
    import re
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    campaign_id = slug or "campaign"

    campaign = {
        "campaign_id":    campaign_id,
        "name":           name,
        "department":     domain,
        "description":    f"{domain} security training — {name}",
        "employees":      [],
        "enabled_events": DOMAIN_EVENTS[domain],
        "pass_score":     85,
        "duration_days":  duration,
    }

    CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CAMPAIGNS_DIR / f"{campaign_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(campaign, f, indent=2)

    print(f"[PHISHVERSE] Campaign saved -> {out_path}")
    return jsonify({"status": "ok", "campaign": campaign})


# ─────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────
if __name__ == "__main__":
    print(f"[PHISHVERSE] Backend starting on http://localhost:5000")
    print(f"[PHISHVERSE] Game path:    {MAIN_PY}")
    print(f"[PHISHVERSE] Results dir:  {RESULTS_DIR}")
    print(f"[PHISHVERSE] Campaigns dir:{CAMPAIGNS_DIR}")
    app.run(port=5000, debug=False)
