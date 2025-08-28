import re
import logging

logger = logging.getLogger(__name__)

def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False if invalid
    """
    if not email:
        return False
    
    # Basic email validation regex - adjusted for minimal valid emails
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9]{1,}$'
    
    # Check if email matches pattern
    if not re.match(email_pattern, email):
        return False
    
    # Additional checks for common issues
    if '..' in email:  # Double dots
        return False
    
    if ',' in email:  # Commas
        return False
    
    if ' ' in email:  # Spaces
        return False
    
    if len(email) > 254:  # Too long
        return False
    
    # Check for leading/trailing dots in username or domain
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    username, domain = parts
    
    # Allow minimal valid emails like "a@b.c"
    if len(username) >= 1 and len(domain) >= 2:
        # Check for leading/trailing dots only if email is longer than minimal
        if len(email) > 5:
            if username.startswith('.') or username.endswith('.') or domain.startswith('.') or domain.endswith('.'):
                return False
    else:
        return False
    
    return True

def clean_email(email):
    """
    Clean and normalize email address.
    
    Args:
        email: Email address to clean
        
    Returns:
        str: Cleaned email or None if invalid
    """
    if not email:
        return None
    
    # Remove leading/trailing whitespace
    email = email.strip()
    
    # Convert to lowercase
    email = email.lower()
    
    # Validate the cleaned email
    if not validate_email(email):
        return None
    
    return email

def sanitize_for_ai(data):
    """
    Sanitize data to prevent masked/sensitive information from reaching the AI agent.
    
    Args:
        data: The data to sanitize (string, dict, or any object)
        
    Returns:
        Sanitized data safe for AI consumption
    """
    if data is None:
        return None
    
    # If it's a string, sanitize it directly
    if isinstance(data, str):
        return _sanitize_string(data)
    
    # If it's a dict, sanitize all string values
    elif isinstance(data, dict):
        return _sanitize_dict(data)
    
    # If it's a list, sanitize all items
    elif isinstance(data, list):
        return [_sanitize_item(item) for item in data]
    
    # For other types, convert to string and sanitize
    else:
        return _sanitize_string(str(data))

def _sanitize_string(text):
    """Sanitize a single string value."""
    if not text:
        return text
    
    # Replace common masking patterns with descriptive placeholders
    sanitized = text
    
    # Replace asterisk patterns with descriptive text
    sanitized = re.sub(r'\*{3,}', '[MASKED]', sanitized)  # *** or more becomes [MASKED]
    sanitized = re.sub(r'\*{2}', '[REDACTED]', sanitized)  # ** becomes [REDACTED]
    
    # Replace other common masking patterns
    sanitized = re.sub(r'\[REDACTED\]', '[REDACTED]', sanitized)
    sanitized = re.sub(r'\[MASKED\]', '[MASKED]', sanitized)
    sanitized = re.sub(r'\[SENSITIVE\]', '[SENSITIVE]', sanitized)
    
    # Replace password-like patterns
    sanitized = re.sub(r'password\s*[:=]\s*\*+', 'password: [MASKED]', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'api_key\s*[:=]\s*\*+', 'api_key: [MASKED]', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'token\s*[:=]\s*\*+', 'token: [MASKED]', sanitized, flags=re.IGNORECASE)
    
    # Replace database connection strings with masked versions
    sanitized = re.sub(r'//[^:]+:[^@]+@', '//[USERNAME]:[PASSWORD]@', sanitized)
    
    # Replace phone numbers that might contain asterisks - improved logic
    # Handle patterns like 555-***-1234 or 555***1234
    # First, handle the case where asterisks are between digits
    sanitized = re.sub(r'(\d{3})[\*\-]*(\d{3})[\*\-]*(\d{4})', r'\1-\2-\3', sanitized)
    
    # Then handle the case where we have [MASKED] between digits (from previous sanitization)
    sanitized = re.sub(r'(\d{3})-\[MASKED\]-(\d{4})', r'\1-\2', sanitized)
    sanitized = re.sub(r'(\d{3})\[MASKED\](\d{4})', r'\1-\2', sanitized)
    
    # Replace any remaining single asterisks that might be formatting
    sanitized = re.sub(r'(?<!\*)\*(?!\*)', '', sanitized)  # Remove single asterisks not part of patterns
    
    return sanitized

def _sanitize_dict(data_dict):
    """Sanitize all string values in a dictionary."""
    sanitized_dict = {}
    
    for key, value in data_dict.items():
        # Skip internal/system keys that might contain sensitive data
        if key.lower() in ['password', 'api_key', 'token', 'secret', 'credential', 'auth']:
            sanitized_dict[key] = '[MASKED]'
        else:
            sanitized_dict[key] = _sanitize_item(value)
    
    return sanitized_dict

def _sanitize_item(item):
    """Sanitize a single item, handling different types."""
    if isinstance(item, str):
        return _sanitize_string(item)
    elif isinstance(item, dict):
        return _sanitize_dict(item)
    elif isinstance(item, list):
        return [_sanitize_item(subitem) for subitem in item]
    else:
        return item

def is_sanitized_safe(text):
    """
    Check if text is safe for AI consumption (no masking patterns).
    
    Args:
        text: Text to check
        
    Returns:
        bool: True if safe, False if contains masking patterns
    """
    if not text:
        return True
    
    # Check for masking patterns
    masking_patterns = [
        r'\*{2,}',  # Two or more asterisks
        r'\[REDACTED\]',
        r'\[MASKED\]',
        r'\[SENSITIVE\]',
        r'password\s*[:=]\s*\*+',
        r'api_key\s*[:=]\s*\*+',
        r'token\s*[:=]\s*\*+'
    ]
    
    for pattern in masking_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    return True

def log_sanitization_warning(original_data, sanitized_data, context=""):
    """Log a warning when data sanitization occurs."""
    if original_data != sanitized_data:
        logger.warning(f"Data sanitization occurred in {context}: "
                      f"Original contained masking patterns, sanitized for AI consumption")
        logger.debug(f"Sanitization context: {context}")
