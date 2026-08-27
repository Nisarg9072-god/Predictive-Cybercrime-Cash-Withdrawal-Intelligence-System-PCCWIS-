from typing import Any, Optional

class FeatureNormalizer:
    """
    Deterministic feature normalization.
    Converts various inputs into normalized numerical features (0.0 to 1.0).
    """

    @staticmethod
    def normalize_min_max(value: Optional[float], min_val: float, max_val: float, default: float = 0.0) -> float:
        """
        Normalizes a value between 0.0 and 1.0 using min/max bounds.
        If value is missing, returns default.
        """
        if value is None:
            return default
            
        if max_val <= min_val:
            return default
            
        clamped = max(min_val, min(value, max_val))
        return (clamped - min_val) / (max_val - min_val)

    @staticmethod
    def safe_divide(numerator: Optional[float], denominator: Optional[float], default: float = 0.0) -> float:
        """
        Safely divide two numbers, avoiding division by zero.
        """
        if numerator is None or denominator is None or denominator == 0:
            return default
        return numerator / denominator
        
    @staticmethod
    def map_categorical(value: Any, mapping: dict, default: float = 0.0) -> float:
        """
        Maps a categorical value to a float using a provided mapping.
        """
        if value is None:
            return default
        return mapping.get(value, default)
