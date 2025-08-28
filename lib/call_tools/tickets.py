import asyncio
import logging

from livekit.agents import get_job_context, function_tool

from config import AGENT_NAME
from lib.api import create_ticket
from lib.utils import sanitize_for_ai, log_sanitization_warning, validate_email, clean_email

logger = logging.getLogger("TICKETS")

@function_tool
async def open_it_support_ticket(
    details: str = None, confirmed: bool = False
):
    """
    Open IT Support Ticket in Halo PSA.
    Args:
        details: The details of the IT support request.
        confirmed: Whether the user has confirmed the info.
    """

    # Get caller's information from context
    ctx = get_job_context()
    if not ctx:
        logger.error("No job context available for ticket creation")
        return "I'm sorry, but I'm unable to create tickets at the moment due to a system error."
    
    # Get caller information from context
    caller_name = getattr(ctx, 'caller_name', None)
    caller_company = getattr(ctx, 'caller_company', None)
    caller_phone = getattr(ctx, 'caller_phone_number', None)  # Use the correct context key
    caller_email = getattr(ctx, 'caller_email', None)  # Get email from context
    halo_client_id = getattr(ctx, 'halo_client_id', None)
    halo_site_id = getattr(ctx, 'halo_site_id', None)
    halo_user_id = getattr(ctx, 'halo_user_id', None)
    
    logger.info(f"open_it_support_ticket called with details='{details}', confirmed={confirmed}")
    logger.info(f"Context caller info - name: {caller_name}, company: {caller_company}, phone: {caller_phone}, email: {caller_email}")
    
    # If no details provided, ask for them
    if not details:
        logger.info("No details provided, asking caller for issue description")
        return "What is the issue you're experiencing? Please describe the problem you need help with."

    # If not confirmed, show confirmation and ask for approval
    if not confirmed:
        logger.info("Ticket not confirmed, showing confirmation to caller")
        
        # Sanitize all data before creating confirmation message
        sanitized_name = sanitize_for_ai(caller_name) if caller_name else None
        sanitized_company = sanitize_for_ai(caller_company) if caller_company else None
        sanitized_phone = sanitize_for_ai(caller_phone) if caller_phone else None
        sanitized_details = sanitize_for_ai(details) if details else None
        
        # Log if sanitization occurred
        if caller_name != sanitized_name or caller_company != sanitized_company or caller_phone != sanitized_phone or details != sanitized_details:
            log_sanitization_warning(
                {"name": caller_name, "company": caller_company, "phone": caller_phone, "details": details},
                {"name": sanitized_name, "company": sanitized_company, "phone": sanitized_phone, "details": sanitized_details},
                "IT support ticket confirmation"
            )
        
        # Check if we're using automatically found information
        auto_found_name = sanitized_name is not None
        auto_found_company = sanitized_company is not None
        auto_found_email = caller_email is not None
        
        info_source = []
        if auto_found_name:
            info_source.append("name from our system")
        if auto_found_company:
            info_source.append("company from our system")
        if auto_found_email:
            info_source.append("email from our system")
        
        source_message = ""
        if info_source:
            source_message = f" (I found your {' and '.join(info_source)} using your phone number)"
        
        confirmation_message = (
            f"[NON_INTERRUPTIBLE] Let me confirm your ticket details{source_message}:\n"
            f"Name: {sanitized_name or 'Not provided'}\n"
            f"Company: {sanitized_company or 'Not provided'}\n"
            f"Request Details: {sanitized_details}\n"
            f"Phone Number: {sanitized_phone or 'Not provided'}\n"
            f"Email: {caller_email or 'Not provided'}\n"
            "Please say 'yes' to confirm and I'll create your ticket, or let me know if you need to add or change anything."
        )
        
        logger.info(f"Returning confirmation message for IT support ticket: {confirmation_message[:100]}...")
        return confirmation_message

    # Ticket is confirmed, proceed with creation
    logger.info("Ticket confirmed, proceeding with creation")
    
    # Validate required information
    if not caller_name or not caller_company or not details:
        logger.error("Missing required information for ticket creation")
        return "[NON_INTERRUPTIBLE] I'm sorry, but I need your name, company, and issue details to create a ticket. Please provide this information."
    
    # Prepare ticket data
    enhanced_details = f"{details}\n\nCaller Phone Number: {caller_phone or 'Unknown'}"
    
    ticket_data = {
        "summary": f"{caller_name} - {caller_company}",
        "details": enhanced_details,
        "status_id": 1,
        "tickettype_id": 1,
        "sla_id": 3,
        "priority_id": 4,
        "client_id": int(halo_client_id) if halo_client_id and halo_client_id != "0" else 174,
        "site_id": int(halo_site_id) if halo_site_id and halo_site_id != "0" else 216,
        "user_id": int(halo_user_id) if halo_user_id and halo_user_id != "0" else 267,
        "team_id": 1,  # IT Support team
        "agent_id": 1,
        "category_1": "Business Applications",
        "impact": 3,
        "urgency": 2
    }
    
    logger.info(f"Creating IT support ticket with data: {ticket_data}")
    
    # Create ticket in Halo PSA
    try:
        ticket = await create_ticket(ticket_data)
        
        if ticket:
            ticket_number = ticket.get('id', 'Unknown')
            success_message = f"[NON_INTERRUPTIBLE] Your IT support ticket has been opened successfully! The ticket number is {ticket_number}. A tech will get back to you in 1 to 2 hours. Is there anything else I can help you with today?"
            logger.info(f"Ticket created successfully: {ticket_number}")
            return success_message
        else:
            error_message = "[NON_INTERRUPTIBLE] I'm sorry, but I was unable to open your ticket. Please try again later or contact our support team directly."
            logger.error("Failed to create ticket - API returned None")
            return error_message

    except Exception as e:
        error_message = "[NON_INTERRUPTIBLE] I'm sorry, but there was an error while creating your ticket. Please try again later or contact our support team directly."
        logger.error(f"Error opening IT support ticket: {str(e)}")
        return error_message

@function_tool
async def open_copier_support_ticket(
    details: str = None, 
    confirmed: bool = False,
    equipment_id: str = None,
    make_model: str = None,
    serial_number: str = None,
    caller_name: str = None,
    caller_phone: str = None,
    caller_email: str = None,
    caller_company: str = None,
    caller_address: str = None,
    point_of_contact: str = None,
    service_agreement: bool = None
):
    """
    Open Copier Support Ticket in Halo PSA with comprehensive data collection.
    Args:
        details: The details of the copier support request.
        confirmed: Whether the user has confirmed the info.
        equipment_id: Equipment ID number if available.
        make_model: Make and model of equipment if no Equipment ID.
        serial_number: Serial number of equipment if no Equipment ID.
        caller_name: Name of the person requesting service.
        caller_phone: Phone number for contact.
        caller_email: Email address for contact.
        caller_company: Company name.
        caller_address: Company address.
        point_of_contact: Point of contact name and email.
        service_agreement: Whether under service maintenance agreement.
    """

    # Get caller's information from context
    ctx = get_job_context()
    if not ctx:
        logger.error("No job context available for copier ticket creation")
        return "I'm sorry, but I'm unable to create tickets at the moment due to a system error."
    
    # Get caller information from context (will be used as defaults)
    ctx_caller_name = getattr(ctx, 'caller_name', None)
    ctx_caller_company = getattr(ctx, 'caller_company', None)
    ctx_caller_phone = getattr(ctx, 'caller_phone_number', None)
    ctx_caller_email = getattr(ctx, 'caller_email', None) # Get email from context
    halo_client_id = getattr(ctx, 'halo_client_id', None)
    halo_site_id = getattr(ctx, 'halo_site_id', None)
    halo_user_id = getattr(ctx, 'halo_user_id', None)
    
    # Use provided values or fall back to context values
    final_caller_name = caller_name or ctx_caller_name
    final_caller_company = caller_company or ctx_caller_company
    final_caller_phone = caller_phone or ctx_caller_phone
    final_caller_email = caller_email or ctx_caller_email # Use provided email or context email
    
    logger.info(f"open_copier_support_ticket called with details='{details}', confirmed={confirmed}")
    logger.info(f"Equipment ID: {equipment_id}, Make/Model: {make_model}, Serial: {serial_number}")
    logger.info(f"Caller info - name: {final_caller_name}, company: {final_caller_company}, phone: {final_caller_phone}, email: {final_caller_email}")
    
    # If no details provided, ask for them
    if not details:
        logger.info("No details provided, asking caller for copier issue description")
        return "What copier issue are you experiencing? Please describe the problem you need help with."

    # If not confirmed, show confirmation and ask for approval
    if not confirmed:
        logger.info("Copier ticket not confirmed, showing confirmation to caller")
        
        # Sanitize all data before creating confirmation message
        sanitized_name = sanitize_for_ai(final_caller_name) if final_caller_name else None
        sanitized_company = sanitize_for_ai(final_caller_company) if final_caller_company else None
        sanitized_phone = sanitize_for_ai(final_caller_phone) if final_caller_phone else None
        sanitized_details = sanitize_for_ai(details) if details else None
        sanitized_email = sanitize_for_ai(final_caller_email) if final_caller_email else None
        
        # Log if sanitization occurred
        if final_caller_name != sanitized_name or final_caller_company != sanitized_company or final_caller_phone != sanitized_phone or details != sanitized_details or final_caller_email != sanitized_email:
            log_sanitization_warning(
                {"name": final_caller_name, "company": final_caller_company, "phone": final_caller_phone, "details": details, "email": final_caller_email},
                {"name": sanitized_name, "company": sanitized_company, "phone": sanitized_phone, "details": sanitized_details, "email": sanitized_email},
                "Copier support ticket confirmation"
            )
        
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
        if final_caller_name:
            confirmation_parts.append(f"Name: {sanitized_name or 'Not provided'}")
        if final_caller_company:
            confirmation_parts.append(f"Company: {sanitized_company or 'Not provided'}")
        if final_caller_phone:
            confirmation_parts.append(f"Phone: {sanitized_phone or 'Not provided'}")
        if final_caller_email:
            confirmation_parts.append(f"Email: {sanitized_email or 'Not provided'}")
        if caller_address:
            confirmation_parts.append(f"Address: {caller_address}")
        if point_of_contact:
            confirmation_parts.append(f"Point of Contact: {point_of_contact}")
        if service_agreement is not None:
            agreement_status = "Yes" if service_agreement else "No"
            confirmation_parts.append(f"Service Agreement: {agreement_status}")
        
        # Issue details
        confirmation_parts.append(f"Problem Description: {sanitized_details}")
        
        # Check if we're using automatically found information
        auto_found_info = []
        if ctx_caller_name:
            auto_found_info.append("name from our system")
        if ctx_caller_company:
            auto_found_info.append("company from our system")
        if ctx_caller_phone:
            auto_found_info.append("phone from our system")
        if ctx_caller_email:
            auto_found_info.append("email from our system")
        
        source_message = ""
        if auto_found_info:
            source_message = f" (I found your {' and '.join(auto_found_info)} using your phone number)"
        
        confirmation_message = (
            f"[NON_INTERRUPTIBLE] Let me confirm your copier support ticket details{source_message}:\n"
            f"{chr(10).join(confirmation_parts)}\n"
            "Please say 'yes' to confirm and I'll create your copier support ticket, or let me know if you need to add or change anything."
        )
        
        logger.info(f"Returning confirmation message for Copier support ticket: {confirmation_message[:100]}...")
        return confirmation_message

    # Ticket is confirmed, proceed with creation
    logger.info("Copier ticket confirmed, proceeding with creation")
    
    # Validate required information
    required_fields = []
    if not final_caller_name:
        required_fields.append("name")
    if not final_caller_company:
        required_fields.append("company")
    if not final_caller_phone:
        required_fields.append("phone number")
    if not final_caller_email: # Add email validation
        required_fields.append("email address")
    if not details:
        required_fields.append("problem description")
    
    if required_fields:
        missing_fields = ", ".join(required_fields)
        error_message = f"[NON_INTERRUPTIBLE] I'm sorry, but I need your {missing_fields} to create a copier support ticket. Please provide this information."
        logger.error(f"Missing required information for copier ticket creation: {missing_fields}")
        return error_message
    
    # Prepare ticket data with enhanced details
    enhanced_details = f"Problem Description: {details}\n"
    enhanced_details += f"Caller Phone Number: {final_caller_phone}\n"
    enhanced_details += f"Caller Email: {final_caller_email}\n" # Add email to enhanced details
    
    if equipment_id:
        enhanced_details += f"Equipment ID: {equipment_id}\n"
    else:
        if make_model:
            enhanced_details += f"Make and Model: {make_model}\n"
        if serial_number:
            enhanced_details += f"Serial Number: {serial_number}\n"
    
    if caller_address:
        enhanced_details += f"Company Address: {caller_address}\n"
    if point_of_contact:
        enhanced_details += f"Point of Contact: {point_of_contact}\n"
    if service_agreement is not None:
        agreement_status = "Yes" if service_agreement else "No"
        enhanced_details += f"Service Maintenance Agreement: {agreement_status}\n"
    
    ticket_data = {
        "summary": f"{final_caller_name} - {final_caller_company} - Copier Support",
        "details": enhanced_details,
        "status_id": 1,
        "tickettype_id": 2,  # Different ticket type for copier support
        "sla_id": 3,
        "priority_id": 4,
        "client_id": int(halo_client_id) if halo_client_id and halo_client_id != "0" else 174,
        "site_id": int(halo_site_id) if halo_site_id and halo_site_id != "0" else 216,
        "user_id": int(halo_user_id) if halo_user_id and halo_user_id != "0" else 267,
        "team_id": 2,  # Copier Support team
        "agent_id": 1,
        "category_1": "Hardware",
        "impact": 3,
        "urgency": 2
    }
    
    logger.info(f"Creating copier ticket with data: {ticket_data}")
    
    # Create ticket in Halo PSA
    try:
        ticket = await create_ticket(ticket_data)
        
        if ticket:
            ticket_number = ticket.get('id', 'Unknown')
            success_message = f"[NON_INTERRUPTIBLE] Thank you — your request has been placed in our service queue and a technician will be in touch soon. Your ticket number is {ticket_number}. Is there anything else I can help you with today?"
            logger.info(f"Copier ticket created successfully: {ticket_number}")
            return success_message
        else:
            error_message = "[NON_INTERRUPTIBLE] I'm sorry, but I was unable to open your copier support ticket. Please try again later or contact our support team directly."
            logger.error("Failed to create copier ticket - API returned None")
            return error_message

    except Exception as e:
        error_message = "[NON_INTERRUPTIBLE] I'm sorry, but there was an error while creating your copier support ticket. Please try again later or contact our support team directly."
        logger.error(f"Error opening copier support ticket: {str(e)}")
        return error_message

@function_tool
async def order_copier_supplies(
    equipment_id: str = None,
    supply_details: str = None,
    item_number: str = None,
    caller_name: str = None,
    caller_email: str = None,
    callback_number: str = None,
    confirmed: bool = False
):
    """
    Order copier supplies and create a ticket for the order.
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
        logger.error("No job context available for supply order")
        return "I'm sorry, but I'm unable to place supply orders at the moment due to a system error."
    
    # Get caller information from context (will be used as defaults)
    ctx_caller_name = getattr(ctx, 'caller_name', None)
    ctx_caller_company = getattr(ctx, 'caller_company', None)
    ctx_caller_phone = getattr(ctx, 'caller_phone_number', None)
    ctx_caller_email = getattr(ctx, 'caller_email', None) # Get email from context
    halo_client_id = getattr(ctx, 'halo_client_id', None)
    halo_site_id = getattr(ctx, 'halo_site_id', None)
    halo_user_id = getattr(ctx, 'halo_user_id', None)
    
    # Use provided values or fall back to context values
    final_caller_name = caller_name or ctx_caller_name
    final_caller_company = ctx_caller_company
    final_caller_phone = callback_number or ctx_caller_phone
    final_caller_email = caller_email or ctx_caller_email # Use provided email or context email
    
    logger.info(f"order_copier_supplies called with equipment_id='{equipment_id}', supply_details='{supply_details}', confirmed={confirmed}")
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
        logger.info("Supply order not confirmed, showing confirmation to caller")
        
        # Sanitize all data before creating confirmation message
        sanitized_name = sanitize_for_ai(final_caller_name) if final_caller_name else None
        sanitized_company = sanitize_for_ai(final_caller_company) if final_caller_company else None
        sanitized_phone = sanitize_for_ai(final_caller_phone) if final_caller_phone else None
        sanitized_details = sanitize_for_ai(supply_details) if supply_details else None
        sanitized_email = sanitize_for_ai(final_caller_email) if final_caller_email else None
        
        # Log if sanitization occurred
        if final_caller_name != sanitized_name or final_caller_company != sanitized_company or final_caller_phone != sanitized_phone or supply_details != sanitized_details or final_caller_email != sanitized_email:
            log_sanitization_warning(
                {"name": final_caller_name, "company": final_caller_company, "phone": final_caller_phone, "details": supply_details, "email": final_caller_email},
                {"name": sanitized_name, "company": sanitized_company, "phone": sanitized_phone, "details": sanitized_details, "email": sanitized_email},
                "Copier supply order confirmation"
            )
        
        # Build confirmation message based on available information
        confirmation_parts = []
        
        # Equipment information
        if equipment_id:
            confirmation_parts.append(f"Equipment ID: {equipment_id}")
        else:
            if item_number:
                confirmation_parts.append(f"Item Number: {item_number}")
        
        # Supply details
        confirmation_parts.append(f"Supply Details: {sanitized_details}")
        
        # Caller information (only show if not using Equipment ID)
        if not equipment_id:
            if final_caller_name:
                confirmation_parts.append(f"Name: {sanitized_name or 'Not provided'}")
            if final_caller_email:
                confirmation_parts.append(f"Email: {sanitized_email or 'Not provided'}")
            if final_caller_phone:
                confirmation_parts.append(f"Callback Number: {sanitized_phone or 'Not provided'}")
        
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
            f"[NON_INTERRUPTIBLE] Let me confirm your copier supply order details{source_message}:\n"
            f"{chr(10).join(confirmation_parts)}\n"
            "Please say 'yes' to confirm and I'll place your supply order, or let me know if you need to add or change anything."
        )
        
        logger.info(f"Returning confirmation message for copier supply order: {confirmation_message[:100]}...")
        return confirmation_message

    # Order is confirmed, proceed with ticket creation
    logger.info("Supply order confirmed, proceeding with ticket creation")
    
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
    else:
        # No Equipment ID path - require manual input
        if not final_caller_name:
            required_fields.append("name")
        if not final_caller_email: # Add email validation
            required_fields.append("email address")
        if not final_caller_phone:
            required_fields.append("callback number")
    
    if required_fields:
        missing_fields = ", ".join(required_fields)
        error_message = f"[NON_INTERRUPTIBLE] I'm sorry, but I need your {missing_fields} to place your supply order. Please provide this information."
        logger.error(f"Missing required information for supply order: {missing_fields}")
        return error_message
    
    # Prepare ticket data with enhanced details
    enhanced_details = f"Supply Order Request\n\n"
    enhanced_details += f"Supply Details: {supply_details}\n"
    
    if equipment_id:
        enhanced_details += f"Equipment ID: {equipment_id}\n"
    else:
        if item_number:
            enhanced_details += f"Item Number: {item_number}\n"
        if final_caller_email:
            enhanced_details += f"Email: {final_caller_email}\n" # Add email to enhanced details
    
    enhanced_details += f"Caller Phone Number: {final_caller_phone}\n"
    
    ticket_data = {
        "summary": f"{final_caller_name} - {final_caller_company} - Copier Supply Order",
        "details": enhanced_details,
        "status_id": 1,
        "tickettype_id": 3,  # Different ticket type for supply orders
        "sla_id": 3,
        "priority_id": 4,
        "client_id": int(halo_client_id) if halo_client_id and halo_client_id != "0" else 174,
        "site_id": int(halo_site_id) if halo_site_id and halo_site_id != "0" else 216,
        "user_id": int(halo_user_id) if halo_user_id and halo_user_id != "0" else 267,
        "team_id": 2,  # Copier Support team
        "agent_id": 1,
        "category_1": "Supplies",
        "impact": 3,
        "urgency": 2
    }
    
    logger.info(f"Creating copier supply order ticket with data: {ticket_data}")
    
    # Create ticket in Halo PSA
    try:
        ticket = await create_ticket(ticket_data)
        
        if ticket:
            ticket_number = ticket.get('id', 'Unknown')
            success_message = f"[NON_INTERRUPTIBLE] Your order has been placed. By the way, we offer an auto-replenishment program so toner ships automatically when your supply level reaches a set percentage. If you'd like to enroll, just press 1. Your order ticket number is {ticket_number}. Is there anything else I can help you with today?"
            logger.info(f"Copier supply order ticket created successfully: {ticket_number}")
            return success_message
        else:
            error_message = "[NON_INTERRUPTIBLE] I'm sorry, but I was unable to place your supply order. Please try again later or contact our support team directly."
            logger.error("Failed to create supply order ticket - API returned None")
            return error_message

    except Exception as e:
        error_message = "[NON_INTERRUPTIBLE] I'm sorry, but there was an error while placing your supply order. Please try again later or contact our support team directly."
        logger.error(f"Error creating copier supply order ticket: {str(e)}")
        return error_message

@function_tool
async def collect_caller_email(email: str = None):
    """
    Collect and validate caller email address.
    Args:
        email: Email address provided by caller
    """
    ctx = get_job_context()
    
    if not ctx:
        return "I'm sorry, but I'm unable to collect your email at the moment due to a system error."
    
    # If no email provided, ask for it
    if not email:
        return "I need your email address to complete this request. Please provide your email address."
    
    # Clean and validate the email
    from lib.utils import clean_email, validate_email
    
    cleaned_email = clean_email(email)
    
    if not cleaned_email:
        return "I'm sorry, but that doesn't appear to be a valid email address. Please provide a valid email address (for example: yourname@company.com)."
    
    # Store the validated email in context
    ctx.caller_email = cleaned_email
    
    logger.info(f"Caller email collected and validated: {cleaned_email}")
    
    return f"Thank you! I've recorded your email address as {cleaned_email}. Now let me continue with your request."

@function_tool
async def debug_ticket_context():
    """
    Debug function to check what caller information is available in the context.
    """
    ctx = get_job_context()
    if not ctx:
        return "No job context available"
    
    # Get all available caller information
    caller_name = getattr(ctx, 'caller_name', None)
    caller_company = getattr(ctx, 'caller_company', None)
    caller_phone = getattr(ctx, 'caller_phone_number', None)
    caller_first_name = getattr(ctx, 'caller_first_name', None)
    caller_last_name = getattr(ctx, 'caller_last_name', None)
    halo_client_id = getattr(ctx, 'halo_client_id', None)
    halo_site_id = getattr(ctx, 'halo_site_id', None)
    halo_user_id = getattr(ctx, 'halo_user_id', None)
    
    debug_info = f"""
Debug Information:
- caller_name: {caller_name}
- caller_company: {caller_company}
- caller_phone_number: {caller_phone}
- caller_first_name: {caller_first_name}
- caller_last_name: {caller_last_name}
- halo_client_id: {halo_client_id}
- halo_site_id: {halo_site_id}
- halo_user_id: {halo_user_id}
"""
    
    logger.info(f"Debug context info: {debug_info}")
    return debug_info