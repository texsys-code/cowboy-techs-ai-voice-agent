"""
Lib package for Cowboy Technologies Voice Agent.
This package contains utility functions and tools for the AI voice agent.
"""

# Import key functions for easy access
from .tools import get_current_time
from .api import (
    lookup_caller,
    create_caller,
    create_ticket,
    send_sales_inquiry_email,
    send_billing_inquiry_email
)

__all__ = [
    'get_current_time',
    'lookup_caller',
    'create_caller',
    'create_ticket',
    'send_sales_inquiry_email',
    'send_billing_inquiry_email'
]
