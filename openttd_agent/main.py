from __future__ import annotations

import argparse

from openttd_agent.agent import AgentCore
from openttd_agent.config import AppConfig
from openttd_agent.game import GameAdapter
from openttd_agent.gemini import GeminiClient
from openttd_agent.memory import MemoryLog
from openttd_agent.server import run_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenTTD Gemini Agent")
    parser.add_argument("--gemini-api-key", help="Gemini API key")
    parser.add_argument("--openttd-host", default=None, help="OpenTTD host")
    parser.add_argument("--openttd-port", type=int, default=None, help="OpenTTD port")
    parser.add_argument("--ui-port", type=int, default=None, help="UI server port")
    parser.add_argument("--model", default=None, help="Gemini model ID")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = AppConfig.from_env(
        gemini_api_key=args.gemini_api_key,
        openttd_host=args.openttd_host,
        openttd_port=args.openttd_port,
        ui_port=args.ui_port,
        model=args.model,
    )

    gemini = GeminiClient(api_key=config.gemini_api_key, model=config.model) if config.gemini_api_key else None
    game = GameAdapter(host=config.openttd_host, port=config.openttd_port)
    memory = MemoryLog()
    agent = AgentCore(gemini=gemini, game=game, memory=memory, model=config.model)

    run_server(
        agent,
        memory,
        config.ui_port,
        {
            "gemini_api_key": config.gemini_api_key,
            "model": config.model,
            "openttd_host": config.openttd_host,
            "openttd_port": config.openttd_port,
        },
    )


if __name__ == "__main__":
    main()
