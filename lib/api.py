import aiohttp
import logging
from typing import Optional, Dict, Any
from config import API_URL
import asyncio

logger = logging.getLogger(__name__)

async def lookup_caller(phone_number: str) -> Optional[Dict[str, Any]]:
    """
    Look up caller information by phone number.
    
    Args:
        phone_number (str): The phone number to search for
        
    Returns:
        Optional[Dict[str, Any]]: Caller information if found, None otherwise
    """
    try:
        # Construct the search URL
        search_url = f"{API_URL}/api/callers/search?phone={phone_number}"
        
        logger.info(f"Looking up caller with phone: {phone_number}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status == 200:
                    caller_data = await response.json()
                    logger.info(f"Found caller")
                    return caller_data['data']
                elif response.status == 404:
                    logger.info(f"No caller found for phone: {phone_number}")
                    return None
                else:
                    logger.error(f"API request failed with status {response.status}: {response.text}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error during caller lookup: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during caller lookup: {e}")
        return None

async def create_caller(caller_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new caller record by POSTing to the API.
    
    Args:
        caller_data (Dict[str, Any]): The caller data to create
        
    Returns:
        Optional[Dict[str, Any]]: The created caller data if successful, None otherwise
    """
    try:
        # Construct the create URL
        create_url = f"{API_URL}/api/callers"
        
        logger.info(f"Creating caller with data: {caller_data}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(create_url, json=caller_data) as response:
                if response.status == 201:  # Created
                    created_caller = await response.json()
                    logger.info(f"Successfully created caller: {created_caller}")
                    return created_caller
                elif response.status == 200:  # OK (some APIs return 200 for creation)
                    created_caller = await response.json()
                    logger.info(f"Successfully created caller: {created_caller}")
                    return created_caller
                elif response.status == 400:  # Bad Request
                    error_text = await response.text()
                    logger.error(f"Bad request when creating caller: {error_text}")
                    return None
                elif response.status == 409:  # Conflict (duplicate)
                    error_text = await response.text()
                    logger.warning(f"Caller already exists: {error_text}")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error during caller creation: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during caller creation: {e}")
        return None

async def create_ticket(ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new ticket record by POSTing to the API.
    
    Args:
        ticket_data (Dict[str, Any]): The ticket data to create
        
    Returns:
        Optional[Dict[str, Any]]: The created ticket data if successful, None otherwise
    """
    try:
        # Construct the create URL
        create_url = f"{API_URL}/api/halo/tickets"
        
        logger.info(f"Creating ticket with data: {ticket_data}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(create_url, json=ticket_data) as response:
                if response.status == 200 or response.status == 201:
                    ticket_response = await response.json()
                    logger.info(f"Successfully created ticket: {ticket_response['data']['id']}")
                    return ticket_response.get('data', ticket_response)
                elif response.status == 400:
                    error_text = await response.text()
                    logger.error(f"Bad request when creating ticket: {error_text}")
                    return None
                elif response.status == 401:
                    logger.error("Unauthorized - check API credentials")
                    return None
                elif response.status == 403:
                    logger.error("Forbidden - insufficient permissions")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {error_text}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error during ticket creation: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during ticket creation: {e}")
        return None

async def send_sales_inquiry_email(
    caller_name: str,
    caller_phone: str,
    caller_email: str,
    inquiry_description: str,
    caller_company: str = None,
    additional_notes: str = None
):
    """
    Send a sales inquiry email via the API.
    
    Args:
        caller_name: Name of the person making the inquiry
        caller_phone: Phone number for contact
        caller_email: Email address for contact
        inquiry_description: Brief description of what they're looking for
        caller_company: Company name (optional)
        additional_notes: Any additional notes or context (optional)
        
    Returns:
        Dict containing success status and message
    """
    
    logger.info(f"API: Sending sales inquiry email for {caller_name}")
    
    try:
        # Prepare the email data for the unified email inquiry endpoint
        email_data = {
            "queue_name": "sales",
            "caller_name": caller_name,
            "caller_phone": caller_phone,
            "caller_email": caller_email,
            "inquiry_description": inquiry_description,
            "caller_company": caller_company,
            "additional_notes": additional_notes,
            "priority": "medium",
            "source": "Voice Agent System - Sales Inquiry"
        }

        logger.info(f"API: Sending sales inquiry email for {caller_name} with data: {email_data}")
        
        # Send POST request to the unified email inquiry endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/email/inquiry",
                json=email_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    logger.info(f"API: Sales inquiry email sent successfully for {caller_name}")
                    return {
                        "success": True,
                        "message": "Sales inquiry submitted successfully",
                        "email_id": result.get("data", {}).get("inquiry_id"),
                        "timestamp": result.get("data", {}).get("timestamp")
                    }
                elif response.status == 400:
                    error_data = await response.json()
                    error_msg = f"Bad request: {error_data.get('message', 'Invalid data provided')}"
                    logger.error(f"API: Sales inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "bad_request"
                    }
                elif response.status == 401:
                    error_msg = "Unauthorized - API credentials invalid"
                    logger.error(f"API: Sales inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "unauthorized"
                    }
                elif response.status == 403:
                    error_msg = "Forbidden - API access denied"
                    logger.error(f"API: Sales inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "forbidden"
                    }
                elif response.status == 500:
                    error_msg = "Internal server error - API temporarily unavailable"
                    logger.error(f"API: Sales inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "server_error"
                    }
                else:
                    error_msg = f"Unexpected response: {response.status}"
                    logger.error(f"API: Sales inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "unexpected_response"
                    }
                    
    except asyncio.TimeoutError:
        error_msg = "Request timeout - API is not responding"
        logger.error(f"API: Sales inquiry email failed - {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "error": "timeout"
        }
    except aiohttp.ClientError as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"API: Sales inquiry email failed - {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "error": "network_error"
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"API: Sales inquiry email failed - {error_msg}", exc_info=True)
        return {
            "success": False,
            "message": error_msg,
            "error": "unexpected_error"
        }

async def send_billing_inquiry_email(
    caller_name: str,
    caller_phone: str,
    caller_email: str,
    inquiry_type: str,
    invoice_number: str = None,
    inquiry_details: str = None,
    caller_company: str = None
):
    """
    Send a billing inquiry email via the API.
    
    Args:
        caller_name: Name of the person making the inquiry
        caller_phone: Phone number for contact
        caller_email: Email address for contact
        inquiry_type: Type of billing inquiry (AP for Accounts Payable, AR for Accounts Receivable)
        invoice_number: Invoice number if related to a specific invoice (optional)
        inquiry_details: Additional details about the billing inquiry (optional)
        caller_company: Company name (optional)
        
    Returns:
        Dict containing success status and message
    """
    
    logger.info(f"API: Sending billing inquiry email for {caller_name} - Type: {inquiry_type}")
    
    try:
        # Prepare the email data for the unified email inquiry endpoint
        email_data = {
            "queue_name": "billing",
            "caller_name": caller_name,
            "caller_phone": caller_phone,
            "caller_email": caller_email,
            "inquiry_type": inquiry_type,
            "invoice_number": invoice_number,
            "inquiry_details": inquiry_details,
            "caller_company": caller_company,
            "priority": "medium",
            "source": f"Voice Agent System - Billing Inquiry ({inquiry_type})"
        }

        logger.info(f"API: Sending billing inquiry email for {caller_name} with data: {email_data}")
        
        # Send POST request to the unified email inquiry endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/email/inquiry",
                json=email_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    logger.info(f"API: Billing inquiry email sent successfully for {caller_name}")
                    return {
                        "success": True,
                        "message": "Billing inquiry submitted successfully",
                        "email_id": result.get("data", {}).get("inquiry_id"),
                        "timestamp": result.get("data", {}).get("timestamp")
                    }
                elif response.status == 400:
                    error_data = await response.json()
                    error_msg = f"Bad request: {error_data.get('message', 'Invalid data provided')}"
                    logger.error(f"API: Billing inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "bad_request"
                    }
                elif response.status == 401:
                    error_msg = "Unauthorized - API credentials invalid"
                    logger.error(f"API: Billing inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "unauthorized"
                    }
                elif response.status == 403:
                    error_msg = "Forbidden - API access denied"
                    logger.error(f"API: Billing inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "forbidden"
                    }
                elif response.status == 500:
                    error_msg = "Internal server error - API temporarily unavailable"
                    logger.error(f"API: Billing inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "server_error"
                    }
                else:
                    error_msg = f"Unexpected response: {response.status}"
                    logger.error(f"API: Billing inquiry email failed - {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": "unexpected_response"
                    }
                    
    except asyncio.TimeoutError:
        error_msg = "Request timeout - API is not responding"
        logger.error(f"API: Billing inquiry email failed - {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "error": "timeout"
        }
    except aiohttp.ClientError as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"API: Billing inquiry email failed - {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "error": "network_error"
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"API: Billing inquiry email failed - {error_msg}", exc_info=True)
        return {
            "success": False,
            "message": error_msg,
            "error": "unexpected_error"
        }