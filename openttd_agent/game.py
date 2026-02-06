from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import base64
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

    def check_connection(self) -> Dict[str, Any]:
        connected = False
        message = "OpenTTD client not detected (stub)."
        print(f"[OpenTTD] connection check: {message}")
        return {"connected": connected, "message": message}

    def capture_screenshot(self) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='960' height='540'>"
            "<rect width='100%' height='100%' fill='#10151c'/>"
            "<text x='50%' y='45%' fill='#f4f6fb' font-size='28' font-family='sans-serif' text-anchor='middle'>"
            "OpenTTD Screenshot Stub"
            "</text>"
            "<text x='50%' y='55%' fill='#9aa7b8' font-size='18' font-family='sans-serif' text-anchor='middle'>"
            f"{timestamp}"
            "</text>"
            "</svg>"
        )
        data_uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        return {"timestamp": timestamp, "data_uri": data_uri, "note": "Stub screenshot."}
