# Conversation Logging Integration

This document describes the conversation logging integration implemented in the telephony agent (`telephony_agent.py`) to log all conversations between AI agents and callers to MongoDB.

## 🏗️ Architecture Overview

The conversation logging system integrates with the Node.js API to provide comprehensive logging of:

- **Call Sessions**: Metadata about each call (room, caller info, timing, etc.)
- **Conversation Messages**: Individual messages from callers and agents
- **Function Calls**: Tool executions with arguments and results
- **System Events**: Call lifecycle events (start, end, errors)

## 📋 Features

### ✅ Call Session Tracking
- Automatic call initialization when a call starts
- Call metadata storage (room name, caller info, agent name)
- Call status management (active, completed, failed)
- Integration with Halo PSA data (user_id, client_id, site_id)

### ✅ Conversation Message Logging
- **Caller Messages**: Speech-to-text output with confidence scores
- **Agent Messages**: AI responses and generated speech
- **Function Calls**: Tool executions with full context
- **System Events**: Call lifecycle and error events

### ✅ Advanced Logging Features
- **Sequence Numbers**: Automatic message ordering
- **Timestamps**: Precise timing for all events
- **Confidence Scores**: Speech recognition confidence
- **Metadata**: Additional context and debugging info
- **Error Handling**: Graceful failure handling

## 🔧 Implementation Details

### Custom Agent Class

The telephony agent uses a custom `LoggingAgent` class that extends the base `Agent`:

```python
class LoggingAgent(Agent):
    def __init__(self, instructions: str, tools: list = None):
        super().__init__(instructions=instructions, tools=tools)
        self.ctx = None
    
    def set_context(self, ctx):
        """Set the job context for logging"""
        self.ctx = ctx
    
    async def on_message(self, message: str):
        """Override to log agent messages"""
        if self.ctx and hasattr(self.ctx, 'call_id') and self.ctx.call_id:
            try:
                await log_agent_message(self.ctx, message)
                logger.debug(f"Logged agent message: {message[:50]}...")
            except Exception as e:
                logger.error(f"Error logging agent message: {str(e)}")
        
        # Call the parent method
        await super().on_message(message)
```

### Logging Functions

The agent includes several utility functions for logging:

#### `initialize_call_logging(ctx, caller_phone_number)`
Initializes a new call session in the database.

#### `log_caller_message(ctx, message, confidence=None)`
Logs a message from the caller with optional confidence score.

#### `log_agent_message(ctx, message)`
Logs a message from the AI agent.

#### `log_function_call(ctx, function_name, args, result)`
Logs a function call with arguments and results.

#### `end_call_logging(ctx, summary=None, ticket_created=False, ticket_id=None)`
Ends the call session with optional summary and ticket information.

### Integration Points

#### 1. Call Initialization
```python
# In entrypoint function
await initialize_call_logging(ctx, caller_phone_number)

# Log call start event
if hasattr(ctx, 'call_id') and ctx.call_id:
    system_event_data = {
        "call_id": ctx.call_id,
        "speaker": "system",
        "message": "Call started",
        "message_type": "system_event"
    }
    await loop.run_in_executor(
        None, lambda: requests.post(f"{API_URL}/api/conversations/system-event", json=system_event_data)
    )
```

#### 2. Function Call Logging
All function tools now include logging:

```python
@function_tool
async def get_open_it_support_ticket(name: str = None, company: str = None, details: str = None, confirmed: bool = False) -> str:
    # ... function logic ...
    
    # Log the function call
    await log_function_call(ctx, "get_open_it_support_ticket", {
        "name": caller_name,
        "company": caller_company,
        "details": details,
        "confirmed": confirmed
    }, success_message)
    
    # Mark ticket as created in call logging
    if ticket_id:
        await end_call_logging(ctx, summary=f"IT support ticket created: {ticket_id}", ticket_created=True, ticket_id=ticket_id)
    
    return success_message
```

#### 3. Call Ending
```python
@function_tool
async def end_call() -> str:
    # ... goodbye message logic ...
    
    # Log the function call
    await log_function_call(ctx, "end_call", {}, goodbye_message)
    
    # Log call end event
    if hasattr(ctx, 'call_id') and ctx.call_id:
        system_event_data = {
            "call_id": ctx.call_id,
            "speaker": "system",
            "message": "Call ended by user request",
            "message_type": "system_event"
        }
        await loop.run_in_executor(
            None, lambda: requests.post(f"{API_URL}/api/conversations/system-event", json=system_event_data)
        )
    
    # End call logging
    await end_call_logging(ctx, summary="Call ended by user request")
```

## 📊 Data Flow

### 1. Call Start
```
Caller connects → Extract phone number → Initialize call logging → 
Look up caller info → Log system event → Generate greeting → Log agent message
```

### 2. Conversation Flow
```
Caller speaks → STT processing → Log caller message → 
AI processing → Function calls → Log function calls → 
AI response → Log agent message
```

### 3. Call End
```
User requests end → Log function call → Log system event → 
End call session → Hang up call
```

## 🧪 Testing

### Test Script
Run the integration test script to verify functionality:

```bash
cd ai-voice-agent
python test_conversation_logging_integration.py
```

### Test Coverage
The test script verifies:
- ✅ Call initialization
- ✅ System event logging
- ✅ Agent message logging
- ✅ Caller message logging
- ✅ Function call logging
- ✅ Conversation retrieval
- ✅ Call ending
- ✅ Statistics generation

## 📈 Analytics & Queries

### Call Statistics
```javascript
// Get call statistics
GET /api/conversations/{callId}/stats

// Response includes:
{
  "total_messages": 15,
  "caller_messages": 8,
  "agent_messages": 5,
  "function_calls": 2,
  "system_events": 2,
  "average_message_length": 45.2,
  "call_duration": "00:05:30"
}
```

### Conversation Retrieval
```javascript
// Get full conversation
GET /api/conversations/{callId}

// Get filtered conversation
GET /api/conversations/{callId}/filtered?speaker=caller&message_type=speech

// Search conversation
GET /api/conversations/{callId}/search?q=computer
```

### Function Call Analysis
```javascript
// Get function calls
GET /api/conversations/{callId}/function-calls

// Response includes function names, arguments, and results
```

## 🔍 Monitoring & Debugging

### Log Levels
- **DEBUG**: Detailed conversation logging
- **INFO**: Call lifecycle events
- **WARNING**: Non-critical errors
- **ERROR**: Critical failures

### Error Handling
- Graceful degradation if API is unavailable
- Automatic retry for transient failures
- Detailed error logging for debugging

### Performance Considerations
- Asynchronous logging to avoid blocking
- Batch operations where possible
- Connection pooling for API calls

## 🚀 Deployment

### Environment Variables
Ensure these are set in your environment:
```bash
API_URL=http://localhost:3000  # Node.js API endpoint
AGENT_NAME=telephony_agent      # Agent identifier
```

### Dependencies
The integration requires:
- `requests` library for HTTP calls
- `asyncio` for asynchronous operations
- Node.js API running and accessible

### Docker Integration
The conversation logging works seamlessly with the Docker setup:
```yaml
# docker-compose.yml
services:
  api:
    # ... API service configuration
  ai-voice-agent:
    environment:
      - API_URL=http://api:3000
    depends_on:
      - api
```

## 📝 Example Logged Data

### Call Session
```json
{
  "call_id": "call_abc123",
  "room_name": "room_xyz789",
  "caller_phone": "555-123-4567",
  "caller_name": "John Doe",
  "caller_company": "Acme Corp",
  "agent_name": "telephony_agent",
  "status": "completed",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:35:30Z",
  "duration": 330,
  "ticket_created": true,
  "ticket_id": "HALO-12345"
}
```

### Conversation Messages
```json
[
  {
    "call_id": "call_abc123",
    "speaker": "system",
    "message": "Call started",
    "message_type": "system_event",
    "sequence_number": 1,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  {
    "call_id": "call_abc123",
    "speaker": "agent",
    "speaker_name": "telephony_agent",
    "message": "Good morning John! Welcome back to IBT. How can I help you today?",
    "message_type": "speech",
    "sequence_number": 2,
    "timestamp": "2024-01-15T10:30:05Z"
  },
  {
    "call_id": "call_abc123",
    "speaker": "caller",
    "message": "I need help with my computer",
    "message_type": "speech",
    "confidence": 0.95,
    "sequence_number": 3,
    "timestamp": "2024-01-15T10:30:15Z"
  },
  {
    "call_id": "call_abc123",
    "speaker": "agent",
    "speaker_name": "telephony_agent",
    "message": "Function call: get_open_it_support_ticket",
    "message_type": "function_call",
    "function_name": "get_open_it_support_ticket",
    "function_args": {
      "name": "John Doe",
      "company": "Acme Corp",
      "details": "Computer not working",
      "confirmed": true
    },
    "function_result": "Your IT support ticket has been opened. Ticket ID: HALO-12345",
    "sequence_number": 4,
    "timestamp": "2024-01-15T10:30:25Z"
  }
]
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Connection Errors
**Symptoms**: `ECONNREFUSED` errors in logs
**Solution**: Ensure Node.js API is running and accessible

#### 2. Missing Call ID
**Symptoms**: Logging functions fail silently
**Solution**: Check that `initialize_call_logging` completed successfully

#### 3. Duplicate Messages
**Symptoms**: Same message logged multiple times
**Solution**: Check for multiple event handlers or function calls

### Debug Commands
```python
# Enable debug logging
logging.getLogger("telephony-agent").setLevel(logging.DEBUG)

# Test API connectivity
python test_conversation_logging_integration.py

# Check MongoDB directly
mongo ibt --eval "db.calls.find().sort({createdAt: -1}).limit(5)"
```

## 📚 Related Documentation

- [Conversation Logging API](../api/CONVERSATION_LOGGING_README.md)
- [Node.js API Documentation](../api/README.md)
- [Telephony Agent Configuration](README.md)
- [Docker Deployment Guide](../docker-compose.yml)

## 🤝 Contributing

When modifying the conversation logging:

1. **Test thoroughly** with the integration test script
2. **Update documentation** for any new features
3. **Maintain backward compatibility** with existing data
4. **Add error handling** for new logging points
5. **Consider performance impact** of additional logging

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Maintainer**: IBT Development Team 