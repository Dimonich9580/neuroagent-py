"""Тесты NeuroAgent: инструменты, парсер агента, ReAct-цикл с мок-LLM."""
import json
import unittest

import agent as agent_mod
import tools


class TestTools(unittest.TestCase):
    def test_calc_basic(self):
        self.assertEqual(tools.calc("2 + 2 * 2"), "6")

    def test_calc_math_funcs(self):
        self.assertEqual(tools.calc("sqrt(16) + 2**10"), "1028.0")

    def test_calc_rejects_dangerous(self):
        with self.assertRaises(ValueError):
            tools.calc("__import__('os').system('dir')")

    def test_calc_rejects_names(self):
        with self.assertRaises(ValueError):
            tools.calc("open('x')")

    def test_now(self):
        self.assertRegex(tools.now(), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

    def test_random_number(self):
        val = int(tools.random_number(5, 10))
        self.assertTrue(5 <= val <= 10)

    def test_run_tool_unknown(self):
        result = tools.run_tool("nope")
        self.assertIn("неизвестный инструмент", result)

    def test_run_tool_error_as_text(self):
        result = tools.run_tool("calc", expression="1/0")
        self.assertIn("Ошибка инструмента", result)

    def test_write_and_read_file(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "t.txt")
            tools.write_file(path, "привет")
            self.assertEqual(tools.read_file(path), "привет")


class FakeLLM:
    """Мок LLM: возвращает заранее заданные ответы по очереди."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def chat(self, messages):
        self.calls.append(messages)
        return self.replies.pop(0)


class TestAgent(unittest.TestCase):
    def make_agent(self, replies):
        llm = FakeLLM(replies)
        return agent_mod.Agent(llm, tools.TOOLS, tools.run_tool, max_steps=5)

    def test_parse_final(self):
        a = self.make_agent([])
        self.assertEqual(a._parse('{"final": "готово"}'), ("final", "готово"))

    def test_parse_action(self):
        a = self.make_agent([])
        parsed = a._parse('{"action": "calc", "args": {"expression": "1+1"}}')
        self.assertEqual(parsed, ("action", "calc", {"expression": "1+1"}))

    def test_parse_markdown_wrapped(self):
        a = self.make_agent([])
        parsed = a._parse('```json\n{"final": "ок"}\n```')
        self.assertEqual(parsed, ("final", "ок"))

    def test_parse_invalid(self):
        a = self.make_agent([])
        self.assertIsNone(a._parse("просто текст"))

    def test_react_loop_tool_then_final(self):
        a = self.make_agent([
            '{"action": "calc", "args": {"expression": "6 * 7"}}',
            '{"final": "Ответ: 42"}',
        ])
        result = a.run("сколько 6*7?")
        self.assertEqual(result, "Ответ: 42")
        # В историю должно было попасть наблюдение с результатом 42
        last_messages = a.llm.calls[-1]
        obs = [m for m in last_messages if m["role"] == "user" and "Наблюдение" in m["content"]]
        self.assertTrue(obs and "42" in obs[0]["content"])

    def test_react_loop_direct_final(self):
        a = self.make_agent(['{"final": "привет!"}'])
        self.assertEqual(a.run("привет"), "привет!")

    def test_react_loop_retry_on_bad_format(self):
        a = self.make_agent([
            "не JSON",
            '{"final": "исправился"}',
        ])
        self.assertEqual(a.run("тест"), "исправился")

    def test_max_steps_limit(self):
        a = self.make_agent(['{"action": "now", "args": {}}'] * 10)
        result = a.run("цикл")
        self.assertIn("лимит шагов", result)


if __name__ == "__main__":
    unittest.main()
