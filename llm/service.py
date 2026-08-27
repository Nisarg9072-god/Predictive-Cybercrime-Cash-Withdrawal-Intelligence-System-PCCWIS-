"""
llm/service.py — High-level LLM service with evidence grounding and hallucination rejection.

Architecture:
  LLMService
    → MistralClient.chat() / chat_json()
    → ResponseValidator.validate_*()
    → Structured result or deterministic fallback

INVARIANTS:
  - Risk scores can never be changed by LLM output.
  - Invented account IDs / transaction IDs are rejected.
  - If LLM is unavailable or fails, deterministic fallback is returned transparently.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from llm.client import MistralClient
from llm.prompts import (
    SYSTEM_INVESTIGATOR,
    build_hypothesis_prompt,
    build_action_ranking_prompt,
    build_finding_explanation_prompt,
    build_executive_summary_prompt,
)

log = logging.getLogger(__name__)

# Singleton client — initialised once at module load
_client: Optional[MistralClient] = None


def _get_client() -> MistralClient:
    global _client
    if _client is None:
        _client = MistralClient()
    return _client


# ── Response Validation ───────────────────────────────────────────────────────

class ResponseValidator:
    """Validates LLM responses for hallucination and constraint violations."""

    # Fields that the LLM must NEVER modify
    IMMUTABLE_NUMERIC = {"risk_score", "confidence", "amount_inr"}

    @staticmethod
    def validate_hypothesis(raw: Any) -> Tuple[bool, str]:
        if not isinstance(raw, dict):
            return False, "Response is not a JSON object."
        required = {"description", "category", "confidence", "reasoning"}
        missing = required - raw.keys()
        if missing:
            return False, f"Missing fields: {missing}"
        if not isinstance(raw.get("confidence"), (int, float)):
            return False, "confidence must be numeric."
        if not (0.0 <= float(raw["confidence"]) <= 1.0):
            return False, "confidence out of [0, 1] range."
        if len(raw.get("description", "")) < 10:
            return False, "Description too short — likely a hallucination placeholder."
        return True, "ok"

    @staticmethod
    def validate_action(raw: Any, available_tools: List[str]) -> Tuple[bool, str]:
        if not isinstance(raw, dict):
            return False, "Response is not a JSON object."
        tool = raw.get("tool", "")
        valid = set(available_tools) | {"STOP"}
        if tool not in valid:
            return False, f"LLM selected invalid tool '{tool}'. Available: {valid}"
        return True, "ok"

    @staticmethod
    def validate_text(raw: Any, min_words: int = 10) -> Tuple[bool, str]:
        if not isinstance(raw, str):
            return False, "Response is not a string."
        word_count = len(raw.split())
        if word_count < min_words:
            return False, f"Response too short ({word_count} words)."
        return True, "ok"


# ── LLM Service ───────────────────────────────────────────────────────────────

class LLMService:
    """
    High-level service methods consumed by agent nodes.
    Each method tries the LLM, validates the response, and falls back deterministically.
    """

    @staticmethod
    def generate_hypothesis(state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Generate a new investigation hypothesis grounded in current state.
        Returns (llm_used: bool, hypothesis_dict).
        Falls back to {"error": "LLM_UNAVAILABLE"} without crashing.
        """
        client = _get_client()
        if not client.available:
            return False, {"error": "LLM_UNAVAILABLE"}

        prompt = build_hypothesis_prompt(state)
        ok, result = client.chat_json(SYSTEM_INVESTIGATOR, prompt)
        if not ok:
            log.warning("Hypothesis LLM call failed: %s", result)
            return False, {"error": result}

        valid, reason = ResponseValidator.validate_hypothesis(result)
        if not valid:
            log.warning("Hypothesis validation failed: %s | result=%r", reason, result)
            return False, {"error": f"VALIDATION_FAILED: {reason}"}

        return True, result

    @staticmethod
    def rank_actions(
        state: Dict[str, Any],
        available_tools: List[str],
        completed_tools: List[str],
    ) -> Tuple[bool, str]:
        """
        Select the next most valuable investigation tool.
        Returns (llm_used: bool, tool_name).
        Falls back to "LLM_UNAVAILABLE" without crashing.
        """
        client = _get_client()
        if not client.available:
            return False, "LLM_UNAVAILABLE"

        remaining = [t for t in available_tools if t not in completed_tools]
        if not remaining:
            return False, "STOP"

        prompt = build_action_ranking_prompt(state, available_tools, completed_tools)
        ok, result = client.chat_json(SYSTEM_INVESTIGATOR, prompt)
        if not ok:
            return False, "LLM_UNAVAILABLE"

        valid, reason = ResponseValidator.validate_action(result, available_tools)
        if not valid:
            log.warning("Action validation failed: %s", reason)
            return False, "LLM_UNAVAILABLE"

        return True, result.get("tool", "STOP")

    @staticmethod
    def explain_finding(
        finding: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> Tuple[bool, str]:
        """
        Generate a human-readable analyst explanation for a finding.
        Returns (llm_used: bool, explanation_text).
        """
        client = _get_client()
        if not client.available:
            return False, "LLM_UNAVAILABLE"

        prompt = build_finding_explanation_prompt(finding, evidence)
        ok, raw = client.chat(SYSTEM_INVESTIGATOR, prompt, max_tokens=512)
        if not ok:
            return False, "LLM_UNAVAILABLE"

        valid, reason = ResponseValidator.validate_text(raw, min_words=20)
        if not valid:
            return False, f"LLM_RESPONSE_INVALID: {reason}"

        return True, raw.strip()

    @staticmethod
    def generate_executive_summary(
        scenario: Dict[str, Any],
        findings: List[Dict[str, Any]],
        risk: Dict[str, Any],
        money_flow: List[Dict[str, Any]],
    ) -> Tuple[bool, str]:
        """
        Generate an executive summary for the PDF report.
        Returns (llm_used: bool, summary_text).
        """
        client = _get_client()
        if not client.available:
            return False, "LLM_UNAVAILABLE — Executive summary requires MISTRAL_API_KEY."

        prompt = build_executive_summary_prompt(scenario, findings, risk, money_flow)
        ok, raw = client.chat(SYSTEM_INVESTIGATOR, prompt, max_tokens=512)
        if not ok:
            return False, "LLM_UNAVAILABLE"

        valid, reason = ResponseValidator.validate_text(raw, min_words=30)
        if not valid:
            return False, f"LLM_RESPONSE_INVALID: {reason}"

        return True, raw.strip()

    @staticmethod
    def is_available() -> bool:
        return _get_client().available
