import json
from typing import Dict, Any, List
from pydantic import BaseModel
from evidence.models import EvidenceClassification

class EvaluationResult(BaseModel):
    investigation_id: str
    evidence_quality_score: float
    evidence_completeness_score: float
    finding_consistency_score: float
    risk_consistency_score: float
    provenance_score: float
    efficiency_score: float
    overall_score: float
    warnings: List[str]
    failures: List[str]

class EvaluationEngine:
    """Deterministically evaluates an investigation's results."""
    
    @staticmethod
    def evaluate(investigation_result: Any) -> EvaluationResult:
        warnings = []
        failures = []
        
        # We will parse the result object or dict.
        if isinstance(investigation_result, dict):
            evidence = investigation_result.get("evidence", [])
            findings = investigation_result.get("findings", [])
            risk_assessments = investigation_result.get("risk_assessments", [])
            tool_calls = investigation_result.get("tool_calls", 0)
            status = investigation_result.get("status", "UNKNOWN")
            inv_id = investigation_result.get("investigation_id", "UNKNOWN")
        else:
            evidence = getattr(investigation_result, "evidence", [])
            findings = getattr(investigation_result, "findings", [])
            risk_assessments = getattr(investigation_result, "risk_assessments", [])
            tool_calls = getattr(investigation_result, "tool_calls", 0)
            status = getattr(investigation_result, "status", "UNKNOWN")
            inv_id = getattr(investigation_result, "investigation_id", "UNKNOWN")
            
        # A. Evidence Quality (all have valid classifications and confidence > 0.0)
        quality_score = 0.0
        if evidence:
            valid = sum(1 for e in evidence if e.get("confidence", 0) > 0.0 and e.get("classification") in [c.value for c in EvidenceClassification])
            quality_score = valid / len(evidence) * 100.0
        else:
            if status == "COMPLETED":
                failures.append("Completed investigation has no evidence.")
                
        # B. Evidence Completeness
        completeness_score = 100.0 if evidence else 0.0
        
        # C. Finding Consistency (every finding must have evidence)
        consistency_score = 100.0
        if findings:
            valid_findings = 0
            for f in findings:
                ev_ids = f.get("evidence_ids", [])
                if isinstance(ev_ids, str):
                    try:
                        ev_ids = json.loads(ev_ids)
                    except:
                        pass
                if ev_ids and len(ev_ids) > 0:
                    valid_findings += 1
                else:
                    failures.append(f"Finding {f.get('finding_id')} has no evidence.")
            consistency_score = valid_findings / len(findings) * 100.0
            
        # D. Risk-score Consistency
        risk_score = 100.0
        if risk_assessments:
            scores = [r.get("risk_score", 0.0) for r in risk_assessments]
            if not all(0.0 <= s <= 100.0 for s in scores):
                failures.append("Risk score out of bounds (0-100).")
                risk_score = 0.0
                
        # E. Provenance Score
        # Every derived/inferred must have a parent_evidence_id (unless synthetic)
        prov_score = 100.0
        if evidence:
            prov_valid = 0
            prov_total = 0
            for e in evidence:
                c = e.get("classification")
                if c in [EvidenceClassification.DERIVED.value, EvidenceClassification.INFERRED.value, EvidenceClassification.PREDICTED.value]:
                    prov_total += 1
                    if e.get("parent_evidence_id"):
                        prov_valid += 1
                    else:
                        warnings.append(f"Evidence {e.get('evidence_id')} missing parent_evidence_id.")
            if prov_total > 0:
                prov_score = prov_valid / prov_total * 100.0
                
        # F. Efficiency Score
        eff_score = 100.0
        if tool_calls > 20:
            warnings.append(f"High tool call volume ({tool_calls}).")
            eff_score = max(0.0, 100.0 - (tool_calls - 20) * 5)
            
        # Overall
        overall = (quality_score + completeness_score + consistency_score + risk_score + prov_score + eff_score) / 6.0
        
        return EvaluationResult(
            investigation_id=inv_id,
            evidence_quality_score=round(quality_score, 2),
            evidence_completeness_score=round(completeness_score, 2),
            finding_consistency_score=round(consistency_score, 2),
            risk_consistency_score=round(risk_score, 2),
            provenance_score=round(prov_score, 2),
            efficiency_score=round(eff_score, 2),
            overall_score=round(overall, 2),
            warnings=warnings,
            failures=failures
        )
