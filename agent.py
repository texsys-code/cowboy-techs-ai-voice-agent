import asyncio
import logging
import re
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool
)
from livekit.plugins import deepgram, openai, cartesia, silero
from config import API_URL, MAIN_OFFICE_NUMBER, COMPANY_NAME, EMAIL_DOMAIN, AGENT_NAME

# Import function tools from separate file
from lib.tools import get_current_time
from lib.call_tools.end_call import end_call
from lib.call_tools.caller import lookup_caller, store_caller_info, format_phone_number
from lib.call_tools.tickets import open_it_support_ticket, open_copier_support_ticket, debug_ticket_context

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

    # Initialize the conversational agent
    agent = Agent(
        instructions="""You are a friendly and helpful AI assistant answering phone calls for Cowboy Technologies, LLC. 
        
        Your personality:
        - Professional yet warm and approachable
        - Speak clearly and at a moderate pace for phone calls
        - Keep responses concise but complete
        - Ask clarifying questions when needed
        
        Your capabilities:
        - Open IT support tickets
        - Open copier support tickets  
        - Help with sales and billing questions
        - Help reorder copier supplies
        - Transfer calls to representatives
        - Look up caller information
        - Store caller information
        - Answer general questions
        - Provide weather information
        - Tell the current time

        Ticket Creation Process:
        When someone wants to open a support ticket:
        1. Ask for details about their issue if not provided
        2. Use the open_it_support_ticket function with details=their_issue and confirmed=False to show confirmation
        3. Wait for user to say "yes" to confirm
        4. Use the open_it_support_ticket function again with details=their_issue and confirmed=True to create the ticket
        5. Provide the ticket number when complete
        6. Ask if there's anything else you can help with
        
        IMPORTANT: You must call the function TWICE:
        - First call: confirmed=False to show confirmation message
        - Second call: confirmed=True to actually create the ticket
        
        Note: The system automatically uses the caller's name and company from their phone number lookup, so you don't need to ask for this information again.

        Important guidelines:
        - When the user says they are done, want to hang up, or end the call, use the end_call function which will say goodbye and then end the call.
        - Always identify yourself as an AI assistant when asked.
        - Keep responses conversational and under 30 seconds for phone clarity.
        - Use caller information from context when available for personalized service.
        
        CRITICAL - Interruption Prevention:
        - When reading back ticket details for confirmation, use open_it_support_ticket with confirmed=False
        - When providing important information (ticket numbers, confirmations), the functions will return [NON_INTERRUPTIBLE] messages
        - When giving instructions or asking for confirmation, the functions will return [NON_INTERRUPTIBLE] messages
        - Only allow interruptions during casual conversation and when asking questions
        - This ensures users hear complete information and don't accidentally interrupt critical messages
        
        IMPORTANT: When you receive a message starting with [NON_INTERRUPTIBLE], you must:
        1. Extract the actual message (remove the [NON_INTERRUPTIBLE] prefix)
        2. Use session.say(message, allow_interruptions=False) to speak it without interruption
        3. This prevents users from cutting off critical information
        
        Example usage:
        - For ticket confirmation: Call open_it_support_ticket with confirmed=False
        - For success messages: The function will return a [NON_INTERRUPTIBLE] message
        - For instructions: The function will return a [NON_INTERRUPTIBLE] message""",
        tools=[get_current_time, end_call, lookup_caller, store_caller_info, open_it_support_ticket, open_copier_support_ticket, debug_ticket_context]
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
        await lookup_caller(clean_phone)
        
        logger.info(f"[CALLER_LOOKUP] Caller lookup completed")
    else:
        logger.warning(f"[CALLER_LOOKUP] Could not format phone number from participant identity: {participant.identity}")
        # Set unknown phone number
        ctx.caller_phone_number = "Unknown"

     # Create personalized greeting based on whether we found caller information
    logger.info(f"[GREETING] Context caller_first_name: '{getattr(ctx, 'caller_first_name', None)}'")
    logger.info(f"[GREETING] Context caller_company: '{getattr(ctx, 'caller_company', None)}'")
    
    base_greeting = "I can help you open an IT support ticket, open a copier support ticket, help you reorder copier supplies, help with a sales or billing question, or transfer you to a representative. What can I help you with today?"

    if hasattr(ctx, 'caller_first_name') and ctx.caller_first_name:
        if ctx.caller_first_name:
            greeting_message = f"{time_greeting} {ctx.caller_first_name}! Thank you for calling {COMPANY_NAME}. I can help you open an IT support ticket, open a copier support ticket, help you reorder copier supplies, help with a sales or billing question, or transfer you to a representative. What can I help you with today?"
    else:
        greeting_message = f"{time_greeting}! Thank you for calling {COMPANY_NAME}. {base_greeting}"

    await session.say(
        greeting_message,
        allow_interruptions=False
    )

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