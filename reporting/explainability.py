"""
reporting/explainability.py — Structured finding explanations.

Rules:
  - Generated entirely from structured evidence and indicator data.
  - LLM may convert prose to readable sentences ONLY if available.
  - LLM may NOT change risk_score, severity, confidence, or any numeric value.
  - If LLM is unavailable, deterministic template output is used.
  - Never invents evidence not present in the EvidenceItem list.
"""

from typing import Any, Dict, List, Optional

from agent.llm_provider import LLMProvider
from evidence.models import EvidenceItem


_llm = LLMProvider(available=False)


class ExplainabilityService:
    """
    Generates human-readable explanations from structured evidence.

    Output structure:
      {
        "finding_id":    str,
        "title":         str,
        "why":           List[str],   # deterministic bullet points
        "risk":          str,         # "78/100"
        "confidence":    str,         # "0.84"
        "status":        str,
        "evidence_refs": List[str],   # evidence_id[:8] references
        "prose":         str,         # deterministic or LLM-polished prose
        "source":        "DETERMINISTIC" | "LLM_ASSISTED"
      }
    """

    @classmethod
    def explain_finding(
        cls,
        finding_id: str,
        title: str,
        category: str,
        severity: str,
        risk_score: float,
        confidence: float,
        status: str,
        indicators: List[Dict[str, Any]],
        evidence_items: List[EvidenceItem],
    ) -> Dict[str, Any]:
        """
        Produces a structured explanation for a single finding.
        All why-bullets are derived from indicators and evidence, not invented.
        """
        # 1. Build why-bullets from indicators (deterministic)
        why_bullets: List[str] = []
        for ind in indicators:
            why_bullets.append(f"- {ind.get('description', ind.get('name', 'Unknown indicator'))}")

        # 2. Group evidence by indicator
        evidence_refs = [ev.evidence_id[:8] + "…" for ev in evidence_items]

        # 3. Build deterministic prose from template
        # This prose is entirely data-derived — no hallucination possible
        prose = cls._build_deterministic_prose(
            title=title,
            category=category,
            severity=severity,
            risk_score=risk_score,
            confidence=confidence,
            status=status,
            why_bullets=why_bullets,
            evidence_count=len(evidence_items),
        )
        source = "DETERMINISTIC"

        # 4. Optional LLM polish (numeric values are locked; only prose changes)
        if _llm.available:
            prose = cls._llm_polish(
                prose=prose,
                risk_score=risk_score,       # passed as constraint — LLM cannot change
                confidence=confidence,
                severity=severity,
                status=status,
            )
            source = "LLM_ASSISTED"

        return {
            "finding_id":    finding_id,
            "title":         title,
            "why":           why_bullets,
            "risk":          f"{risk_score:.0f}/100",
            "confidence":    f"{confidence:.2f}",
            "status":        status,
            "evidence_refs": evidence_refs,
            "prose":         prose,
            "source":        source,
        }

    @staticmethod
    def _build_deterministic_prose(
        title: str,
        category: str,
        severity: str,
        risk_score: float,
        confidence: float,
        status: str,
        why_bullets: List[str],
        evidence_count: int,
    ) -> str:
        bullets_text = "\n".join(why_bullets) if why_bullets else "- No indicators triggered."
        return (
            f"FINDING: {title}\n\n"
            f"WHY THIS WAS FLAGGED:\n{bullets_text}\n\n"
            f"RISK: {risk_score:.0f}/100\n"
            f"CONFIDENCE: {confidence:.2f}\n"
            f"SEVERITY: {severity}\n"
            f"STATUS: {status}\n\n"
            f"EVIDENCE: {evidence_count} item(s) collected.\n\n"
            f"NOTE: This assessment is based on data patterns observed in structured "
            f"records. It does not constitute a legal determination. Manual expert "
            f"review is required before any enforcement action."
        )

    @staticmethod
    def _llm_polish(
        prose: str,
        risk_score: float,
        confidence: float,
        severity: str,
        status: str,
    ) -> str:
        """
        LLM may only rewrite the prose for readability.
        It receives the locked numeric values and must preserve them exactly.
        This method is only called if LLMProvider.available is True.
        """
        # In current state LLM is unavailable so this is never called.
        # Implementation stub for future wiring.
        locked = (
            f"[LOCKED VALUES — DO NOT CHANGE: "
            f"risk_score={risk_score}, confidence={confidence}, "
            f"severity={severity}, status={status}]"
        )
        # Would call: llm.generate(prompt=f"{locked}\n\nRewrite this assessment:\n{prose}")
        return prose  # Fallback: return unchanged

    @classmethod
    def format_for_pdf(cls, explanation: Dict[str, Any]) -> str:
        """Returns a compact formatted string for the PDF findings section."""
        lines = [
            "─" * 50,
            f"FINDING: {explanation['title']}",
            "",
            "WHY THIS WAS FLAGGED:",
        ]
        for bullet in explanation.get("why", []):
            lines.append(f"  {bullet}")
        lines += [
            "",
            f"RISK:       {explanation['risk']}",
            f"CONFIDENCE: {explanation['confidence']}",
            f"STATUS:     {explanation['status']}",
            "",
            "EVIDENCE:",
        ]
        for ref in explanation.get("evidence_refs", []):
            lines.append(f"  {ref}")
        if explanation.get("source") == "LLM_ASSISTED":
            lines.append("")
            lines.append("[Prose polished by LLM — numeric values unchanged]")
        lines.append("─" * 50)
        return "\n".join(lines)
