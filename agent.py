"""Ядро NeuroAgent: ReAct-цикл «мысль → инструмент → наблюдение → ответ»."""
import json
import re

SYSTEM_PROMPT = """Ты — NeuroAgent, полезный ассистент с доступом к инструментам.

Доступные инструменты:
{tools}

В каждом ответе действуй строго по одной из схем:

1) Вызвать инструмент — верни ТОЛЬКО JSON без markdown-обёрток:
{{"action": "имя_инструмента", "args": {{"параметр": "значение"}}}}

2) Дать финальный ответ — верни ТОЛЬКО JSON:
{{"final": "твой ответ пользователю"}}

Правила:
- Не выдумывай параметры, используй только описанные.
- Если инструмент не нужен — сразу давай final.
- После наблюдения продолжай рассуждение: либо новый action, либо final."""


class Agent:
    def __init__(self, llm, tool_specs, tool_runner, max_steps: int = 8, verbose: bool = False):
        self.llm = llm
        self.tool_specs = tool_specs
        self.run_tool = tool_runner
        self.max_steps = max_steps
        self.verbose = verbose

    def _parse(self, text: str):
        """Разбирает ответ модели: ('final', ответ) или ('action', имя, args) или None."""
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        if isinstance(data, dict) and "final" in data:
            return ("final", str(data["final"]))
        if isinstance(data, dict) and "action" in data:
            return ("action", str(data["action"]), data.get("args") or {})
        return None

    def run(self, user_input: str) -> str:
        tools_desc = json.dumps(self.tool_specs, ensure_ascii=False, indent=2)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(tools=tools_desc)},
            {"role": "user", "content": user_input},
        ]
        for step in range(1, self.max_steps + 1):
            reply = self.llm.chat(messages)
            parsed = self._parse(reply)
            if parsed is None:
                messages.append({"role": "assistant", "content": reply})
                messages.append({
                    "role": "user",
                    "content": 'Ответ не по схеме. Верни корректный JSON: {"action": ...} или {"final": ...}.',
                })
                continue
            if parsed[0] == "final":
                return parsed[1]
            _, name, args = parsed
            if self.verbose:
                print(f"  [шаг {step}] {name}({args})")
            observation = self.run_tool(name, **args)
            if self.verbose:
                print(f"  [шаг {step}] -> {observation[:200]}")
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": f"Наблюдение: {observation}"})
        return "Достигнут лимит шагов без финального ответа."
