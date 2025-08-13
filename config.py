import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LiveKit configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_WS_URL = os.getenv("LIVEKIT_WS_URL", "ws://localhost:7881")

# AI Service API Keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

# Halo PSA Configuration
HALO_CLIENT_ID = os.getenv("HALO_CLIENT_ID")
HALO_CLIENT_SECRET = os.getenv("HALO_CLIENT_SECRET")
HALO_API_URL = os.getenv("HALO_API_URL", "https://intergrated.halopsa.com/api")

# Node.js API configuration
API_URL = os.getenv("API_URL", "http://localhost:3000")

# Company configuration
COMPANY_NAME = os.getenv("COMPANY_NAME", "Cowboy Technologies, LLC")
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN", "cowboytech.com")

# Call transfer configuration
MAIN_OFFICE_NUMBER = os.getenv("MAIN_OFFICE_NUMBER", "+12108884900") 

# Agent configuration
AGENT_NAME = os.getenv("AGENT_NAME", "telephony_agent")
MODE = os.getenv("MODE", "production")

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SALES_EMAIL = os.getenv('SALES_EMAIL', 'sales@cowboytechnologies.com')