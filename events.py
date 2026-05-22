"""
PHISHVERSE – events.py
Loads event definitions from JSON and provides lookup helpers.
"""

import json
from pathlib import Path
from constants import EVENT_FILE


class EventDefinition:
    """Immutable wrapper around a single event's JSON data."""

    def __init__(self, data: dict):
        self.id              = data["id"]
        self.title           = data["title"]
        self.location        = data["location"]
        self.trigger_tiles   = [tuple(t) for t in data["trigger_tiles"]]
        self.trigger_type    = data["trigger_type"]
        self.narrative       = data["narrative"]
        self.choices         = data["choices"]
        self.correct         = data["correct"]
        self.wrong           = data["wrong"]
        self.penalties       = data.get("penalties", {})
        self.success_message = data.get("success_message", "Well done!")
        self.bias_tag        = data.get("bias_tag", "")
        self.is_final        = data.get("is_final", False)

    def is_correct(self, choice: str) -> bool:
        return choice in self.correct

    def get_penalty(self, choice: str) -> dict:
        return self.penalties.get(choice, {})


class EventDatabase:
    """Loads all events from JSON; provides tile-based lookup."""

    def __init__(self):
        path = Path(EVENT_FILE)
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self._events: list[EventDefinition] = [
            EventDefinition(e) for e in raw["events"]
        ]
        # Build tile → event index
        self._tile_index: dict[tuple[int, int], EventDefinition] = {}
        for ev in self._events:
            for tile in ev.trigger_tiles:
                self._tile_index[tile] = ev
        # Campaign filter: None = all events active
        self._enabled: set[str] | None = None

    # ── Campaign filter ──────────────────────────────────────────────────

    def set_enabled_events(self, event_ids: list[str] | set[str]):
        """
        Restrict which events are active for this session.
        Called by the campaign runner before the game loop starts.
        Pass None to re-enable all events.
        """
        self._enabled = set(event_ids) if event_ids is not None else None

    # ── Lookups ────────────────────────────────────────────────────────

    def get_by_tile(self, tx: int, ty: int) -> EventDefinition | None:
        ev = self._tile_index.get((tx, ty))
        if ev is None:
            return None
        # Honour campaign filter
        if self._enabled is not None and ev.id not in self._enabled:
            return None
        return ev

    def get_by_id(self, event_id: str) -> EventDefinition | None:
        for ev in self._events:
            if ev.id == event_id:
                return ev
        return None

    def all_events(self) -> list[EventDefinition]:
        """Returns only campaign-enabled events (or all if no filter is set)."""
        if self._enabled is None:
            return list(self._events)
        return [ev for ev in self._events if ev.id in self._enabled]

    @property
    def total(self) -> int:
        """Count of active (campaign-filtered) events."""
        if self._enabled is None:
            return len(self._events)
        return sum(1 for ev in self._events if ev.id in self._enabled)
