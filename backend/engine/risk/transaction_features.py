from typing import List, Dict, Any
from database.models import TransactionSummary

class TransactionFeatureExtractor:
    """Extracts aggregate features from a list of transactions."""
    
    @staticmethod
    def extract(transactions: List[TransactionSummary]) -> Dict[str, Any]:
        """Calculates transaction features from the dataset."""
        if not transactions:
            return {
                "transaction_count": 0,
                "total_amount": 0.0,
                "avg_amount": 0.0,
                "laundering_count": 0,
                "terminal_cashout_count": 0,
                "max_hop_layer": 0,
                "unique_channels": 0,
                "unique_counterparties": 0,
                "has_high_value": False
            }
            
        total_amt = sum(t.amount_inr for t in transactions)
        laundering_count = sum(t.is_laundering for t in transactions)
        cashout_count = sum(t.is_terminal_cashout for t in transactions)
        max_hop = max(t.hop_layer for t in transactions)
        
        channels = set(t.channel for t in transactions if t.channel)
        
        # Calculate counterparties (both incoming and outgoing to the subjects involved)
        counterparties = set()
        for t in transactions:
            counterparties.add(t.from_account_id)
            counterparties.add(t.to_account_id)
            
        high_value = any(t.amount_inr > 50000 for t in transactions)
        
        return {
            "transaction_count": len(transactions),
            "total_amount": total_amt,
            "avg_amount": total_amt / len(transactions),
            "laundering_count": laundering_count,
            "terminal_cashout_count": cashout_count,
            "max_hop_layer": max_hop,
            "unique_channels": len(channels),
            "unique_counterparties": len(counterparties),
            "has_high_value": high_value
        }
