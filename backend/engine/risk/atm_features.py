from typing import Dict, Any, List
from database.models import ATMRecord

class ATMFeatureExtractor:
    """Extracts features from ATMs."""
    
    @staticmethod
    def extract(atms: List[ATMRecord]) -> Dict[str, Any]:
        """Calculates ATM features."""
        if not atms:
            return {
                "atm_count": 0,
                "high_risk_atm_presence": False,
                "offline_atm_presence": False
            }
            
        high_risk = any(a.cash_availability_index < 0.2 for a in atms)
        offline = any(a.operational_status == "OFFLINE" for a in atms)
        
        return {
            "atm_count": len(atms),
            "high_risk_atm_presence": high_risk,
            "offline_atm_presence": offline
        }
