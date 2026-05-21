"""
PHISHVERSE – event_manager.py
Orchestrates the full event lifecycle with score-change callback support.
"""

import pygame
from events      import EventDatabase, EventDefinition
from dialogue    import DialogBox
from risk_engine import RiskEngine
from constants   import *


class EventManager:
    def __init__(self, db: EventDatabase, dialog: DialogBox, risk: RiskEngine):
        self.db     = db
        self.dialog = dialog
        self.risk   = risk
        self._seen: set[str] = set()
        self._active: EventDefinition | None = None
        self._on_game_end  = None
        self._on_score_chg = None   # callback(delta: int, good: bool)

    def set_game_end_callback(self, cb):
        self._on_game_end = cb

    def set_score_callback(self, cb):
        self._on_score_chg = cb

    # ── Triggers ─────────────────────────────────────────────────────────────

    def check_tile(self, tx: int, ty: int) -> bool:
        ev = self.db.get_by_tile(tx, ty)
        if ev and ev.id not in self._seen:
            self._start_event(ev)
            return True
        return False

    def check_interaction(self, tx: int, ty: int) -> bool:
        ev = self.db.get_by_tile(tx, ty)
        if ev and ev.id not in self._seen:
            self._start_event(ev)
            return True
        return False

    # ── Flow ─────────────────────────────────────────────────────────────────

    def _start_event(self, ev: EventDefinition):
        self._active = ev
        self.dialog.show(
            speaker=ev.title,
            lines=ev.narrative,
            choices=ev.choices,
            on_choice=self._handle_choice,
        )

    def _handle_choice(self, choice: str):
        ev = self._active
        if ev is None:
            return

        is_correct = ev.is_correct(choice)
        penalty    = ev.get_penalty(choice)

        if is_correct:
            self.risk.record_success(ev.id, choice)
            if self._on_score_chg:
                self._on_score_chg(5, True)    # show "+5 pts" reward
            outcome_lines = ev.success_message.split("\n")
            outcome_title = "✓ GREAT CHOICE!"
        else:
            score_before = self.risk.score
            self.risk.apply_penalty(ev.id, choice, penalty)
            self.risk.record_wrong(ev.id, choice)
            score_delta  = abs(self.risk.score - score_before)
            if self._on_score_chg and score_delta > 0:
                self._on_score_chg(score_delta, False)
            msg = penalty.get("message", "That was risky.")
            outcome_lines = msg.split("\n")
            outcome_title = "⚠ PHISHING DETECTED"

        self._seen.add(ev.id)
        is_final = ev.is_final

        self.dialog.show(
            speaker=outcome_title,
            lines=outcome_lines,
            on_done=self._after_outcome if not is_final else self._on_final_done,
        )

    def _after_outcome(self):
        self._active = None

    def _on_final_done(self):
        self._active = None
        if self._on_game_end:
            self._on_game_end()

    # ── Queries ──────────────────────────────────────────────────────────────

    def is_seen(self, event_id: str) -> bool:
        return event_id in self._seen

    @property
    def completed_count(self) -> int:
        return len(self._seen)
