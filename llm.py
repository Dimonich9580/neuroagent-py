"""Клиент LLM для NeuroAgent — работает с любым OpenAI-совместимым API."""
import os

import requests


class LLMClient:
    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    def chat(self, messages, temperature=0.2, max_tokens=1024):
        """Отправляет историю сообщений, возвращает текст ответа модели."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Не удалось обратиться к LLM API ({self.base_url}): {exc}") from exc
        if resp.status_code >= 400:
            raise RuntimeError(f"LLM API вернул {resp.status_code}: {resp.text[:500]}")
        return resp.json()["choices"][0]["message"]["content"]
