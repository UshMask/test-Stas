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
    config: Dict[str, Any]

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
            return self._send_json(
                {"memory": self.memory.serialize(), "config": self._public_config()}
            )
        if self.path == "/api/config":
            return self._send_json(self._public_config())
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/cycle":
            response = self.agent.run_cycle()
            return self._send_json(
                {
                    "plan": response.plan,
                    "actions": response.actions,
                    "memory": self.memory.serialize(),
                    "config": self._public_config(),
                }
            )
        if self.path == "/api/command":
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            command = payload.get("command", "")
            self.memory.add_event({"type": "manual_command", "command": command})
            return self._send_json({"status": "received", "command": command})
        if self.path == "/api/config":
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            if "gemini_api_key" in payload:
                self.config["gemini_api_key"] = payload.get("gemini_api_key") or None
            api_key = self.config.get("gemini_api_key")
            model = payload.get("model")
            host = payload.get("openttd_host")
            port = payload.get("openttd_port")
            if model:
                self.config["model"] = model
            if host:
                self.config["openttd_host"] = host
            if port:
                self.config["openttd_port"] = int(port)
            self.agent.set_gemini_credentials(self.config.get("gemini_api_key"), self.config.get("model"))
            self.agent.game.host = self.config.get("openttd_host", self.agent.game.host)
            self.agent.game.port = int(self.config.get("openttd_port", self.agent.game.port))
            self.memory.add_event({"type": "config_update", "payload": self._public_config()})
            return self._send_json({"status": "updated", "config": self._public_config()})
        if self.path == "/api/check_api":
            result = self.agent.check_api()
            self.memory.add_event({"type": "api_check", "payload": result})
            return self._send_json(result)
        if self.path == "/api/check_game":
            result = self.agent.game.check_connection()
            self.memory.add_event({"type": "game_check", "payload": result})
            return self._send_json(result)
        if self.path == "/api/screenshot":
            shot = self.agent.game.capture_screenshot()
            self.memory.add_event({"type": "screenshot", "payload": shot})
            return self._send_json(shot)
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def _public_config(self) -> Dict[str, Any]:
        api_key = self.config.get("gemini_api_key") or ""
        masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else ""
        return {
            "gemini_api_key_set": bool(api_key),
            "gemini_api_key_masked": masked,
            "model": self.config.get("model"),
            "openttd_host": self.config.get("openttd_host"),
            "openttd_port": self.config.get("openttd_port"),
        }


def run_server(agent: AgentCore, memory: MemoryLog, port: int, config: Dict[str, Any]) -> None:
    handler = AgentRequestHandler
    handler.agent = agent
    handler.memory = memory
    handler.config = config
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"OpenTTD Agent UI running on http://localhost:{port}")
    server.serve_forever()
