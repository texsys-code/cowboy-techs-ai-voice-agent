import asyncio
import logging
import sys
import os

from livekit import api, rtc
from livekit.agents import get_job_context, RunContext, function_tool

from config import AGENT_NAME, COMPANY_NAME

logger = logging.getLogger(AGENT_NAME)

async def hangup_call():
    """Hang up the call by properly ending the agent session."""
    ctx = get_job_context()

    logger.info("Hanging up call")

    if ctx is None:
        logger.error("No job context available in end_call")
        return

    logger.info(f"Ending call in room {ctx.room.name}")
    
    await ctx.api.room.delete_room(
        api.DeleteRoomRequest(
            room=ctx.room.name
        )
    )

@function_tool
async def end_call(ctx: RunContext):
    """End the call and hang up."""
    logger.info("Ending call")

    await ctx.session.say(f"Thank you for calling {COMPANY_NAME}. Have a great day!", allow_interruptions=False)

    # Wait for any current speech to finish
    current_speech = ctx.session.current_speech

    #if current_speech:
    #    logger.info("Waiting for current speech to finish")
    #    await current_speech.wait_for_playout()
    
    logger.info("Current speech finished, hanging up call")
    
    # Call the hangup function to terminate the call
    await hangup_call()
    
    logger.info("Call ended successfully")
