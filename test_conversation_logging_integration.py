#!/usr/bin/env python3
"""
Test script to verify conversation logging integration in telephony_agent.py
"""

import asyncio
import requests
import json
import os
from datetime import datetime

# Import the logging functions from telephony_agent
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock API URL for testing
API_URL = "http://localhost:3000"

async def test_call_logging_integration():
    """Test the conversation logging integration"""
    print("🧪 Testing Conversation Logging Integration")
    print("=" * 50)
    
    # Test 1: Initialize call logging
    print("\n1. Testing call initialization...")
    try:
        # Mock context object
        class MockContext:
            def __init__(self):
                self.room = type('Room', (), {'name': 'test-room-123'})()
                self.caller_name = "John Doe"
                self.caller_company = "Test Company"
                self.halo_user_id = "123"
                self.halo_client_id = "456"
                self.halo_site_id = "789"
        
        ctx = MockContext()
        
        # Test call initialization
        call_data = {
            "room_name": ctx.room.name,
            "caller_phone": "555-123-4567",
            "caller_name": ctx.caller_name,
            "caller_company": ctx.caller_company,
            "agent_name": "telephony_agent",
            "status": "active",
            "halo_user_id": ctx.halo_user_id,
            "halo_client_id": ctx.halo_client_id,
            "halo_site_id": ctx.halo_site_id
        }
        
        response = requests.post(f"{API_URL}/api/calls", json=call_data)
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                call_id = result['data']['call_id']
                ctx.call_id = call_id
                print(f"✅ Call initialized successfully with ID: {call_id}")
            else:
                print(f"❌ Failed to initialize call: {result.get('message')}")
                return
        else:
            print(f"❌ API error initializing call: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error testing call initialization: {str(e)}")
        return
    
    # Test 2: Log system event (call start)
    print("\n2. Testing system event logging...")
    try:
        system_event_data = {
            "call_id": ctx.call_id,
            "speaker": "system",
            "message": "Call started",
            "message_type": "system_event"
        }
        
        response = requests.post(f"{API_URL}/api/conversations/system-event", json=system_event_data)
        if response.status_code == 201:
            print("✅ System event logged successfully")
        else:
            print(f"❌ Failed to log system event: {response.status_code}")
    except Exception as e:
        print(f"❌ Error logging system event: {str(e)}")
    
    # Test 3: Log agent message
    print("\n3. Testing agent message logging...")
    try:
        agent_message_data = {
            "call_id": ctx.call_id,
            "speaker": "agent",
            "speaker_name": "telephony_agent",
            "message": "Hello! Welcome to IBT. How can I help you today?",
            "message_type": "speech",
            "language": "en-US"
        }
        
        response = requests.post(f"{API_URL}/api/conversations", json=agent_message_data)
        if response.status_code == 201:
            print("✅ Agent message logged successfully")
        else:
            print(f"❌ Failed to log agent message: {response.status_code}")
    except Exception as e:
        print(f"❌ Error logging agent message: {str(e)}")
    
    # Test 4: Log caller message
    print("\n4. Testing caller message logging...")
    try:
        caller_message_data = {
            "call_id": ctx.call_id,
            "speaker": "caller",
            "message": "I need help with my computer",
            "message_type": "speech",
            "confidence": 0.95,
            "language": "en-US"
        }
        
        response = requests.post(f"{API_URL}/api/conversations", json=caller_message_data)
        if response.status_code == 201:
            print("✅ Caller message logged successfully")
        else:
            print(f"❌ Failed to log caller message: {response.status_code}")
    except Exception as e:
        print(f"❌ Error logging caller message: {str(e)}")
    
    # Test 5: Log function call
    print("\n5. Testing function call logging...")
    try:
        function_call_data = {
            "call_id": ctx.call_id,
            "speaker": "agent",
            "speaker_name": "telephony_agent",
            "message": "Function call: get_open_it_support_ticket",
            "message_type": "function_call",
            "function_name": "get_open_it_support_ticket",
            "function_args": {
                "name": "John Doe",
                "company": "Test Company",
                "details": "Computer not working",
                "confirmed": True
            },
            "function_result": "Your IT support ticket has been opened. Ticket ID: 12345"
        }
        
        response = requests.post(f"{API_URL}/api/conversations/function-call", json=function_call_data)
        if response.status_code == 201:
            print("✅ Function call logged successfully")
        else:
            print(f"❌ Failed to log function call: {response.status_code}")
    except Exception as e:
        print(f"❌ Error logging function call: {str(e)}")
    
    # Test 6: Get conversation
    print("\n6. Testing conversation retrieval...")
    try:
        response = requests.get(f"{API_URL}/api/conversations/{ctx.call_id}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                messages = result['data']
                print(f"✅ Retrieved {len(messages)} conversation messages")
                for i, msg in enumerate(messages[:3]):  # Show first 3 messages
                    print(f"   {i+1}. [{msg['speaker']}] {msg['message'][:50]}...")
            else:
                print(f"❌ Failed to retrieve conversation: {result.get('message')}")
        else:
            print(f"❌ Failed to retrieve conversation: {response.status_code}")
    except Exception as e:
        print(f"❌ Error retrieving conversation: {str(e)}")
    
    # Test 7: End call
    print("\n7. Testing call ending...")
    try:
        end_data = {
            "status": "completed",
            "summary": "Test call completed successfully",
            "ticket_created": True,
            "ticket_id": "12345"
        }
        
        response = requests.put(f"{API_URL}/api/calls/{ctx.call_id}/end", json=end_data)
        if response.status_code == 200:
            print("✅ Call ended successfully")
        else:
            print(f"❌ Failed to end call: {response.status_code}")
    except Exception as e:
        print(f"❌ Error ending call: {str(e)}")
    
    # Test 8: Get call statistics
    print("\n8. Testing call statistics...")
    try:
        response = requests.get(f"{API_URL}/api/conversations/{ctx.call_id}/stats")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                stats = result['data']
                print(f"✅ Call statistics retrieved:")
                print(f"   - Total messages: {stats.get('total_messages', 0)}")
                print(f"   - Caller messages: {stats.get('caller_messages', 0)}")
                print(f"   - Agent messages: {stats.get('agent_messages', 0)}")
                print(f"   - Function calls: {stats.get('function_calls', 0)}")
                print(f"   - System events: {stats.get('system_events', 0)}")
            else:
                print(f"❌ Failed to get statistics: {result.get('message')}")
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting statistics: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Conversation logging integration test completed!")

def test_api_connectivity():
    """Test basic API connectivity"""
    print("🔌 Testing API connectivity...")
    try:
        response = requests.get(f"{API_URL}/api/halo/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is accessible")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - make sure it's running on localhost:3000")
        return False
    except Exception as e:
        print(f"❌ Error testing API connectivity: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Conversation Logging Integration Tests")
    print(f"📡 API URL: {API_URL}")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("\n❌ API connectivity test failed. Please ensure the Node.js API is running.")
        print("   Run: cd api && npm start")
        sys.exit(1)
    
    # Run the integration tests
    asyncio.run(test_call_logging_integration()) 