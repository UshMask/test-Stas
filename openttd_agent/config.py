from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass
class AppConfig:
    gemini_api_key: str
    openttd_host: str = "127.0.0.1"
    openttd_port: int = 3979
    ui_port: int = 8123
    model: str = "gemini-1.5-flash"

    @staticmethod
    def from_env(**overrides: str | int | None) -> "AppConfig":
        def _env(key: str, default: str) -> str:
            return os.environ.get(key, default)

        config = AppConfig(
            gemini_api_key=overrides.get("gemini_api_key")
            or _env("GEMINI_API_KEY", ""),
            openttd_host=str(
                overrides.get("openttd_host")
                or _env("OPENTTD_HOST", "127.0.0.1")
            ),
            openttd_port=int(
                overrides.get("openttd_port")
                or _env("OPENTTD_PORT", "3979")
            ),
            ui_port=int(overrides.get("ui_port") or _env("UI_PORT", "8123")),
            model=str(overrides.get("model") or _env("GEMINI_MODEL", "gemini-1.5-flash")),
        )
        return config
