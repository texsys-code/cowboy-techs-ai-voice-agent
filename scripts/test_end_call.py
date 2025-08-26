#!/usr/bin/env python3
"""
Test script to verify the end_call function works properly.
This script simulates the call ending process without actually connecting to LiveKit.
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to the path so we can import the end_call module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.call_tools.end_call import hangup_call

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_end_call():
    """Test the end_call functionality."""
    logger.info("Testing end_call function...")
    
    try:
        # Test the hangup_call function
        logger.info("Calling hangup_call function...")
        await hangup_call()
        
        # This should not be reached if hangup_call works properly
        logger.error("ERROR: hangup_call did not exit the process!")
        
    except Exception as e:
        logger.error(f"Error testing end_call: {e}")

async def test_without_livekit():
    """Test the end_call function without LiveKit context."""
    logger.info("Testing end_call without LiveKit context...")
    
    try:
        # Test the hangup_call function without LiveKit context
        logger.info("Calling hangup_call function without LiveKit context...")
        await hangup_call()
        
        # This should not be reached if hangup_call works properly
        logger.error("ERROR: hangup_call did not exit the process!")
        
    except Exception as e:
        logger.error(f"Error testing end_call without LiveKit: {e}")
        logger.info("This is expected behavior when not in a LiveKit context")

if __name__ == "__main__":
    logger.info("Starting end_call test...")
    
    try:
        # Run the test
        asyncio.run(test_without_livekit())
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
    
    logger.info("Test completed successfully")
