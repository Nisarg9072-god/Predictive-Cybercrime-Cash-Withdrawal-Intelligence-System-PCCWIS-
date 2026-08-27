from typing import Dict, Any, List
from database.models import TransactionChainSummary

class ChainFeatureExtractor:
    """Extracts features from transaction chains."""
    
    @staticmethod
    def extract(chains: List[TransactionChainSummary]) -> Dict[str, Any]:
        """Calculates aggregate chain features."""
        if not chains:
            return {
                "max_chain_length": 0,
                "total_chain_amount": 0.0,
                "multi_hop_presence": False,
                "chain_count": 0
            }
            
        max_length = max(c.hop_count for c in chains)
        total_amount = sum(c.total_amount for c in chains)
        
        multi_hop = any(c.hop_count >= 3 for c in chains)
        
        return {
            "max_chain_length": max_length,
            "total_chain_amount": total_amount,
            "multi_hop_presence": multi_hop,
            "chain_count": len(chains)
        }
