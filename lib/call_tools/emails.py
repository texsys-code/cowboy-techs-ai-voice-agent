import asyncio
import logging
import aiohttp
import json

from livekit.agents import get_job_context, function_tool

from config import AGENT_NAME, API_URL

logger = logging.getLogger("EMAILS")

@function_tool
async def send_copier_support_email(
    details: str = None, 
    confirmed: bool = False,
    equipment_id: str = None,
    make_model: str = None,
    serial_number: str = None,
    service_agreement: bool = None
):
    """
    Send copier support email instead of creating a ticket.
    Args:
        details: The details of the copier support request.
        confirmed: Whether the user has confirmed the info.
        equipment_id: Equipment ID number if available.
        make_model: Make and model of equipment if no Equipment ID.
        serial_number: Serial number of equipment if no Equipment ID.
        service_agreement: Whether under service maintenance agreement.
    """

    # Get caller's information from context
    ctx = get_job_context()
    if not ctx:
        logger.error("No job context available for copier support email")
        return "I'm sorry, but I'm unable to send copier support emails at the moment due to a system error."
    
    # Get caller information from context
    caller_name = getattr(ctx, 'caller_name', None)
    caller_company = getattr(ctx, 'caller_company', None)
    caller_phone = getattr(ctx, 'caller_phone_number', None)
    caller_email = getattr(ctx, 'caller_email', None)  # Get email from context
    
    logger.info(f"send_copier_support_email called with details='{details}', confirmed={confirmed}")
    logger.info(f"Equipment ID: {equipment_id}, Make/Model: {make_model}, Serial: {serial_number}")
    logger.info(f"Caller info - name: {caller_name}, company: {caller_company}, phone: {caller_phone}, email: {caller_email}")
    
    # If no details provided, ask for them
    if not details:
        logger.info("No details provided, asking caller for copier issue description")
        return "What copier issue are you experiencing? Please describe the problem you need help with."

    # If not confirmed, show confirmation and ask for approval
    if not confirmed:
        logger.info("Copier support email not confirmed, showing confirmation to caller")
        
        # Build confirmation message based on available information
        confirmation_parts = []
        
        # Equipment information
        if equipment_id:
            confirmation_parts.append(f"Equipment ID: {equipment_id}")
        else:
            if make_model:
                confirmation_parts.append(f"Make and Model: {make_model}")
            if serial_number:
                confirmation_parts.append(f"Serial Number: {serial_number}")
        
        # Caller information
        if caller_name:
            confirmation_parts.append(f"Name: {caller_name}")
        if caller_company:
            confirmation_parts.append(f"Company: {caller_company}")
        if caller_phone:
            confirmation_parts.append(f"Phone: {caller_phone}")
        if caller_email:
            confirmation_parts.append(f"Email: {caller_email}")
        
        if service_agreement is not None:
            agreement_status = "Yes" if service_agreement else "No"
            confirmation_parts.append(f"Service Agreement: {agreement_status}")
        
        # Issue details
        confirmation_parts.append(f"Problem Description: {details}")
        
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
            f"[NON_INTERRUPTIBLE] Let me confirm your copier support email details{source_message}:\n"
            f"{chr(10).join(confirmation_parts)}\n"
            "Please say 'yes' to confirm and I'll send your copier support email, or let me know if you need to add or change anything."
        )
        
        logger.info(f"Returning confirmation message for Copier support email: {confirmation_message[:100]}...")
        return confirmation_message

    # Email is confirmed, proceed with sending
    logger.info("Copier support email confirmed, proceeding with sending")
    
    # Validate required information
    required_fields = []
    if not caller_name:
        required_fields.append("name")
    if not caller_company:
        required_fields.append("company")
    if not caller_phone:
        required_fields.append("phone number")
    if not caller_email:
        required_fields.append("email address")
    if not details:
        required_fields.append("problem description")
    
    if required_fields:
        missing_fields = ", ".join(required_fields)
        error_message = f"[NON_INTERRUPTIBLE] I'm sorry, but I need your {missing_fields} to send your copier support email. Please provide this information."
        logger.error(f"Missing required information for copier support email: {missing_fields}")
        return error_message
    
    # Prepare email data with enhanced details
    enhanced_details = f"Copier Support Request\n\n"
    enhanced_details += f"Problem Description: {details}\n"
    enhanced_details += f"Caller Phone Number: {caller_phone}\n"
    enhanced_details += f"Caller Email: {caller_email}\n"
    
    if equipment_id:
        enhanced_details += f"Equipment ID: {equipment_id}\n"
    else:
        if make_model:
            enhanced_details += f"Make and Model: {make_model}\n"
        if serial_number:
            enhanced_details += f"Serial Number: {serial_number}\n"
    
    if service_agreement is not None:
        agreement_status = "Yes" if service_agreement else "No"
        enhanced_details += f"Service Maintenance Agreement: {agreement_status}\n"
    
    # Prepare email inquiry data
    email_data = {
        "queue_name": "copier",
        "caller_name": caller_name,
        "caller_phone": caller_phone,
        "caller_email": caller_email,
        "inquiry_description": f"Copier Support Request - {details}",
        "caller_company": caller_company,
        "additional_notes": enhanced_details,
        "priority": "high",
        "source": "Voice Agent System - Copier Support"
    }
    
    logger.info(f"Sending copier support email with data: {email_data}")
    
    # Send email via API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/email/inquiry",
                json=email_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 201:
                    result = await response.json()
                    success_message = f"[NON_INTERRUPTIBLE] Thank you — your copier support request has been sent to our service team. They will review your request and get back to you soon. Is there anything else I can help you with today?"
                    logger.info(f"Copier support email sent successfully")
                    return success_message
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send copier support email - API returned status {response.status}: {error_text}")
                    error_message = "[NON_INTERRUPTIBLE] I'm sorry, but I was unable to send your copier support email. Please try again later or contact our support team directly."
                    return error_message

    except Exception as e:
        error_message = "[NON_INTERRUPTIBLE] I'm sorry, but there was an error while sending your copier support email. Please try again later or contact our support team directly."
        logger.error(f"Error sending copier support email: {str(e)}")
        return error_message

@function_tool
async def send_copier_supplies_email(
    equipment_id: str = None,
    supply_details: str = None,
    item_number: str = None,
    caller_name: str = None,
    caller_email: str = None,
    callback_number: str = None,
    confirmed: bool = False
):
    """
    Send copier supplies email instead of creating a ticket.
    Args:
        equipment_id: Equipment ID number if available.
        supply_details: Description of supplies needed.
        item_number: Item number if no Equipment ID.
        caller_name: Name for callback (if no Equipment ID).
        caller_email: Email address (if no Equipment ID).
        callback_number: Callback number (if no Equipment ID).
        confirmed: Whether the user has confirmed the order.
    """

    # Get caller's information from context
    ctx = get_job_context()
    if not ctx:
        logger.error("No job context available for copier supplies email")
        return "I'm sorry, but I'm unable to send copier supplies emails at the moment due to a system error."
    
    # Get caller information from context (will be used as defaults)
    ctx_caller_name = getattr(ctx, 'caller_name', None)
    ctx_caller_company = getattr(ctx, 'caller_company', None)
    ctx_caller_phone = getattr(ctx, 'caller_phone_number', None)
    ctx_caller_email = getattr(ctx, 'caller_email', None)  # Get email from context
    
    # Use provided values or fall back to context values
    final_caller_name = ctx_caller_name
    final_caller_company = ctx_caller_company
    final_caller_phone = ctx_caller_phone
    final_caller_email = ctx_caller_email  # Use provided email or context email
    
    logger.info(f"send_copier_supplies_email called with equipment_id='{equipment_id}', supply_details='{supply_details}', confirmed={confirmed}")
    logger.info(f"Context caller info - name: {final_caller_name}, company: {final_caller_company}, phone: {final_caller_phone}, email: {final_caller_email}")
    
    # If no supply details provided, ask for them
    if not supply_details:
        logger.info("No supply details provided, asking caller for supply description")
        if equipment_id:
            return "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"
        else:
            return "Please tell me the item number and type of supplies you need."

    # If not confirmed, show confirmation and ask for approval
    if not confirmed:
        logger.info("Copier supplies email not confirmed, showing confirmation to caller")
        
        # Build confirmation message based on available information
        confirmation_parts = []
        
        # Equipment information
        if equipment_id:
            confirmation_parts.append(f"Equipment ID: {equipment_id}")
        else:
            if item_number:
                confirmation_parts.append(f"Item Number: {item_number}")
        
        # Supply details
        confirmation_parts.append(f"Supply Details: {supply_details}")
        
        # Caller information (only show if not using Equipment ID)
        if not equipment_id:
            if final_caller_name:
                confirmation_parts.append(f"Name: {final_caller_name}")
            if final_caller_email:
                confirmation_parts.append(f"Email: {final_caller_email}")
            if final_caller_phone:
                confirmation_parts.append(f"Callback Number: {final_caller_phone}")
        
        # Check if we're using automatically found information
        auto_found_info = []
        if ctx_caller_name and equipment_id:
            auto_found_info.append("name from our system")
        if ctx_caller_company and equipment_id:
            auto_found_info.append("company from our system")
        if ctx_caller_phone and equipment_id:
            auto_found_info.append("phone from our system")
        if ctx_caller_email and equipment_id:
            auto_found_info.append("email from our system")
        
        source_message = ""
        if auto_found_info:
            source_message = f" (I found your {' and '.join(auto_found_info)} using your phone number)"
        
        confirmation_message = (
            f"[NON_INTERRUPTIBLE] Let me confirm your copier supplies email details{source_message}:\n"
            f"{chr(10).join(confirmation_parts)}\n"
            "Please say 'yes' to confirm and I'll send your supplies request, or let me know if you need to add or change anything."
        )
        
        logger.info(f"Returning confirmation message for copier supplies email: {confirmation_message[:100]}...")
        return confirmation_message

    # Email is confirmed, proceed with sending
    logger.info("Copier supplies email confirmed, proceeding with sending")
    
    # Validate required information
    required_fields = []
    if not supply_details:
        required_fields.append("supply details")
    
    if equipment_id:
        # Equipment ID path - use context information
        if not final_caller_name:
            required_fields.append("name")
        if not final_caller_company:
            required_fields.append("company")
        if not final_caller_phone:
            required_fields.append("phone number")
        if not final_caller_email:
            required_fields.append("email address")
    else:
        # No Equipment ID path - require manual input
        if not final_caller_name:
            required_fields.append("name")
        if not final_caller_email:
            required_fields.append("email address")
        if not final_caller_phone:
            required_fields.append("callback number")
    
    if required_fields:
        missing_fields = ", ".join(required_fields)
        error_message = f"[NON_INTERRUPTIBLE] I'm sorry, but I need your {missing_fields} to send your supplies request. Please provide this information."
        logger.error(f"Missing required information for copier supplies email: {missing_fields}")
        return error_message
    
    # Prepare email data with enhanced details
    enhanced_details = f"Copier Supplies Request\n\n"
    enhanced_details += f"Supply Details: {supply_details}\n"
    enhanced_details += f"Caller Email: {final_caller_email}\n"
    
    if equipment_id:
        enhanced_details += f"Equipment ID: {equipment_id}\n"
    else:
        if item_number:
            enhanced_details += f"Item Number: {item_number}\n"
        if final_caller_email:
            enhanced_details += f"Email: {final_caller_email}\n"
    
    enhanced_details += f"Caller Phone Number: {final_caller_phone}\n"
    
    # Prepare email inquiry data
    email_data = {
        "queue_name": "copier",
        "caller_name": final_caller_name,
        "caller_phone": final_caller_phone,
        "caller_email": final_caller_email,
        "inquiry_description": f"Copier Supplies Request - {supply_details}",
        "caller_company": final_caller_company,
        "additional_notes": enhanced_details,
        "priority": "medium",
        "source": "Voice Agent System - Copier Supplies"
    }
    
    logger.info(f"Sending copier supplies email with data: {email_data}")
    
    # Send email via API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/email/inquiry",
                json=email_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 201:
                    result = await response.json()
                    success_message = f"[NON_INTERRUPTIBLE] Your supplies request has been sent to our service team. By the way, we offer an auto-replenishment program so toner ships automatically when your supply level reaches a set percentage. If you'd like to enroll, just press 1. Is there anything else I can help you with today?"
                    logger.info(f"Copier supplies email sent successfully")
                    return success_message
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send copier supplies email - API returned status {response.status}: {error_text}")
                    error_message = "[NON_INTERRUPTIBLE] I'm sorry, but I was unable to send your supplies request. Please try again later or contact our support team directly."
                    return error_message

    except Exception as e:
        error_message = "[NON_INTERRUPTIBLE] I'm sorry, but there was an error while sending your supplies request. Please try again later or contact our support team directly."
        logger.error(f"Error sending copier supplies email: {str(e)}")
        return error_message
