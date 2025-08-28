import asyncio
import logging
import aiohttp
import json

from livekit.agents import get_job_context, function_tool

from config import AGENT_NAME, API_URL

logger = logging.getLogger("CALLBACK")

@function_tool
async def request_callback(
    reason: str = None,
    confirmed: bool = False
):
    """
    Request a callback from a representative when call volumes are high.
    Args:
        reason: The reason for requesting a callback.
        confirmed: Whether the user has confirmed the callback request.
    """

    # Get caller's information from context
    ctx = get_job_context()
    if not ctx:
        logger.error("No job context available for callback request")
        return "I'm sorry, but I'm unable to process your callback request at the moment due to a system error."
    
    # Get caller information from context
    caller_name = getattr(ctx, 'caller_name', None)
    caller_company = getattr(ctx, 'caller_company', None)
    caller_phone = getattr(ctx, 'caller_phone_number', None)
    caller_email = getattr(ctx, 'caller_email', None)
    
    logger.info(f"request_callback called with reason='{reason}', confirmed={confirmed}")
    logger.info(f"Caller info - name: {caller_name}, company: {caller_company}, phone: {caller_phone}, email: {caller_email}")
    
    # If no reason provided, ask for it
    if not reason:
        logger.info("No reason provided, asking caller for callback reason")
        return "What is the reason for your call? This will help our team prepare for your callback."
    
    # If not confirmed, show confirmation and ask for approval
    if not confirmed:
        logger.info("Callback request not confirmed, showing confirmation to caller")
        
        # Build confirmation message based on available information
        confirmation_parts = []
        
        # Caller information
        if caller_name:
            confirmation_parts.append(f"Name: {caller_name}")
        if caller_company:
            confirmation_parts.append(f"Company: {caller_company}")
        if caller_phone:
            confirmation_parts.append(f"Phone: {caller_phone}")
        if caller_email:
            confirmation_parts.append(f"Email: {caller_email}")
        
        # Callback reason
        confirmation_parts.append(f"Reason for Call: {reason}")
        
        # Check if we're using automatically found information
        auto_found_info = []
        if caller_name:
            auto_found_info.append("name from our system")
        if caller_company:
            auto_found_info.append("company from our system")
        if caller_phone:
            auto_found_info.append("phone from our system")
        if caller_email:
            auto_found_info.append("email from our system")
        
        source_message = ""
        if auto_found_info:
            source_message = f" (I found your {' and '.join(auto_found_info)} using your phone number)"
        
        confirmation_message = (
            f"[NON_INTERRUPTIBLE] Let me confirm your callback request details{source_message}:\n"
            f"{chr(10).join(confirmation_parts)}\n"
            "Please say 'yes' to confirm and I'll submit your callback request, or let me know if you need to add or change anything."
        )
        
        logger.info(f"Returning confirmation message for callback request: {confirmation_message[:100]}...")
        return confirmation_message

    # Callback request is confirmed, proceed with submitting
    logger.info("Callback request confirmed, proceeding with submission")
    
    # Validate required information
    required_fields = []
    if not caller_name:
        required_fields.append("name")
    if not caller_phone:
        required_fields.append("phone number")
    if not reason:
        required_fields.append("reason for call")
    
    if required_fields:
        missing_fields = ", ".join(required_fields)
        error_message = f"[NON_INTERRUPTIBLE] I'm sorry, but I need your {missing_fields} to submit your callback request. Please provide this information."
        logger.error(f"Missing required information for callback request: {missing_fields}")
        return error_message
    
    # Prepare callback request data
    callback_data = {
        "queue_name": "callback",
        "caller_name": caller_name,
        "caller_phone": caller_phone,
        "caller_email": caller_email or "Not provided",
        "inquiry_description": f"Callback Request - {reason}",
        "caller_company": caller_company or "Not provided",
        "additional_notes": f"Reason for Call: {reason}\nCaller requested callback due to high call volumes",
        "priority": "high",
        "source": "Voice Agent System - Callback Request"
    }
    
    logger.info(f"Submitting callback request with data: {callback_data}")
    
    # Submit callback request via API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/email/inquiry",
                json=callback_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 201:
                    result = await response.json()
                    success_message = f"[NON_INTERRUPTIBLE] Thank you for your patience. I've submitted your callback request. Our team will call you back at {caller_phone} as soon as possible. Is there anything else I can help you with today?"
                    logger.info(f"Callback request submitted successfully")
                    return success_message
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to submit callback request - API returned status {response.status}: {error_text}")
                    error_message = "[NON_INTERRUPTIBLE] I'm sorry, but I was unable to submit your callback request. Please try again later or contact our support team directly."
                    return error_message

    except Exception as e:
        error_message = "[NON_INTERRUPTIBLE] I'm sorry, but there was an error while submitting your callback request. Please try again later or contact our support team directly."
        logger.error(f"Error submitting callback request: {str(e)}")
        return error_message
