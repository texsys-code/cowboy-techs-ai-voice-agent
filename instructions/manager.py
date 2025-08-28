"""
Instruction Manager for Cowboy Technologies Voice Agent
This module dynamically loads appropriate instructions based on caller requests.
"""

from .base import BASE_INSTRUCTIONS
from .it_support import IT_SUPPORT_INSTRUCTIONS
from .copier_support import COPIER_SUPPORT_INSTRUCTIONS
from .copier_supplies import COPIER_SUPPLIES_INSTRUCTIONS
from .sales import SALES_INQUIRY_INSTRUCTIONS
from .callback import CALLBACK_REQUEST_INSTRUCTIONS
from .representative import REPRESENTATIVE_INSTRUCTIONS
from .billing import BILLING_INQUIRY_INSTRUCTIONS

class InstructionManager:
    """Manages dynamic loading of AI agent instructions based on context."""
    
    def __init__(self):
        """Initialize the instruction manager."""
        self.base_instructions = BASE_INSTRUCTIONS
        self.specialized_instructions = {
            'it_support': IT_SUPPORT_INSTRUCTIONS,
            'copier_support': COPIER_SUPPORT_INSTRUCTIONS,
            'copier_supplies': COPIER_SUPPLIES_INSTRUCTIONS,
            'sales': SALES_INQUIRY_INSTRUCTIONS,
            'callback': CALLBACK_REQUEST_INSTRUCTIONS,
            'representative': REPRESENTATIVE_INSTRUCTIONS,
            'billing': BILLING_INQUIRY_INSTRUCTIONS,
        }
    
    def get_instructions(self, context=None, caller_request=None):
        """
        Get appropriate instructions based on context and caller request.
        
        Args:
            context (str, optional): The context of the call (e.g., 'greeting', 'active')
            caller_request (str, optional): What the caller is asking for
            
        Returns:
            str: Combined instructions for the AI agent
        """
        # Start with base instructions
        instructions = self.base_instructions
        
        # If we have a specific caller request, add specialized instructions
        if caller_request:
            specialized = self._get_specialized_instructions(caller_request)
            if specialized:
                instructions += specialized
        
        return instructions
    
    def _get_specialized_instructions(self, caller_request):
        """
        Get specialized instructions based on caller request.
        
        Args:
            caller_request (str): What the caller is asking for
            
        Returns:
            str: Specialized instructions or empty string if none found
        """
        request_lower = caller_request.lower()
        
        # IT Support requests
        if any(phrase in request_lower for phrase in [
            'computer', 'it support', 'technical support', 'computer help', 
            'computer problem', 'computer issue', 'computer won\'t work',
            'computer broken', 'computer slow', 'computer virus', 'password',
            'login', 'email', 'internet', 'network', 'printer', 'software'
        ]):
            return self.specialized_instructions['it_support']
        
        # Copier Support requests
        elif any(phrase in request_lower for phrase in [
            'copier', 'copier problem', 'copier broken', 'copier not working',
            'copier jam', 'copier error', 'copier service', 'copier repair',
            'machine', 'machine problem', 'machine broken', 'machine not working',
            'equipment', 'equipment problem', 'equipment broken'
        ]):
            return self.specialized_instructions['copier_support']
        
        # Copier Supplies requests
        elif any(phrase in request_lower for phrase in [
            'toner', 'supplies', 'order supplies', 'order toner', 'need toner',
            'need supplies', 'out of toner', 'out of supplies', 'buy toner',
            'buy supplies', 'supply order', 'toner order', 'ink', 'paper'
        ]):
            return self.specialized_instructions['copier_supplies']
        
        # Sales inquiries
        elif any(phrase in request_lower for phrase in [
            'sales', 'pricing', 'quote', 'cost', 'price', 'service agreement',
            'contract', 'new service', 'interested in', 'looking for', 'need service',
            'business', 'company', 'start service', 'switch to', 'competitor'
        ]):
            return self.specialized_instructions['sales']
        
        # Billing inquiries
        elif any(phrase in request_lower for phrase in [
            'billing', 'bill', 'invoice', 'payment', 'pay', 'account', 'accounts',
            'accounts payable', 'accounts receivable', 'ap', 'ar', 'money owed',
            'owe', 'owing', 'charge', 'charges', 'statement', 'balance'
        ]):
            return self.specialized_instructions['billing']
        
        # Representative requests (speak to someone)
        elif any(phrase in request_lower for phrase in [
            'speak to someone', 'talk to someone', 'speak to representative',
            'talk to representative', 'speak to person', 'talk to person',
            'human', 'real person', 'live person', 'speak to live person',
            'representative', 'agent', 'operator', 'live agent', 'live operator'
        ]):
            return self.specialized_instructions['representative']
        
        # Callback requests
        elif any(phrase in request_lower for phrase in [
            'call me back', 'call back', 'callback', 'return call'
        ]):
            return self.specialized_instructions['callback']
        
        # No specialized instructions needed
        return ""
    
    def get_greeting_instructions(self):
        """Get instructions for the initial greeting phase."""
        return self.base_instructions
    
    def get_active_instructions(self, caller_request):
        """Get instructions for active conversation based on caller request."""
        return self.get_instructions(context='active', caller_request=caller_request)
    
    def update_instructions_during_call(self, current_instructions, new_request):
        """
        Update instructions during an active call based on new requests.
        
        Args:
            current_instructions (str): Current instructions being used
            new_request (str): New request from caller
            
        Returns:
            str: Updated instructions
        """
        # If we already have specialized instructions for this request type,
        # don't add them again
        if any(specialized in current_instructions for specialized in self.specialized_instructions.values()):
            return current_instructions
        
        # Add new specialized instructions
        specialized = self._get_specialized_instructions(new_request)
        if specialized:
            return current_instructions + specialized
        
        return current_instructions

# Create a global instance
instruction_manager = InstructionManager()

# Convenience functions
def get_instructions(context=None, caller_request=None):
    """Get instructions using the global instruction manager."""
    return instruction_manager.get_instructions(context, caller_request)

def get_greeting_instructions():
    """Get greeting instructions."""
    return instruction_manager.get_greeting_instructions()

def get_active_instructions(caller_request):
    """Get active conversation instructions."""
    return instruction_manager.get_active_instructions(caller_request)

def update_instructions_during_call(current_instructions, new_request):
    """Update instructions during an active call."""
    return instruction_manager.update_instructions_during_call(current_instructions, new_request)
