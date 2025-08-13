# Copier Supplies Ordering System

## Overview
The copier supplies ordering system provides a comprehensive, scripted approach for handling supply orders with or without Equipment ID numbers. The system automatically creates tickets for all supply orders and handles multiple equipment scenarios.

## Why This System is Important

### **Problems Without Supply Ordering System**
- **No Ticket Tracking**: Supply orders weren't tracked in the ticketing system
- **Inconsistent Process**: Different agents handled supply orders differently
- **Missing Information**: Incomplete supply order details led to fulfillment issues
- **No Follow-up**: Orders couldn't be tracked or updated

### **Benefits With Supply Ordering System**
- **Complete Tracking**: All supply orders create tickets for full visibility
- **Standardized Process**: Consistent script and data collection every time
- **Professional Experience**: Clear, guided process for supply ordering
- **Better Fulfillment**: Complete information ensures accurate order processing

## The Complete Script Flow

### **Initial Question**
```
Agent: "Sure, I can help you place a supply order. Do you have an Equipment ID number for this request?"
```

### **Scenario 1: Equipment ID Available (YES)**

#### **Step-by-Step Process**
1. **Supply Details Collection**
   ```
   Agent: "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"
   Caller: [Provides Equipment ID and supply details]
   ```

2. **Order Confirmation**
   - Use `order_copier_supplies` with `confirmed=False` for confirmation
   - After user confirms, use `order_copier_supplies` with `confirmed=True`

3. **Additional Equipment Question**
   ```
   Agent: "Will that be all today or Would you like to add another Equipment ID number for a separate supply request? (Yes/No)"
   Caller: [Answers Yes/No]
   ```

4. **If YES - Repeat Process**
   - Repeat steps 1-3 for additional equipment
   - Each order creates a separate ticket

5. **If NO - Continue Conversation**
   - Move to next topic or end call

#### **Data Collected**
- ✅ Equipment ID number
- ✅ Supply details (specific or general)
- ✅ **Automatic from phone lookup**: Name, company, phone number

### **Scenario 2: No Equipment ID (NO)**

#### **Step-by-Step Process**
1. **Supply Details Collection**
   ```
   Agent: "Please tell me the item number and type of supplies you need."
   Caller: [Provides item number and supply details]
   ```

2. **Contact Information Collection**
   ```
   Agent: "May I have your name, email address, and callback number?"
   Caller: [Provides name, email, callback number]
   ```

3. **Order Confirmation**
   - Use `order_copier_supplies` with `confirmed=False` for confirmation
   - After user confirms, use `order_copier_supplies` with `confirmed=True`

#### **Data Collected**
- ✅ Item number
- ✅ Supply details
- ✅ Caller name
- ✅ Email address
- ✅ Callback number

### **Final Success Message**
```
"Your order has been placed. By the way, we offer an auto-replenishment program so toner ships automatically when your supply level reaches a set percentage. If you'd like to enroll, just press 1."
```

## Technical Implementation

### **Function Parameters**
```python
@function_tool
async def order_copier_supplies(
    equipment_id: str = None,        # Equipment ID if available
    supply_details: str = None,      # Description of supplies needed
    item_number: str = None,         # Item number if no Equipment ID
    caller_name: str = None,         # Name for callback (if no Equipment ID)
    caller_email: str = None,        # Email address (if no Equipment ID)
    callback_number: str = None,     # Callback number (if no Equipment ID)
    confirmed: bool = False          # Confirmation status
):
```

### **Smart Data Handling**
- **Context Integration**: Automatically uses caller information from phone lookup when Equipment ID is available
- **Fallback Logic**: Uses provided values or falls back to context values
- **Validation**: Ensures all required fields are present before order creation
- **Enhanced Details**: Creates comprehensive ticket descriptions with all collected information

### **Confirmation Process**
- **First Call**: `confirmed=False` shows comprehensive confirmation message
- **Second Call**: `confirmed=True` creates the actual ticket
- **Non-Interruptible**: All confirmation messages use `[NON_INTERRUPTIBLE]` prefix

## Ticket Creation Details

### **Ticket Information**
- **Summary**: "{Caller Name} - {Company} - Copier Supply Order"
- **Category**: Supplies
- **Team**: Copier Support team (team_id: 2)
- **Ticket Type**: Supply orders (tickettype_id: 3)
- **Priority**: Standard (priority_id: 4)

### **Ticket Content**
```
Supply Order Request

Supply Details: [User's supply description]
Equipment ID: [Equipment ID if available]
Item Number: [Item number if no Equipment ID]
Email: [Email if no Equipment ID]
Caller Phone Number: [Phone number]
```

### **Halo PSA Integration**
- **Automatic Assignment**: Routes to appropriate team and agent
- **Complete Tracking**: Full order history and status updates
- **Integration**: Seamless connection with existing ticketing system

## Example Usage Scenarios

### **Example 1: Equipment ID Available (Single Order)**
```
User: "I need to order copier supplies"
Agent: "Sure, I can help you place a supply order. Do you have an Equipment ID number for this request?"

User: "Yes, it's EQ-2024-001"
Agent: "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"

User: "I need BP700NT toner for that equipment"
Agent: [Calls order_copier_supplies with equipment_id, supply_details, confirmed=False]
[Shows confirmation message using existing caller info from phone lookup]

User: "Yes, that's correct"
Agent: [Calls order_copier_supplies with confirmed=True]
[Creates ticket and provides success message]

Agent: "Will that be all today or Would you like to add another Equipment ID number for a separate supply request? (Yes/No)"

User: "No, that's all"
[Continues conversation]
```

### **Example 2: Equipment ID Available (Multiple Orders)**
```
User: "I need to order copier supplies"
Agent: "Sure, I can help you place a supply order. Do you have an Equipment ID number for this request?"

User: "Yes, it's EQ-2024-001"
Agent: "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"

User: "I need BP700NT toner for that equipment"
[First order processed]

Agent: "Will that be all today or Would you like to add another Equipment ID number for a separate supply request? (Yes/No)"

User: "Yes, I also need supplies for EQ-2024-002"
Agent: "Please provide the Equipment ID number and the type of supplies you need — you can be as specific as 'BP700NT toner' or as general as 'cyan toner for this ID number.'"

User: "I need magenta toner for that one"
[Second order processed]

Agent: "Will that be all today or Would you like to add another Equipment ID number for a separate supply request? (Yes/No)"

User: "No, that's all"
[Continues conversation]
```

### **Example 3: No Equipment ID**
```
User: "I need to order copier supplies"
Agent: "Sure, I can help you place a supply order. Do you have an Equipment ID number for this request?"

User: "No, I don't have that"
Agent: "Please tell me the item number and type of supplies you need."

User: "I need item number SUP-001, which is HP 26A toner"
Agent: "May I have your name, email address, and callback number?"

User: "My name is John Doe, email is john@company.com, and callback number is 555-1234"
[Processes order with manual contact information]
```

## Data Flow and Storage

### **Information Sources**
1. **Automatic Lookup (Phone Number)**: 
   - ✅ Name
   - ✅ Company
   - ✅ Phone number
   - ✅ Halo client/site/user IDs

2. **User Input (Supplies & Equipment)**:
   - Equipment ID (if available)
   - Supply details
   - Item number (if no Equipment ID)
   - Contact information (if no Equipment ID)

3. **Combined Data**: Merges automatic lookup with manual supply/equipment details

### **What the Agent Should NOT Ask For (Equipment ID Path)**
- ❌ **Name** - Already available from phone lookup
- ❌ **Company** - Already available from phone lookup  
- ❌ **Phone number** - Already available from phone lookup

### **What the Agent Should Ask For**
- ✅ **Equipment ID** (if available)
- ✅ **Supply details** (always required)
- ✅ **Item number** (if no Equipment ID)
- ✅ **Name, email, callback** (only if no Equipment ID)

## Benefits for Different Stakeholders

### **For Callers**
- **Clear Process**: Step-by-step guidance through supply ordering
- **Professional Experience**: Consistent, professional interaction
- **Complete Information**: Ensures all necessary details are captured
- **Confirmation**: Opportunity to review and confirm order details
- **Multiple Equipment**: Easy ordering for multiple machines

### **For Fulfillment Team**
- **Complete Information**: All necessary details for accurate order processing
- **Equipment Identification**: Clear equipment details for proper supply matching
- **Contact Information**: Multiple ways to reach the caller if needed
- **Ticket Tracking**: Full order history and status updates

### **For Support Team**
- **Standardized Process**: Consistent order collection across all calls
- **Quality Assurance**: Comprehensive information reduces order errors
- **Efficient Routing**: Proper team assignment and order categorization
- **Better Metrics**: Complete data for reporting and analysis

## Testing the System

### **Test Scenarios**

#### **1. Equipment ID Available (Single Order)**
1. Request copier supplies
2. Provide Equipment ID and supply details
3. Confirm order details
4. **Expected**: Ticket created with Equipment ID and complete information

#### **2. Equipment ID Available (Multiple Orders)**
1. Request copier supplies
2. Provide first Equipment ID and supply details
3. Confirm first order
4. Request additional equipment
5. Provide second Equipment ID and supply details
6. Confirm second order
7. **Expected**: Two tickets created with complete information

#### **3. No Equipment ID**
1. Request copier supplies
2. Provide item number and supply details
3. Provide contact information
4. Confirm order details
5. **Expected**: Ticket created with manual contact information

### **Verification Points**
- **Data Collection**: All required information is captured
- **Confirmation Process**: Users can review and confirm order details
- **Ticket Creation**: Tickets are created successfully in Halo PSA
- **Success Message**: Appropriate success message with ticket number
- **Interruption Prevention**: Critical messages cannot be interrupted

## Troubleshooting

### **Common Issues**

#### **1. Missing Equipment Information**
- **Problem**: Caller doesn't have Equipment ID
- **Solution**: Guide them through the alternative data collection process

#### **2. Incomplete Supply Details**
- **Problem**: Vague supply descriptions
- **Solution**: Ask for more specific details or item numbers

#### **3. Multiple Equipment Orders**
- **Problem**: Complex multi-equipment scenarios
- **Solution**: Process each equipment ID separately with clear confirmation

### **Debug Tools**
- **debug_ticket_context**: Check what caller information is available
- **Enhanced Logging**: Track all order collection steps
- **Function Parameters**: Verify all collected data is passed correctly

## Future Enhancements

### **Potential Improvements**
1. **Supply Database**: Look up supply details by Equipment ID automatically
2. **Smart Suggestions**: Suggest common supplies based on equipment type
3. **Inventory Integration**: Check supply availability in real-time
4. **Auto-Replenishment**: Integrate with the auto-replenishment program
5. **Order History**: Show caller's previous supply orders

## Conclusion

The copier supplies ordering system provides a professional, comprehensive approach to handling supply orders with or without Equipment ID numbers. By following the structured script and collecting detailed information, the system ensures:

- ✅ **Complete Order Tracking**: All supply orders create tickets for full visibility
- ✅ **Professional User Experience**: Clear, guided process for supply ordering
- ✅ **Better Order Fulfillment**: Complete information ensures accurate processing
- ✅ **Standardized Process**: Consistent experience across all supply orders
- ✅ **Multiple Equipment Support**: Easy handling of complex multi-equipment scenarios

This system transforms copier supply ordering from a basic request process to a comprehensive order management system that benefits callers, fulfillment teams, and the support organization.
