"""
agent/llm_provider.py — Delegates to llm.service.LLMService.

Retained for backward compatibility with existing node imports.
"""

from typing import Any, Dict, List, Tuple

from llm.service import LLMService


class LLMProvider:
    """
    Thin adapter used by agent graph nodes.
    Delegates all calls to llm.service.LLMService.
    """

    def __init__(self, available: bool = True):
        # 'available' is now determined by whether MISTRAL_API_KEY is set,
        # not by the constructor argument.
        pass

    @property
    def available(self) -> bool:
        return LLMService.is_available()

    def generate_observation(self, state: Dict[str, Any]) -> Tuple[bool, str]:
        """Deprecated — observations are generated deterministically."""
        return False, "LLM_NOT_USED_FOR_OBSERVATIONS"

    def generate_hypothesis(self, state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        return LLMService.generate_hypothesis(state)

    def rank_actions(
        self,
        state: Dict[str, Any],
        open_hypotheses: List[Dict[str, Any]],
        available_tools: List[str],
    ) -> Tuple[bool, str]:
        completed = state.get("completed_tools", [])
        return LLMService.rank_actions(state, available_tools, completed)

    def summarize_evidence(self, evidence: List[Dict[str, Any]]) -> Tuple[bool, str]:
        if not self.available:
            return False, "LLM_UNAVAILABLE"
        # Build a minimal finding dict for the explanation prompt
        dummy_finding: Dict[str, Any] = {
            "title": "Evidence Summary",
            "category": "SUMMARY",
            "severity": "N/A",
            "confidence": 1.0,
            "description": "Summarise the supplied evidence.",
        }
        return LLMService.explain_finding(dummy_finding, evidence)

    def generate_executive_summary(
        self,
        scenario: Dict[str, Any],
        findings: List[Dict[str, Any]],
        risk: Dict[str, Any],
        money_flow: List[Dict[str, Any]],
    ) -> Tuple[bool, str]:
        return LLMService.generate_executive_summary(scenario, findings, risk, money_flow)
