from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

from openttd_agent.game import GameAdapter
from openttd_agent.gemini import GeminiClient
from openttd_agent.memory import MemoryLog


SYSTEM_POLICY = """
Ты — автономный агент для управления OpenTTD.
Твоя цель — развивать прибыльную и устойчивую транспортную компанию.
Соблюдай стратегию, оценивай риски, предпочитай стабильный рост.
Не выдумывай факты, которых нет в наблюдениях.
""".strip()

GAME_GUIDANCE = """
OpenTTD — экономическая стратегия. Управляй маршрутами, строй станций и депо,
следи за кредитами и окупаемостью. Учитывай производительность, загруженность,
стоимость обслуживания и перспективу расширения.
""".strip()

ROLE_PROMPTS = {
    "observer": "Ты наблюдаешь за игрой и формируешь точное описание состояния.",
    "planner": "Ты планируешь стратегию и предлагаешь шаги развития.",
    "actor": "Ты преобразуешь план в конкретные действия для игры.",
}


@dataclass
class AgentResponse:
    thoughts: List[str]
    actions: List[Dict[str, Any]]
    plan: str


class AgentCore:
    def __init__(self, gemini: GeminiClient, game: GameAdapter, memory: MemoryLog) -> None:
        self.gemini = gemini
        self.game = game
        self.memory = memory

    def _build_system_prompt(self, role: str) -> str:
        role_prompt = ROLE_PROMPTS.get(role, "")
        return "\n\n".join([SYSTEM_POLICY, GAME_GUIDANCE, role_prompt])

    def _extract_text(self, response: Dict[str, Any]) -> str:
        candidates = response.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "\n".join(part.get("text", "") for part in parts)

    def run_cycle(self) -> AgentResponse:
        state = self.game.capture_state()
        self.memory.add_event({"type": "state", "summary": state.summary})

        observer_prompt = (
            f"Состояние игры: {state.summary}\n"
            f"Детали: {state.details}\n"
            "Опиши ситуацию кратко и точно."
        )
        observer_resp = self.gemini.generate(
            self._build_system_prompt("observer"), observer_prompt
        )
        observation = self._extract_text(observer_resp)
        self.memory.add_thought("observer", observation)

        planner_prompt = (
            "Наблюдение:\n"
            f"{observation}\n\n"
            "Сформируй краткий план из 3-5 шагов."
        )
        planner_resp = self.gemini.generate(
            self._build_system_prompt("planner"), planner_prompt
        )
        plan = self._extract_text(planner_resp)
        self.memory.add_thought("planner", plan)

        actor_prompt = (
            "План:\n"
            f"{plan}\n\n"
            "Сгенерируй список действий в JSON (массив объектов)."
        )
        actor_resp = self.gemini.generate(
            self._build_system_prompt("actor"), actor_prompt
        )
        actions_text = self._extract_text(actor_resp)
        self.memory.add_thought("actor", actions_text)

        actions = self._parse_actions(actions_text)
        executed_actions = []
        for action in actions:
            result = self.game.execute_action(action)
            self.memory.add_event({"type": "action", "payload": result})
            executed_actions.append(result)

        return AgentResponse(thoughts=[observation, plan, actions_text], actions=executed_actions, plan=plan)

    def _parse_actions(self, actions_text: str) -> List[Dict[str, Any]]:
        try:
            import json

            data = json.loads(actions_text)
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
        except Exception:
            pass
        return [{"type": "note", "content": actions_text}]
