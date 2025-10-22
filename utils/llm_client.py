"""Minimal OpenAI-compatible local LLM client (e.g., Ollama, LM Studio)."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx


class LLMClient:
    def __init__(self, base_url: str, model: str, api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key or ""
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        response_format: Optional[Any] = None,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format is not None:
            # Accept simple "json" or OpenAI dict
            if isinstance(response_format, str) and response_format.lower() in {"json", "json_object"}:
                payload["response_format"] = {"type": "json_object"}
            else:
                payload["response_format"] = response_format
        resp = self._client.post(url, headers=self._headers(), data=json.dumps(payload))
        resp.raise_for_status()
        data = resp.json()
        # Basic OpenAI-compatible shape
        return data["choices"][0]["message"]["content"].strip()
