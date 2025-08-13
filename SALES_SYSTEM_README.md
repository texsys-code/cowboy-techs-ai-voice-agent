# Sales Inquiry System

## Overview
The sales inquiry system provides a comprehensive, scripted approach for handling sales and billing questions. The system automatically collects caller information and sends detailed emails to the sales team for follow-up.

## Why This System is Important

### **Problems Without Sales Inquiry System**
- **No Lead Tracking**: Sales inquiries weren't systematically captured
- **Inconsistent Process**: Different agents handled sales questions differently
- **Missing Information**: Incomplete inquiry details led to poor follow-up
- **No Follow-up System**: Sales team couldn't track or prioritize inquiries

### **Benefits With Sales Inquiry System**
- **Complete Lead Capture**: All sales inquiries are systematically recorded
- **Standardized Process**: Consistent script and data collection every time
- **Professional Experience**: Clear, guided process for sales inquiries
- **Better Follow-up**: Complete information ensures effective sales team response

## The Complete Script Flow

### **Initial Response**
```
Agent: "Great — I can take your information and have one of our sales representatives get in touch. May I have your name, phone number, email, and a brief description of what you're looking for?"
```

### **Data Collection Process**

#### **Required Information (Always Collected)**
1. **Name**: Caller's full name
2. **Phone Number**: Contact phone number
3. **Email**: Contact email address
4. **Description**: Brief description of what they're looking for

#### **Optional Information (Collected if Provided)**
5. **Company**: Company name
6. **Additional Notes**: Any other relevant information

### **Information Submission**
- Use `submit_sales_inquiry` function with all collected information
- System automatically sends email to sales team
- Provides caller with confirmation and next steps

### **Follow-up Process**
- Sales team receives detailed email within minutes
- 24-hour follow-up commitment communicated to caller
- Caller can continue with other requests or end call

## Technical Implementation

### **Core Components**

#### **1. Email System Module (`lib/email_system.py`)**
- **SMTP Integration**: Handles email sending via configured SMTP server
- **Template System**: Creates professional, formatted sales inquiry emails
- **Error Handling**: Comprehensive error handling and logging
- **Configuration**: Environment variable-based configuration

#### **2. Sales Functions (`lib/call_tools/sales.py`)**
- **submit_sales_inquiry**: Main function for processing sales inquiries
- **test_email_system**: Debug tool for testing email functionality
- **Integration**: Seamless integration with voice agent system

#### **3. Agent Integration**
- **Function Tools**: Available as `@function_tool` for LLM access
- **Script Integration**: Built into agent instructions and capabilities
- **Error Handling**: Graceful fallback for system issues

### **Function Parameters**
```python
@function_tool
async def submit_sales_inquiry(
    caller_name: str,           # Required: Full name
    caller_phone: str,          # Required: Phone number
    caller_email: str,          # Required: Email address
    inquiry_description: str,    # Required: What they're looking for
    caller_company: str = None, # Optional: Company name
    additional_notes: str = None # Optional: Additional context
):
```

## Email System Details

### **SMTP Configuration**
The system supports configurable SMTP settings via environment variables:

```bash
# Required SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional Configuration
SALES_EMAIL=sales@cowboytechnologies.com
COMPANY_NAME=Cowboy Technologies, LLC
```

### **Email Format**
Sales inquiry emails include:

#### **Subject Line**
```
New Sales Inquiry - {Caller Name} ({Company Name})
```

#### **Email Body Structure**
```
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

### **Email Delivery**
- **Recipient**: Sales team email address (configurable)
- **Sender**: Configured SMTP account
- **Delivery**: Immediate delivery via SMTP
- **Tracking**: Email ID and timestamp for reference

## Example Usage Scenarios

### **Example 1: Basic Sales Inquiry**
```
User: "I have a question about your services"
Agent: "Great — I can take your information and have one of our sales representatives get in touch. May I have your name, phone number, email, and a brief description of what you're looking for?"

User: "My name is John Smith, phone is 555-1234, email is john@company.com, and I'm interested in your copier services for a new office we're opening."

Agent: [Calls submit_sales_inquiry with all collected information]
[System sends email to sales team]
[Agent provides confirmation and asks if there's anything else]
```

### **Example 2: Detailed Sales Inquiry with Company**
```
User: "I need pricing information for your IT services"
Agent: "Great — I can take your information and have one of our sales representatives get in touch. May I have your name, phone number, email, and a brief description of what you're looking for?"

User: "I'm Sarah Johnson from ABC Corporation, my phone is 555-5678, email is sarah@abccorp.com, and we're looking for comprehensive IT support for our 50-person office, including network management, help desk support, and cybersecurity services."

Agent: [Calls submit_sales_inquiry with all information including company and detailed description]
[System sends comprehensive email to sales team]
[Agent provides confirmation and asks if there's anything else]
```

### **Example 3: Billing Question**
```
User: "I have a question about my monthly bill"
Agent: "Great — I can take your information and have one of our sales representatives get in touch. May I have your name, phone number, email, and a brief description of what you're looking for?"

User: "My name is Mike Davis, phone is 555-9012, email is mike@business.com, and I'm calling about an unexpected charge on my last invoice for copier maintenance."

Agent: [Calls submit_sales_inquiry with billing inquiry details]
[System sends email to sales team for billing follow-up]
[Agent provides confirmation and asks if there's anything else]
```

## Data Flow and Storage

### **Information Collection**
1. **Voice Input**: Caller provides information verbally
2. **Agent Processing**: AI agent collects and validates information
3. **Function Call**: `submit_sales_inquiry` function processes data
4. **Email Generation**: System creates formatted email
5. **SMTP Delivery**: Email sent to sales team
6. **Confirmation**: Caller receives confirmation message

### **Data Validation**
- **Required Fields**: Name, phone, email, description
- **Optional Fields**: Company, additional notes
- **Format Validation**: Basic email and phone format checking
- **Error Handling**: Clear messages for missing information

### **Privacy and Security**
- **No Local Storage**: Information not stored locally
- **Secure Transmission**: Email sent via encrypted SMTP
- **Data Retention**: Follows email system retention policies
- **Access Control**: Limited to sales team recipients

## Benefits for Different Stakeholders

### **For Callers**
- **Clear Process**: Step-by-step guidance through inquiry submission
- **Professional Experience**: Consistent, professional interaction
- **Immediate Action**: Know their inquiry is being processed
- **Follow-up Commitment**: 24-hour response commitment

### **For Sales Team**
- **Complete Information**: All necessary details for effective follow-up
- **Immediate Notification**: Real-time email delivery
- **Structured Format**: Consistent, easy-to-read inquiry format
- **Lead Tracking**: Systematic capture of all sales inquiries

### **For Support Team**
- **Standardized Process**: Consistent inquiry collection across all calls
- **Quality Assurance**: Complete information reduces follow-up calls
- **Efficient Routing**: Direct delivery to sales team
- **Better Metrics**: Complete data for sales reporting and analysis

## Testing the System

### **Test Scenarios**

#### **1. Basic Sales Inquiry**
1. Request sales information
2. Provide name, phone, email, and description
3. **Expected**: Email sent to sales team with complete information

#### **2. Detailed Sales Inquiry**
1. Request sales information
2. Provide all information including company and additional notes
3. **Expected**: Comprehensive email sent with all details

#### **3. Missing Required Information**
1. Request sales information
2. Provide incomplete information
3. **Expected**: Clear error message about missing fields

#### **4. Email System Test**
1. Use `test_email_system` function
2. **Expected**: Connection test results and configuration status

### **Verification Points**
- **Data Collection**: All required information is captured
- **Email Delivery**: Sales team receives inquiry email
- **Confirmation Process**: Caller receives confirmation message
- **Error Handling**: Graceful handling of system issues
- **Logging**: Complete audit trail of all inquiries

## Troubleshooting

### **Common Issues**

#### **1. SMTP Configuration Issues**
- **Problem**: Email not sending due to SMTP configuration
- **Solution**: Check SMTP credentials and server settings
- **Debug Tool**: Use `test_email_system` function

#### **2. Missing Required Information**
- **Problem**: Incomplete inquiry data
- **Solution**: Ensure all required fields are collected
- **Validation**: System validates before processing

#### **3. Email Delivery Failures**
- **Problem**: Email not reaching sales team
- **Solution**: Check recipient email configuration
- **Fallback**: Provide alternative contact methods

### **Debug Tools**
- **test_email_system**: Test SMTP connection and configuration
- **Enhanced Logging**: Track all inquiry processing steps
- **Error Messages**: Clear feedback for troubleshooting

## Configuration Requirements

### **Environment Variables**
```bash
# Required for Email Functionality
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional Configuration
SALES_EMAIL=sales@cowboytechnologies.com
COMPANY_NAME=Cowboy Technologies, LLC
```

### **SMTP Setup Instructions**

#### **Gmail Setup**
1. Enable 2-factor authentication
2. Generate App Password
3. Use App Password in SMTP_PASSWORD
4. Ensure "Less secure app access" is disabled

#### **Other SMTP Providers**
1. Check provider's SMTP settings
2. Use appropriate port (587 for TLS, 465 for SSL)
3. Verify authentication requirements
4. Test connection before deployment

## Future Enhancements

### **Potential Improvements**
1. **Lead Scoring**: Automatically score leads based on inquiry content
2. **CRM Integration**: Direct integration with CRM systems
3. **Follow-up Automation**: Automatic follow-up email sequences
4. **Analytics Dashboard**: Sales inquiry metrics and reporting
5. **Multi-language Support**: Support for different languages
6. **SMS Integration**: Text message notifications for urgent inquiries

## Conclusion

The sales inquiry system provides a professional, comprehensive approach to handling sales and billing questions. By following the structured script and collecting detailed information, the system ensures:

- ✅ **Complete Lead Capture**: All sales inquiries are systematically recorded
- ✅ **Professional User Experience**: Clear, guided process for inquiry submission
- ✅ **Better Sales Follow-up**: Complete information ensures effective response
- ✅ **Standardized Process**: Consistent experience across all sales inquiries
- ✅ **Immediate Action**: Real-time email delivery to sales team

This system transforms sales inquiry handling from a basic note-taking process to a comprehensive lead management system that benefits callers, sales teams, and the organization as a whole.

## Next Steps

1. **Configure SMTP Settings**: Set up email credentials in environment variables
2. **Test Email System**: Use `test_email_system` function to verify configuration
3. **Train Sales Team**: Ensure sales team knows to check for inquiry emails
4. **Monitor Performance**: Track inquiry volume and response times
5. **Gather Feedback**: Collect feedback from callers and sales team for improvements
