# Company Configuration

This document explains how to configure company-specific settings in the AI Voice Agent.

## Environment Variables

### Company Name
Set your company name using the `COMPANY_NAME` environment variable:

```bash
COMPANY_NAME="Your Company Name, Inc."
```

**Default value**: `Cowboy Technologies, LLC`

### Email Domain
Set your company's email domain using the `EMAIL_DOMAIN` environment variable:

```bash
EMAIL_DOMAIN="yourcompany.com"
```

**Default value**: `cowboytech.com`

### Main Office Number
Set your main office phone number for call transfers:

```bash
MAIN_OFFICE_NUMBER="+12108884900"
```

**Default value**: `+12108884900`

## Example .env File

Create a `.env` file in the `ai-voice-agent` directory with these settings:

```bash
# Company Configuration
COMPANY_NAME=Your Company Name, Inc.
EMAIL_DOMAIN=yourcompany.com
MAIN_OFFICE_NUMBER=+12108884900

# Other required configurations...
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here
# ... etc
```

## What Gets Updated

When you change these environment variables, the following will be updated:

1. **Greeting Messages**: All phone call greetings will use your company name
2. **Goodbye Messages**: All call endings will use your company name  
3. **Email Generation**: New caller records will use your email domain
4. **Call Transfers**: Calls will be transferred to your main office number

## Code Changes Made

The following files were updated to use these configuration variables:

- `config.py` - Added COMPANY_NAME and EMAIL_DOMAIN configurations
- `telephony_agent.py` - Updated all hardcoded company references to use variables

## Benefits

- **No more hardcoding**: Company name and email domain are now configurable
- **Easy updates**: Change company information without touching code
- **Environment-specific**: Different settings for development, staging, and production
- **Consistent branding**: All messages automatically use the configured company name

## Testing

After updating your `.env` file, restart the AI Voice Agent to see the changes take effect. The agent will now use your configured company name in all greetings and messages.
