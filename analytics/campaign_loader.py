"""
PHISHVERSE – analytics/campaign_loader.py
Loads and validates campaign JSON files.

Usage:
    from analytics.campaign_loader import CampaignLoader, Campaign

    campaign = CampaignLoader.load("hr_campaign")
    print(campaign.name, campaign.enabled_events)
"""

import json
from pathlib import Path

# All campaign JSON files live in this directory
CAMPAIGNS_DIR = Path(__file__).parent.parent / "campaigns"

# All valid event IDs (matches data/events.json)
VALID_EVENT_IDS = {
    "email_phishing",
    "qr_phishing",
    "usb_drop",
    "hr_message",
    "voice_phishing",
    "ceo_fraud",
}


class Campaign:
    """
    Immutable wrapper around a single campaign's JSON data.

    Fields:
        campaign_id    – unique identifier (matches filename without .json)
        name           – human-readable campaign name
        department     – target department ("HR", "Finance", "ALL", etc.)
        employees      – list of employee ID strings
        enabled_events – list of event IDs active in this campaign
        pass_score     – minimum score to pass (default 80)
        duration_days  – recommended completion window (informational)
    """

    def __init__(self, data: dict):
        self.campaign_id    = data["campaign_id"]
        self.name           = data["name"]
        self.department     = data["department"]
        self.description    = data.get("description", "")
        self.employees      = data.get("employees", [])
        self.enabled_events = data["enabled_events"]
        self.pass_score     = data.get("pass_score", 80)
        self.duration_days  = data.get("duration_days", 7)

    def has_employee(self, employee_id: str) -> bool:
        return employee_id in self.employees

    def is_passing(self, score: int) -> bool:
        return score >= self.pass_score

    def to_dict(self) -> dict:
        return {
            "campaign_id":    self.campaign_id,
            "name":           self.name,
            "department":     self.department,
            "description":    self.description,
            "employees":      self.employees,
            "enabled_events": self.enabled_events,
            "pass_score":     self.pass_score,
            "duration_days":  self.duration_days,
        }

    def __repr__(self) -> str:
        return (f"Campaign(id={self.campaign_id!r}, dept={self.department!r}, "
                f"events={self.enabled_events})")


class CampaignLoader:
    """
    Loads campaign definitions from the campaigns/ directory.

    Static methods — no instantiation needed.
    """

    @staticmethod
    def load(campaign_id: str) -> Campaign:
        """
        Load a campaign by ID.
        Looks for campaigns/<campaign_id>.json.
        Raises FileNotFoundError if the file does not exist.
        Raises ValueError if required fields are missing or event IDs are invalid.
        """
        path = CAMPAIGNS_DIR / f"{campaign_id}.json"
        if not path.exists():
            available = CampaignLoader.list_available()
            raise FileNotFoundError(
                f"Campaign '{campaign_id}' not found at {path}.\n"
                f"Available campaigns: {available}"
            )

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        CampaignLoader._validate(data)
        return Campaign(data)

    @staticmethod
    def load_all() -> list[Campaign]:
        """Load every .json file in the campaigns/ directory."""
        campaigns = []
        for path in sorted(CAMPAIGNS_DIR.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            CampaignLoader._validate(data)
            campaigns.append(Campaign(data))
        return campaigns

    @staticmethod
    def list_available() -> list[str]:
        """Return a list of available campaign IDs."""
        return [p.stem for p in sorted(CAMPAIGNS_DIR.glob("*.json"))]

    @staticmethod
    def _validate(data: dict):
        """Raise ValueError if the campaign JSON is malformed."""
        required = ["campaign_id", "name", "department", "enabled_events"]
        for field in required:
            if field not in data:
                raise ValueError(f"Campaign JSON missing required field: '{field}'")

        unknown = set(data["enabled_events"]) - VALID_EVENT_IDS
        if unknown:
            raise ValueError(
                f"Campaign '{data['campaign_id']}' references unknown event IDs: {unknown}\n"
                f"Valid event IDs: {sorted(VALID_EVENT_IDS)}"
            )

        if not data["enabled_events"]:
            raise ValueError(
                f"Campaign '{data['campaign_id']}' has an empty enabled_events list."
            )
