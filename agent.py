import asyncio
import logging
import re
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
    get_job_context
)
from livekit.plugins import deepgram, openai, cartesia, silero
from config import API_URL, MAIN_OFFICE_NUMBER, COMPANY_NAME, EMAIL_DOMAIN, AGENT_NAME, MODE

# Import function tools from separate file
from lib.tools import get_current_time
from lib.call_tools.end_call import end_call
from lib.call_tools.caller import lookup_caller, store_caller_info, format_phone_number, collect_caller_info
from lib.call_tools.tickets import open_it_support_ticket, debug_ticket_context, collect_caller_email
from lib.call_tools.emails import send_copier_support_email, send_copier_supplies_email, send_auto_replenishment_enrollment_email
from lib.call_tools.sales import submit_sales_inquiry, test_email_system
from lib.call_tools.billing import submit_billing_inquiry
from lib.call_tools.callback import request_callback

# Import agent instructions from modular system
from instructions import get_greeting_instructions, get_active_instructions

#load_dotenv()
logger = logging.getLogger(AGENT_NAME)

async def entrypoint(ctx: JobContext):
    """Main entry point for the telephony voice agent."""
    await ctx.connect()
        
    # Wait for participant (caller) to join
    participant = await ctx.wait_for_participant()
    logger.info(f"Phone call connected from participant: {participant.identity}")
    
    # Try to extract phone number from participant identity
    # Participant identity might be the phone number or contain it
    phone_number = participant.identity
    logger.info(f"Phone number: {phone_number}")

    # Use the format_phone_number function for consistent phone number formatting
    clean_phone = format_phone_number(phone_number)
    logger.info(f"Formatted phone number: {clean_phone}")

    # Initialize the conversational agent with greeting instructions
    # Instructions will be updated dynamically based on caller requests
    agent = Agent(
    instructions=get_greeting_instructions(),
        tools=[get_current_time, end_call, lookup_caller, store_caller_info, open_it_support_ticket, debug_ticket_context, send_copier_support_email, send_copier_supplies_email, send_auto_replenishment_enrollment_email, submit_sales_inquiry, submit_billing_inquiry, test_email_system, collect_caller_email, collect_caller_info, request_callback]
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
        #tts=cartesia.TTS(
        #    model="sonic-2",
        #    voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",  # Professional female voice
        #    language="en",
        #    speed=1.0,
        #    sample_rate=24000
        #)
        
        # Text-to-Speech - OpenAI TTS (Alternative to Cartesia)
        tts=openai.TTS(
            model="tts-1",  # OpenAI's high-quality TTS model
            voice="alloy",  # Professional voice (alloy, echo, fable, onyx, nova, shimmer)
            speed=1.0
        )
    )
    
    # Start the agent session
    await session.start(agent=agent, room=ctx.room)
    
    # Generate personalized greeting based on time of day
    import datetime
    hour = datetime.datetime.now().hour
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 18:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"
    
    # Look up caller information using their phone number
    logger.info(f"[CALLER_LOOKUP] Looking up caller information for participant: {participant.identity}")  
    
    if clean_phone:  # Check if we got a valid phone number back
        logger.info(f"[CALLER_LOOKUP] Formatted phone number: {clean_phone}")
        
        # Store phone number in context for later use
        ctx.caller_phone_number = clean_phone
        
        # Look up caller in database using your fixed function
        logger.info(f"[CALLER_LOOKUP] About to call lookup_caller with phone: {clean_phone}")
        await lookup_caller(clean_phone)
        
        logger.info(f"[CALLER_LOOKUP] Caller lookup completed")
        logger.info(f"[CALLER_LOOKUP] Context after lookup - caller_first_name: '{getattr(ctx, 'caller_first_name', None)}'")
        logger.info(f"[CALLER_LOOKUP] Context after lookup - caller_email: '{getattr(ctx, 'caller_email', None)}'")
        logger.info(f"[CALLER_LOOKUP] Context after lookup - caller_company: '{getattr(ctx, 'caller_company', None)}'")
    else:
        logger.warning(f"[CALLER_LOOKUP] Could not format phone number from participant identity: {participant.identity}")
        # Set unknown phone number
        ctx.caller_phone_number = "Unknown"

    # Check if we have complete caller information after lookup
    has_complete_info = (
        hasattr(ctx, 'caller_first_name') and ctx.caller_first_name and
        hasattr(ctx, 'caller_email') and ctx.caller_email and
        hasattr(ctx, 'caller_company') and ctx.caller_company
    )
    
    if not has_complete_info:
        logger.info("[CALLER_LOOKUP] Incomplete caller information detected, will prompt caller for missing details")
        # Set flag to indicate we need to collect caller information
        ctx.need_caller_info = True
        ctx.missing_caller_fields = []
        
        # Check what specific fields are missing
        if not getattr(ctx, 'caller_first_name', None):
            ctx.missing_caller_fields.append('name')
        if not getattr(ctx, 'caller_email', None):
            ctx.missing_caller_fields.append('email')
        if not getattr(ctx, 'caller_company', None):
            ctx.missing_caller_fields.append('company')
        
        logger.info(f"[CALLER_LOOKUP] Missing caller fields: {ctx.missing_caller_fields}")
    else:
        logger.info("[CALLER_LOOKUP] Complete caller information found")
        ctx.need_caller_info = False

    # Create personalized greeting based on whether we found caller information
    logger.info(f"[GREETING] Context caller_first_name: '{getattr(ctx, 'caller_first_name', None)}'")
    logger.info(f"[GREETING] Context caller_company: '{getattr(ctx, 'caller_company', None)}'")
    
    base_greeting = "I can help you open an IT support ticket, send a copier support request, help you reorder copier supplies, help with a sales question, help with a billing inquiry, or speak with a representative. What can I help you with today?"

    # If we need caller information, collect it first
    if hasattr(ctx, 'need_caller_info') and ctx.need_caller_info:
        logger.info("[GREETING] Collecting missing caller information before greeting")
        
        # Build the information collection request
        missing_fields = ctx.missing_caller_fields
        if missing_fields:
            info_request = f"{time_greeting}! Thank you for calling {COMPANY_NAME}. Before I can help you, I need to collect some information. "
            if 'name' in missing_fields:
                info_request += "What is your name? "
            if 'company' in missing_fields:
                info_request += "What company are you calling from? "
            if 'email' in missing_fields:
                info_request += "What is your email address? "
            
            # Ask for the missing information
            await session.say(
                info_request,
                allow_interruptions=False
            )
            logger.info(f"[GREETING] Requested missing caller info: {missing_fields}")
            
            # Note: The actual collection will happen during the conversation
            # The agent will use collect_caller_info function when the caller responds
        else:
            # Fallback greeting if no specific missing fields identified
            await session.say(
                f"{time_greeting}! I need to collect some information before I can help you. What is your name?",
                allow_interruptions=False
            )
    else:
        # We have complete caller information, give personalized greeting
        if hasattr(ctx, 'caller_first_name') and ctx.caller_first_name:
            if MODE == "dev":
                greeting_message = f"{time_greeting} {ctx.caller_first_name}! How can I help you today?"
            else:
                greeting_message = f"{time_greeting} {ctx.caller_first_name}! Thank you for calling {COMPANY_NAME}. {base_greeting}"
        else:
            if MODE == "dev":
                greeting_message = f"{time_greeting}! How can I help you today?"
            else:
                greeting_message = f"{time_greeting}! Thank you for calling {COMPANY_NAME}. {base_greeting}"
        
        await session.say(
            greeting_message,
            allow_interruptions=False
        )
        logger.info("[GREETING] Personalized greeting sent successfully")
    
    logger.info("Agent session started and greeting sent successfully")
    
    # For LiveKit agents, the conversation is handled automatically by the agent framework
    # Once we start the session, the framework will:
    # 1. Listen for user input continuously
    # 2. Process user requests using the available tools
    # 3. Call the end_call function when users say goodbye
    # 4. Automatically terminate the call when appropriate
    
    logger.info("LiveKit agent framework will now handle the conversation automatically")
    logger.info("Users can say 'goodbye', 'end call', 'hang up', etc. to trigger the end_call function")
    
    # If we need caller information, the agent will automatically prompt for it
    # The agent instructions will guide it to collect missing caller details
    if hasattr(ctx, 'need_caller_info') and ctx.need_caller_info:
        logger.info("Agent will collect missing caller information during conversation")
        logger.info(f"Missing fields to collect: {ctx.missing_caller_fields}")
        


if __name__ == "__main__":
    # Configure logging for better debugging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the agent with the name that matches your dispatch rule
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name=AGENT_NAME  # This must match your dispatch rule
    ))