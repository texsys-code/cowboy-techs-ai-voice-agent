#!/usr/bin/env python3
"""
Test script to verify the Node.js API integration works correctly
"""

import requests
import json
import os
from config import API_URL

def test_caller_search():
    """Test the caller search endpoint"""
    print(f"Testing API at: {API_URL}")
    
    # Test with a sample phone number
    test_phone = "210-380-8073"  # Use the example from the user's data
    
    try:
        response = requests.get(f"{API_URL}/api/callers/search?phone={test_phone}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('success') and result.get('data'):
                caller = result['data']
                print(f"\n✅ Found caller: {caller.get('firstname')} {caller.get('lastname')}")
                print(f"   Company: {caller.get('company')}")
                print(f"   Email: {caller.get('email')}")
                print(f"   Phone: {caller.get('phone')}")
            else:
                print("❌ No caller found")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_halo_health():
    """Test the Halo API health endpoint"""
    try:
        response = requests.get(f"{API_URL}/api/halo/health")
        print(f"\nHalo Health Check - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Halo Health Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Halo Health Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Halo Health Exception: {str(e)}")

def test_ticket_creation():
    """Test ticket creation endpoint"""
    print(f"\nTesting Ticket Creation")
    
    # Check if TEST_MODE is enabled
    test_mode = os.environ.get('TEST_MODE', 'false').lower() == 'true'
    if test_mode:
        print("⚠️  TEST_MODE is enabled - using mock responses")
    
    # Test ticket data
    ticket_data = {
        "summary": "Test Ticket - Test Company",
        "details": "This is a test ticket created by the telephony agent.\n\nCaller Phone Number: 210-380-8073",
        "status_id": 1,
        "tickettype_id": 1,
        "sla_id": 3,
        "priority_id": 4,
        "client_id": 174,
        "site_id": 216,
        "user_id": 267,
        "team_id": 1,
        "agent_id": 1,
        "category_1": "Business Applications",
        "impact": 3,
        "urgency": 2
    }
    
    try:
        response = requests.post(f"{API_URL}/api/halo/tickets", json=ticket_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            print("Ticket Creation Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('success') and result.get('data', {}).get('id'):
                print(f"✅ Ticket created successfully with ID: {result['data']['id']}")
            elif result.get('id'):
                print(f"✅ Ticket created successfully with ID: {result['id']}")
            else:
                print("❌ Ticket created but no ID returned")
        else:
            print(f"❌ Error creating ticket: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception creating ticket: {str(e)}")

if __name__ == "__main__":
    print("Testing Node.js API Integration")
    print("=" * 40)
    
    # Check TEST_MODE status
    test_mode = os.environ.get('TEST_MODE', 'false').lower() == 'true'
    if test_mode:
        print("🔧 TEST_MODE is enabled - using mock responses")
    else:
        print("🔧 TEST_MODE is disabled - using real API calls")
    print()
    
    test_caller_search()
    test_halo_health()
    test_ticket_creation()
    
    print("\n" + "=" * 40)
    print("Test completed!") 