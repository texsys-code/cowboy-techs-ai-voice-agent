"""
Call Tools package for Cowboy Technologies Voice Agent.
This package contains tools for handling various types of call interactions.
"""

# Import all the call tool functions
from .end_call import end_call
from .caller import lookup_caller, store_caller_info, format_phone_number, collect_caller_info
from .tickets import open_it_support_ticket, debug_ticket_context, collect_caller_email
from .emails import send_copier_support_email, send_copier_supplies_email
from .sales import submit_sales_inquiry, test_email_system
from .billing import submit_billing_inquiry
from .callback import request_callback

__all__ = [
    'end_call',
    'lookup_caller',
    'store_caller_info',
    'format_phone_number',
    'collect_caller_info',
    'open_it_support_ticket',
    'debug_ticket_context',
    'collect_caller_email',
    'send_copier_support_email',
    'send_copier_supplies_email',
    'submit_sales_inquiry',
    'test_email_system',
    'submit_billing_inquiry',
    'request_callback'
]
