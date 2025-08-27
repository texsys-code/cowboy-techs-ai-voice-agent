"""
IT Support Ticket Instructions for Cowboy Technologies Voice Agent
This module contains instructions for handling IT support ticket requests.
"""

IT_SUPPORT_INSTRUCTIONS = """

Ticket Creation Process:
When someone wants to open a support ticket:
1. Ask for details about their issue if not provided
2. Use the open_it_support_ticket function with details=their_issue and confirmed=False to show confirmation
3. Wait for user to say "yes" to confirm
4. Use the open_it_support_ticket function again with details=their_issue and confirmed=True to create the ticket
5. Provide the ticket number when complete
6. Ask if there's anything else you can help with

IMPORTANT: You must call the function TWICE:
- First call: confirmed=False to show confirmation message
- Second call: confirmed=True to actually create the ticket"""
