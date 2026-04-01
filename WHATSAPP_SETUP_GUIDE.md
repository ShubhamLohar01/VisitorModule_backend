# WhatsApp Business API Integration Guide

This guide explains how to set up the WhatsApp Business API integration for the Visitor Management System.

## Overview

The system now uses **Meta WhatsApp Business API** for sending notifications instead of Twilio SMS. This provides:
- Native WhatsApp messaging (not SMS)
- Pre-approved message templates
- Better delivery rates
- Cost efficiency
- Official WhatsApp status updates

## Prerequisites

1. **Meta Business Account** - Create at https://business.facebook.com/
2. **WhatsApp Business App** - Set up in Meta Business Manager
3. **Phone Number Verification** - A dedicated WhatsApp Business phone number
4. **Access Token** - Generated from Meta Business Manager
5. **Phone Number ID** - From your WhatsApp Business Account

## Step-by-Step Setup

### 1. Create Meta Business Account
- Go to https://business.facebook.com/
- Sign up with your business email
- Complete verification process

### 2. Set Up WhatsApp Business App
- Access **Apps and Assets > Apps** in Meta Business Manager
- Create a new app or use WhatsApp Business app
- Configure WhatsApp Business Platform

### 3. Get Your Credentials

#### Access Token
1. Go to **Settings > Business Apps**
2. Find your app and click **Settings**
3. Go to **System Users**
4. Create a new system user with **Admin** role
5. Generate **Access Token** with these permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
6. Copy the token

#### Phone Number ID
1. Go to **WhatsApp Business > Phone Numbers**
2. Click on your verified phone number
3. Copy the **Phone Number ID** (not the phone number itself)

### 4. Create Message Templates

You need to create **4 message templates** in Meta Business Manager. Each template must be approved before use.

#### Template 1: `visitor_approval_emp` (For Approvers)
**Purpose**: Notify approver about a new visitor

**Header**: None  
**Body**:
```
New Visitor Alert

Visitor: {{1}}
Meeting: {{2}}
Company: {{3}}
Purpose: {{4}}

Please approve or reject from dashboard.
```

**Footer**: Candor Foods Visitor Management  
**Language**: English (US)  
**Buttons**: None required

**Parameters**: 
1. Visitor Name
2. Person to Meet
3. Company
4. Reason for Visit

---

#### Template 2: `visitor_approved` (For Visitors)
**Purpose**: Confirm visitor approval

**Header**: None  
**Body**:
```
Welcome {{1}}!

Your visit has been approved.
Please proceed to the reception.

Host: {{2}}

Thank you for visiting Candor Foods.
```

**Footer**: Candor Foods  
**Language**: English (US)  
**Buttons**: None required

**Parameters**:
1. Visitor Name
2. Host/Person to Meet

---

#### Template 3: `visitor_revisit_otp` (For OTP Verification)
**Purpose**: Send OTP for revisit

**Header**: None  
**Body**:
```
Candor Foods - Revisit Verification

Your OTP: {{1}}
Valid for {{2}} minutes

Do not share this code.
```

**Footer**: Candor Foods  
**Language**: English (US)  
**Buttons**: None required

**Parameters**:
1. OTP Code
2. Expiry Time (minutes)

---

#### Template 4: `visitor_rejected` (For Rejected Visitors)
**Purpose**: Notify visitor of rejection

**Header**: None  
**Body**:
```
Hello {{1}},

We regret to inform you that your visit request has been cannot be approved at this time.

Reason: {{2}}

Please contact us for more information.
```

**Footer**: Candor Foods  
**Language**: English (US)  
**Buttons**: None required

**Parameters**:
1. Visitor Name
2. Rejection Reason

---

### 5. Configure Environment Variables

Update your `.env` file:

```env
# WhatsApp Business API Configuration (Meta)
Whatsapp_access_token=YOUR_ACCESS_TOKEN_HERE
Whatsapp_number_id=YOUR_PHONE_NUMBER_ID_HERE
WHATSAPP_ENABLED=true
```

**Example**:
```env
Whatsapp_access_token=EAAdsM9l9K4cBRBQO1QdjeTyZA7CL7R3uxh4XNyju75ag9iqsswZCpenIW6IzXT7kJxV9FbbcIhGhOTduM9...
Whatsapp_number_id=1013172898549548
WHATSAPP_ENABLED=true
```

### 6. Test the Integration

#### Send a Test Message
```bash
curl -X POST "https://graph.instagram.com/v18.0/YOUR_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "919876543210",
    "type": "template",
    "template": {
      "name": "visitor_approval_emp",
      "language": {
        "code": "en_US"
      },
      "components": [
        {
          "type": "body",
          "parameters": [
            {"type": "text", "text": "John Smith"},
            {"type": "text", "text": "Ramesh Kumar"},
            {"type": "text", "text": "ABC Corp"},
            {"type": "text", "text": "Business Meeting"}
          ]
        }
      ]
    }
  }'
```

#### Check Backend Logs
```bash
# Watch for WhatsApp logs
tail -f app.log | grep -i whatsapp
```

## Message Flow

### New Visitor Check-in
1. Visitor checks in at gate
2. System sends **`visitor_approval_emp`** to approver via WhatsApp
3. Approver approves/rejects from dashboard
4. If approved → System sends **`visitor_approved`** to visitor
5. If rejected → System sends **`visitor_rejected`** to visitor

### Appointment Flow
1. Appointment created via Google Form
2. System sends **`visitor_approval_emp`** to approver
3. Approver action triggers approval/rejection
4. Visitor gets **`visitor_approved`** or **`visitor_rejected`** notification

### Revisit with OTP
1. Returning visitor checks in
2. System sends **`visitor_revisit_otp`** with code

## Troubleshooting

### "Unauthorized" Error
- ✓ Check `Whatsapp_access_token` is correct
- ✓ Verify token hasn't expired
- ✓ Check token has required permissions

### "Template not found"
- ✓ Verify template names match exactly (case-sensitive)
- ✓ Confirm templates are **APPROVED** in Meta Manager
- ✓ Wait 5-10 minutes after approval before testing

### "Invalid Recipient"
- ✓ Phone number must be in E.164 format (e.g., 919876543210)
- ✓ Include country code (91 for India)
- ✓ No spaces or special characters

### "Invalid Phone Number ID"
- ✓ Copy exact Phone Number ID from WhatsApp Business Manager
- ✓ Should be numeric (e.g., 1013172898549548)
- ✓ Not the phone number itself

### Messages Not Sending
1. Check backend logs for errors
2. Verify credentials in `.env`
3. Ensure `WHATSAPP_ENABLED=true`
4. Test with cURL command above
5. Check message template parameters match

## Monitoring

### View Message Status
1. Go to Meta Business Manager
2. Navigate to **WhatsApp > Messages**
3. View delivery and read status

### Chat Analytics
- Monitor engagement in WhatsApp Manager
- Track message delivery rates
- Analyze response patterns

## API Reference

### WhatsApp Service Methods

#### `send_visitor_notification()`
```python
whatsapp_service.send_visitor_notification(
    to_phone="919876543210",
    visitor_name="John Smith",
    person_to_meet_name="Ramesh Kumar",
    visitor_company="ABC Corp",
    reason_for_visit="Business Meeting"
)
```

#### `send_approval_notification()`
```python
whatsapp_service.send_approval_notification(
    to_phone="919876543210",
    visitor_name="John Smith",
    person_to_meet_name="Ramesh Kumar"
)
```

#### `send_rejection_notification()`
```python
whatsapp_service.send_rejection_notification(
    to_phone="919876543210",
    visitor_name="John Smith"
)
```

#### `send_otp_notification()`
```python
whatsapp_service.send_otp_notification(
    to_phone="919876543210",
    otp_code="123456",
    visitor_name="John Smith"
)
```

## Cost Considerations

### Pricing
- WhatsApp Business API is **FREE for the first 1,000 messages per month**
- After that, standard WhatsApp message rates apply
- Template messages are typically cheaper than utility messages

### Optimization
- Use templates for all notifications (required and cost-effective)
- Combine multiple updates into single message when possible
- Remove invalid/inactive phone numbers from system

## Security Best Practices

1. **Never commit credentials** - Keep tokens in `.env` only
2. **Rotate tokens regularly** - Change access tokens quarterly
3. **Limit permissions** - Give tokens only needed abilities
4. **Monitor usage** - Check Meta Manager for suspicious activity
5. **Validate phone numbers** - Ensure recipients are legitimate

## Support

For issues:
- Meta Business Support: https://www.facebook.com/business/help
- WhatsApp API Docs: https://developers.facebook.com/docs/whatsapp
- Check backend logs for detailed error messages

## Migration from Twilio

The system has been updated to use WhatsApp Business API instead of Twilio SMS:

- SMS service is still available for backwards compatibility
- WhatsApp is now the **default** notification method
- Both services can run simultaneously during transition
- Old SMS logs remain in database

To disable SMS completely:
```python
# In config.py
twilio_enabled = False
twilio_sms_enabled = False
```
