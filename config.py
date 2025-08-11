import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_WS_URL = os.getenv("LIVEKIT_WS_URL", "ws://localhost:7881")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

HALO_CLIENT_ID = os.getenv("HALO_CLIENT_ID")
HALO_CLIENT_SECRET = os.getenv("HALO_CLIENT_SECRET")
HALO_API_URL = os.getenv("HALO_API_URL", "https://intergrated.halopsa.com/api")

# Node.js API configuration
API_URL = os.getenv("API_URL", "http://localhost:3000")

# Call transfer configuration
MAIN_OFFICE_NUMBER = os.getenv("MAIN_OFFICE_NUMBER", "+12108884900") 