# API Sales Inquiry Endpoint

## Overview
The sales inquiry endpoint handles email sending for sales inquiries submitted through the AI voice agent. This endpoint receives inquiry data and sends formatted emails to the sales team.

## Endpoint Details

### **URL**
```
POST /api/email/sales/inquiry
```

### **Request Headers**
```
Content-Type: application/json
```

### **Request Body**
```json
{
  "caller_name": "John Smith",
  "caller_phone": "555-123-4567",
  "caller_email": "john@company.com",
  "inquiry_description": "Interested in copier services for new office",
  "caller_company": "ABC Corporation",
  "additional_notes": "Looking for comprehensive service agreement"
}
```

#### **Required Fields**
- `caller_name` (string): Full name of the person making the inquiry
- `caller_phone` (string): Contact phone number
- `caller_email` (string): Contact email address
- `inquiry_description` (string): Brief description of what they're looking for

#### **Optional Fields**
- `caller_company` (string): Company name
- `additional_notes` (string): Any additional context or information

## Response Format

### **Success Response (200/201)**
```json
{
  "success": true,
  "message": "Sales inquiry email sent successfully",
  "email_id": "email_12345_67890",
  "timestamp": "2025-01-27T14:30:00Z"
}
```

### **Error Responses**

#### **400 Bad Request**
```json
{
  "success": false,
  "message": "Missing required fields: caller_name, caller_phone",
  "error": "validation_error"
}
```

#### **401 Unauthorized**
```json
{
  "success": false,
  "message": "API key invalid or missing",
  "error": "unauthorized"
}
```

#### **500 Internal Server Error**
```json
{
  "success": false,
  "message": "Email service temporarily unavailable",
  "error": "email_service_error"
}
```

## Implementation Requirements

### **Backend API Implementation**
The API endpoint should:

1. **Validate Input**: Ensure all required fields are present
2. **Process Data**: Format the inquiry data for email
3. **Send Email**: Use configured SMTP settings to send email
4. **Log Activity**: Record all inquiry submissions
5. **Return Response**: Provide success/error feedback

### **Email Template**
The endpoint should send emails with this structure:

```
Subject: New Sales Inquiry - {Caller Name} ({Company Name})

New Sales Inquiry Received
Timestamp: {Date and Time}

=== CONTACT INFORMATION ===
Name: {Caller Name}
Phone: {Phone Number}
Email: {Email Address}
Company: {Company Name} (if provided)

=== INQUIRY DETAILS ===
Description: {What they're looking for}

=== ADDITIONAL NOTES ===
{Any additional information provided}

=== SYSTEM INFORMATION ===
Source: Voice Agent System
Company: {Company Name}

Please follow up with this potential customer within 24 hours.

Best regards,
Voice Agent System
```

### **SMTP Configuration**
The API should handle SMTP configuration:

```bash
# Environment Variables for API
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SALES_EMAIL=sales@cowboytechnologies.com
COMPANY_NAME=Cowboy Technologies, LLC
```

## Security Considerations

### **Input Validation**
- Validate all required fields
- Sanitize input data
- Check email format validity
- Limit field lengths

### **Rate Limiting**
- Implement request rate limiting
- Prevent spam submissions
- Monitor for abuse patterns

### **Authentication**
- Require valid API keys
- Log all access attempts
- Monitor for unauthorized access

## Error Handling

### **Common Error Scenarios**
1. **Missing Required Fields**: Return 400 with specific field names
2. **Invalid Email Format**: Return 400 with validation error
3. **SMTP Connection Failed**: Return 500 with service error
4. **Rate Limit Exceeded**: Return 429 with retry information

### **Fallback Procedures**
1. **Email Service Down**: Queue inquiries for later processing
2. **Invalid Data**: Log errors and return appropriate status codes
3. **Network Issues**: Implement retry logic with exponential backoff

## Testing

### **Test Cases**
1. **Valid Inquiry**: Submit complete inquiry data
2. **Missing Fields**: Test validation of required fields
3. **Invalid Email**: Test email format validation
4. **Rate Limiting**: Test rate limit enforcement
5. **Error Handling**: Test various error scenarios

### **Test Data**
```json
{
  "caller_name": "Test User",
  "caller_phone": "555-000-0000",
  "caller_email": "test@example.com",
  "inquiry_description": "Test inquiry for system validation",
  "caller_company": "Test Company",
  "additional_notes": "This is a test submission"
}
```

## Monitoring and Logging

### **Metrics to Track**
- Inquiry submission volume
- Email delivery success rate
- Response times
- Error rates by type

### **Log Information**
- All inquiry submissions
- Email delivery status
- Error details and stack traces
- Performance metrics

## Integration with AI Agent

### **Function Call**
The AI agent calls this endpoint via the `send_sales_inquiry_email` function:

```python
result = await send_sales_inquiry_email(
    caller_name="John Smith",
    caller_phone="555-123-4567",
    caller_email="john@company.com",
    inquiry_description="Interested in copier services",
    caller_company="ABC Corp"
)
```

**Note**: The AI agent now calls `/api/email/sales/inquiry` instead of the previous `/api/sales/inquiry` endpoint.

### **Response Handling**
The agent handles the API response:

```python
if result["success"]:
    # Provide success message to caller
    success_message = "Thank you for your interest! I've submitted your inquiry..."
else:
    # Provide fallback message
    error_message = "I'm sorry, but I encountered an issue..."
```

## Future Enhancements

### **Potential Improvements**
1. **Lead Scoring**: Automatically score leads based on inquiry content
2. **CRM Integration**: Direct integration with CRM systems
3. **Follow-up Automation**: Automatic follow-up email sequences
4. **Analytics Dashboard**: Sales inquiry metrics and reporting
5. **Multi-language Support**: Support for different languages

## Conclusion

This API endpoint provides a clean, secure way for the AI voice agent to submit sales inquiries without handling email configuration directly. The separation of concerns improves maintainability and security while providing a robust foundation for sales lead management.

## Next Steps

1. **Implement API Endpoint**: Create the `/api/sales/inquiry` endpoint in your backend
2. **Configure Email Service**: Set up SMTP configuration in your API environment
3. **Test Integration**: Verify the AI agent can successfully submit inquiries
4. **Monitor Performance**: Track inquiry volume and email delivery success
5. **Gather Feedback**: Collect feedback from sales team on email quality
