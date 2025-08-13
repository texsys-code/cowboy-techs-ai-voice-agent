# Enhanced Copier Support Ticket System

## Overview
The copier support ticket system has been enhanced to provide a comprehensive, scripted approach that handles different scenarios based on whether callers have an Equipment ID number or need to provide make/model information.

## Why This Enhancement is Important

### **Problems Without Enhanced System**
- **Inconsistent Data Collection**: Different agents collected different information
- **Missing Critical Details**: Equipment identification information was often incomplete
- **Poor User Experience**: Callers weren't guided through a clear process
- **Incomplete Tickets**: Technicians lacked necessary information to provide service

### **Benefits With Enhanced System**
- **Standardized Process**: Consistent data collection every time
- **Complete Information**: All necessary details captured systematically
- **Professional Experience**: Clear, guided process for callers
- **Better Service**: Technicians have complete information for faster resolution

## The Enhanced Script Flow

### **Initial Question**
```
Agent: "Sure, I can help you with that. Do you have an Equipment ID number for the machine that needs service?"
```

**IMPORTANT**: The system automatically has the caller's name, company, and phone number from the phone lookup. DO NOT ask for this information again!

### **Scenario 1: Equipment ID Available (YES)**

#### **Step-by-Step Process**
1. **Equipment ID Collection**
   ```
   Agent: "Great — please provide the Equipment ID number."
   Caller: [Provides Equipment ID]
   ```

2. **Problem Description**
   ```
   Agent: "Can you describe the problem you're having with this equipment?"
   Caller: [Describes the issue]
   ```

3. **Ticket Creation**
   - Use `open_copier_support_ticket` with `confirmed=False` for confirmation
   - After user confirms, use `open_copier_support_ticket` with `confirmed=True`

#### **Data Collected**
- ✅ Equipment ID number
- ✅ Problem description
- ✅ **Automatic from phone lookup**: Name, company, phone number

### **Scenario 2: No Equipment ID (NO)**

#### **Step-by-Step Process**
1. **Equipment Identification**
   ```
   Agent: "No problem — please provide the make and model and serial number, if you have it, of the equipment."
   Caller: [Provides make/model and serial number]
   ```

2. **Service Agreement Status**
   ```
   Agent: "Are you currently contracted under a service maintenance agreement with Cowboy Technologies, LLC?"
   Caller: [Answers yes/no]
   ```

3. **Problem Description**
   ```
   Agent: "Can you describe the problem you're having?"
   Caller: [Describes the issue]
   ```

4. **Ticket Creation**
   - Use `open_copier_support_ticket` with `confirmed=False` for confirmation
   - After user confirms, use `open_copier_support_ticket` with `confirmed=True`

#### **Data Collected**
- ✅ Make and model
- ✅ Serial number (if available)
- ✅ Service agreement status
- ✅ Problem description
- ✅ **Automatic from phone lookup**: Name, company, phone number

## Technical Implementation

### **Enhanced Function Parameters**
```python
@function_tool
async def open_copier_support_ticket(
    details: str = None,           # Problem description
    confirmed: bool = False,       # Confirmation status
    equipment_id: str = None,      # Equipment ID if available
    make_model: str = None,        # Make and model if no Equipment ID
    serial_number: str = None,     # Serial number if no Equipment ID
    caller_name: str = None,       # Caller's name
    caller_phone: str = None,      # Phone number
    caller_email: str = None,      # Email address
    caller_company: str = None,    # Company name
    caller_address: str = None,    # Company address
    point_of_contact: str = None,  # Point of contact info
    service_agreement: bool = None # Service agreement status
):
```

### **Smart Data Handling**
- **Context Integration**: Automatically uses caller information from phone lookup
- **Fallback Logic**: Uses provided values or falls back to context values
- **Validation**: Ensures all required fields are present before ticket creation
- **Enhanced Details**: Creates comprehensive ticket descriptions with all collected information

### **Confirmation Process**
- **First Call**: `confirmed=False` shows comprehensive confirmation message
- **Second Call**: `confirmed=True` creates the actual ticket
- **Non-Interruptible**: All confirmation messages use `[NON_INTERRUPTIBLE]` prefix

## Example Usage Scenarios

### **Example 1: Equipment ID Available**
```
User: "I need help with my copier"
Agent: "Sure, I can help you with that. Do you have an Equipment ID number for the machine that needs service?"

User: "Yes, it's EQ-2024-001"
Agent: "Great — please provide the Equipment ID number."
[Collects Equipment ID]

Agent: "Can you describe the problem you're having with this equipment?"
[Collects problem description]

Agent: [Calls open_copier_support_ticket with equipment_id, details, confirmed=False]
[Shows confirmation message using existing caller info from phone lookup]

User: "Yes, that's correct"
Agent: [Calls open_copier_support_ticket with confirmed=True]
[Creates ticket and provides success message]
```

### **Example 2: No Equipment ID**
```
User: "I need help with my copier"
Agent: "Sure, I can help you with that. Do you have an Equipment ID number for the machine that needs service?"

User: "No, I don't have that"
Agent: "No problem — please provide the make and model and serial number, if you have it, of the equipment."
[Collects equipment details]

Agent: "Are you currently contracted under a service maintenance agreement with Cowboy Technologies, LLC?"
[Collects service agreement status]

Agent: "Can you describe the problem you're having?"
[Collects problem description]

Agent: [Calls open_copier_support_ticket with make_model, serial_number, service_agreement, details, confirmed=False]
[Shows confirmation message using existing caller info from phone lookup]

User: "Yes, that's correct"
Agent: [Calls open_copier_support_ticket with confirmed=True]
[Creates ticket and provides success message]
```

## Success Message
```
"Thank you — your request has been placed in our service queue and a technician will be in touch soon. Your ticket number is [TICKET_NUMBER]. Is there anything else I can help you with today?"
```

## Data Flow and Storage

### **Information Sources**
1. **Automatic Lookup (Phone Number)**: 
   - ✅ Name
   - ✅ Company
   - ✅ Phone number
   - ✅ Halo client/site/user IDs

2. **User Input (Equipment & Problem)**:
   - Equipment ID (if available)
   - Make and model (if no Equipment ID)
   - Serial number (if no Equipment ID)
   - Service agreement status
   - Problem description

3. **Combined Data**: Merges automatic lookup with manual equipment/problem details

### **What the Agent Should NOT Ask For**
- ❌ **Name** - Already available from phone lookup
- ❌ **Company** - Already available from phone lookup  
- ❌ **Phone number** - Already available from phone lookup
- ❌ **Email address** - Not required for copier tickets
- ❌ **Company address** - Not required for copier tickets
- ❌ **Point of contact** - Not required for copier tickets

### **What the Agent Should Ask For**
- ✅ **Equipment ID** (if available)
- ✅ **Make and model** (if no Equipment ID)
- ✅ **Serial number** (if no Equipment ID)
- ✅ **Service agreement status** (if no Equipment ID)
- ✅ **Problem description** (always required)

### **Ticket Creation**
- **Halo PSA Integration**: Creates comprehensive tickets with all collected data
- **Enhanced Details**: Includes equipment information, contact details, and problem description
- **Team Assignment**: Automatically assigns to Copier Support team (team_id: 2)
- **Ticket Type**: Uses copier-specific ticket type (tickettype_id: 2)

### **Data Validation**
- **Required Fields**: Name, company, phone, problem description
- **Optional Fields**: Equipment ID, make/model, serial number, email, address, point of contact
- **Error Handling**: Clear messages for missing required information

## Benefits for Different Stakeholders

### **For Callers**
- **Clear Process**: Step-by-step guidance through ticket creation
- **Professional Experience**: Consistent, professional interaction
- **Complete Information**: Ensures all necessary details are captured
- **Confirmation**: Opportunity to review and confirm information before submission

### **For Technicians**
- **Complete Information**: All necessary details for faster problem resolution
- **Equipment Identification**: Clear equipment details for service planning
- **Contact Information**: Multiple ways to reach the caller
- **Service Agreement Status**: Understanding of coverage and billing

### **For Support Team**
- **Standardized Process**: Consistent data collection across all calls
- **Quality Assurance**: Comprehensive information reduces follow-up calls
- **Efficient Routing**: Proper team assignment and ticket categorization
- **Better Metrics**: Complete data for reporting and analysis

## Testing the Enhanced System

### **Test Scenarios**

#### **1. Equipment ID Available**
1. Request copier support
2. Provide Equipment ID
3. Describe problem
4. Confirm details
5. **Expected**: Ticket created with Equipment ID and complete information

#### **2. No Equipment ID**
1. Request copier support
2. Provide make/model and serial number
3. Answer service agreement question
4. Describe problem
5. Confirm details
6. **Expected**: Ticket created with equipment details and complete information

#### **3. Missing Required Information**
1. Request copier support
2. Skip required fields
3. **Expected**: Clear error message about missing information

### **Verification Points**
- **Data Collection**: All required information is captured
- **Confirmation Process**: Users can review and confirm details
- **Ticket Creation**: Tickets are created successfully in Halo PSA
- **Success Message**: Appropriate success message with ticket number
- **Interruption Prevention**: Critical messages cannot be interrupted

## Troubleshooting

### **Common Issues**

#### **1. Missing Equipment Information**
- **Problem**: Caller doesn't have Equipment ID or equipment details
- **Solution**: Guide them through the alternative data collection process

#### **2. Incomplete Contact Information**
- **Problem**: Missing required contact details
- **Solution**: Use automatic lookup data and ask for missing information

#### **3. Confirmation Issues**
- **Problem**: User doesn't confirm ticket details
- **Solution**: Explain the confirmation process and ask again

### **Debug Tools**
- **debug_ticket_context**: Check what caller information is available
- **Enhanced Logging**: Track all data collection steps
- **Function Parameters**: Verify all collected data is passed correctly

## Future Enhancements

### **Potential Improvements**
1. **Equipment Database**: Look up equipment details by ID automatically
2. **Smart Defaults**: Suggest common equipment makes and models
3. **Photo Upload**: Allow callers to send photos of equipment issues
4. **Scheduling**: Integrate with technician scheduling system
5. **Follow-up Automation**: Automatic follow-up calls and status updates

## Conclusion

The enhanced copier support ticket system provides a professional, comprehensive approach to collecting all necessary information for copier service requests. By following the structured script and collecting detailed information, the system ensures:

- ✅ **Complete Data Collection**: All necessary information is captured systematically
- ✅ **Professional User Experience**: Clear, guided process for callers
- ✅ **Better Service Delivery**: Technicians have complete information for faster resolution
- ✅ **Standardized Process**: Consistent experience across all copier support calls
- ✅ **Quality Assurance**: Comprehensive information reduces follow-up and improves service quality

This system transforms copier support from a basic ticket creation process to a comprehensive service request system that benefits callers, technicians, and the support team.
