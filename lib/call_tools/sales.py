import logging
from livekit.agents import function_tool, get_job_context
from lib.api import send_sales_inquiry_email

# Configure logging
logger = logging.getLogger("SALES")

@function_tool
async def submit_sales_inquiry(
    details: str = None, 
    confirmed: bool = False
):
    """
    Submit a sales inquiry that will be sent to the sales team via the API.
    
    Args:
        details: The details of the sales inquiry.
        confirmed: Whether the user has confirmed the info.
    """
    
    logger.info(f"submit_sales_inquiry ENTRY - inquiry_description: '{details}', confirmed: {confirmed}")
    
    try:
        # Get caller's information from context
        ctx = get_job_context()
        if not ctx:
            logger.error("No job context available for sales email")
            return "I'm sorry, but I'm unable to send sales emails at the moment due to a system error."
        
        # Debug: Log context object info
        logger.info(f"DEBUG: Context object type: {type(ctx)}")
        logger.info(f"DEBUG: Context object id: {id(ctx)}")
        logger.info(f"DEBUG: All context attributes: {dir(ctx)}")
        
        # Get caller information from context (will be used as defaults)
        # Note: caller lookup sets ctx.caller_phone, but agent.py sets ctx.caller_phone_number
        ctx_caller_name = getattr(ctx, 'caller_name', None)
        ctx_caller_company = getattr(ctx, 'caller_company', None)
        ctx_caller_phone = getattr(ctx, 'caller_phone_number', None) or getattr(ctx, 'caller_phone', None)
        ctx_caller_email = getattr(ctx, 'caller_email', None)
        
        # Debug: Log what we found in context
        logger.info(f"DEBUG: Context caller_name: {ctx_caller_name}")
        logger.info(f"DEBUG: Context caller_company: {ctx_caller_company}")
        logger.info(f"DEBUG: Context caller_phone_number: {ctx_caller_phone}")
        logger.info(f"DEBUG: Context caller_email: {ctx_caller_email}")
        
        # Debug: Check if we have the raw attributes that caller lookup sets
        logger.info(f"DEBUG: Raw ctx.caller_first_name: {getattr(ctx, 'caller_first_name', None)}")
        logger.info(f"DEBUG: Raw ctx.caller_last_name: {getattr(ctx, 'caller_last_name', None)}")
        logger.info(f"DEBUG: Raw ctx.caller_phone: {getattr(ctx, 'caller_phone', None)}")
        logger.info(f"DEBUG: Raw ctx.caller_email: {getattr(ctx, 'caller_email', None)}")
        
        # Use provided values or fall back to context values
        final_caller_name = ctx_caller_name
        final_caller_company = ctx_caller_company
        final_caller_phone = ctx_caller_phone
        final_caller_email = ctx_caller_email
        
        logger.info(f"submit_sales_inquiry called with inquiry_description='{details}', confirmed={confirmed}")
        logger.info(f"Final caller info - name: {final_caller_name}, company: {final_caller_company}, phone: {final_caller_phone}, email: {final_caller_email}")
        
        # If no inquiry description provided, ask for it
        if not details:
            logger.info("No inquiry description provided, asking caller for description")
            return "Please describe what you're looking for or what services you're interested in."
        
        # If not confirmed, show confirmation and ask for approval
        if not confirmed:
            logger.info("Sales inquiry not confirmed, showing confirmation to caller")
            
            # Check if we have all required information from context
            has_all_required = (
                details and 
                final_caller_name and 
                final_caller_phone and 
                final_caller_email
            )
            
            # If we have all required info from context, just confirm the inquiry
            if has_all_required:
                confirmation_message = (
                    f"[NON_INTERRUPTIBLE] Perfect! I have all the information I need from our system. "
                    f"Let me confirm your sales inquiry:\n"
                    f"Inquiry: {details}\n"
                    f"Name: {final_caller_name}\n"
                    f"Company: {final_caller_company or 'Not specified'}\n"
                    f"Phone: {final_caller_phone}\n"
                    f"Email: {final_caller_email}\n\n"
                    f"Please say 'yes' to confirm and I'll submit your inquiry, or let me know if you need to change anything."
                )
                logger.info("All required information available from context, showing simple confirmation")
                return confirmation_message
            
            # If we're missing some information, show what we have and ask for missing pieces
            confirmation_parts = []
            confirmation_parts.append(f"Inquiry: {details}")
            
            # Show available information
            if final_caller_name:
                confirmation_parts.append(f"Name: {final_caller_name}")
            if final_caller_company:
                confirmation_parts.append(f"Company: {final_caller_company}")
            if final_caller_phone:
                confirmation_parts.append(f"Phone: {final_caller_phone}")
            if final_caller_email:
                confirmation_parts.append(f"Email: {final_caller_email}")
            
            # Check what information was found automatically
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
            
            # Identify missing information
            missing_info = []
            if not final_caller_name:
                missing_info.append("name")
            if not final_caller_phone:
                missing_info.append("phone number")
            if not final_caller_email:
                missing_info.append("email address")
            
            missing_message = ""
            if missing_info:
                missing_message = f"\n\nI still need your {', '.join(missing_info)} to complete this inquiry."
            
            confirmation_message = (
                f"[NON_INTERRUPTIBLE] Let me confirm what I have so far{source_message}:\n"
                f"{chr(10).join(confirmation_parts)}"
                f"{missing_message}\n\n"
                "Please provide the missing information or say 'yes' if what I have is correct."
            )
            
            logger.info(f"Missing information for sales inquiry: {missing_info}")
            return confirmation_message
        
        # Inquiry is confirmed, proceed with submission
        logger.info("Sales inquiry confirmed, proceeding with submission")
        
        # Validate required information
        required_fields = []
        if not details:
            required_fields.append("inquiry description")
        if not final_caller_name:
            required_fields.append("name")
        if not final_caller_phone:
            required_fields.append("phone number")
        if not final_caller_email:
            required_fields.append("email address")
        
        if required_fields:
            missing_fields = ", ".join(required_fields)
            error_message = f"[NON_INTERRUPTIBLE] I'm sorry, but I need your {missing_fields} to submit your sales inquiry. Please provide this information."
            logger.error(f"Missing required information for sales inquiry: {missing_fields}")
            return error_message
        
        logger.info(f"Sales inquiry submitted for {final_caller_name} - {details[:50]}...")
        
        try:
            # Send the sales inquiry via API
            result = await send_sales_inquiry_email(
                caller_name=final_caller_name,
                caller_phone=final_caller_phone,
                caller_email=final_caller_email,
                inquiry_description=details,
                caller_company=final_caller_company
            )
            
            if result["success"]:
                success_message = (
                    f"[NON_INTERRUPTIBLE] Thank you for your interest! I've submitted your inquiry to our sales team. "
                    f"One of our representatives will be in touch with you within 24 hours to discuss your needs. "
                    f"Is there anything else I can help you with today?"
                )
                logger.info(f"Sales inquiry submitted successfully for {final_caller_name}")
                return success_message
            else:
                error_message = (
                    f"[NON_INTERRUPTIBLE] I'm sorry, but I encountered an issue submitting your inquiry. "
                    f"Please try calling our sales team directly at our main office number, or let me know if there's anything else I can help you with."
                )
                logger.error(f"Failed to submit sales inquiry: {result['message']}")
                return error_message
                
        except Exception as e:
            error_message = (
                f"[NON_INTERRUPTIBLE] I'm sorry, but I encountered an unexpected error while submitting your inquiry. "
                f"Please try calling our sales team directly at our main office number, or let me know if there's anything else I can help you with."
            )
            logger.error(f"Unexpected error in submit_sales_inquiry: {str(e)}", exc_info=True)
            return error_message
            
    except Exception as e:
        logger.error(f"CRITICAL ERROR in submit_sales_inquiry: {str(e)}", exc_info=True)
        return f"I'm sorry, but I encountered an unexpected error: {str(e)}. Please try again or contact support."

@function_tool
async def test_email_system():
    """
    Test the email system connection and configuration via the API.
    This is a debug tool to verify email functionality.
    """
    
    logger.info("Testing email system connection via API...")
    
    try:
        # Test email system via API
        result = await send_sales_inquiry_email(
            caller_name="TEST",
            caller_phone="555-0000",
            caller_email="test@example.com",
            inquiry_description="This is a test inquiry to verify email system functionality",
            caller_company="Test Company",
            additional_notes="System test - please ignore"
        )
        
        if result["success"]:
            test_message = (
                f"[NON_INTERRUPTIBLE] Email system test successful! "
                f"The API successfully processed the test sales inquiry. "
                f"Email functionality is working properly."
            )
            logger.info("Email system test successful via API")
            return test_message
        else:
            test_message = (
                f"[NON_INTERRUPTIBLE] Email system test failed: {result.get('message', 'Unknown error')}. "
                f"Please check your API configuration and email settings."
            )
            logger.error(f"Email system test failed via API: {result.get('message', 'Unknown error')}")
            return test_message
            
    except Exception as e:
        test_message = (
            f"[NON_INTERRUPTIBLE] Email system test encountered an error: {str(e)}. "
            f"Please check your API configuration."
        )
        logger.error(f"Email system test error via API: {str(e)}", exc_info=True)
        return test_message
