# Call Transfer Functionality

The telephony agent now supports transferring calls to a human agent at the main office number.

## Configuration

### Main Office Number
Set the main office number in your `.env` file:

```env
MAIN_OFFICE_NUMBER=+15105550123
```

Replace `+15105550123` with your actual main office phone number.

## How It Works

The `transfer_call` function tool allows the AI agent to:

1. **Confirm transfer**: The agent will confirm with the user before transferring
2. **Inform user**: The agent will inform the user that they're being transferred
3. **Execute transfer**: Uses LiveKit's SIP transfer functionality to transfer the call
4. **Error handling**: Provides feedback if the transfer fails

## Usage Scenarios

The agent will automatically offer to transfer calls when:

- User explicitly requests to speak with a human agent
- User asks to be transferred
- The agent cannot help with the user's specific request
- User indicates they need assistance beyond the AI's capabilities

## Example Conversations

**User**: "I need to speak with a human"
**Agent**: "I understand you'd like to speak with a human agent. I can transfer you to our main office. Would you like me to do that now?"

**User**: "Can you transfer me?"
**Agent**: "I'd be happy to transfer you to a human agent. Let me do that for you right away."

## Technical Details

The transfer uses LiveKit's `transfer_sip_participant` API with:
- Room name: Current call room
- Participant identity: Caller's phone number
- Transfer destination: `tel:MAIN_OFFICE_NUMBER`

## Error Handling

If a transfer fails, the agent will:
1. Log the error for debugging
2. Inform the user of the issue
3. Offer alternative assistance

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MAIN_OFFICE_NUMBER` | Phone number to transfer calls to | `+15105550123` |
