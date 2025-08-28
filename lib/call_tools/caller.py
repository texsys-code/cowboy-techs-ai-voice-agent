import asyncio
import logging
import re

from livekit import api, rtc
from livekit.agents import get_job_context, RunContext, JobContext, function_tool

from config import AGENT_NAME, API_URL
from lib.api import create_caller, lookup_caller as api_lookup_caller
from lib.utils import sanitize_for_ai, log_sanitization_warning

logger = logging.getLogger("CALLER")

@function_tool
async def lookup_caller(phone_number: str = None):
    """Look up the caller's information in our system using their phone number."""
    ctx = get_job_context()

    # Use provided phone number or fall back to context
    phone_to_lookup = phone_number or getattr(ctx, 'caller_phone_number', None)
    
    if not phone_to_lookup or phone_to_lookup == "Unknown":
        logger.warning(f"unable to find caller context or phone number")
        return
    
    # Check if we already have caller information from automatic lookup
    # Only skip if we have both first name and email (indicating complete lookup)
    existing_first_name = getattr(ctx, 'caller_first_name', None)
    existing_email = getattr(ctx, 'caller_email', None)
    
    logger.info(f"DEBUG: Checking existing caller info - first_name: '{existing_first_name}', email: '{existing_email}'")
    
    if existing_first_name and existing_email:
        logger.info("Caller information already available, skipping lookup")
        return
    else:
        logger.info("Caller information incomplete, proceeding with lookup")
    
    # If we don't have the information, perform the lookup
    try:
        logger.info(f"Looking up caller with phone number: {phone_to_lookup}")

        # If we don't have caller information, look it up
        caller_info = await api_lookup_caller(phone_to_lookup)
        
        if caller_info:
            # Debug: Log the raw caller info
            logger.info(f"DEBUG: Raw caller info from API: {caller_info}")
            
            # Sanitize all caller information before storing in context
            sanitized_caller_info = sanitize_for_ai(caller_info)
            
            # Log if sanitization occurred
            log_sanitization_warning(caller_info, sanitized_caller_info, "caller lookup")
            
            # Store sanitized information in context
            ctx.caller_name = f"{sanitized_caller_info.get('firstname', '')} {sanitized_caller_info.get('lastname', '')}".strip()
            ctx.caller_first_name = sanitized_caller_info.get('firstname', '')
            ctx.caller_last_name = sanitized_caller_info.get('lastname', '')
            ctx.caller_company = sanitized_caller_info.get('company', '')
            ctx.caller_email = sanitized_caller_info.get('email', '')
            ctx.caller_phone = sanitized_caller_info.get('phone', '')
            ctx.halo_user_id = sanitized_caller_info.get('user_id', '')
            ctx.halo_client_id = sanitized_caller_info.get('client_id', '')
            ctx.halo_site_id = sanitized_caller_info.get('site_id', '')
            ctx.caller_id = sanitized_caller_info.get('_id', '')

            logger.info(f"Caller information stored (sanitized): {ctx.caller_name}")
            logger.info(f"DEBUG: Stored email: {ctx.caller_email}")
            logger.info(f"DEBUG: Stored phone: {ctx.caller_phone}")
            logger.info(f"DEBUG: Stored company: {ctx.caller_company}")
    except Exception as e:
        logger.error(f"Error looking up caller: {str(e)}")
    
    return

@function_tool
async def store_caller_info(name: str, company: str):
    ctx = get_job_context()

    if not ctx:
        logger.warning(f"unable to find caller context")
        return

    # If we have a phone number, try to create a caller record
    if hasattr(ctx, 'caller_phone_number') and ctx.caller_phone_number != "Unknown":
        try:
            loop = asyncio.get_event_loop()

            # Create caller data
            caller_data = {
                "firstname": ctx.caller_first_name,
                "lastname": ctx.caller_last_name,
                "email": ctx.caller_email,
                "phone": ctx.caller_phone_number,
                "company": ctx.caller_company,
                "user_id": ctx.halo_user_id,
                "client_id": ctx.halo_client_id,
                "site_id": ctx.halo_site_id
            }

            # Create caller record
            caller_record = await create_caller(caller_data)
        except Exception as e:
            logger.warning(f"Error creating caller record: {str(e)}")

@function_tool
async def collect_caller_info(name: str = None, company: str = None, email: str = None):
    """
    Collect missing caller information and store it in context.
    
    Args:
        name: Caller's name
        company: Caller's company
        email: Caller's email address
    """
    
    logger.info(f"Collecting caller info: {name}, {company}, {email}")

    ctx = get_job_context()

    if not ctx:
        return "I'm sorry, but I'm unable to collect your information at the moment due to a system error."
    
    caller_name = getattr(ctx, 'caller_name', None)

    if caller_name is not None:
        logger.info("Caller information already available, skipping collection")
        logger.info(f"From collect_caller_info Caller name: {ctx.caller_name}")
        return
    
    # Store the provided information in context
    if name:
        ctx.caller_name = name
        ctx.caller_first_name = name.split()[0] if name else None
        ctx.caller_last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else None
        logger.info(f"Stored caller name: {name}")
    
    if company:
        ctx.caller_company = company
        logger.info(f"Stored caller company: {company}")
    
    if email:
        ctx.caller_email = email
        logger.info(f"Stored caller email: {email}")
    
    # Check if we now have complete information
    has_complete_info = (
        hasattr(ctx, 'caller_name') and ctx.caller_name and
        hasattr(ctx, 'caller_email') and ctx.caller_email and
        hasattr(ctx, 'caller_company') and ctx.caller_company
    )
    
    if has_complete_info:
        ctx.need_caller_info = False
        ctx.missing_caller_fields = []
        logger.info("Caller information collection complete")
        
        return "Thank you! I now have all the information I need. How can I help you today?"
    else:
        # Determine what's still missing
        still_missing = []
        if not getattr(ctx, 'caller_name', None):
            still_missing.append('name')
        if not getattr(ctx, 'caller_email', None):
            still_missing.append('email')
        if not getattr(ctx, 'caller_company', None):
            still_missing.append('company')
        
        missing_message = f"I still need your {', '.join(still_missing)}. "
        if 'name' in still_missing:
            missing_message += "What is your name? "
        if 'company' in still_missing:
            missing_message += "What company are you calling from? "
        if 'email' in still_missing:
            missing_message += "What is your email address? "
        
        return missing_message
    
def format_phone_number(phone_number):
    """
    Format phone number as xxx-xxx-xxxx
    @param phone_number: Raw phone number string
    @return: Formatted phone number or original if can't format
    """
    if not phone_number:
        return phone_number
    
    # Remove all non-digit characters
    digits_only = re.sub(r'[^\d]', '', str(phone_number))
    
    # Handle different length phone numbers
    if len(digits_only) == 10:
        # Standard US format: xxx-xxx-xxxx
        return f"{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        # US with country code: 1-xxx-xxx-xxxx
        return f"{digits_only[1:4]}-{digits_only[4:7]}-{digits_only[7:]}"
    elif len(digits_only) == 7:
        # Local format: xxx-xxxx
        return f"{digits_only[:3]}-{digits_only[3:]}"
    else:
        # Return original if we can't format it properly
        logger.warning(f"Could not format phone number: {phone_number} (digits: {digits_only})")
        return phone_number







