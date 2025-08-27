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
from config import API_URL, MAIN_OFFICE_NUMBER, COMPANY_NAME, EMAIL_DOMAIN, AGENT_NAME, MODE

# Import function tools from separate file
from lib.tools import get_current_time
from lib.call_tools.end_call import end_call
from lib.call_tools.caller import lookup_caller, store_caller_info, format_phone_number
from lib.call_tools.tickets import open_it_support_ticket, debug_ticket_context, collect_caller_email
from lib.call_tools.emails import send_copier_support_email, send_copier_supplies_email
from lib.call_tools.sales import submit_sales_inquiry, test_email_system
from lib.call_tools.callback import request_callback

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
        instructions="""You are a friendly and helpful AI assistant answering phone calls. 
        
        Your personality:
        - Professional yet warm and approachable
        - Speak clearly and at a moderate pace for phone calls
        - Keep responses concise but complete
        - Ask clarifying questions when needed
        
        Your capabilities:
        - Open IT support tickets
        - Send copier support requests (emails to service team)
        - Help with sales and billing questions
        - Send copier supplies requests (emails to service team)
        - Transfer calls to representatives
        - Request callbacks when call volumes are high
        - Look up caller information
        - Store caller information
        - Answer general questions
        - Provide weather information
        - Tell the current time
    
        CRITICAL - Copier Requests:
        - Copier support requests: Use send_copier_support_email function
        - Copier supplies requests: Use send_copier_supplies_email function
        - NEVER use order_copier_supplies or open_copier_support_ticket functions
        - All copier requests now send emails to the service team instead of creating tickets
        
        CRITICAL - Data Sanitization:
        - All data has been sanitized to remove masking patterns (***, **, etc.)
        - If you see [MASKED], [REDACTED], or [SENSITIVE] in any data, this is normal and expected
        - NEVER read these placeholders literally - they indicate sensitive information has been removed
        - When reading back information, skip any [MASKED], [REDACTED], or [SENSITIVE] placeholders
        - Focus on the actual user-provided information, not system placeholders
        
        CRITICAL - Email Handling:
        - ALWAYS check if caller email is already available from the phone lookup first
        - If email is found in caller lookup: Use it automatically, do NOT ask for it again
        - If email is NOT found in caller lookup: Use collect_caller_email function to get it
        - NEVER accept invalid email formats (like "travis.thomsen@ibt,inc..com")
        - The collect_caller_email function will validate and clean the email address
        - Store the validated email in context for future use
        
        Example of proper email handling:
        - If caller lookup found email: "I have your email from our system: john@company.com"
        - If no email found: "I need your email address to complete this request. Please provide your email address."
        - After collecting: "Thank you! I've recorded your email address as jane@company.com"
        
        Example usage:
        - For ticket creation: Check if ctx.caller_email exists, if not use collect_caller_email
        - For supply orders: Check if ctx.caller_email exists, if not use collect_caller_email
        - For sales inquiries: Check if ctx.caller_email exists, if not use collect_caller_email

        Example of proper data handling:
        - If you see: "Name: John Doe, Company: [MASKED], Phone: 555-1234"
        - You should say: "Name: John Doe, Phone: 555-1234" (skip the [MASKED] company)
        - DO NOT say: "Name: John Doe, Company: masked, Phone: 555-1234"

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

        Copier Support Process:
        CRITICAL: Use send_copier_support_email function for ALL copier support requests.
        When someone wants to open a copier support ticket, follow this script:
        
        IMPORTANT: DO NOT ask for caller information that's already available from the phone lookup!
        The system automatically has: name, company, phone number from the caller lookup.
        Only ask for information that's NOT already available.
        
        1. Start with: "Sure, I can help you with that. Do you have an Equipment ID number for the machine that needs service?"

        2. If they say YES:
            - Ask: "Great — please provide the Equipment ID number."
            - Collect: Equipment ID number
            - Ask: "Can you describe the problem you're having with this equipment?"
            - Collect: problem description
            - Use send_copier_support_email with equipment_id, details, and confirmed=False
            - After confirmation, use send_copier_support_email with confirmed=True
            - NOTE: Use existing caller info (name, company, phone) from context
        
        3. If they say NO:
            - Ask: "No problem — please provide the make and model and serial number, if you have it, of the equipment."
            - Collect: make_model, serial_number
            - Ask: "Are you currently contracted under a service maintenance agreement with Cowboy Technologies, LLC?"
            - Collect: service_agreement (true/false)
            - Ask: "Can you describe the problem you're having?"
            - Collect: problem description
            - Use send_copier_support_email with make_model, serial_number, service_agreement, details, and confirmed=False
            - After confirmation, use send_copier_support_email with confirmed=True
            - NOTE: Use existing caller info (name, company, phone) from context
        
        CRITICAL: The caller's name, company, and phone number are automatically available from the phone lookup.
        DO NOT ask for this information again. Only collect equipment details and problem description.
        
        NOTE: This process now sends emails to the service team instead of creating tickets.
        CRITICAL: Always use send_copier_support_email function, never use open_copier_support_ticket.

        Copier Supplies Ordering Process:
        CRITICAL: Use send_copier_supplies_email function for ALL copier supplies requests.
        When someone wants to order copier supplies, follow this script:
        
        1. Start with: "Sure, I can help you place a supply order. Do you have an Equipment ID number for this request?"
        
        2. If they say YES:
            - Ask: "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"
            - Collect: Equipment ID and supply details
            - Use send_copier_supplies_email with equipment_id, supply_details, and confirmed=False
            - After confirmation, use send_copier_supplies_email with confirmed=True
            - After order is placed, ask: "Will that be all today or Would you like to add another Equipment ID number for a separate supply request? (Yes/No)"
            - If YES, repeat the process for additional equipment
            - If NO, continue with conversation
            - NOTE: Use existing caller info (name, company, phone) from context
        
        3. If they say NO:
            - Ask: "Please tell me the item number and type of supplies you need."
            - Collect: item_number and supply_details
            - Ask: "May I have your name, email address, and callback number?"
            - Collect: caller_name, caller_email, callback_number
            - Use send_copier_supplies_email with item_number, supply_details, caller_name, caller_email, callback_number, and confirmed=False
            - After confirmation, use send_copier_supplies_email with confirmed=True
        
        4. After final order is placed:
            - Say: "Your supplies request has been sent to our service team. By the way, we offer an auto-replenishment program so toner ships automatically when your supply level reaches a set percentage. If you'd like to enroll, just press 1."
        
        CRITICAL: For Equipment ID orders, use existing caller info from phone lookup.
        For non-Equipment ID orders, collect name, email, and callback number manually.
        
        NOTE: This process now sends emails to the service team instead of creating tickets.
        CRITICAL: Always use send_copier_supplies_email function, never use order_copier_supplies.
        
        Important guidelines:
        - When the user says they are done, want to hang up, or end the call, use the end_call function which will say goodbye and then end the call.
        
        Always identify yourself as an AI assistant when asked.
        Keep responses conversational and under 30 seconds for phone clarity.""",
        tools=[get_current_time, end_call, lookup_caller, store_caller_info, open_it_support_ticket, debug_ticket_context, send_copier_support_email, send_copier_supplies_email, submit_sales_inquiry, test_email_system, collect_caller_email, request_callback]
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
        if MODE == "dev":
            greeting_message = f"{time_greeting} {ctx.caller_first_name}! How can I help you today?"
        else:
            if ctx.caller_first_name:
                greeting_message = f"{time_greeting} {ctx.caller_first_name}! Thank you for calling {COMPANY_NAME}. I can help you open an IT support ticket, send a copier support request, help you reorder copier supplies, help with a sales or billing question, request a callback from a representative, or transfer you to a representative. What can I help you with today?"
    else:
        if MODE == "dev":
            greeting_message = f"{time_greeting}! How can I help you today?"
        else:
            greeting_message = f"{time_greeting}! Thank you for calling {COMPANY_NAME}. {base_greeting}"

    await session.generate_reply(
        instructions=f"""Say '{greeting_message}'""",
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