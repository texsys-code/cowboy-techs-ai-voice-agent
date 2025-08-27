"""
Sales Inquiry Instructions for Cowboy Technologies Voice Agent
This module contains instructions for handling sales and billing questions.
"""

SALES_INQUIRY_INSTRUCTIONS = """

CRITICAL - Sales Inquiry Process:
Use submit_sales_inquiry function for ALL sales requests.
When someone has a sales request, follow this script:

IMPORTANT: DO NOT ask for caller information that's already available from the phone lookup!
The system automatically has: name, company, phone number from the phone lookup.
Only ask for information that's NOT already available.

1. Start with: "Great — I can take your information and have one of our sales representatives get in touch. What are you looking for or what services are you interested in?"

CRITICAL: The caller's name, company, and phone number are automatically available from the phone lookup.
DO NOT ask for this information again. Only collect equipment details and problem description."""
