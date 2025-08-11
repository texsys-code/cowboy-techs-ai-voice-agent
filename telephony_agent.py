import asyncio
import logging
import requests
import json
import re
from dotenv import load_dotenv
from livekit import api, rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    get_job_context
)
from livekit.plugins import deepgram, openai, cartesia, silero
import os
from config import API_URL, MAIN_OFFICE_NUMBER, COMPANY_NAME, EMAIL_DOMAIN

load_dotenv()
logger = logging.getLogger("telephony-agent")

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

async def hangup_call():
    ctx = get_job_context()
    if ctx is None:
        # Not running in a job context
        return
    
    await ctx.api.room.delete_room(
        api.DeleteRoomRequest(
            room=ctx.room.name,
        )
    )

# Function tools to enhance your agent's capabilities
@function_tool
async def get_current_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return f"The current time is {datetime.now().strftime('%I:%M %p')}"

@function_tool
async def end_call() -> str:
    """End the call when the user is done with the conversation."""
    
    logger.info("end_call function called - attempting to end the call")
    
    # Get the context - try RunContext first, then JobContext
    ctx = get_job_context()
    
    if not ctx:
        logger.error("No job context available in end_call")
        return "Error: No context available to end call"
    
    logger.info(f"Context type: {type(ctx)}")
    logger.info(f"Context attributes: {dir(ctx)}")
    
    # Create a personalized goodbye message
    if ctx and hasattr(ctx, 'caller_name') and ctx.caller_name:
        first_name = ctx.caller_name.split()[0] if ctx.caller_name else ''
        if first_name:
            goodbye_message = f"Thank you for calling {COMPANY_NAME}, {first_name}. Have a great day!"
        else:
            goodbye_message = f"Thank you for calling {COMPANY_NAME}. Have a great day!"
    else:
        goodbye_message = f"Thank you for calling {COMPANY_NAME}. Have a great day!"
    
    # Use session.say if we have access to it, otherwise just return the message
    try:
        # Try to get the session from the context
        if hasattr(ctx, 'session'):
            logger.info("Found session, using session.say and session.end")
            await ctx.session.say(goodbye_message, allow_interruptions=False)
            
            # Wait for the message to finish playing with multiple fallback methods
            logger.info("Waiting for goodbye message to finish playing...")
            
            # Method 1: Try to wait for current speech to finish
            try:
                current_speech = ctx.session.current_speech
                if current_speech:
                    logger.info("Found current speech, waiting for playout...")
                    await current_speech.wait_for_playout()
                    logger.info("Speech playout completed")
                else:
                    logger.info("No current speech found, using fallback timing")
            except Exception as e:
                logger.warning(f"Error waiting for speech playout: {e}, using fallback timing")
            
            # Method 2: Check for any active speech operations
            try:
                # Check if there are any active speech operations
                if hasattr(ctx.session, '_speech_queue') and ctx.session._speech_queue:
                    logger.info("Found active speech queue, waiting for completion...")
                    # Wait a bit more for any queued speech
                    await asyncio.sleep(1.0)
                    logger.info("Speech queue wait completed")
            except Exception as e:
                logger.warning(f"Error checking speech queue: {e}")
            
            # Method 3: Fallback timing to ensure message is spoken
            # Estimate time needed based on message length (roughly 2.5 words per second)
            word_count = len(goodbye_message.split())
            estimated_duration = max(2.0, word_count / 2.5)  # Minimum 2 seconds
            logger.info(f"Message has {word_count} words, estimated duration: {estimated_duration:.1f} seconds")
            
            # Wait for estimated duration plus buffer
            wait_time = estimated_duration + 1.5  # Add 1.5 second buffer for safety
            logger.info(f"Waiting {wait_time:.1f} seconds to ensure message is spoken...")
            await asyncio.sleep(wait_time)
            logger.info("Wait time completed")
            
            # Final verification: Check if we can detect that speech has finished
            try:
                # One more check for any remaining speech operations
                if hasattr(ctx.session, 'current_speech') and ctx.session.current_speech:
                    logger.info("Speech still active, waiting a bit more...")
                    await asyncio.sleep(0.5)
                    logger.info("Additional wait completed")
            except Exception as e:
                logger.warning(f"Error in final speech check: {e}")
            
            logger.info("Goodbye message should now be complete, proceeding to end call")
            
            # End the session/call
            logger.info("Ending session...")
            try:
                await ctx.session.end()
                logger.info("Session ended successfully")
            except Exception as e:
                logger.warning(f"Session.end() failed: {e}, trying alternative methods")
                # Try to disconnect the participant
                if hasattr(ctx, 'api') and hasattr(ctx, 'room'):
                    try:
                        # Get participants and disconnect them
                        participants = await ctx.api.room.list_participants(
                            api.ListParticipantsRequest(room=ctx.room.name)
                        )
                        for participant in participants.participants:
                            if participant.identity != "agent":
                                logger.info(f"Disconnecting participant: {participant.identity}")
                                await ctx.api.room.remove_participant(
                                    api.RemoveParticipantRequest(
                                        room=ctx.room.name,
                                        participant=participant.identity
                                    )
                                )
                        logger.info("All participants disconnected")
                    except Exception as e2:
                        logger.error(f"Failed to disconnect participants: {e2}")
                
                # Try the job context disconnect method as a last resort
                try:
                    if hasattr(ctx, 'disconnect'):
                        logger.info("Attempting to disconnect via job context")
                        await ctx.disconnect()
                        logger.info("Job context disconnect successful")
                    else:
                        logger.warning("Job context has no disconnect method")
                except Exception as e3:
                    logger.error(f"Job context disconnect failed: {e3}")
            
            return ""
        else:
            logger.warning("No session found in context, trying alternative methods")
            # Try alternative methods to end the call
            if hasattr(ctx, 'api') and hasattr(ctx, 'room'):
                logger.info("Attempting to delete room via API")
                try:
                    await ctx.api.room.delete_room(
                        api.DeleteRoomRequest(room=ctx.room.name)
                    )
                    logger.info("Room deleted successfully")
                    return ""
                except Exception as e:
                    logger.error(f"Failed to delete room: {e}")
                    return f"Goodbye! {goodbye_message}"
            else:
                logger.warning("No API or room available, returning goodbye message")
                return goodbye_message
    except Exception as e:
        logger.error(f"Error in end_call function: {e}")
        return f"Goodbye! {goodbye_message}"
    


@function_tool
async def get_caller_phone_number() -> str:
    """Get the caller's phone number."""
    ctx = get_job_context()
    if ctx and hasattr(ctx, 'caller_phone_number'):
        return f"The caller's phone number is {ctx.caller_phone_number}"
    return "Phone number not available"

@function_tool
async def debug_caller_info() -> str:
    """Debug function to show all available caller information."""
    ctx = get_job_context()
    if not ctx:
        return "No job context available"
    
    info = []
    if hasattr(ctx, 'caller_phone_number'):
        info.append(f"Caller phone: {ctx.caller_phone_number}")
    if hasattr(ctx, 'caller_name'):
        info.append(f"Caller name: {ctx.caller_name}")
    if hasattr(ctx, 'caller_company'):
        info.append(f"Caller company: {ctx.caller_company}")
    if hasattr(ctx, 'callback_number'):
        info.append(f"Callback number: {ctx.callback_number}")
    if hasattr(ctx, 'room'):
        info.append(f"Room name: {ctx.room.name}")
    
    # Add more detailed information for debugging
    if hasattr(ctx, 'halo_user_id'):
        info.append(f"Halo user ID: {ctx.halo_user_id}")
    if hasattr(ctx, 'halo_client_id'):
        info.append(f"Halo client ID: {ctx.halo_client_id}")
    if hasattr(ctx, 'halo_site_id'):
        info.append(f"Halo site ID: {ctx.halo_site_id}")
    if hasattr(ctx, 'caller_id'):
        info.append(f"Caller ID: {ctx.caller_id}")
    
    if info:
        return "Caller information: " + ", ".join(info)
    else:
        return "No caller information available"

@function_tool
async def lookup_caller_in_system() -> str:
    """Look up the caller's information in our system using their phone number."""
    ctx = get_job_context()
    if not ctx or not hasattr(ctx, 'caller_phone_number') or ctx.caller_phone_number == "Unknown":
        return "I don't have a valid phone number to look up your information."
    
    # Check if we already have caller information from automatic lookup
    if hasattr(ctx, 'caller_name') and ctx.caller_name:
        first_name = ctx.caller_name.split()[0] if ctx.caller_name else ''
        if first_name:
            return f"I already have your information {first_name}! You're calling from {ctx.caller_company}. What can I help you with today?"
        else:
            return f"I already have your information! You're calling from {ctx.caller_company}. What can I help you with today?"
    
    # If we don't have the information, perform the lookup
    try:
        logger.info(f"Looking up caller with phone number: {ctx.caller_phone_number}")
        
        # Use the Node.js API to look up the caller
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: requests.get(f"{API_URL}/api/callers/search?phone={ctx.caller_phone_number}")
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                caller_data = result['data']
                
                # Store the found information in context
                logger.info(f"Caller data: {caller_data}")
                
                ctx.caller_name = f"{caller_data.get('firstname', '')} {caller_data.get('lastname', '')}".strip()
                ctx.caller_company = caller_data.get('company', '')
                ctx.caller_email = caller_data.get('email', '')
                ctx.caller_phone = caller_data.get('phone', '')
                ctx.halo_user_id = caller_data.get('user_id', '')
                ctx.halo_client_id = caller_data.get('client_id', '')
                ctx.halo_site_id = caller_data.get('site_id', '')
                ctx.caller_id = caller_data.get('_id', '')
                
                # Update last called timestamp
                if ctx.caller_id:
                    try:
                        await loop.run_in_executor(
                            None, lambda: requests.patch(f"{API_URL}/api/callers/{ctx.caller_id}/last-called")
                        )
                    except Exception as e:
                        logger.warning(f"Could not update last called timestamp: {str(e)}")
                
                # Extract first name for personalized greeting
                first_name = caller_data.get('firstname', '').strip()
                if not first_name and ctx.caller_name:
                    # Fallback: extract first name from full name
                    first_name = ctx.caller_name.split()[0] if ctx.caller_name else ''
                
                if first_name:
                    return f"Welcome back {first_name}! I found your information in our system using your phone number {ctx.caller_phone_number}. You're calling from {ctx.caller_company}. What can I help you with today?"
                else:
                    return f"Welcome back! I found your information in our system using your phone number {ctx.caller_phone_number}. You're calling from {ctx.caller_company}. What can I help you with today?"
            else:
                return "I couldn't find your information in our system. Could you please tell me your name and company so I can help you better?"
        elif response.status_code == 404:
            return "I couldn't find your information in our system. Could you please tell me your name and company so I can help you better?"
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return "I had trouble looking up your information. Could you please tell me your name and company so I can help you better?"
            
    except Exception as e:
        logger.error(f"Error looking up caller: {str(e)}")
        return "I had trouble looking up your information. Could you please tell me your name and company so I can help you better?"

@function_tool
async def store_caller_info(name: str, company: str) -> str:
    """Store the caller's name and company information and create a caller record if needed."""
    ctx = get_job_context()
    if not ctx:
        return "I couldn't save your information. How can I help you today?"
    
    # Parse name into first and last name
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        firstname = name_parts[0]
        lastname = ' '.join(name_parts[1:])
    else:
        firstname = name
        lastname = "Unknown"
    
    # Store in context
    ctx.caller_name = name
    ctx.caller_company = company
    
    # If we have a phone number, try to create a caller record
    if hasattr(ctx, 'caller_phone_number') and ctx.caller_phone_number != "Unknown":
        try:
            loop = asyncio.get_event_loop()
            
            # First, check if caller already exists in database
            search_response = await loop.run_in_executor(
                None, lambda: requests.get(f"{API_URL}/api/callers/search?phone={ctx.caller_phone_number}")
            )
            
            if search_response.status_code == 200:
                result = search_response.json()
                if result.get('success') and result.get('data'):
                    # Caller exists, check if they have an email
                    existing_caller = result['data']
                    if existing_caller.get('email') and existing_caller['email'].strip():
                        # Email exists, update the caller record with new name/company
                        ctx.caller_id = existing_caller['_id']
                        ctx.caller_email = existing_caller['email']
                        logger.info(f"Found existing caller with email: {existing_caller['email']}")
                        
                        # Update the caller record
                        update_data = {
                            "firstname": firstname,
                            "lastname": lastname,
                            "company": company
                        }
                        
                        update_response = await loop.run_in_executor(
                            None, lambda: requests.patch(f"{API_URL}/api/callers/{ctx.caller_id}", json=update_data)
                        )
                        
                        if update_response.status_code == 200:
                            logger.info(f"Updated existing caller record for {name}")
                        else:
                            logger.warning(f"Could not update caller record: {update_response.status_code}")
                        
                        # Extract first name for personalized response
                        first_name = firstname.strip() if firstname else name.split()[0] if name else ''
                        if first_name:
                            return f"Welcome back {first_name}! I found your information in our system. I've updated your name and company. What can I help you with today?"
                        else:
                            return f"Welcome back! I found your information in our system. I've updated your name and company. What can I help you with today?"
                    else:
                        # No email found, prompt for one
                        logger.info("Existing caller found but no email address")
                        ctx.caller_id = existing_caller['_id']
                        return f"I found your information in our system, but I need your email address to complete your profile. Could you please provide your email address?"
                else:
                    # Caller doesn't exist, create new record
                    logger.info("Creating new caller record")
                    # Create caller data with generated email
                    caller_data = {
                        "firstname": firstname,
                        "lastname": lastname,
                        "email": ctx.caller_email,  # Generate email
                        "phone": ctx.caller_phone_number,
                        "company": company,
                        "user_id": "0",  # Default values for new callers
                        "client_id": "0",
                        "site_id": "0"
                    }
                    
                    # Try to create the caller record
                    response = await loop.run_in_executor(
                        None, lambda: requests.post(f"{API_URL}/api/callers", json=caller_data)
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        if result.get('success'):
                            ctx.caller_id = result['data']['_id']
                            ctx.caller_email = caller_data['email']
                            # Extract first name for personalized response
                            first_name = firstname.strip() if firstname else name.split()[0] if name else ''
                            
                            if first_name:
                                return f"Thank you {first_name} from {company}. I've saved your information in our system with a generated email address. What can I help you with today?"
                            else:
                                return f"Thank you {name} from {company}. I've saved your information in our system with a generated email address. What can I help you with today?"
                    
                    # If creation failed, just store in context
                    logger.warning(f"Could not create caller record: {response.status_code} - {response.text}")
            else:
                logger.warning(f"API error searching for caller: {search_response.status_code} - {search_response.text}")
                
        except Exception as e:
            logger.warning(f"Error creating/updating caller record: {str(e)}")
    
    # Extract first name for personalized response
    first_name = firstname.strip() if firstname else name.split()[0] if name else ''
    
    if first_name:
        return f"Thank you {first_name} from {company}. I've noted your information. What can I help you with today?"
    else:
        return f"Thank you {name} from {company}. I've noted your information. What can I help you with today?"

@function_tool
async def store_caller_email(email: str) -> str:
    """Store the caller's email address in our system."""
    ctx = get_job_context()
    if not ctx:
        return "I couldn't save your email address. How can I help you today?"
    
    if not email or not email.strip():
        return "I need a valid email address. Could you please provide your email address?"
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        return "That doesn't look like a valid email address. Could you please provide your email address in the format: yourname@company.com?"
    
    try:
        loop = asyncio.get_event_loop()
        
        # If we have a caller ID, update the existing record
        if hasattr(ctx, 'caller_id') and ctx.caller_id:
            update_data = {"email": email.strip()}
            response = await loop.run_in_executor(
                None, lambda: requests.patch(f"{API_URL}/api/callers/{ctx.caller_id}", json=update_data)
            )
            
            if response.status_code == 200:
                ctx.caller_email = email.strip()
                logger.info(f"Updated caller email to: {email}")
                return f"Perfect! I've saved your email address {email} in our system. What can I help you with today?"
            else:
                logger.warning(f"Could not update caller email: {response.status_code} - {response.text}")
                return "I had trouble saving your email address, but I've noted it for this call. What can I help you with today?"
        
        # If we don't have a caller ID but have a phone number, try to find and update
        elif hasattr(ctx, 'caller_phone_number') and ctx.caller_phone_number != "Unknown":
            # Search for caller by phone number
            search_response = await loop.run_in_executor(
                None, lambda: requests.get(f"{API_URL}/api/callers/search?phone={ctx.caller_phone_number}")
            )
            
            if search_response.status_code == 200:
                result = search_response.json()
                if result.get('success') and result.get('data'):
                    caller_id = result['data']['_id']
                    update_data = {"email": email.strip()}
                    response = await loop.run_in_executor(
                        None, lambda: requests.patch(f"{API_URL}/api/callers/{caller_id}", json=update_data)
                    )
                    
                    if response.status_code == 200:
                        ctx.caller_id = caller_id
                        ctx.caller_email = email.strip()
                        logger.info(f"Updated caller email to: {email}")
                        return f"Perfect! I've saved your email address {email} in our system. What can I help you with today?"
                    else:
                        logger.warning(f"Could not update caller email: {response.status_code} - {response.text}")
                        return "I had trouble saving your email address, but I've noted it for this call. What can I help you with today?"
                else:
                    # Store in context for now
                    ctx.caller_email = email.strip()
                    return f"Thank you! I've noted your email address {email} for this call. What can I help you with today?"
            else:
                # Store in context for now
                ctx.caller_email = email.strip()
                return f"Thank you! I've noted your email address {email} for this call. What can I help you with today?"
        else:
            # Store in context for now
            ctx.caller_email = email.strip()
            return f"Thank you! I've noted your email address {email} for this call. What can I help you with today?"
            
    except Exception as e:
        logger.error(f"Error storing caller email: {str(e)}")
        # Store in context for now
        ctx.caller_email = email.strip()
        return f"Thank you! I've noted your email address {email} for this call. What can I help you with today?"

@function_tool
async def store_callback_number(callback_number: str) -> str:
    """Store the caller's preferred callback number."""
    ctx = get_job_context()
    if ctx:
        ctx.callback_number = callback_number
        return f"Thank you. I've noted your callback number as {callback_number}. How can I help you today?"
    return "I couldn't save your callback number. How can I help you today?"

@function_tool
async def transfer_call(ctx: RunContext) -> str:
    """Transfer the call to a human agent, called after confirming with the user"""
    
    # Main office number - configured via config.py
    transfer_to = MAIN_OFFICE_NUMBER

    logger.info(f"Transferring call to {transfer_to}")

    # let the message play fully before transferring
    await ctx.session.generate_reply(
        instructions="Inform the user that you're transferring them to a different agent."
    )

    job_ctx = get_job_context()
    try:
        # First, try SIP transfer (if enabled)
        try:
            # Get the actual participant from the room
            participants = await job_ctx.api.room.list_participants(
                api.ListParticipantsRequest(room=job_ctx.room.name)
            )
            
            # Find the SIP participant (the caller)
            sip_participant = None
            for participant in participants.participants:
                if participant.identity and participant.identity != "agent":
                    sip_participant = participant
                    break
            
            if not sip_participant:
                logger.error("No SIP participant found in room for transfer")
                return "Sorry, I couldn't find the caller to transfer. Please try again or contact support directly."
            
            logger.info(f"Attempting SIP transfer for participant: {sip_participant.identity} to {transfer_to}")
            
            await job_ctx.api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=job_ctx.room.name,
                    participant_identity=sip_participant.identity,
                    transfer_to=f"tel:{transfer_to}",
                )
            )
            return f"Transferring your call to {transfer_to}."
            
        except Exception as sip_error:
            logger.warning(f"SIP transfer failed: {sip_error}")
            
            # Fallback: Use call forwarding approach
            logger.info("Attempting call forwarding as fallback")
            
            # Inform the user about the transfer
            await ctx.session.say(
                f"I'm transferring you to our main office at {transfer_to}. Please hold while I connect you.",
                allow_interruptions=False
            )
            
            # Wait for the message to complete
            current_speech = ctx.session.current_speech
            if current_speech:
                await current_speech.wait_for_playout()
            
            # End the current call (this will disconnect the caller)
            await hangup_call()
            
            return f"Call transferred to {transfer_to}. The caller has been disconnected and should call the main office number directly."
            
    except Exception as e:
        logger.error(f"Error transferring call: {e}")
        return f"Sorry, I encountered an error while trying to transfer your call. Please call our main office directly at {transfer_to}."

@function_tool
async def get_open_it_support_ticket(
    ctx: RunContext, name: str = None, company: str = None, details: str = None, confirmed: bool = False
) -> str:
    """
    Open IT Support Ticket in Halo PSA.
    Args:
        ctx: The run context for accessing session methods.
        name: The user's name (optional if already provided).
        company: The user's company (optional if already provided).
        details: The details of the IT support request.
        confirmed: Whether the user has confirmed the info.
    """
    # Get caller's information from context if not provided
    job_ctx = get_job_context()
    caller_phone = getattr(job_ctx, 'caller_phone_number', 'Unknown') if job_ctx else 'Unknown'
    callback_number = getattr(job_ctx, 'callback_number', None) if job_ctx else None
    
    # Prioritize caller information found during automatic lookup
    # Use provided parameters only if caller info wasn't found automatically
    context_name = getattr(job_ctx, 'caller_name', None)
    context_company = getattr(job_ctx, 'caller_company', None)
    
    # Use context values first, then fall back to provided parameters
    # Make this more explicit to ensure context values are prioritized
    # Handle both None and empty string cases
    if context_name and context_name.strip():
        caller_name = context_name
        logger.info(f"[TICKET] Using context name: '{context_name}'")
    else:
        caller_name = name if name and name.strip() else None
        logger.info(f"[TICKET] Using parameter name: '{name}'")
    
    if context_company and context_company.strip():
        caller_company = context_company
        logger.info(f"[TICKET] Using context company: '{context_company}'")
    else:
        caller_company = company if company and company.strip() else None
        logger.info(f"[TICKET] Using context company: '{company}'")
    
    # Log what information we're using
    logger.info(f"[TICKET] Context values - caller_name: '{context_name}', caller_company: '{context_company}'")
    logger.info(f"[TICKET] Function parameters - name: '{name}', company: '{company}'")
    logger.info(f"[TICKET] Final values - caller_name: '{caller_name}', caller_company: '{caller_company}'")
    logger.info(f"[TICKET] Using context name: {context_name is not None}, Using context company: {context_company is not None}")
    logger.info(f"[TICKET] Parameter types - name type: {type(name)}, company type: {type(company)}")
    logger.info(f"[TICKET] Context types - context_name type: {type(context_name)}, context_company type: {type(context_company)}")
    
    # Use callback number if available, otherwise use caller phone
    contact_number = callback_number or caller_phone
    
    logger.info(f"[DEBUG] Name: {caller_name}, Company: {caller_company}, Details: {details}, Confirmed: {confirmed}")
    logger.info(f"[DEBUG] Caller phone number: {caller_phone}")
    logger.info(f"[DEBUG] Callback number: {callback_number}")
    logger.info(f"[DEBUG] Contact number to use: {contact_number}")
    
    # If we don't have name or company, ask for them
    logger.info(f"[TICKET] Checking required info - caller_name: '{caller_name}', caller_company: '{caller_company}'")
    logger.info(f"[TICKET] Boolean check - caller_name truthy: {bool(caller_name)}, caller_company truthy: {bool(caller_company)}")
    
    if not caller_name or not caller_company:
        missing_info = []
        if not caller_name:
            missing_info.append("name")
        if not caller_company:
            missing_info.append("company")
        
        logger.info(f"[TICKET] Missing info: {missing_info}")
        return f"I need your {' and '.join(missing_info)} to create a support ticket. Could you please provide your {' and '.join(missing_info)}?"
    
    # If we don't have details, ask for them
    if not details:
        return "What is the issue you're experiencing? Please describe the problem you need help with?"
    
    if not confirmed:
        logger.info("[TICKET] Starting confirmation process - caller has NOT confirmed yet")
        
        # Check if we're using automatically found information
        auto_found_name = getattr(job_ctx, 'caller_name', None) is not None
        auto_found_company = getattr(job_ctx, 'caller_company', None) is not None
        
        info_source = []
        if auto_found_name:
            info_source.append("name from our system")
        if auto_found_company:
            info_source.append("company from our system")
        
        source_message = ""
        if info_source:
            source_message = f" (I found your {' and '.join(info_source)} using your phone number)"
        
        # Use session.say() with allow_interruptions=False to prevent interruptions
        confirmation_message = (
            f"Let me confirm your ticket details{source_message}:\n"
            f"Name: {caller_name}\n"
            f"Company: {caller_company}\n"
            f"Request Details: {details}\n"
            f"Phone Number: {contact_number}\n"
            "Please say 'yes' to confirm and I'll create your ticket, or let me know if you need to add or change anything."
        )

        logger.info(f"[TICKET] Confirmation message: {confirmation_message}")
        
        logger.info(f"[TICKET] Saying confirmation message with allow_interruptions=False")
        # Say the confirmation message without allowing interruptions
        await ctx.session.say(confirmation_message, allow_interruptions=False)
        
        logger.info(f"[TICKET] Confirmation message completed, now saying wait message")
        # Return a clear message that we're waiting for confirmation
        # Use allow_interruptions=False to prevent interruption during this critical message
        await ctx.session.say("I'm waiting for your confirmation to create the ticket. Please say 'yes' if the information is correct, or let me know what needs to be changed.", allow_interruptions=False)
        
        logger.info(f"[TICKET] Wait message completed, returning empty string to prevent additional speaking")
        # Return empty string to prevent any additional speaking
        return ""
    
    # If confirmed, proceed to create the ticket
    logger.info("[TICKET] Caller has confirmed - proceeding to create ticket")
    loop = asyncio.get_event_loop()
    try:
        # Inform the caller that we're now creating the ticket
        creation_message = "Perfect! I'm now creating your IT support ticket. Please hold while I process this for you."
        await ctx.session.say(creation_message, allow_interruptions=False)
        
        # Include phone number in the ticket details
        enhanced_details = f"{details}\n\nCaller Phone Number: {contact_number}"
        
        # Create ticket using the Node.js API with correct Halo format
        ticket_data = {
            "summary": f"{caller_name} - {caller_company}",
            "details": enhanced_details,
            "status_id": 1,
            "tickettype_id": 1,
            "sla_id": 3,
            "priority_id": 4,
            "client_id": int(job_ctx.halo_client_id) if hasattr(job_ctx, 'halo_client_id') and job_ctx.halo_client_id and job_ctx.halo_client_id != "0" else 174,
            "site_id": int(job_ctx.halo_site_id) if hasattr(job_ctx, 'halo_site_id') and job_ctx.halo_site_id and job_ctx.halo_site_id != "0" else 216,
            "user_id": int(job_ctx.halo_user_id) if hasattr(job_ctx, 'halo_user_id') and job_ctx.halo_user_id and job_ctx.halo_user_id != "0" else 267,
            "team_id": 1,  # IT Support team
            "agent_id": 1,
            "category_1": "Business Applications",
            "impact": 3,
            "urgency": 2
        }
        
        logger.info(f"[DEBUG] Creating ticket with data: {json.dumps(ticket_data, indent=2)}")
        
        response = await loop.run_in_executor(
            None, lambda: requests.post(f"{API_URL}/api/halo/tickets", json=ticket_data)
        )
        
        logger.info(f"[DEBUG] Ticket creation response status: {response.status_code}")
        logger.info(f"[DEBUG] Ticket creation response: {response.text}")
        
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data', {}).get('id'):
                ticket_id = result['data']['id']
                # Use session.say() with allow_interruptions=False for the success message
                success_message = f"Your IT support ticket has been opened. Ticket ID: {ticket_id}. A tech will get back to you in 1 to 2 hours. Is there anything else I can help you with today?"
                await ctx.session.say(success_message, allow_interruptions=False)
                return None
            elif result.get('id'):  # Direct Halo API response format
                ticket_id = result['id']
                # Use session.say() with allow_interruptions=False for the success message
                success_message = f"Your IT support ticket has been opened. Ticket ID: {ticket_id}. A tech will get back to you in 1 to 2 hours. Is there anything else I can help you with today?"
                await ctx.session.say(success_message, allow_interruptions=False)
                return None
            else:
                # Use session.say() with allow_interruptions=False for the success message
                success_message = "Your IT support ticket has been opened, but I could not retrieve the ticket ID. A tech will get back to you in 1 to 2 hours. Is there anything else I can help you with today?"
                await ctx.session.say(success_message, allow_interruptions=False)
                return None
        else:
            logger.error(f"API error creating ticket: {response.status_code} - {response.text}")
            # Use session.say() with allow_interruptions=False for the error message
            error_message = "Sorry, there was an error opening your IT support ticket. Please try again or contact support directly. Is there anything else I can help you with today?"
            await ctx.session.say(error_message, allow_interruptions=False)
            return None
    except Exception as e:
        logger.error(f"Error opening IT support ticket: {str(e)}")
        # Use session.say() with allow_interruptions=False for the error message
        error_message = f"Sorry, there was an error opening your IT support ticket: {str(e)}. Is there anything else I can help you with today?"
        await ctx.session.say(error_message, allow_interruptions=False)
        return None

@function_tool
async def get_open_copier_support_ticket(
    name: str = None, company: str = None, details: str = None, confirmed: bool = False
) -> str:
    """
    Open Copier Support Ticket in Halo PSA.
    Args:
        name: The user's name (optional if already provided).
        company: The user's company (optional if already provided).
        details: The details of the copier support request.
        confirmed: Whether the user has confirmed the info.
    """
    # Get caller's information from context if not provided
    ctx = get_job_context()
    
    # Prioritize caller information found during automatic lookup
    caller_name = getattr(ctx, 'caller_name', None) or name
    caller_company = getattr(ctx, 'caller_company', None) or company
    
    # Log what information we're using
    logger.info(f"[COPIER TICKET] Using caller name: {caller_name} (from context: {getattr(ctx, 'caller_name', None) is not None})")
    logger.info(f"[COPIER TICKET] Using caller company: {caller_company} (from context: {getattr(ctx, 'caller_company', None) is not None})")
    
    return "I apologize, but the copier support ticket functionality is not implemented yet. Please contact our support team directly for copier-related issues, or I can help you with IT support tickets instead."

@function_tool
async def reorder_copier_supplies(
    name: str = None, company: str = None, supplies_needed: str = None, confirmed: bool = False
) -> str:
    """
    Reorder copier supplies.
    Args:
        name: The user's name (optional if already provided).
        company: The user's company (optional if already provided).
        supplies_needed: The supplies that need to be reordered.
        confirmed: Whether the user has confirmed the info.
    """
    # Get caller's information from context if not provided
    ctx = get_job_context()
    
    # Prioritize caller information found during automatic lookup
    caller_name = getattr(ctx, 'caller_name', None) or name
    caller_company = getattr(ctx, 'caller_company', None) or company
    
    # Log what information we're using
    logger.info(f"[SUPPLIES] Using caller name: {caller_name} (from context: {getattr(ctx, 'caller_name', None) is not None})")
    logger.info(f"[SUPPLIES] Using caller company: {caller_company} (from context: {getattr(ctx, 'caller_company', None) is not None})")
    
    return "I apologize, but the copier supplies reordering functionality is not implemented yet. Please contact our supplies department directly for copier supply orders, or I can help you with IT support tickets instead."


async def entrypoint(ctx: JobContext):
    """Main entry point for the telephony voice agent."""
    await ctx.connect()
    
    # Wait for participant (caller) to join
    participant = await ctx.wait_for_participant()
    logger.info(f"Phone call connected from participant: {participant.identity}")
    
    # Extract caller's phone number from participant.identity first, then metadata
    caller_phone_number = None
    try:
        logger.info(f"Participant identity: {participant.identity}")
        logger.info(f"Participant metadata: {participant.metadata}")
        
        # Priority 1: Use participant.identity as the primary source
        if participant.identity:
            caller_phone_number = participant.identity
            logger.info(f"Using participant.identity as phone number: {caller_phone_number}")
        
        # Priority 2: If identity doesn't contain digits, try metadata
        if not caller_phone_number or not any(char.isdigit() for char in str(caller_phone_number)):
            if hasattr(participant, 'metadata') and participant.metadata:
                try:
                    metadata = json.loads(participant.metadata)
                    logger.info(f"Parsed metadata: {metadata}")
                    
                    # Try various common field names for phone numbers
                    phone_fields = ['phone_number', 'caller_number', 'from', 'caller_id', 'phone', 'number', 'contact_number']
                    for field in phone_fields:
                        if field in metadata and metadata[field]:
                            caller_phone_number = metadata[field]
                            logger.info(f"Found phone number in metadata field '{field}': {caller_phone_number}")
                            break
                except json.JSONDecodeError as e:
                    logger.warning(f"Could not parse metadata as JSON: {e}")
                    # Try to extract phone number from raw metadata string
                    metadata_str = str(participant.metadata)
                    logger.info(f"Raw metadata string: {metadata_str}")
        
        # Priority 3: If still no phone number, try to extract from room name
        if not caller_phone_number or not any(char.isdigit() for char in str(caller_phone_number)):
            logger.info(f"Room name: {ctx.room.name}")
            # Sometimes the room name contains the phone number
            if ctx.room.name and any(char.isdigit() for char in ctx.room.name):
                caller_phone_number = ctx.room.name
                logger.info(f"Using room name as phone number: {caller_phone_number}")
        
        # Format the phone number as xxx-xxx-xxxx
        if caller_phone_number and caller_phone_number != "Unknown":
            formatted_phone = format_phone_number(caller_phone_number)
            logger.info(f"Original phone number: {caller_phone_number}")
            logger.info(f"Formatted phone number: {formatted_phone}")
            caller_phone_number = formatted_phone
            logger.info(f"Caller phone number: {caller_phone_number}")
        
        logger.info(f"Final caller phone number: {caller_phone_number}")
    except Exception as e:
        logger.warning(f"Could not extract phone number: {str(e)}")
        caller_phone_number = "Unknown"
    
    # Store phone number in a global variable or context for later use
    ctx.caller_phone_number = caller_phone_number
    
    # Automatically look up caller information if we have a valid phone number
    if caller_phone_number and caller_phone_number != "Unknown":
        try:
            logger.info(f"Automatically looking up caller with phone number: {caller_phone_number}")
            
            # Use the Node.js API to look up the caller
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: requests.get(f"{API_URL}/api/callers/search?phone={caller_phone_number}")
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    caller_data = result['data']
                    
                    # Store the found information in context
                    ctx.caller_name = f"{caller_data.get('firstname', '')} {caller_data.get('lastname', '')}".strip()
                    ctx.caller_company = caller_data.get('company', '')
                    ctx.caller_email = caller_data.get('email', '')
                    ctx.caller_phone = caller_data.get('phone', '')
                    ctx.halo_user_id = caller_data.get('user_id', '')
                    ctx.halo_client_id = caller_data.get('client_id', '')
                    ctx.halo_site_id = caller_data.get('site_id', '')
                    ctx.caller_id = caller_data.get('_id', '')
                    
                    # Log what we stored in context
                    logger.info(f"[AUTO LOOKUP] Stored in context - Name: '{ctx.caller_name}', Company: '{ctx.caller_company}'")
                    
                    # Update last called timestamp
                    if ctx.caller_id:
                        try:
                            await loop.run_in_executor(
                                None, lambda: requests.patch(f"{API_URL}/api/callers/{ctx.caller_id}/last-called")
                            )
                            logger.info(f"Updated last called timestamp for caller ID: {ctx.caller_id}")
                        except Exception as e:
                            logger.warning(f"Could not update last called timestamp: {str(e)}")
                    
                    logger.info(f"Found caller: {ctx.caller_name} from {ctx.caller_company}")
                else:
                    logger.info("No caller found in system - will ask for information")
            else:
                logger.warning(f"API error during automatic lookup: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"Error during automatic caller lookup: {str(e)}")
    else:
        logger.info("No valid phone number available for automatic lookup")
    
    # Initialize the conversational agent
    agent = Agent(
        instructions="""You are a friendly and helpful AI assistant answering phone calls. 
        
        Your personality:
        - Professional yet warm and approachable
        - Speak clearly and at a moderate pace for phone calls
        - Keep responses concise but complete
        - Ask clarifying questions when needed
        - Use first names when greeting callers to make conversations more personal
        
        Your capabilities:
        - Open an IT support ticket
        - Open a copier support ticket
        - Reorder copier supplies
        - Transfer the call to a human agent
        - End the call when the user is done
        - Get the caller's phone number
        - Look up caller information in our system
        
        Important guidelines:
        - When the user says they are done, want to hang up, or end the call, use the end_call function which will say goodbye and then end the call.
        - CRITICAL: Immediately recognize and respond to end call requests. Common phrases include: "I'm done", "That's all", "Goodbye", "Hang up", "End call", "I'm finished", "That's everything", "No more help needed", "Bye", "Thank you, goodbye", "I'm all set", "That's it", "No more questions", "I'm good", "That's all I need", "End the call", "Hang up the phone", "I'm ready to go", "That's all I wanted", "I'm satisfied", "No more assistance needed".
        - Always identify yourself as an AI assistant when asked.
        - Keep responses conversational and under 30 seconds for phone clarity.
        - When users provide their name and company, remember this information for the duration of the call.
        - When users provide their callback number, remember this information for the duration of the call.
        - When users provide their email address, remember this information for the duration of the call.
        - If a user asks to create a ticket but hasn't provided their name or company yet, ask for this information first.
        - Use the caller's first name in your responses to make the conversation more personal when appropriate.
        - Always ask "What can I help you with today?" or similar questions to understand their needs.
        - Use the store_callback_number function when users provide their preferred callback number.
        - Use the store_caller_email function when users provide their email address.
        - When creating tickets, use the caller information that was automatically found in our system if available.
        - If caller information was found automatically, mention this to the user when confirming ticket details.
        - When calling get_open_it_support_ticket, do NOT provide name and company parameters if the system already found this information automatically.
        - Only ask for name and company if the system couldn't find the caller's information automatically.
        - IMPORTANT: If caller information was found automatically during the initial lookup, call get_open_it_support_ticket with NO parameters for name and company.
        - The function will automatically use the caller information that was found and stored in the system.
        - IMPORTANT: When calling get_open_it_support_ticket, always provide the RunContext as the first parameter, followed by other optional parameters.
        - If the system prompts for an email address (when no email is found in the database), ask the user to provide their email address.
        - CRITICAL: When reading back ticket details for confirmation, use the session.say() method with allow_interruptions=False to prevent the caller from accidentally interrupting you.
        - CRITICAL: When providing important information like ticket confirmations, ticket IDs, or final status updates, always use allow_interruptions=False to ensure the caller hears the complete message.
        - CRITICAL: During ticket creation, NEVER allow interruptions when reading back ticket details or asking for confirmation. The caller must hear the complete confirmation message.
        - CRITICAL: If a caller interrupts during ticket confirmation, politely ask them to wait until you finish reading the details, then ask for confirmation again.
        - CRITICAL: Ticket creation is a multi-step process: 1) Read back details (non-interruptible), 2) Wait for "yes" confirmation, 3) Create ticket (non-interruptible), 4) Provide result (non-interruptible).
        - Use the transfer_call function when a user requests to speak with a human agent, wants to be transferred, or when you cannot help with their specific request.
        - Before transferring, confirm with the user that they want to be transferred to a human agent.
        - When transferring, inform the user that you're transferring them to a different agent.""",
        tools=[get_current_time, get_open_it_support_ticket, get_open_copier_support_ticket, reorder_copier_supplies, end_call, get_caller_phone_number, debug_caller_info, lookup_caller_in_system, store_caller_info, store_caller_email, store_callback_number, transfer_call]
    )
    
    # Configure the voice processing pipeline optimized for telephony
    session = AgentSession(
        # Voice Activity Detection
        vad=silero.VAD.load(),
        
        # Speech-to-Text - Deepgram Nova-3
        stt=deepgram.STT(
            model="nova-3",  # Latest model
            language="en-US",
            interim_results=True,
            punctuate=True,
            smart_format=True,
            filler_words=True,
            endpointing_ms=25,
            sample_rate=16000
        ),
        
        # Large Language Model - GPT-4o-mini
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7
        ),
        
        # Text-to-Speech - Cartesia Sonic-2
        tts=cartesia.TTS(
            model="sonic-2",
            voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",  # Professional female voice
            language="en",
            speed=1.0,
            sample_rate=24000
        )
    )
    
    # Start the agent session
    await session.start(agent=agent, room=ctx.room)
    
    # Generate personalized greeting and information gathering in one message
    import datetime
    hour = datetime.datetime.now().hour
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 18:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"
    
    # Create personalized greeting based on whether we found caller information
    logger.info(f"[GREETING] Context caller_name: '{getattr(ctx, 'caller_name', None)}'")
    logger.info(f"[GREETING] Context caller_company: '{getattr(ctx, 'caller_company', None)}'")
    
    if hasattr(ctx, 'caller_name') and ctx.caller_name:
        # We found the caller's information
        first_name = ctx.caller_name.split()[0] if ctx.caller_name else ''
        if first_name:
            greeting_message = f"{time_greeting} {first_name}! Thank you for calling {COMPANY_NAME}. I can help you open an IT support ticket, open a copier support ticket, help you reorder copier supplies, or transfer you to a human agent if needed. What can I help you with today?"
        else:
            greeting_message = f"{time_greeting}! Thank you for calling {COMPANY_NAME}. I can help you open an IT support ticket, open a copier support ticket, help you reorder copier supplies, or transfer you to a human agent if needed. What can I help you with today?"
    else:
        # We didn't find the caller's information
        greeting_message = f"{time_greeting}! Thank you for calling {COMPANY_NAME}. I can help you open an IT support ticket, open a copier support ticket, help you reorder copier supplies, or transfer you to a human agent if needed. Could you please tell me your name and company so I can assist you better?"
    
    await session.generate_reply(
        instructions=f"""Say '{greeting_message}'""",
        allow_interruptions=False
    )
    
    # Initialize callback number (but preserve caller_name and caller_company if found automatically)
    ctx.callback_number = None
    
    # The agent will naturally gather additional information through conversation
    # and we can access it later through the context

if __name__ == "__main__":
    # Configure logging for better debugging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get agent name from environment variable with fallback
    agent_name = os.environ.get("AGENT_NAME", "telephony_agent")
    
    # Run the agent with the name that matches your dispatch rule
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name=agent_name  # This must match your dispatch rule
    ))
