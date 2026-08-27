from typing import Dict, Any, List
from database.models import ProfileSummary
from .features import FeatureNormalizer

class ProfileFeatureExtractor:
    """Extracts aggregate and normalized features from profiles."""
    
    @staticmethod
    def extract(profiles: List[ProfileSummary]) -> Dict[str, Any]:
        """Calculates profile features."""
        if not profiles:
            return {
                "max_risk_score": 0.0,
                "mule_count": 0,
                "avg_account_age": 0.0,
                "has_new_account": False,
                "has_high_velocity": False,
                "kyc_failed_count": 0
            }
            
        max_risk = max(p.risk_score for p in profiles)
        mule_count = sum(p.is_mule for p in profiles)
        
        total_age = sum(p.account_age_days for p in profiles)
        avg_age = total_age / len(profiles)
        
        # New account defined as < 30 days
        has_new = any(p.account_age_days < 30 for p in profiles)
        
        # High withdrawal velocity defined as > 50000 per day
        has_velocity = any(p.withdrawal_velocity_per_day > 50000 for p in profiles)
        
        kyc_failed = sum(1 for p in profiles if p.kyc_status in ["REJECTED", "PENDING", "FAILED"])
        
        return {
            "max_risk_score": max_risk,
            "mule_count": mule_count,
            "avg_account_age": avg_age,
            "has_new_account": has_new,
            "has_high_velocity": has_velocity,
            "kyc_failed_count": kyc_failed
        }
