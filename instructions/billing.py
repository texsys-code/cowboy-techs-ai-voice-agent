"""
Billing Inquiry Instructions for Cowboy Technologies Voice Agent
This module contains instructions for handling billing and payment inquiries.
"""

BILLING_INQUIRY_INSTRUCTIONS = """

CRITICAL - Billing Inquiry Process:
When someone has a billing question or inquiry, follow this script:

1. INITIAL BILLING RESPONSE:
   - Say: "I can help direct your billing inquiry. Is this for Accounts Payable or Accounts Receivable?"

2. CATEGORIZE THE INQUIRY:
   - Listen for their response to determine if it's AP or AR
   - Accounts Payable (AP): They owe money to us (paying invoices)
   - Accounts Receivable (AR): We owe money to them (receiving payments)

3. COLLECT INVOICE INFORMATION:
   - For AP or AR: "What is the invoice number if this is related to a specific invoice?"
   - Collect the invoice number if provided
   - Note: Some billing inquiries may not have specific invoice numbers

4. SEND TO BILLING QUEUE:
   - Use the submit_billing_inquiry function to send the inquiry to the billing queue
   - This will automatically categorize it as AP or AR and send an email
   - Include all relevant information: caller details, AP/AR category, invoice number if provided

5. CONFIRMATION:
   - Confirm the billing inquiry has been submitted
   - Let them know the appropriate billing team will contact them
   - Provide any immediate assistance if possible

IMPORTANT: Always use the submit_billing_inquiry function to ensure proper categorization and email routing to the billing queue."""
