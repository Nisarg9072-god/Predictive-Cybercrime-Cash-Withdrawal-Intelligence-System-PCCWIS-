from typing import Dict, Any, List
from database.models import StateRiskSummary

class GeographicFeatureExtractor:
    """Extracts features from geographic data."""
    
    @staticmethod
    def extract(states: List[StateRiskSummary]) -> Dict[str, Any]:
        """Calculates geographic features."""
        if not states:
            return {
                "high_risk_state_presence": False,
                "max_incident_density": 0.0,
                "state_count": 0
            }
            
        high_risk = any(s.risk_tier in ["HIGH", "CRITICAL"] for s in states)
        max_density = max(s.incident_density for s in states)
        
        return {
            "high_risk_state_presence": high_risk,
            "max_incident_density": max_density,
            "state_count": len(states)
        }
