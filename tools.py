"""Встроенные инструменты NeuroAgent."""
import ast
import datetime
import math
import os
import random

# --- Безопасный калькулятор на AST ---

_ALLOWED_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}
_ALLOWED_UNARY = {ast.USub: lambda a: -a, ast.UAdd: lambda a: +a}
_ALLOWED_FUNCS = {n: f for n, f in vars(math).items() if not n.startswith("_")}
_ALLOWED_FUNCS.update({"abs": abs, "round": round, "min": min, "max": max})


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCS:
        return _ALLOWED_FUNCS[node.func.id](*[_safe_eval(a) for a in node.args])
    if isinstance(node, ast.Name) and node.id in _ALLOWED_FUNCS:  # pi, e, tau...
        return _ALLOWED_FUNCS[node.id]
    raise ValueError(f"Запрещённое выражение: {ast.dump(node)}")


def calc(expression: str) -> str:
    """Вычисляет математическое выражение без eval()."""
    tree = ast.parse(expression, mode="eval")
    return str(_safe_eval(tree))


# --- Прочие инструменты ---

def now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def random_number(low: int = 0, high: int = 100) -> str:
    return str(random.randint(int(low), int(high)))


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()[:5000]


def write_file(path: str, content: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Записано {len(content)} символов в {path}"


def list_dir(path: str = ".") -> str:
    entries = sorted(os.listdir(path))[:100]
    return "\n".join(entries) or "(пусто)"


# --- Реестр инструментов (показывается модели) ---

TOOLS = [
    {
        "name": "calc",
        "description": "Вычислить математическое выражение. Пример: '2**10 + sqrt(16)'.",
        "parameters": {"expression": "строка — математическое выражение"},
    },
    {
        "name": "read_file",
        "description": "Прочитать текстовый файл (до 5000 символов).",
        "parameters": {"path": "строка — путь к файлу"},
    },
    {
        "name": "write_file",
        "description": "Записать текст в файл.",
        "parameters": {"path": "строка — путь к файлу", "content": "строка — содержимое"},
    },
    {
        "name": "list_dir",
        "description": "Показать список файлов в каталоге.",
        "parameters": {"path": "строка — путь к каталогу (по умолчанию '.')"},
    },
    {
        "name": "now",
        "description": "Текущие дата и время (ISO-формат).",
        "parameters": {},
    },
    {
        "name": "random_number",
        "description": "Случайное целое число в диапазоне включительно.",
        "parameters": {"low": "целое — минимум (по умолчанию 0)", "high": "целое — максимум (по умолчанию 100)"},
    },
]


def run_tool(name: str, **kwargs) -> str:
    """Исполняет инструмент по имени; ошибки возвращаются как текст-наблюдение."""
    handlers = {
        "calc": lambda **kw: calc(kw["expression"]),
        "now": lambda **kw: now(),
        "random_number": lambda **kw: random_number(kw.get("low", 0), kw.get("high", 100)),
        "read_file": lambda **kw: read_file(kw["path"]),
        "write_file": lambda **kw: write_file(kw["path"], kw["content"]),
        "list_dir": lambda **kw: list_dir(kw.get("path", ".")),
    }
    if name not in handlers:
        return f"Ошибка: неизвестный инструмент '{name}'. Доступны: {', '.join(handlers)}"
    try:
        return handlers[name](**kwargs)
    except KeyError as exc:
        return f"Ошибка: не хватает параметра {exc} для инструмента '{name}'"
    except Exception as exc:
        return f"Ошибка инструмента '{name}': {exc}"
