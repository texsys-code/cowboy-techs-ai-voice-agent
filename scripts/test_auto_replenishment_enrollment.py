#!/usr/bin/env python3
"""
Test script for auto-replenishment enrollment functionality
This script tests the send_auto_replenishment_enrollment_email function
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.call_tools.emails import send_auto_replenishment_enrollment_email

async def test_auto_replenishment_enrollment():
    """Test the auto-replenishment enrollment function"""
    
    print("🧪 Testing Auto-Replenishment Enrollment Function")
    print("=" * 50)
    
    # Test 1: Without equipment ID (not confirmed)
    print("\n📋 Test 1: Enrollment without Equipment ID (not confirmed)")
    print("-" * 40)
    
    try:
        # Mock context with caller information
        class MockContext:
            caller_name = "John Doe"
            caller_company = "Test Company"
            caller_phone_number = "555-123-4567"
            caller_email = "john.doe@testcompany.com"
        
        # Mock the get_job_context function
        import lib.call_tools.emails as emails_module
        emails_module.get_job_context = lambda: MockContext()
        
        result = await send_auto_replenishment_enrollment_email(confirmed=False)
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: With equipment ID (not confirmed)
    print("\n📋 Test 2: Enrollment with Equipment ID (not confirmed)")
    print("-" * 40)
    
    try:
        result = await send_auto_replenishment_enrollment_email(
            equipment_id="XYZ789",
            confirmed=False
        )
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Without equipment ID (confirmed)
    print("\n📋 Test 3: Enrollment without Equipment ID (confirmed)")
    print("-" * 40)
    
    try:
        result = await send_auto_replenishment_enrollment_email(confirmed=True)
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: With equipment ID (confirmed)
    print("\n📋 Test 4: Enrollment with Equipment ID (confirmed)")
    print("-" * 40)
    
    try:
        result = await send_auto_replenishment_enrollment_email(
            equipment_id="XYZ789",
            confirmed=True
        )
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 5: Missing caller information
    print("\n📋 Test 5: Missing caller information")
    print("-" * 40)
    
    try:
        # Mock context with missing caller information
        class MockContextMissing:
            caller_name = None
            caller_company = None
            caller_phone_number = None
            caller_email = None
        
        emails_module.get_job_context = lambda: MockContextMissing()
        
        result = await send_auto_replenishment_enrollment_email(confirmed=True)
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Auto-Replenishment Enrollment Testing Complete!")
    print("\n📝 Test Summary:")
    print("- Test 1: Enrollment without Equipment ID (not confirmed) - Should show confirmation")
    print("- Test 2: Enrollment with Equipment ID (not confirmed) - Should show confirmation with equipment ID")
    print("- Test 3: Enrollment without Equipment ID (confirmed) - Should send email to copier queue")
    print("- Test 4: Enrollment with Equipment ID (confirmed) - Should send email to copier queue with equipment ID")
    print("- Test 5: Missing caller information (confirmed) - Should show error about missing information")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_auto_replenishment_enrollment())
