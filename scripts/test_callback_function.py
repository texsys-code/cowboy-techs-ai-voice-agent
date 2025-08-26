#!/usr/bin/env python3
"""
Test script for the callback functionality
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.call_tools.callback import request_callback
from config import API_URL

async def test_callback_function():
    """Test the callback function with mock data"""
    
    print("🚀 Testing Callback Function...")
    print(f"API URL: {API_URL}")
    
    # Test 1: No reason provided (should ask for reason)
    print("\n=== Test 1: No reason provided ===")
    try:
        result = await request_callback(reason=None, confirmed=False)
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: With reason but not confirmed (should show confirmation)
    print("\n=== Test 2: With reason but not confirmed ===")
    try:
        result = await request_callback(reason="Technical support question", confirmed=False)
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: With reason and confirmed (should submit to API)
    print("\n=== Test 3: With reason and confirmed ===")
    try:
        result = await request_callback(reason="Technical support question", confirmed=True)
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Callback function tests completed!")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_callback_function())
