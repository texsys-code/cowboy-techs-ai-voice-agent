"""
Instructions package for Cowboy Technologies Voice Agent.
This package contains modular instructions for different types of caller requests.
"""

from .manager import (
    InstructionManager,
    instruction_manager,
    get_instructions,
    get_greeting_instructions,
    get_active_instructions,
    update_instructions_during_call
)

from .base import BASE_INSTRUCTIONS
from .it_support import IT_SUPPORT_INSTRUCTIONS
from .copier_support import COPIER_SUPPORT_INSTRUCTIONS
from .copier_supplies import COPIER_SUPPLIES_INSTRUCTIONS
from .sales import SALES_INQUIRY_INSTRUCTIONS
from .callback import CALLBACK_REQUEST_INSTRUCTIONS

__all__ = [
    'InstructionManager',
    'instruction_manager',
    'get_instructions',
    'get_greeting_instructions',
    'get_active_instructions',
    'update_instructions_during_call',
    'BASE_INSTRUCTIONS',
    'IT_SUPPORT_INSTRUCTIONS',
    'COPIER_SUPPORT_INSTRUCTIONS',
    'COPIER_SUPPLIES_INSTRUCTIONS',
    'SALES_INQUIRY_INSTRUCTIONS',
    'CALLBACK_REQUEST_INSTRUCTIONS'
]
