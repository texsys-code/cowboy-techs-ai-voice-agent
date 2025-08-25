#!/usr/bin/env python3
"""
Test script for data sanitization functionality.
This script tests the sanitize_for_ai function to ensure it properly handles masked data.
"""

import sys
import os

# Add the lib directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from utils import sanitize_for_ai, is_sanitized_safe, log_sanitization_warning

def test_sanitization():
    """Test various sanitization scenarios."""
    
    print("Testing Data Sanitization for AI Agent")
    print("=" * 50)
    
    # Test cases with expected results
    test_cases = [
        # Basic masking patterns
        ("***", "[MASKED]"),
        ("**", "[REDACTED]"),
        ("****", "[MASKED]"),
        
        # Password patterns
        ("password: ***", "password: [MASKED]"),
        ("API_KEY=***", "API_KEY=[MASKED]"),
        ("token:***", "token:[MASKED]"),
        
        # Database connection strings
        ("mongodb://user:pass@host", "mongodb://[USERNAME]:[PASSWORD]@host"),
        ("postgresql://admin:secret@localhost", "postgresql://[USERNAME]:[PASSWORD]@localhost"),
        
        # Phone numbers with asterisks
        ("555-***-1234", "555-1234"),
        ("555***1234", "555-1234"),
        
        # Mixed content
        ("Name: John, Company: ***, Phone: 555-1234", "Name: John, Company: [MASKED], Phone: 555-1234"),
        
        # Normal content (should not change)
        ("Hello World", "Hello World"),
        ("Phone: 555-1234", "Phone: 555-1234"),
        ("Company: Acme Corp", "Company: Acme Corp"),
        
        # Edge cases
        ("", ""),
        (None, None),
        ("*", ""),  # Single asterisk should be removed
        ("**", "[REDACTED]"),  # Double asterisk becomes [REDACTED]
    ]
    
    passed = 0
    failed = 0
    
    for test_input, expected_output in test_cases:
        try:
            result = sanitize_for_ai(test_input)
            if result == expected_output:
                print(f"✅ PASS: '{test_input}' -> '{result}'")
                passed += 1
            else:
                print(f"❌ FAIL: '{test_input}' -> '{result}' (expected: '{expected_output}')")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: '{test_input}' -> Exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Data sanitization is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the sanitization logic.")
    
    return failed == 0

def test_safety_check():
    """Test the safety checking functionality."""
    
    print("\nTesting Safety Check Functionality")
    print("=" * 50)
    
    # Test cases for safety checking
    safety_tests = [
        ("Hello World", True),  # Safe
        ("***", False),  # Not safe
        ("**", False),  # Not safe
        ("password: ***", False),  # Not safe
        ("Name: John", True),  # Safe
        ("[MASKED]", False),  # Contains placeholder
        ("[REDACTED]", False),  # Contains placeholder
        ("", True),  # Empty is safe
        (None, True),  # None is safe
    ]
    
    passed = 0
    failed = 0
    
    for test_input, expected_safe in safety_tests:
        try:
            is_safe = is_sanitized_safe(test_input)
            if is_safe == expected_safe:
                print(f"✅ PASS: '{test_input}' -> Safe: {is_safe}")
                passed += 1
            else:
                print(f"❌ FAIL: '{test_input}' -> Safe: {is_safe} (expected: {expected_safe})")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: '{test_input}' -> Exception: {e}")
            failed += 1
    
    print(f"\nSafety Check Results: {passed} passed, {failed} failed")
    return failed == 0

def test_dict_sanitization():
    """Test sanitization of dictionary data."""
    
    print("\nTesting Dictionary Sanitization")
    print("=" * 50)
    
    test_dict = {
        "name": "John Doe",
        "company": "***",
        "phone": "555-***-1234",
        "email": "john@company.com",
        "password": "secret123",
        "api_key": "***",
        "nested": {
            "internal_id": "***",
            "status": "active"
        }
    }
    
    expected_sanitized = {
        "name": "John Doe",
        "company": "[MASKED]",
        "phone": "555-1234",
        "email": "john@company.com",
        "password": "[MASKED]",
        "api_key": "[MASKED]",
        "nested": {
            "internal_id": "[MASKED]",
            "status": "active"
        }
    }
    
    try:
        sanitized = sanitize_for_ai(test_dict)
        
        # Check if the sanitization worked correctly
        if sanitized == expected_sanitized:
            print("✅ PASS: Dictionary sanitization working correctly")
            print(f"   Input: {test_dict}")
            print(f"   Output: {sanitized}")
            return True
        else:
            print("❌ FAIL: Dictionary sanitization not working correctly")
            print(f"   Expected: {expected_sanitized}")
            print(f"   Got: {sanitized}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Dictionary sanitization failed with exception: {e}")
        return False

def main():
    """Run all tests."""
    print("Data Sanitization Test Suite")
    print("This script tests the sanitization functions to prevent masked data from reaching the AI agent.")
    print()
    
    # Run all tests
    test1_passed = test_sanitization()
    test2_passed = test_safety_check()
    test3_passed = test_dict_sanitization()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The data sanitization system is working correctly and will prevent")
        print("masked data (like ***) from reaching the AI agent.")
        print("\nThis should fix the issue where the AI agent was saying 'asterisk'")
        print("when reading back information.")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED!")
        print("Please review the sanitization logic before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
