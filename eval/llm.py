#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval/llm.py --- shared LLM client for the evaluation harness.

Implements the LLM configuration contract from ``docs/FORMATS.md`` §3.1 using only the
standard library (``urllib``), so no ``requests`` dependency is required.

Environment variables
---------------------
================  =====================================================
``LLM_PROVIDER``  ``deepseek`` | ``openai`` | ``none`` (default ``deepseek``)
``LLM_API_KEY``   API key (required for ``deepseek`` / ``openai``)
``LLM_BASE_URL``  OpenAI-compatible base URL
``LLM_MODEL``     model name (defaults: ``deepseek-chat`` / ``gpt-4o-mini``)
================  =====================================================

Hard constraints honoured here:

* **No I/O at import time.** The client is inert until :meth:`LLMClient.chat` is called.
* ``LLM_PROVIDER=none`` keeps the client disabled; callers must check
  :attr:`LLMClient.enabled` and skip LLM-dependent layers with a clear message.
* Talks to any OpenAI-compatible ``POST /v1/chat/completions`` endpoint.

Typical usage::

    from llm import get_client, LLMError
    client = get_client()
    if not client.enabled:
        ...  # skip L1 / L4
    answer = client.chat([{"role": "user", "content": "..."}])
    verdict = client.chat_json([...])  # -> dict | None
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Sequence

DEFAULT_PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "key_env": "OPENAI_API_KEY",
    },
}


class LLMError(RuntimeError):
    """Raised when an LLM call cannot be performed or fails repeatedly."""


def _endpoint(base_url: str) -> str:
    """Build the chat-completions URL from an OpenAI-compatible base URL."""
    base = (base_url or "").rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if re.search(r"/v\d+(?:beta)?$", base):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def extract_json_object(text: str) -> Optional[dict]:
    """Best-effort extraction of a JSON object from an LLM reply.

    Handles ```json fences and leading/trailing prose. Returns ``None`` on failure
    (callers should treat that as ``unclear`` / ``other`` rather than crashing).
    """
    if not text:
        return None
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", stripped, re.DOTALL | re.IGNORECASE)
    if fence:
        stripped = fence.group(1).strip()
    try:
        obj = json.loads(stripped)
        return obj if isinstance(obj, dict) else None
    except (ValueError, TypeError):
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            obj = json.loads(stripped[start : end + 1])
            return obj if isinstance(obj, dict) else None
        except (ValueError, TypeError):
            return None
    return None


class LLMClient:
    """Minimal OpenAI-compatible chat client."""

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 90.0,
        max_retries: int = 2,
    ) -> None:
        self.provider = (provider or os.environ.get("LLM_PROVIDER") or "deepseek").strip().lower()
        preset = DEFAULT_PROVIDERS.get(self.provider, {})

        env_key = os.environ.get("LLM_API_KEY")
        if not env_key and preset.get("key_env"):
            env_key = os.environ.get(preset["key_env"])
        self.api_key = api_key if api_key is not None else env_key

        self.base_url = (
            base_url
            or os.environ.get("LLM_BASE_URL")
            or preset.get("base_url")
            or ""
        ).strip()
        self.model = (
            model
            or os.environ.get("LLM_MODEL")
            or preset.get("model")
            or "deepseek-chat"
        ).strip()
        self.timeout = timeout
        self.max_retries = max(0, int(max_retries))

    # ---------------------------------------------------------------- state --
    @property
    def enabled(self) -> bool:
        """False when ``LLM_PROVIDER=none`` (or empty); no calls should be attempted."""
        return self.provider not in ("", "none", "off", "disabled")

    @property
    def endpoint(self) -> str:
        return _endpoint(self.base_url)

    def describe(self) -> str:
        if not self.enabled:
            return "LLM disabled (LLM_PROVIDER=none)"
        return f"provider={self.provider} model={self.model} base_url={self.base_url or '<unset>'}"

    # ----------------------------------------------------------------- chat --
    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout: Optional[float] = None,
    ) -> str:
        """Send a chat-completions request and return the assistant message content.

        Raises :class:`LLMError` when the client is disabled, the key is missing, or the
        request fails after retries. Performs NO network I/O unless called.
        """
        if not self.enabled:
            raise LLMError("LLM_PROVIDER=none: no LLM calls are permitted. Skipping.")
        if not self.api_key:
            raise LLMError(
                "LLM_API_KEY is not set (set LLM_API_KEY, or DEEPSEEK_API_KEY / OPENAI_API_KEY)."
            )
        if not self.base_url:
            raise LLMError("LLM_BASE_URL is not set and no default exists for this provider.")

        payload = {
            "model": self.model,
            "messages": list(messages),
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": False,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            },
            method="POST",
        )

        last_error: Optional[LLMError] = None
        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=timeout or self.timeout) as resp:
                    body = resp.read().decode("utf-8", "replace")
                return self._parse_response(body)
            except urllib.error.HTTPError as exc:
                detail = ""
                try:
                    detail = exc.read().decode("utf-8", "replace")[:800]
                except Exception:  # noqa: BLE001
                    pass
                last_error = LLMError(f"HTTP {exc.code} from {self.endpoint}: {detail}")
                if exc.code in (408, 409, 429, 500, 502, 503, 504) and attempt < self.max_retries:
                    time.sleep(0.6 * (2 ** attempt))
                    continue
                raise last_error
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = LLMError(f"network error calling {self.endpoint}: {exc}")
                if attempt < self.max_retries:
                    time.sleep(0.6 * (2 ** attempt))
                    continue
                raise last_error
        raise last_error or LLMError("unknown LLM failure")  # pragma: no cover

    @staticmethod
    def _parse_response(body: str) -> str:
        try:
            obj = json.loads(body)
        except (ValueError, TypeError) as exc:
            raise LLMError(f"invalid JSON response from LLM: {str(exc)}; body={body[:400]}") from exc
        if isinstance(obj, dict) and obj.get("error"):
            raise LLMError(f"LLM API error: {obj['error']}")
        choices = obj.get("choices") if isinstance(obj, dict) else None
        if not choices:
            raise LLMError(f"LLM response has no choices: {body[:400]}")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if content is None:
            raise LLMError(f"LLM response has no message content: {body[:400]}")
        return str(content)

    def chat_json(
        self,
        messages: Sequence[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
        retry_on_parse_error: bool = True,
    ) -> Optional[dict]:
        """Like :meth:`chat` but parse the reply as a JSON object.

        Returns ``None`` if the reply cannot be parsed as JSON (network errors still
        raise :class:`LLMError`). Appends a stern reminder and retries once.
        """
        text = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        obj = extract_json_object(text)
        if obj is not None or not retry_on_parse_error:
            return obj
        reminder = list(messages) + [
            {"role": "assistant", "content": text},
            {
                "role": "user",
                "content": "Your previous reply was not valid JSON. Reply with ONLY a single JSON object, no prose, no code fences.",
            },
        ]
        text2 = self.chat(reminder, temperature=temperature, max_tokens=max_tokens)
        return extract_json_object(text2)


def get_client() -> LLMClient:
    """Construct an :class:`LLMClient` from the environment (no network I/O)."""
    return LLMClient()


def is_llm_enabled() -> bool:
    """Convenience check for scripts that must skip LLM layers when disabled."""
    return get_client().enabled


if __name__ == "__main__":  # pragma: no cover - manual connectivity probe
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    client = get_client()
    print(client.describe())
    if not client.enabled:
        print("Set LLM_PROVIDER=deepseek and LLM_API_KEY to enable chat.")
    else:
        try:
            reply = client.chat([{"role": "user", "content": "Reply with the single word: ok"}], max_tokens=16)
            print("reply:", reply)
        except LLMError as exc:
            print("LLM error:", exc)
