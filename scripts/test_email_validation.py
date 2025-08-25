#!/usr/bin/env python3
"""
Test script for email validation functionality.
This script tests the email validation functions to ensure invalid emails are properly rejected.
"""

import sys
import os

# Add the lib directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from utils import validate_email, clean_email

def test_email_validation():
    """Test various email validation scenarios."""
    
    print("Testing Email Validation")
    print("=" * 50)
    
    # Test cases with expected results
    test_cases = [
        # Valid emails (should pass)
        ("john.doe@company.com", True),
        ("jane@example.org", True),
        ("user123@domain.co.uk", True),
        ("test+tag@email.com", True),
        ("user.name@subdomain.domain.com", True),
        
        # Invalid emails (should fail)
        ("travis.thomsen@ibt,inc..com", False),  # Comma and double dots
        ("invalid@email", False),  # Missing domain
        ("@domain.com", False),  # Missing username
        ("user@.com", False),  # Missing domain name
        ("user..name@domain.com", False),  # Double dots in username
        ("user@domain..com", False),  # Double dots in domain
        ("user name@domain.com", False),  # Space in username
        ("user@domain name.com", False),  # Space in domain
        ("user@domain.com.", False),  # Trailing dot
        (".user@domain.com", False),  # Leading dot
        ("", False),  # Empty string
        (None, False),  # None value
        
        # Edge cases
        ("a@b.c", True),  # Minimal valid email
        ("very.long.email.address.that.exceeds.normal.length@very.long.domain.name.that.also.exceeds.normal.length.com", True),  # Long but valid
    ]
    
    passed = 0
    failed = 0
    
    for test_input, expected_valid in test_cases:
        try:
            is_valid = validate_email(test_input)
            if is_valid == expected_valid:
                print(f"✅ PASS: '{test_input}' -> Valid: {is_valid}")
                passed += 1
            else:
                print(f"❌ FAIL: '{test_input}' -> Valid: {is_valid} (expected: {expected_valid})")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: '{test_input}' -> Exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All email validation tests passed!")
    else:
        print("⚠️  Some email validation tests failed. Please review the validation logic.")
    
    return failed == 0

def test_email_cleaning():
    """Test email cleaning functionality."""
    
    print("\nTesting Email Cleaning")
    print("=" * 50)
    
    # Test cases for cleaning
    cleaning_tests = [
        # Normal cleaning
        ("  JOHN.DOE@COMPANY.COM  ", "john.doe@company.com"),  # Trim and lowercase
        ("User.Name@Domain.Com", "user.name@domain.com"),  # Lowercase conversion
        
        # Invalid emails that should return None
        ("travis.thomsen@ibt,inc..com", None),  # Invalid format
        ("invalid@email", None),  # Missing domain
        ("", None),  # Empty
        (None, None),  # None
    ]
    
    passed = 0
    failed = 0
    
    for test_input, expected_output in cleaning_tests:
        try:
            cleaned = clean_email(test_input)
            if cleaned == expected_output:
                print(f"✅ PASS: '{test_input}' -> '{cleaned}'")
                passed += 1
            else:
                print(f"❌ FAIL: '{test_input}' -> '{cleaned}' (expected: '{expected_output}')")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: '{test_input}' -> Exception: {e}")
            failed += 1
    
    print(f"\nEmail Cleaning Results: {passed} passed, {failed} failed")
    return failed == 0

def test_specific_problem_case():
    """Test the specific problematic email that was reported."""
    
    print("\nTesting Specific Problem Case")
    print("=" * 50)
    
    problematic_email = "travis.thomsen@ibt,inc..com"
    
    print(f"Problematic email: {problematic_email}")
    
    # Test validation
    is_valid = validate_email(problematic_email)
    print(f"Validation result: {is_valid}")
    
    # Test cleaning
    cleaned = clean_email(problematic_email)
    print(f"Cleaning result: {cleaned}")
    
    if not is_valid and cleaned is None:
        print("✅ PASS: Problematic email properly rejected")
        return True
    else:
        print("❌ FAIL: Problematic email not properly handled")
        return False

def main():
    """Run all email validation tests."""
    print("Email Validation Test Suite")
    print("This script tests the email validation functions to ensure invalid emails")
    print("like 'travis.thomsen@ibt,inc..com' are properly rejected.")
    print()
    
    # Run all tests
    test1_passed = test_email_validation()
    test2_passed = test_email_cleaning()
    test3_passed = test_specific_problem_case()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 ALL EMAIL VALIDATION TESTS PASSED!")
        print("The email validation system is working correctly and will prevent")
        print("invalid emails like 'travis.thomsen@ibt,inc..com' from being accepted.")
        print("\nThis should fix the issue where invalid emails were being stored.")
        return 0
    else:
        print("⚠️  SOME EMAIL VALIDATION TESTS FAILED!")
        print("Please review the email validation logic before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
