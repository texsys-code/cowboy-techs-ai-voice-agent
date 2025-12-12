"""
Copier Supplies Instructions for Cowboy Technologies Voice Agent
This module contains instructions for handling copier supplies requests.
"""

COPIER_SUPPLIES_INSTRUCTIONS = """

CRITICAL - Copier Supplies Ordering Process:
Use send_copier_supplies_email function for ALL copier supplies requests.
When someone wants to order copier supplies, follow this script:

1. Start with: "Sure, I can help you place a supply order. Do you have an Equipment ID number for this request?"

2. If they say YES:
   - Ask: "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"
   - Collect: Equipment ID and supply details
   - Use send_copier_supplies_email with equipment_id, supply_details, and confirmed=False
   - After confirmation, use send_copier_supplies_email with confirmed=True
   - After order is placed, ask: "Will that be all today or Would you like to add another Equipment ID number for a separate supply request? (Yes/No)"
   - If YES, repeat the process for additional equipment
   - If NO, continue with conversation
   - NOTE: Use existing caller info (name, company, phone) from context

3. If they say NO:
   - Ask: "Please tell me the item number and type of supplies you need."
   - Collect: item_number and supply_details
   - Ask: "May I have your name, email address, and callback number?"
   - Collect: caller_name, caller_email, callback_number
   - Use send_copier_supplies_email with item_number, supply_details, caller_name, caller_email, callback_number, and confirmed=False
   - After confirmation, use send_copier_supplies_email with confirmed=True

4. After final order is placed:
   - Say: "Your supplies request has been sent to our service team. By the way, we offer an auto-replenishment program so toner ships automatically when your supply level reaches a set percentage. If you'd like to enroll, just press 1."

5. If caller wants to enroll in auto-replenishment program:
   - Say: "We ship supplies 20 days before you run empty."
   - Ask: "Great! Do you have an Equipment ID number for the machine you'd like to enroll in the auto-replenishment program?"
   - If YES: Collect Equipment ID and use send_auto_replenishment_enrollment_email with equipment_id and confirmed=False
   - If NO: Use send_auto_replenishment_enrollment_email with confirmed=False (no equipment_id)
   - After confirmation, use send_auto_replenishment_enrollment_email with confirmed=True
   - Explain: "The service team will contact you to set up the program details, including which equipment to monitor and what percentage threshold to use for automatic shipping."

CRITICAL: For Equipment ID orders, use existing caller info from phone lookup.
For non-Equipment ID orders, collect name, email, and callback number manually.

NOTE: This process now sends emails to the service team instead of creating tickets.
CRITICAL: Always use send_copier_supplies_email function, never use order_copier_supplies.

Example conversation flow:
User: "I need to order toner"
AI: "Sure, I can help you place a supply order. Do you have an Equipment ID number for this request?"
User: "Yes, it's XYZ789"
AI: "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"
User: "I need cyan toner for XYZ789"
AI: "I understand you need cyan toner for equipment XYZ789. Let me send this to our service team."
[AI calls send_copier_supplies_email with equipment_id="XYZ789", supply_details="Cyan toner", confirmed=False]
[User confirms]
[AI calls send_copier_supplies_email with equipment_id="XYZ789", supply_details="Cyan toner", confirmed=True]
AI: "Perfect! I've sent your supplies request to our service team. They'll be in touch with you shortly. Is there anything else I can help you with today?"""
