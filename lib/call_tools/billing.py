import logging
from livekit.agents import function_tool, get_job_context
from lib.api import send_billing_inquiry_email

# Configure logging
logger = logging.getLogger("BILLING")

@function_tool
async def submit_billing_inquiry(
    inquiry_type: str = None,
    invoice_number: str = None,
    inquiry_description: str = None,
    confirmed: bool = False
):
    """
    Submit a billing inquiry that will be sent to the billing queue via the API.
    
    Args:
        inquiry_type: Type of billing inquiry (AP for Accounts Payable, AR for Accounts Receivable)
        invoice_number: Invoice number if related to a specific invoice (optional)
        inquiry_description: Additional details about the billing inquiry (optional)
        confirmed: Whether the user has confirmed the inquiry details
    """
    
    logger.info(f"submit_billing_inquiry ENTRY - type: '{inquiry_type}', invoice: '{invoice_number}', confirmed: {confirmed}")
    
    try:
        # Get caller's information from context
        ctx = get_job_context()
        if not ctx:
            logger.error("No job context available for billing inquiry")
            return "I'm sorry, but I'm unable to submit billing inquiries at the moment due to a system error."
        
        # Get caller information from context
        ctx_caller_name = getattr(ctx, 'caller_name', None)
        ctx_caller_company = getattr(ctx, 'caller_company', None)
        ctx_caller_phone = getattr(ctx, 'caller_phone_number', None) or getattr(ctx, 'caller_phone', None)
        ctx_caller_email = getattr(ctx, 'caller_email', None)
        
        logger.info(f"Context caller info - name: {ctx_caller_name}, company: {ctx_caller_company}, phone: {ctx_caller_phone}, email: {ctx_caller_email}")
        
        # If no inquiry type provided, ask for it
        if not inquiry_type:
            logger.info("No inquiry type provided, asking caller to specify AP or AR")
            return "I can help direct your billing inquiry. Is this for Accounts Payable or Accounts Receivable?"
        
        # Validate inquiry type
        if inquiry_type.upper() not in ['AP', 'AR', 'ACCOUNTS PAYABLE', 'ACCOUNTS RECEIVABLE']:
            logger.warning(f"Invalid inquiry type: {inquiry_type}")
            return "Please specify whether this is for Accounts Payable (AP) or Accounts Receivable (AR)."
        
        # Normalize inquiry type
        if inquiry_type.upper() in ['ACCOUNTS PAYABLE', 'AP']:
            normalized_type = 'AP'
        else:
            normalized_type = 'AR'
        
        # If not confirmed, show confirmation and ask for approval
        if not confirmed:
            logger.info("Billing inquiry not confirmed, showing confirmation to caller")
            
            confirmation_message = f"[NON_INTERRUPTIBLE] Let me confirm your billing inquiry:\n"
            confirmation_message += f"Type: {normalized_type} ({'Accounts Payable' if normalized_type == 'AP' else 'Accounts Receivable'})\n"
            if invoice_number:
                confirmation_message += f"Invoice Number: {invoice_number}\n"
            if inquiry_description:
                confirmation_message += f"Details: {inquiry_description}\n"
            confirmation_message += f"Name: {ctx_caller_name or 'Not provided'}\n"
            confirmation_message += f"Company: {ctx_caller_company or 'Not provided'}\n"
            confirmation_message += f"Phone: {ctx_caller_phone or 'Not provided'}\n"
            confirmation_message += f"Email: {ctx_caller_email or 'Not provided'}\n\n"
            confirmation_message += "Please say 'yes' to confirm and I'll submit your billing inquiry, or let me know if you need to change anything."
            
            return confirmation_message
        
        # Inquiry is confirmed, proceed with submission
        logger.info(f"Billing inquiry confirmed, proceeding with submission for {normalized_type}")
        
        try:
            # Send the billing inquiry via API
            result = await send_billing_inquiry_email(
                caller_name=ctx_caller_name,
                caller_phone=ctx_caller_phone,
                caller_email=ctx_caller_email,
                inquiry_type=normalized_type,
                invoice_number=invoice_number,
                inquiry_description=inquiry_description,
                caller_company=ctx_caller_company
            )
            
            if result["success"]:
                success_message = (
                    f"[NON_INTERRUPTIBLE] Thank you! I've submitted your {normalized_type} billing inquiry to our billing team. "
                    f"One of our representatives will be in touch with you within 24 hours to address your inquiry. "
                    f"Is there anything else I can help you with today?"
                )
                logger.info(f"Billing inquiry submitted successfully for {ctx_caller_name} - Type: {normalized_type}")
                return success_message
            else:
                error_message = (
                    f"[NON_INTERRUPTIBLE] I'm sorry, but I encountered an issue submitting your billing inquiry. "
                    f"Please try calling our billing team directly at our main office number, or let me know if there's anything else I can help you with."
                )
                logger.error(f"Failed to submit billing inquiry: {result['message']}")
                return error_message
                
        except Exception as e:
            error_message = (
                f"[NON_INTERRUPTIBLE] I'm sorry, but I encountered an unexpected error while submitting your billing inquiry. "
                f"Please try calling our billing team directly at our main office number, or let me know if there's anything else I can help you with."
            )
            logger.error(f"Unexpected error in submit_billing_inquiry: {str(e)}", exc_info=True)
            return error_message
            
    except Exception as e:
        logger.error(f"CRITICAL ERROR in submit_billing_inquiry: {str(e)}", exc_info=True)
        return f"I'm sorry, but I encountered an unexpected error: {str(e)}. Please try again or contact support."
