from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Any

from openttd_agent.agent import AgentCore
from openttd_agent.memory import MemoryLog


WEB_ROOT = Path(__file__).parent / "web"


class AgentRequestHandler(BaseHTTPRequestHandler):
    agent: AgentCore
    memory: MemoryLog

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        if path.suffix == ".css":
            content_type = "text/css"
        elif path.suffix == ".js":
            content_type = "application/javascript"
        else:
            content_type = "text/html"
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            return self._send_file(WEB_ROOT / "index.html")
        if self.path == "/app.js":
            return self._send_file(WEB_ROOT / "app.js")
        if self.path == "/styles.css":
            return self._send_file(WEB_ROOT / "styles.css")
        if self.path == "/api/state":
            return self._send_json({"memory": self.memory.serialize()})
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/cycle":
            response = self.agent.run_cycle()
            return self._send_json(
                {"plan": response.plan, "actions": response.actions, "memory": self.memory.serialize()}
            )
        if self.path == "/api/command":
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            command = payload.get("command", "")
            self.memory.add_event({"type": "manual_command", "command": command})
            return self._send_json({"status": "received", "command": command})
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")


def run_server(agent: AgentCore, memory: MemoryLog, port: int) -> None:
    handler = AgentRequestHandler
    handler.agent = agent
    handler.memory = memory
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"OpenTTD Agent UI running on http://localhost:{port}")
    server.serve_forever()
