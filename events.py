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

    def get_by_tile(self, tx: int, ty: int) -> EventDefinition | None:
        return self._tile_index.get((tx, ty))

    def get_by_id(self, event_id: str) -> EventDefinition | None:
        for ev in self._events:
            if ev.id == event_id:
                return ev
        return None

    def all_events(self) -> list[EventDefinition]:
        return list(self._events)

    @property
    def total(self) -> int:
        return len(self._events)
