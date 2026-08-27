import hashlib

class Sanitizer:
    @staticmethod
    def mask_account_number(account: str) -> str:
        if not account:
            return account
        if len(account) <= 4:
            return "****"
        return f"****{account[-4:]}"

    @staticmethod
    def mask_phone_number(phone: str) -> str:
        if not phone:
            return phone
        if len(phone) <= 4:
            return "****"
        return f"{phone[:3]}****{phone[-4:]}"

    @staticmethod
    def mask_pan(pan: str) -> str:
        if not pan or len(pan) < 10:
            return "****"
        return f"{pan[:2]}******{pan[-2:]}"

    @staticmethod
    def hash_identifier(identifier: str) -> str:
        if not identifier:
            return ""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    @staticmethod
    def sanitize_profile(profile_data: dict) -> dict:
        """Sanitizes sensitive fields in a profile dictionary."""
        sanitized = profile_data.copy()
        
        if "account_number" in sanitized and sanitized["account_number"]:
            sanitized["account_number"] = Sanitizer.mask_account_number(sanitized["account_number"])
        if "phone" in sanitized and sanitized["phone"]:
            sanitized["phone"] = Sanitizer.mask_phone_number(sanitized["phone"])
        if "pan" in sanitized and sanitized["pan"]:
            sanitized["pan"] = Sanitizer.mask_pan(sanitized["pan"])
            
        return sanitized
