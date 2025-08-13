# Email System Configuration Guide

## Overview
This guide explains how to configure the email system for the sales inquiry functionality. The system uses SMTP to send emails to the sales team when callers submit sales inquiries.

## Required Environment Variables

### **SMTP Configuration**
```bash
# SMTP Server Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Sales Team Email
SALES_EMAIL=sales@cowboytechnologies.com
```

### **Company Configuration**
```bash
# Company Information
COMPANY_NAME=Cowboy Technologies, LLC
```

## SMTP Provider Setup

### **Gmail Setup (Recommended for Testing)**

#### **Step 1: Enable 2-Factor Authentication**
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification

#### **Step 2: Generate App Password**
1. Go to Security → App passwords
2. Select "Mail" as the app
3. Select "Other" as the device
4. Enter "Voice Agent" as the name
5. Click "Generate"
6. Copy the 16-character password

#### **Step 3: Configure Environment Variables**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

### **Office 365 Setup**

#### **Step 1: Get SMTP Settings**
```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-account-password
```

#### **Step 2: Enable SMTP Authentication**
1. Go to Office 365 Admin Center
2. Navigate to Exchange → Mail Flow
3. Ensure SMTP authentication is enabled

### **Other SMTP Providers**

#### **Generic SMTP Settings**
```bash
# For most providers
SMTP_SERVER=smtp.yourprovider.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Complete .env File Example

```bash
# API Configuration
API_URL=https://your-api-domain.com

# Office Configuration
MAIN_OFFICE_NUMBER=+15105550123
COMPANY_NAME=Cowboy Technologies, LLC
EMAIL_DOMAIN=cowboytechnologies.com

# Agent Configuration
AGENT_NAME=telephony_agent
MODE=production

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SALES_EMAIL=sales@cowboytechnologies.com
```

## Testing the Configuration

### **Using the Test Function**
The system includes a `test_email_system` function that can verify your configuration:

1. **Call the function**: Ask the agent to "test the email system"
2. **Check the response**: The agent will report connection status
3. **Review logs**: Check the application logs for detailed information

### **Manual SMTP Test**
You can also test SMTP manually using Python:

```python
import smtplib

# Test connection
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("Connection successful!")
server.quit()
```

## Security Considerations

### **Password Security**
- **Never commit passwords to version control**
- **Use environment variables or secure configuration files**
- **Consider using a dedicated email account for the system**
- **Regularly rotate app passwords**

### **Network Security**
- **Use TLS encryption (port 587)**
- **Avoid unencrypted connections (port 25)**
- **Ensure firewall allows outbound SMTP traffic**

### **Access Control**
- **Limit email account access to necessary personnel**
- **Monitor email sending activity**
- **Set up alerts for unusual activity**

## Troubleshooting Common Issues

### **Authentication Failed**
```
Error: SMTP authentication failed
```
**Solutions:**
1. Check username and password
2. Verify 2-factor authentication is enabled (Gmail)
3. Ensure app password is correct (Gmail)
4. Check account security settings

### **Connection Refused**
```
Error: Connection refused
```
**Solutions:**
1. Verify SMTP server and port
2. Check firewall settings
3. Ensure network allows outbound SMTP
4. Try alternative ports (587, 465, 25)

### **Recipient Refused**
```
Error: Recipient email refused
```
**Solutions:**
1. Verify sales email address is correct
2. Check if recipient mailbox exists
3. Ensure no spam filters are blocking
4. Verify domain reputation

### **Server Disconnected**
```
Error: SMTP server disconnected
```
**Solutions:**
1. Check internet connection stability
2. Verify SMTP server is operational
3. Try reconnecting
4. Check for rate limiting

## Performance Optimization

### **Connection Pooling**
- The system creates new connections for each email
- Consider implementing connection pooling for high volume

### **Rate Limiting**
- Most SMTP providers have sending limits
- Gmail: 500 emails/day for regular accounts
- Office 365: 10,000 emails/day for business accounts

### **Monitoring**
- Track email delivery success rates
- Monitor response times
- Set up alerts for failures

## Backup and Recovery

### **Alternative Email Providers**
Keep backup SMTP configurations ready:

```bash
# Primary (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Backup (Office 365)
SMTP_SERVER_BACKUP=smtp.office365.com
SMTP_PORT_BACKUP=587
```

### **Fallback Procedures**
1. **Immediate**: Use backup SMTP provider
2. **Short-term**: Queue emails for later sending
3. **Long-term**: Implement alternative notification methods

## Support and Maintenance

### **Regular Maintenance**
- **Monthly**: Review email delivery logs
- **Quarterly**: Update SMTP credentials
- **Annually**: Review and update email templates

### **Monitoring Tools**
- **Log Analysis**: Review application logs regularly
- **Email Tracking**: Monitor delivery and bounce rates
- **Performance Metrics**: Track response times and success rates

### **Contact Information**
- **Technical Support**: Your IT team or system administrator
- **SMTP Provider Support**: Contact your email service provider
- **Documentation**: Refer to this guide and system logs

## Conclusion

Proper email configuration is essential for the sales inquiry system to function effectively. By following this guide and implementing the recommended security measures, you'll ensure reliable email delivery and maintain the security of your system.

Remember to:
- ✅ Test your configuration before going live
- ✅ Monitor email delivery regularly
- ✅ Keep credentials secure and updated
- ✅ Have backup configurations ready
- ✅ Document any customizations or changes
