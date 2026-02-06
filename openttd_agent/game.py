from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class GameState:
    summary: str
    details: Dict[str, Any]


class GameAdapter:
    """
    Stub adapter for OpenTTD.

    Replace with a real implementation that reads the game state and executes actions.
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def capture_state(self) -> GameState:
        return GameState(
            summary="OpenTTD adapter stub - no live game state connected.",
            details={"host": self.host, "port": self.port},
        )

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "queued",
            "action": action,
            "note": "Stub action - integrate with OpenTTD automation here.",
        }
