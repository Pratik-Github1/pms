import re

# ------------------------------------------------------------------------------
# Profile Field Validators
# ------------------------------------------------------------------------------
def validate_mobile_number(mobile: str, field_name: str = None):
    label = field_name if field_name else "Mobile number"

    if not mobile:
        return False, f"{label} is required."

    # Check length and numeric
    if not re.fullmatch(r'\d{10}', mobile):
        return False, f"{label} must be exactly 10 digits and contain only numbers."

    # Number cannot start with 0–5
    if mobile[0] in {'0', '1', '2', '3', '4', '5'}:
        return False, f"{label} cannot start with {mobile[0]}."

    # All digits identical
    if mobile == mobile[0] * 10:
        return False, f"{label} cannot have all same digits."

    # Reject obvious sequential invalid numbers
    invalid_sequences = {"1234567890", "0123456789"}
    if mobile in invalid_sequences:
        return False, f"{label} contains invalid or sequential digits."

    return True, None

def validate_email_address(email: str):

    if not email:
        return False, "Email address is required."

    # Basic RFC 5322 compliant pattern for email validation
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.fullmatch(pattern, email):
        return False, "Invalid email address format."

    # Reject emails with consecutive dots
    if ".." in email:
        return False, "Email address cannot contain consecutive dots."

    # Reject emails starting or ending with special characters
    if email.startswith(".") or email.endswith("."):
        return False, "Email address cannot start or end with a dot."

    # Reject emails with spaces
    if " " in email:
        return False, "Email address cannot contain spaces."

    return True, None

def validate_password(password: str, email: str = None):
    """
    Validate password with rules:
    1. At least one uppercase letter
    2. At least one lowercase letter
    3. At least one number
    4. At least one special character
    5. Minimum 8 characters
    6. Cannot contain parts of the email
    7. Cannot be the same as the email
    """
    if not password:
        return False, "Password is required."

    # Minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # Uppercase
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."

    # Lowercase
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."

    # Number
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."

    # Special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\[\]\\\/]', password):
        return False, "Password must contain at least one special character."

    # Email checks
    if email:
        email_lower = email.lower()
        password_lower = password.lower()

        # Password cannot be same as email
        if password_lower == email_lower:
            return False, "Password cannot be the same as the email address."

        # Password cannot contain parts of email (before @)
        email_username = email_lower.split("@")[0]
        if email_username and email_username in password_lower:
            return False, "Password cannot contain parts of the email address."

    return True, None

def validate_full_name(name: str):
    """
    Validate a person's name.
    Rules:
    - First letter of each word must be capital.
    - Minimum length: 5 characters.
    - Maximum length: 120 characters.
    - Only alphabetic characters and spaces allowed (no digits or special characters).
    - Example: 'Pratik Kumar Pradhan'
    """
    if not name:
        return False, "Name is required."

    name = name.strip()
    name_length = len(name)

    # Length checks
    if name_length < 5:
        return False, "Name must be at least 5 characters long."
    if name_length > 120:
        return False, "Name must not exceed 120 characters."

    # Pattern: Each word starts with capital letter followed by lowercase letters
    pattern = r'^[A-Z][a-z]+(?: [A-Z][a-z]+)*$'
    if not re.fullmatch(pattern, name):
        return False, "Name must start with capital letters and contain only alphabets and spaces."

    return True, None