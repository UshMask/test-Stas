# OpenTTD Gemini Agent

This project is a **standard-library-only** Python application that runs an autonomous LLM agent via the Gemini API and connects it to an OpenTTD game session. The design emphasizes a structured agent architecture with clear roles, system prompts, and a human-facing control panel for detailed agent steering and an internal-thoughts chat stream.

> ✅ The default implementation does **not** install any external Python dependencies. It is built to run on Arch Linux with only the Python standard library available.

## Features

- **Gemini API client** via `urllib` (no extra libraries).
- **Agent architecture** with Observer / Planner / Actor roles and layered system prompts.
- **OpenTTD control adapter** abstraction so that the agent can "see" and "act" like a player.
- **Web control panel** (local HTTP server) with:
  - live agent status
  - command injection
  - internal thoughts stream (for transparency)
  - detailed manual control
- **Single executable entrypoint** (`bin/openttd-agent`).

## Quick start

```bash
./bin/openttd-agent --help
```

Start the agent server (default port: 8123):

```bash
./bin/openttd-agent
```

Open the UI in your browser and set the Gemini API key in the settings panel:

```
http://localhost:8123
```

## Configuration

You can pass all configuration from CLI flags or environment variables.

- `--gemini-api-key` or `GEMINI_API_KEY`
- `--openttd-host` or `OPENTTD_HOST`
- `--openttd-port` or `OPENTTD_PORT`
- `--ui-port` or `UI_PORT`

## OpenTTD integration

The `GameAdapter` in `openttd_agent/game.py` provides two key methods:

- `capture_state()` — returns a structured snapshot of the game.
- `execute_action()` — applies an action to the game (build, pause, inspect, etc.).

This default implementation is a **safe stub** and logs commands instead of driving a real client. Plug in your preferred automation layer (e.g., OpenTTD admin API, local scripting, window automation) while keeping the agent architecture unchanged.

## Architecture overview

```
┌─────────────┐   state   ┌─────────────┐   plan   ┌────────────┐
│  Observer   ├──────────▶│  Planner    ├────────▶│  Actor     │
└─────┬───────┘           └─────┬───────┘         └─────┬──────┘
      │                          │                    │
      ▼                          ▼                    ▼
  memory log                system prompt         game actions
```

The `AgentCore` layers system prompts to ensure advanced behavior:

- **Global policy** (safety + goals)
- **Game-specific guidance** (OpenTTD economy/strategy)
- **Role-specific prompts** (Observer/Planner/Actor)

This design makes it easy to expand with more expert sub-agents.

## Project layout

```
bin/openttd-agent       # executable entrypoint
openttd_agent/
  agent.py              # AgentCore and orchestration
  config.py             # Configuration model
  game.py               # OpenTTD adapter interface
  gemini.py             # Gemini API client
  memory.py             # Thoughts + memory log
  server.py             # HTTP UI server
  web/                  # HTML/CSS/JS UI
```

## Notes

- This repo contains *architecture-first* scaffolding so you can plug in the real game integration layer as needed.
- When ready, replace `GameAdapter.capture_state()` and `GameAdapter.execute_action()` with your OpenTTD automation of choice.
