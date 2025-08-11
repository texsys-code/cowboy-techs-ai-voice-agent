# Email Functionality

This document explains how the AI Voice Agent now handles email addresses for callers.

## Overview

The system now intelligently manages caller email addresses by:
1. **Checking existing records** for email addresses
2. **Prompting for email** when none is found
3. **Storing email addresses** in the database
4. **Using email addresses** for ticket creation and caller records

## How It Works

### 1. **Automatic Email Check**
When a caller provides their name and company, the system:
- Searches the database for existing caller records
- Checks if an email address already exists
- If email exists: Updates the caller record with new name/company
- If no email: Prompts the caller to provide their email address

### 2. **Email Prompting**
When no email is found, the system returns:
```
"I found your information in our system, but I need your email address to complete your profile. Could you please provide your email address?"
```

### 3. **Email Storage**
The new `store_caller_email` function:
- Validates the email format (basic validation)
- Updates the database record if caller ID exists
- Searches by phone number if no caller ID
- Stores email in context for the current call

## New Function: `store_caller_email`

### Purpose
Stores the caller's email address in the system.

### Parameters
- `email` (string): The email address to store

### Behavior
1. **Basic validation**: Checks for `@` and `.` in the email
2. **Database update**: Updates existing caller records
3. **Fallback storage**: Stores in context if database update fails
4. **User feedback**: Provides clear confirmation messages

### Usage Examples
- User: "My email is john.doe@company.com"
- Agent: Uses `store_caller_email("john.doe@company.com")`
- Response: "Perfect! I've saved your email address john.doe@company.com in our system."

## Updated Function: `store_caller_info`

### Changes Made
- **Database search**: Now checks if caller already exists
- **Email handling**: Different behavior based on email existence
- **Record updates**: Updates existing records instead of always creating new ones
- **Smart responses**: Different messages for new vs. existing callers

### Scenarios

#### Scenario 1: New Caller
- Creates new caller record with generated email
- Response: "Thank you [Name] from [Company]. I've saved your information in our system with a generated email address."

#### Scenario 2: Existing Caller with Email
- Updates existing record with new name/company
- Response: "Welcome back [Name]! I found your information in our system. I've updated your name and company."

#### Scenario 3: Existing Caller without Email
- Prompts for email address
- Response: "I found your information in our system, but I need your email address to complete your profile. Could you please provide your email address?"

## Agent Instructions Updated

The AI agent now knows to:
- Use `store_caller_email` when users provide email addresses
- Prompt for email addresses when the system requests them
- Remember email addresses for the duration of the call
- Handle email-related scenarios appropriately

## Benefits

1. **Complete caller profiles**: All callers now have email addresses
2. **Better ticket creation**: Email addresses included in support tickets
3. **Improved communication**: Can follow up with callers via email
4. **Data consistency**: No more missing email addresses in the system
5. **User experience**: Clear prompts guide callers to provide missing information

## Database Impact

- **New field**: Email addresses stored in caller records
- **Updates**: Existing records can be updated with email addresses
- **Search**: Email addresses can be used for caller lookups
- **Tickets**: Email addresses included in ticket details

## Testing

To test the email functionality:
1. Call with a new caller (no existing record)
2. Call with an existing caller who has no email
3. Call with an existing caller who has an email
4. Provide email addresses in various formats
5. Verify email addresses are stored in the database

## Error Handling

The system gracefully handles:
- Invalid email formats
- Database connection issues
- Missing caller records
- API failures

All errors result in the email being stored in context for the current call, ensuring no information is lost.
