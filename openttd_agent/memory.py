from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class Thought:
    timestamp: str
    role: str
    content: str


@dataclass
class MemoryLog:
    thoughts: List[Thought] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def add_thought(self, role: str, content: str) -> None:
        self.thoughts.append(
            Thought(timestamp=datetime.utcnow().isoformat(), role=role, content=content)
        )

    def add_event(self, event: Dict[str, Any]) -> None:
        event = dict(event)
        event.setdefault("timestamp", datetime.utcnow().isoformat())
        self.events.append(event)

    def serialize(self) -> Dict[str, Any]:
        return {
            "thoughts": [thought.__dict__ for thought in self.thoughts[-200:]],
            "events": self.events[-200:],
        }
