"""
llm/client.py — Mistral API client.

Reads MISTRAL_API_KEY and MISTRAL_MODEL from environment.
Falls back gracefully when the key is absent or the API is unreachable.

SECURITY:
  - Never logs the API key.
  - All prompts receive only sanitized, structured evidence — never raw PII.
  - Never returns invented facts; response validation enforced in llm/service.py.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger(__name__)


class MistralUnavailableError(Exception):
    """Raised when the Mistral API cannot be reached or the key is missing."""


class MistralClient:
    """
    Thin wrapper around the Mistral API.
    Uses the official `mistralai` Python SDK when available;
    falls back to `requests` if SDK is not installed.
    """

    def __init__(self):
        self._api_key: Optional[str] = os.getenv("MISTRAL_API_KEY", "").strip()
        self._model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self._available: bool = bool(self._api_key)
        self._client = None

        if self._available:
            try:
                from mistralai import Mistral  # type: ignore
                self._client = Mistral(api_key=self._api_key)
                log.info("Mistral client initialised (model=%s)", self._model)
            except ImportError:
                log.warning(
                    "mistralai SDK not installed. "
                    "Install with: pip install mistralai. "
                    "Falling back to requests."
                )
                self._client = None
            except Exception as exc:
                log.warning("Failed to initialise Mistral client: %s", exc)
                self._available = False

    @property
    def available(self) -> bool:
        return self._available

    # ── Core chat call ────────────────────────────────────────────────────────

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> Tuple[bool, str]:
        """
        Sends a chat request to Mistral.

        Returns (success: bool, content: str).
        On failure returns (False, error_message).
        """
        if not self._available:
            return False, "MISTRAL_UNAVAILABLE"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Prefer SDK
        if self._client is not None:
            try:
                resp = self._client.chat.complete(
                    model=self._model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                content = resp.choices[0].message.content
                return True, content
            except Exception as exc:
                log.warning("Mistral SDK call failed: %s", exc)
                return False, f"MISTRAL_ERROR: {exc}"

        # Fallback to requests
        return self._chat_via_requests(messages, max_tokens, temperature)

    def _chat_via_requests(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> Tuple[bool, str]:
        try:
            import requests  # type: ignore

            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self._model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
            return True, data["choices"][0]["message"]["content"]
        except Exception as exc:
            log.warning("Mistral requests fallback failed: %s", exc)
            return False, f"MISTRAL_ERROR: {exc}"

    # ── JSON chat call ────────────────────────────────────────────────────────

    def chat_json(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
    ) -> Tuple[bool, Any]:
        """
        Like chat() but attempts to parse response as JSON.
        Returns (success, parsed_dict_or_error_string).
        """
        ok, raw = self.chat(system_prompt, user_message, max_tokens=max_tokens)
        if not ok:
            return False, raw

        # Strip markdown fences if present
        clean = raw.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:-1]) if len(lines) > 2 else clean

        try:
            return True, json.loads(clean)
        except json.JSONDecodeError as exc:
            log.warning("Failed to parse Mistral JSON response: %s | raw=%r", exc, raw[:200])
            return False, f"JSON_PARSE_ERROR: {exc}"
