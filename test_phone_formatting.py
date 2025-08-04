#!/usr/bin/env python3
"""
Test script to verify phone number formatting works correctly
"""

import re

def format_phone_number(phone_number):
    """
    Format phone number as xxx-xxx-xxxx
    @param phone_number: Raw phone number string
    @return: Formatted phone number or original if can't format
    """
    if not phone_number:
        return phone_number
    
    # Remove all non-digit characters
    digits_only = re.sub(r'[^\d]', '', str(phone_number))
    
    # Handle different length phone numbers
    if len(digits_only) == 10:
        # Standard US format: xxx-xxx-xxxx
        return f"{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        # US with country code: 1-xxx-xxx-xxxx
        return f"{digits_only[1:4]}-{digits_only[4:7]}-{digits_only[7:]}"
    elif len(digits_only) == 7:
        # Local format: xxx-xxxx
        return f"{digits_only[:3]}-{digits_only[3:]}"
    else:
        # Return original if we can't format it properly
        print(f"Warning: Could not format phone number: {phone_number} (digits: {digits_only})")
        return phone_number

def test_phone_formatting():
    """Test various phone number formats"""
    test_cases = [
        # Standard 10-digit numbers
        ("2103808073", "210-380-8073"),
        ("5551234567", "555-123-4567"),
        ("1234567890", "123-456-7890"),
        
        # Numbers with country code
        ("12103808073", "210-380-8073"),
        ("15551234567", "555-123-4567"),
        
        # Numbers with existing formatting
        ("210-380-8073", "210-380-8073"),
        ("(210) 380-8073", "210-380-8073"),
        ("210.380.8073", "210-380-8073"),
        ("210 380 8073", "210-380-8073"),
        
        # 7-digit local numbers
        ("3808073", "380-8073"),
        ("1234567", "123-4567"),
        
        # Edge cases
        ("", ""),
        ("abc", "abc"),
        ("123", "123"),
        ("123456789", "123456789"),  # 9 digits - can't format
        ("12345678901", "12345678901"),  # 11 digits but doesn't start with 1
    ]
    
    print("Testing Phone Number Formatting")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    for input_phone, expected_output in test_cases:
        result = format_phone_number(input_phone)
        if result == expected_output:
            print(f"✅ PASS: '{input_phone}' -> '{result}'")
            passed += 1
        else:
            print(f"❌ FAIL: '{input_phone}' -> '{result}' (expected: '{expected_output}')")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")

if __name__ == "__main__":
    test_phone_formatting() 