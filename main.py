#!/usr/bin/env python
"""CLI-точка входа NeuroAgent."""
import argparse
import os

import tools
from agent import Agent
from llm import LLMClient


def build_agent(args) -> Agent:
    llm = LLMClient(
        base_url=args.base_url or os.getenv("LLM_BASE_URL"),
        api_key=args.api_key or os.getenv("LLM_API_KEY"),
        model=args.model or os.getenv("LLM_MODEL"),
    )
    return Agent(llm, tools.TOOLS, tools.run_tool, max_steps=args.max_steps, verbose=args.verbose)


def main():
    parser = argparse.ArgumentParser(description="NeuroAgent — AI-агент с инструментами")
    parser.add_argument("query", nargs="*", help="Вопрос; без аргументов — интерактивный режим")
    parser.add_argument("--base-url", help="Базовый URL OpenAI-совместимого API")
    parser.add_argument("--api-key", help="API-ключ")
    parser.add_argument("--model", help="Название модели")
    parser.add_argument("--max-steps", type=int, default=8, help="Лимит шагов на запрос")
    parser.add_argument("-v", "--verbose", action="store_true", help="Показывать вызовы инструментов")
    args = parser.parse_args()

    agent = build_agent(args)

    if args.query:
        print(agent.run(" ".join(args.query)))
        return

    print("NeuroAgent REPL. Команды: /tools, /exit")
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input == "/exit":
            break
        if user_input == "/tools":
            for t in tools.TOOLS:
                print(f"- {t['name']}: {t['description']}")
            continue
        try:
            print(f"agent> {agent.run(user_input)}")
        except RuntimeError as exc:
            print(f"agent> Ошибка: {exc}")


if __name__ == "__main__":
    main()
