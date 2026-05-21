"""
PHISHVERSE – story.py
StoryManager: drives 4-act narrative progression.

Acts advance automatically based on completed-event count and room visits.
Provides:
  - act-keyed objectives list
  - room-entry cutscene registry (each fires at most once)
  - alert_mode flag (True during acts 3 & 4, used for HUD tint)

Architecture: purely data + state — zero pygame dependency.
"""


# ── Act definitions ────────────────────────────────────────────────────────────

ACT_NAMES = {
    1: "ACT 1 — FIRST DAY",
    2: "ACT 2 — RISING THREAT",
    3: "ACT 3 — CYBER ALERT",
    4: "ACT 4 — CEO CRISIS",
}

# Objectives shown at the bottom HUD strip, indexed by act
ACT_OBJECTIVES = {
    1: [
        "Walk inside — your internship begins today!",
        "Speak to the receptionist and check in.",
        "Head to the Work Area and set up your workstation.",
    ],
    2: [
        "Check your computer — something looks off.",
        "Someone spotted a USB on the floor. Investigate.",
        "A coworker in HR received a suspicious message.",
        "Visit the Cafeteria — a strange poster was reported.",
    ],
    3: [
        "The office is on CYBER ALERT. Investigate HR.",
        "An unknown caller rang through — assess the threat.",
        "Check all flagged locations before the final meeting.",
    ],
    4: [
        "An urgent CEO request is in the Meeting Room.",
        "Your decision determines the company's fate.",
    ],
}

# ── Room-entry cutscenes ───────────────────────────────────────────────────────
# Key: (act, room_name)   Value: (speaker, [lines])
# Each entry fires exactly once per playthrough.

ROOM_CUTSCENES: dict[tuple[int, str], tuple[str, list[str]]] = {
    # ── ACT 1 ──────────────────────────────────────────────────────────────────
    (1, "RECEPTION"): (
        "🏢 MANAGER PRIYA",
        [
            "Welcome to PhishVerse Inc!",
            "Today is your first day as a security-aware intern.",
            "Pay close attention to everything around you.",
            "If anything feels wrong — trust that instinct and report it.",
        ],
    ),
    (1, "WORK AREA"): (
        "💻 TEAM LEAD",
        [
            "Here's your workstation. We handle sensitive data daily.",
            "Security is everyone's responsibility — not just IT's.",
            "If an email, message, or link looks even slightly off...",
            "...stop, verify, and report. Don't click first.",
        ],
    ),
    (1, "HR ROOM"): (
        "📋 HR COORDINATOR",
        [
            "Hi! I'm from HR. We'll finish your onboarding paperwork today.",
            "All official HR comms come from our verified company domain.",
            "Never fill in forms from links sent via email.",
            "When in doubt, come see us in person — right here.",
        ],
    ),
    (1, "CAFETERIA"): (
        "💬 COLLEAGUE",
        [
            "Welcome! This is where we unwind.",
            "Free lunch Fridays are the best perk here.",
            "Pro tip: always check what you're scanning or clicking.",
            "Even in the break room, stay alert.",
        ],
    ),

    # ── ACT 2 ──────────────────────────────────────────────────────────────────
    (2, "WORK AREA"): (
        "⚠ COWORKER ALERT",
        [
            "Hey — did you see that suspicious email going around?",
            "IT confirmed there's unusual activity on the network.",
            "Finance already reported three phishing attempts this morning.",
            "Stay sharp. This is no coincidence.",
        ],
    ),
    (2, "CAFETERIA"): (
        "💬 COLLEAGUE",
        [
            "Someone put up a poster near the lunch tables.",
            "No one from HR recognizes it or approved it.",
            "There's a QR code on it — nobody scan that thing.",
            "I've reported it but it's still there. Be careful.",
        ],
    ),
    (2, "HR ROOM"): (
        "📋 HR COORDINATOR",
        [
            "We've been getting reports of fake HR messages.",
            "If you receive ANY official request via a link — verify first.",
            "Come to us directly. Our real portal is internal-only.",
            "And the phone in this room has been ringing strangely today...",
        ],
    ),
    (2, "MEETING ROOM"): (
        "💬 DEPT HEAD",
        [
            "Good timing. We're tracking a coordinated phishing campaign.",
            "They're impersonating internal departments across the board.",
            "The IT team is monitoring all accounts.",
            "Stay alert — something bigger may be coming.",
        ],
    ),

    # ── ACT 3 ──────────────────────────────────────────────────────────────────
    (3, "RECEPTION"): (
        "🚨 SECURITY CHIEF",
        [
            "ATTENTION: A company-wide Cyber Security Alert is now active.",
            "Do NOT share credentials, OTPs, or personal data with anyone.",
            "All suspicious calls, emails, and messages must be reported.",
            "This is not a drill. Repeat — this is NOT a drill.",
        ],
    ),
    (3, "HR ROOM"): (
        "🚨 HR MANAGER",
        [
            "We've declared a full Cyber Security Alert.",
            "Several employees received vishing calls posing as IT Support.",
            "IT staff will NEVER ask for your OTP — not by phone, not ever.",
            "Report immediately if you receive any such call.",
        ],
    ),
    (3, "MEETING ROOM"): (
        "💬 DEPT HEAD",
        [
            "Whoever is behind this is targeting our entire executive chain.",
            "They've compromised several internal-looking email addresses.",
            "Verify every single request you receive — especially financial ones.",
            "The final attack may come from the top. Stay vigilant.",
        ],
    ),
    (3, "IT SUPPORT"): (
        "💻 IT LEAD",
        [
            "We're seeing coordinated intrusion attempts across all systems.",
            "Logs show spoofed emails from domains nearly identical to ours.",
            "If you get a CEO-style urgent request — that's the attack vector.",
            "Report it to us immediately. Do NOT act on it alone.",
        ],
    ),

    # ── ACT 4 ──────────────────────────────────────────────────────────────────
    (4, "MEETING ROOM"): (
        "🚨 SECURITY CHIEF",
        [
            "An unauthorized wire transfer request has been received.",
            "It appears to come from the CEO — it is NOT from the CEO.",
            "This is a Business Email Compromise attack — BEC.",
            "Your response right now will determine the company's outcome.",
            "Think clearly. Act correctly. The team is counting on you.",
        ],
    ),
    (4, "IT SUPPORT"): (
        "💻 IT LEAD",
        [
            "We've traced the attack to a domain spoofing our executive email.",
            "The real CEO has been notified and confirmed: they sent nothing.",
            "If anyone approved a transfer — it's already being reversed.",
            "Whatever decision you made in that room... it mattered.",
        ],
    ),
}


# ── StoryManager ──────────────────────────────────────────────────────────────

class StoryManager:
    """
    Tracks the current act and phase of the narrative.
    Call advance() every frame — it returns the new act name if act changed.
    Call get_cutscene(room) when the player enters a room.
    """

    # Minimum completed-event counts to unlock act transitions.
    # Act 2 also unlocks on Work Area entry (handled in advance()).
    ACT_THRESHOLDS = {
        2: 0,   # unlocked by room entry (Work Area), not count
        3: 3,   # 3 events done
        4: 5,   # 5 events done
    }

    def __init__(self):
        self.act: int = 1
        self._entered_work_area: bool = False
        self._fired_cutscenes: set[tuple[int, str]] = set()
        self._act_objective_idx: int = 0   # which line within the act we're on

    # ── Advance ───────────────────────────────────────────────────────────────

    def advance(self, completed_count: int, current_room: str) -> str | None:
        """
        Called every game tick. Returns the ACT_NAMES string for the new act
        if the act just changed, otherwise returns None.
        """
        new_act = self.act

        if self.act == 1:
            # Transition to Act 2 when player first enters the Work Area
            if current_room == "WORK AREA":
                self._entered_work_area = True
            if self._entered_work_area:
                new_act = 2

        if self.act >= 2 and completed_count >= self.ACT_THRESHOLDS[3]:
            new_act = max(new_act, 3)

        if self.act >= 3 and completed_count >= self.ACT_THRESHOLDS[4]:
            new_act = max(new_act, 4)

        if new_act != self.act:
            self.act = new_act
            self._act_objective_idx = 0
            return ACT_NAMES[self.act]

        return None

    # ── Cutscene ──────────────────────────────────────────────────────────────

    def get_cutscene(self, room: str) -> tuple[str, list[str]] | None:
        """
        Returns (speaker, lines) for a room-entry cutscene if one exists
        for the current act AND has not fired yet. Returns None otherwise.
        """
        key = (self.act, room)
        if key in ROOM_CUTSCENES and key not in self._fired_cutscenes:
            self._fired_cutscenes.add(key)
            return ROOM_CUTSCENES[key]
        return None

    # ── Objectives ────────────────────────────────────────────────────────────

    def get_current_objective(self) -> str:
        lines = ACT_OBJECTIVES.get(self.act, ["Keep exploring."])
        idx   = min(self._act_objective_idx, len(lines) - 1)
        return lines[idx]

    def next_objective(self):
        """Advance to the next objective line within the current act."""
        lines = ACT_OBJECTIVES.get(self.act, [])
        if self._act_objective_idx < len(lines) - 1:
            self._act_objective_idx += 1

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def alert_mode(self) -> bool:
        """True during acts 3 & 4 — used for the red HUD tint."""
        return self.act >= 3

    @property
    def act_name(self) -> str:
        return ACT_NAMES.get(self.act, "")
