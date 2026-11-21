# NeuroAgent

Учебный нейроагент на Python: ReAct-цикл («мысль → инструмент → наблюдение → ответ») поверх любого OpenAI-совместимого API. Работает на ПК и Android (APK).

## Возможности

- **ReAct-агент** — модель сама решает, когда вызвать инструмент, а когда дать финальный ответ
- **Инструменты**: безопасный калькулятор (AST, без `eval`), чтение/запись файлов, список каталога, текущее время, случайные числа
- **Любой LLM-провайдер** — OpenAI, OpenRouter, локальный Ollama/LM Studio и т.д.
- **CLI + REPL-режим** на ПК
- **Android-приложение** — чат-UI на Kivy, APK собирается через GitHub Actions
- **Тесты** на `unittest` с мок-LLM (не требуют API-ключа)

## Установка (ПК)

```bash
pip install -r requirements.txt
```

## Настройка

Переменные окружения (или флаги CLI):

| Переменная | Описание | По умолчанию |
|---|---|---|
| `LLM_BASE_URL` | Базовый URL OpenAI-совместимого API | `https://api.openai.com/v1` |
| `LLM_API_KEY` | API-ключ | — |
| `LLM_MODEL` | Название модели | `gpt-4o-mini` |

Пример с Ollama (без ключа):

```bash
$env:LLM_BASE_URL = "http://localhost:11434/v1"
$env:LLM_MODEL = "qwen2.5:7b"
```

## Запуск (ПК)

```bash
# Однократный запрос
python main.py "сколько будет 2**10 + sqrt(144)?"

# Интерактивный REPL
python main.py

# С подробным логом вызовов инструментов
python main.py -v "создай файл note.txt с текстом 'привет'"
```

## Android APK

APK собирается автоматически при каждом push в `main` через GitHub Actions (buildozer + Kivy).

**Скачать APK:**
1. Откройте [Actions](https://github.com/Dimonich9580/neuroagent-py/actions) → последний успешный запуск **build-apk**
2. Внизу страницы — артефакт **neuroagent-apk** → скачайте ZIP, внутри APK
3. Установите на телефон (разрешите «установку из неизвестных источников»)

**Локальная сборка APK** (нужен Linux, JDK 17, ~15 ГБ диска):

```bash
pip install buildozer cython
buildozer android debug
# APK появится в bin/
```

**Запуск мобильного UI на ПК** (для отладки):

```bash
pip install kivy
python mobile_app.py
```

## Тесты

```bash
python -m unittest test_neuroagent -v
```

## Структура

- [agent.py](agent.py) — ядро ReAct-цикла и парсер ответов модели
- [llm.py](llm.py) — клиент OpenAI-совместимого API
- [tools.py](tools.py) — инструменты и их реестр
- [main.py](main.py) — CLI/REPL
- [mobile_app.py](mobile_app.py) — чат-UI на Kivy для Android
- [buildozer.spec](buildozer.spec) — конфигурация сборки APK
- [test_neuroagent.py](test_neuroagent.py) — тесты

## Устранение неполадок

- **`LLM API вернул 401`** — неверный `LLM_API_KEY`
- **`Не удалось обратиться к LLM API`** — проверьте `LLM_BASE_URL` и доступность сервера
- **«Достигнут лимит шагов»** — модель зациклилась; попробуйте другую модель или увеличьте `--max-steps`
- **APK не собирается в Actions** — проверьте лог воркфлоу; первая сборка качает Android SDK/NDK и занимает ~20–30 минут
