# TEST_MODE Usage Example

## Overview
TEST_MODE allows you to test the telephony agent and API integration without making real calls to the Halo API. This is useful for development, testing, and debugging.

## How to Enable TEST_MODE

### 1. **Environment Variable Setup**
Add to your `.env` file:
```env
TEST_MODE=true
```

### 2. **What TEST_MODE Does**

#### **Ticket Creation**
When TEST_MODE is enabled, ticket creation returns a mock response:
```json
{
  "id": 12345,
  "summary": "John Doe - Acme Corp",
  "details": "User is experiencing login issues\n\nCaller Phone Number: +1-555-123-4567",
  "status_id": 1,
  "tickettype_id": 1,
  "sla_id": 3,
  "priority_id": 4,
  "client_id": 174,
  "site_id": 216,
  "user_id": 267,
  "team_id": 1,
  "agent_id": 1,
  "category_1": "Business Applications",
  "impact": 3,
  "urgency": 2,
  "created_at": "2025-01-31T20:22:48.505Z",
  "updated_at": "2025-01-31T20:22:48.505Z"
}
```

#### **Health Check**
Health check always returns success:
```json
{
  "success": true,
  "message": "Halo API is healthy",
  "timestamp": "2025-01-31T20:22:48.505Z"
}
```

### 3. **Testing with TEST_MODE**

#### **Run the Test Script**
```bash
cd ai-voice-agent
python test_api_integration.py
```

**Output with TEST_MODE enabled:**
```
Testing Node.js API Integration
========================================
🔧 TEST_MODE is enabled - using mock responses

Testing API at: http://localhost:3000
Status Code: 200
Response:
{
  "success": true,
  "data": {
    "firstname": "Travis",
    "lastname": "Thomsen",
    ...
  },
  "message": "Caller found"
}

✅ Found caller: Travis Thomsen
   Company: IBT, Inc.
   Email: tthomsen@ibt-i.com
   Phone: 210-380-8073

Halo Health Check - Status Code: 200
Halo Health Response:
{
  "success": true,
  "message": "Halo API is healthy",
  "timestamp": "2025-01-31T20:22:48.505Z"
}

Testing Ticket Creation
⚠️  TEST_MODE is enabled - using mock responses
Status Code: 201
Ticket Creation Response:
{
  "success": true,
  "data": {
    "id": 45678,
    "summary": "Test Ticket - Test Company",
    "details": "This is a test ticket...",
    ...
  },
  "message": "Ticket created successfully"
}

✅ Ticket created successfully with ID: 45678

========================================
Test completed!
```

### 4. **Benefits of TEST_MODE**

#### **✅ Development**
- No need for real Halo API credentials
- Fast testing without network delays
- Consistent test results

#### **✅ Debugging**
- No risk of creating real tickets
- Easy to test different scenarios
- Clear logging of what would be sent

#### **✅ CI/CD**
- Automated testing without external dependencies
- Reliable test environments
- No API rate limiting concerns

### 5. **When to Use TEST_MODE**

#### **✅ Use TEST_MODE for:**
- Development and testing
- Debugging API integration
- Automated testing
- Demo environments
- When Halo API is unavailable

#### **❌ Don't use TEST_MODE for:**
- Production environments
- Real user interactions
- Actual ticket creation
- Performance testing

### 6. **Disabling TEST_MODE**

To use real API calls, either:
- Remove `TEST_MODE=true` from your `.env` file
- Set `TEST_MODE=false` in your `.env` file
- Don't include TEST_MODE in your `.env` file

### 7. **Example .env Configuration**

```env
# Development with TEST_MODE
API_URL=http://localhost:3000
TEST_MODE=true

# Production without TEST_MODE
API_URL=https://your-api-domain.com
# TEST_MODE not set (defaults to false)
```

This setup allows you to easily switch between test and production modes by changing your environment configuration. 