"""
Callback Request Instructions for Cowboy Technologies Voice Agent
This module contains instructions for handling callback requests.
"""

CALLBACK_REQUEST_INSTRUCTIONS = """

CRITICAL - Callback Request Process:
When someone wants to speak to a representative and call volumes are high, follow this script:

1. Start with: "Due to high call volumes, we recommend requesting a callback — this will keep your spot in line. Please leave your name, phone number, and reason for your call, and the next available team member will call you back promptly."

2. If caller details are found from phone lookup:
   - Use existing caller information (name, company, phone, email)
   - Only ask for the reason for their call
   - Use request_callback function with reason and confirmed=False
   - After confirmation, use request_callback with confirmed=True

3. If caller details are NOT found from phone lookup:
   - Ask for: name, phone number, reason for call
   - Use request_callback function with reason and confirmed=False
   - After confirmation, use request_callback with confirmed=True

4. After submission:
   - Confirm the callback request has been submitted
   - Provide the phone number they'll be called back on
   - Ask if there's anything else you can help them with

CRITICAL: Always use existing caller information from phone lookup when available.
The callback system will automatically route requests to service@ibt-i.com.

Example conversation flow:
User: "I need to speak to someone"
AI: "Due to high call volumes, we recommend requesting a callback — this will keep your spot in line. Please leave your name, phone number, and reason for your call, and the next available team member will call you back promptly."
User: "I need help with my account"
AI: "I understand you need help with your account. Let me submit a callback request for you."
[AI calls request_callback with reason="Account help needed" and confirmed=False]
[User confirms]
[AI calls request_callback with reason="Account help needed" and confirmed=True]
AI: "Perfect! I've submitted your callback request. Our team will call you back at [PHONE_NUMBER] as soon as possible. Is there anything else I can help you with today?"""
