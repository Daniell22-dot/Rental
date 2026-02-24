# backend/app/core/validators.py
import re
from app.core.exceptions import ValidationException

class PasswordValidator:
    """Validate password strength and constraints"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 72  # bcrypt limit
    
    @staticmethod
    def validate(password: str) -> dict:
        """
        Validate password and return errors if any.
        Returns: {"valid": bool, "errors": [list of error messages]}
        """
        errors = []
        
        # Check length
        if len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(f"Password must be at least {PasswordValidator.MIN_LENGTH} characters")
        
        if len(password) > PasswordValidator.MAX_LENGTH:
            errors.append(f"Password cannot exceed {PasswordValidator.MAX_LENGTH} characters (bcrypt limit)")
        
        # Check complexity
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_or_raise(password: str) -> None:
        """Validate password and raise exception if invalid"""
        result = PasswordValidator.validate(password)
        if not result["valid"]:
            error_msg = " | ".join(result["errors"])
            raise ValidationException(detail=error_msg)

class EmailValidator:
    """Validate email format"""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @staticmethod
    def validate(email: str) -> bool:
        """Check if email is valid"""
        return re.match(EmailValidator.EMAIL_PATTERN, email) is not None
    
    @staticmethod
    def validate_or_raise(email: str) -> None:
        """Validate email and raise exception if invalid"""
        if not EmailValidator.validate(email):
            raise ValidationException(detail="Invalid email format")

class PhoneValidator:
    """Validate phone numbers (Kenya focus)"""
    
    # Kenya phone pattern: +254... or 0... or just 7 digits for shortcode
    KENYA_PATTERN = r'^(\+254|0|254)?([1-9]\d{7,8})$'
    
    @staticmethod
    def validate(phone: str) -> bool:
        """Check if phone is valid Kenya number"""
        # Remove spaces and dashes
        cleaned = phone.replace(' ', '').replace('-', '')
        return re.match(PhoneValidator.KENYA_PATTERN, cleaned) is not None
    
    @staticmethod
    def validate_or_raise(phone: str) -> None:
        """Validate phone and raise exception if invalid"""
        if not PhoneValidator.validate(phone):
            raise ValidationException(detail="Invalid phone number. Please use Kenya format (e.g., 0712345678 or +254712345678)")
    
    @staticmethod
    def normalize(phone: str) -> str:
        """Normalize phone to standard format (254XXXXXXXXX)"""
        cleaned = phone.replace(' ', '').replace('-', '')
        
        # Convert 0 prefix to 254
        if cleaned.startswith('0'):
            return '254' + cleaned[1:]
        # Remove + if present
        elif cleaned.startswith('+254'):
            return cleaned[1:]
        # Assume 254 if just digits
        elif cleaned.startswith('254'):
            return cleaned
        else:
            return phone
