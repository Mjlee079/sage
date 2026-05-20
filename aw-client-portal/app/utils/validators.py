"""
SAGEN-Sync: Form Validation Utilities
=====================================

Shared validation functions used across routes and models.
Centralizes validation logic to prevent duplication.

Usage:
    from app.utils.validators import validate_ssn_last_four, validate_dob
    
    is_valid = validate_ssn_last_four("1234")  # True
    is_valid = validate_ssn_last_four("123")   # False (too short)
    is_valid = validate_dob("1970-05-15")      # True
    is_valid = validate_dob("invalid")         # False
"""

import re
from datetime import datetime


def validate_ssn_last_four(ssn):
    """
    Validate the last four digits of an SSN.
    
    Rules:
        - Must be exactly 4 digits
        - Only numeric characters
        - No sequential patterns (e.g., "0000", "1111")
    
    Args:
        ssn (str): The last four digits of SSN
    
    Returns:
        tuple: (bool is_valid, str error_message)
    """
    if not ssn:
        return False, "SSN last four is required"
    
    # Remove any formatting characters
    cleaned = str(ssn).strip()
    
    # Check length
    if len(cleaned) != 4:
        return False, "SSN last four must be exactly 4 digits"
    
    # Check numeric
    if not cleaned.isdigit():
        return False, "SSN last four must contain only numbers"
    
    # Check for obvious patterns
    if cleaned in ["0000", "1111", "2222", "3333", "4444",
                    "5555", "6666", "7777", "8888", "9999"]:
        return False, "SSN cannot have all identical digits"
    
    return True, ""


def validate_dob(date_string):
    """
    Validate a date of birth string.
    
    Rules:
        - Must be valid date
        - Person must be at least 18 years old
        - Person must not be older than 120 years
    
    Args:
        date_string (str): Date in YYYY-MM-DD format
    
    Returns:
        tuple: (bool is_valid, str age_or_error)
    """
    if not date_string:
        return False, "Date of birth is required"
    
    try:
        dob = datetime.strptime(str(date_string), "%Y-%m-%d")
        today = datetime.now()
        
        # Calculate age
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        
        # Validation rules
        if age < 18:
            return False, f"Age ({age}) is below minimum of 18"
        
        if age > 120:
            return False, f"Age ({age}) exceeds maximum of 120"
        
        if dob > today:
            return False, "Date of birth cannot be in the future"
        
        return True, str(age)
        
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"


def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): Email address
    
    Returns:
        tuple: (bool is_valid, str error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, ""


def validate_currency(amount):
    """
    Validate a currency amount.
    
    Args:
        amount: Currency value
    
    Returns:
        tuple: (bool is_valid, str error_message)
    """
    try:
        value = float(amount)
        if value < 0:
            return False, "Amount cannot be negative"
        return True, ""
    except (ValueError, TypeError):
        return False, "Invalid amount"
