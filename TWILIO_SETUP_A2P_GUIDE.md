# Complete Twilio Setup & A2P Registration Guide for Candor Foods Pvt Ltd

## Table of Contents
1. [Initial Account Setup](#initial-account-setup)
2. [A2P Registration Process](#a2p-registration-process)
3. [Phone Number Purchase](#phone-number-purchase)
4. [Brand Registration](#brand-registration)
5. [Campaign Registration](#campaign-registration)
6. [Integration Setup](#integration-setup)
7. [Testing & Verification](#testing--verification)
8. [Compliance Requirements](#compliance-requirements)
9. [Troubleshooting](#troubleshooting)

---

## Initial Account Setup

### 1. Create Twilio Account
1. Go to [twilio.com](https://www.twilio.com)
2. Click "Sign Up" and create account with business email
3. Complete phone verification
4. Upgrade to a paid account (required for A2P)

### 2. Account Verification
```bash
# Required Documents for Business Account:
- Business Registration Certificate
- Tax ID/EIN for Candor Foods Pvt Ltd
- Business Address Verification
- Authorized Representative ID
```

### 3. Get Account Credentials
```env
# Save these securely
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
```

---

## A2P Registration Process

### Phase 1: Brand Registration

#### Step 1: Gather Company Information
```yaml
Company Details:
  Legal Name: "Candor Foods Pvt Ltd"
  Business Type: "Private Limited Company"
  Industry: "Food & Beverages"
  Website: "https://candorfoods.com"
  Business Address: "[Your complete business address]"
  Tax ID: "[Your company tax ID/GST number]"
  Stock Symbol: "N/A (Private Company)"
  
Contact Information:
  Business Email: "admin@candorfoods.com"
  Business Phone: "+91-XXXXXXXXXX"
  Support Email: "support@candorfoods.com"
  Support Phone: "+91-XXXXXXXXXX"
```

#### Step 2: Register Your Brand
1. **Navigate to Twilio Console**
   ```
   Console > Messaging > Regulatory Compliance > A2P Registration
   ```

2. **Create Brand Profile**
   ```json
   {
     "brand_type": "STANDARD",
     "company_name": "Candor Foods Pvt Ltd",
     "website": "https://candorfoods.com",
     "vertical": "FOOD_AND_BEVERAGE",
     "ein": "YOUR_TAX_ID",
     "ein_country": "IN",
     "phone": "+91XXXXXXXXXX",
     "street": "Complete Street Address",
     "city": "Your City",
     "state": "Your State", 
     "postal_code": "PIN Code",
     "country": "IN"
   }
   ```

3. **Upload Required Documents**
   ```
   Required Documents:
   - Certificate of Incorporation
   - GST Registration Certificate
   - Address Proof (Utility Bill/Bank Statement)
   - Authorized Signatory ID Proof
   ```

#### Step 3: Brand Verification Process
```
Timeline: 1-5 business days
Status Tracking: Console > A2P Registration > Brand Status
```

---

## Phone Number Purchase

### Step 1: Choose Number Type
```yaml
Number Requirements for Visitor Module:
  Type: "Toll-Free" (Recommended for business)
  Alternative: "Local Number"
  Country: "United States" (for US messaging)
  Capabilities: ["SMS", "Voice"]
```

### Step 2: Purchase Process
```bash
# Via Twilio Console
Console > Phone Numbers > Manage > Buy a Number

# Filter Options:
- Country: United States
- Capabilities: SMS
- Number Type: Toll-free (1-8XX) or Local
- Area Code: Your preference
```

### Step 3: Configure Number
```python
# Python SDK Configuration
from twilio.rest import Client

client = Client(account_sid, auth_token)

# Configure webhook for incoming messages
number = client.incoming_phone_numbers('YOUR_PHONE_SID').update(
    sms_url='https://yourapp.com/sms/webhook',
    sms_method='POST'
)
```

---

## Campaign Registration

### Step 1: Create Campaign
```json
{
  "campaign_type": "MIXED",
  "description": "Visitor Management System - Appointment confirmations, visitor notifications, and security alerts for Candor Foods facilities",
  "message_flow": "Automated notifications sent to pre-registered visitors and internal staff for appointment scheduling, check-in confirmations, and security protocols",
  "help_message": "Reply HELP for assistance or call +1-XXX-XXX-XXXX",
  "opt_out_message": "Reply STOP to unsubscribe from Candor Foods visitor notifications",
  "opt_in_process": "Visitors provide consent during appointment booking process on Candor Foods visitor portal"
}
```

### Step 2: Campaign Use Cases
```yaml
Primary Use Cases:
  - Appointment Confirmations: "Your appointment at Candor Foods is confirmed for [DATE] at [TIME]"
  - Check-in Notifications: "Welcome to Candor Foods! Your visitor pass is ready at reception"
  - Security Alerts: "Security notification: Please follow safety protocols during your visit"
  - Appointment Reminders: "Reminder: Your appointment at Candor Foods is tomorrow at [TIME]"
  
Message Categories:
  - Transactional: Appointment confirmations, check-in status
  - Notifications: Security alerts, facility updates
  - Reminders: Appointment reminders, document requirements
```

### Step 3: Sample Messages
```
Message Templates for Campaign Approval:

1. Appointment Confirmation:
"Hi [NAME], your appointment at Candor Foods is confirmed for [DATE] at [TIME]. Please bring valid ID. Reply STOP to opt out."

2. Check-in Notification:  
"Welcome to Candor Foods! Please proceed to reception. Your visitor ID: [ID]. Reply STOP to opt out."

3. Security Alert:
"Security reminder: Please wear your visitor badge at all times. For help, reply HELP. Reply STOP to opt out."

4. Appointment Reminder:
"Reminder: Your Candor Foods appointment is tomorrow at [TIME]. Bring valid ID. Reply STOP to opt out."
```

---

## Integration Setup

### Step 1: Install Twilio SDK
```bash
# Python Installation
pip install twilio

# Node.js Installation  
npm install twilio

# Environment Variables
echo "TWILIO_ACCOUNT_SID=your_account_sid" >> .env
echo "TWILIO_AUTH_TOKEN=your_auth_token" >> .env
echo "TWILIO_PHONE_NUMBER=your_purchased_number" >> .env
```

### Step 2: Basic Integration Code
```python
# backend/services/twilio_service.py
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)
    
    def send_appointment_confirmation(self, to_number, visitor_name, date, time):
        """Send appointment confirmation SMS"""
        message_body = f"""
        Hi {visitor_name}, your appointment at Candor Foods is confirmed for {date} at {time}. 
        Please bring valid ID. Reply STOP to opt out.
        """
        
        try:
            message = self.client.messages.create(
                body=message_body.strip(),
                from_=self.phone_number,
                to=to_number
            )
            return {"success": True, "sid": message.sid}
        except TwilioException as e:
            return {"success": False, "error": str(e)}
    
    def send_checkin_notification(self, to_number, visitor_name, visitor_id):
        """Send check-in notification"""
        message_body = f"""
        Welcome to Candor Foods! Please proceed to reception. 
        Your visitor ID: {visitor_id}. Reply STOP to opt out.
        """
        
        try:
            message = self.client.messages.create(
                body=message_body.strip(),
                from_=self.phone_number,
                to=to_number
            )
            return {"success": True, "sid": message.sid}
        except TwilioException as e:
            return {"success": False, "error": str(e)}
    
    def send_security_alert(self, to_number):
        """Send security reminder"""
        message_body = """
        Security reminder: Please wear your visitor badge at all times. 
        For help, reply HELP. Reply STOP to opt out.
        """
        
        try:
            message = self.client.messages.create(
                body=message_body.strip(),
                from_=self.phone_number,
                to=to_number
            )
            return {"success": True, "sid": message.sid}
        except TwilioException as e:
            return {"success": False, "error": str(e)}
```

### Step 3: Webhook Handler for Incoming Messages
```python
# backend/api/twilio_webhook.py
from fastapi import APIRouter, Request, Form
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter()

@router.post("/sms/webhook")
async def handle_incoming_sms(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...)
):
    """Handle incoming SMS messages"""
    
    # Create TwiML response
    resp = MessagingResponse()
    
    # Handle different message types
    message_body = Body.strip().upper()
    
    if message_body == "STOP":
        # Handle opt-out (automatically handled by Twilio)
        resp.message("You have been unsubscribed from Candor Foods notifications.")
    
    elif message_body == "HELP":
        resp.message("""
        Candor Foods Visitor System Help:
        - STOP: Unsubscribe from notifications
        - For assistance call: +91-XXXXXXXXXX
        """)
    
    elif message_body == "START":
        # Handle opt-in
        resp.message("You are now subscribed to Candor Foods visitor notifications.")
    
    else:
        # Handle general inquiries
        resp.message("""
        Thank you for contacting Candor Foods. 
        For immediate assistance, please call +91-XXXXXXXXXX
        """)
    
    return Response(content=str(resp), media_type="application/xml")
```

---

## Testing & Verification

### Step 1: Test Environment Setup
```python
# test_twilio_integration.py
import os
from dotenv import load_dotenv
from services.twilio_service import TwilioService

load_dotenv()

def main():
    twilio = TwilioService()
    
    # Test numbers (use your verified test numbers)
    test_number = "+1234567890"  # Replace with verified test number
    
    print("Testing Twilio Integration for Candor Foods...")
    
    # Test 1: Appointment Confirmation
    result1 = twilio.send_appointment_confirmation(
        test_number, 
        "John Doe", 
        "February 15, 2026", 
        "2:00 PM"
    )
    print(f"Appointment Confirmation: {result1}")
    
    # Test 2: Check-in Notification
    result2 = twilio.send_checkin_notification(
        test_number,
        "John Doe",
        "CF-VIS-001"
    )
    print(f"Check-in Notification: {result2}")
    
    # Test 3: Security Alert
    result3 = twilio.send_security_alert(test_number)
    print(f"Security Alert: {result3}")

if __name__ == "__main__":
    main()
```

### Step 2: Run Tests
```bash
# Run integration test
python test_twilio_integration.py

# Check message delivery status
python check_message_status.py
```

---

## Compliance Requirements

### 1. Consent Management
```python
# Implement proper consent tracking
class ConsentManager:
    def __init__(self):
        self.consents = {}
    
    def record_consent(self, visitor_id, phone_number, consent_type="appointment_sms"):
        """Record visitor SMS consent"""
        self.consents[visitor_id] = {
            "phone": phone_number,
            "consent_type": consent_type,
            "timestamp": datetime.now(),
            "ip_address": request.remote_addr,
            "opted_in": True
        }
    
    def check_consent(self, visitor_id):
        """Check if visitor has consented to SMS"""
        return self.consents.get(visitor_id, {}).get("opted_in", False)
```

### 2. Message Requirements
```yaml
Required Elements in Every SMS:
  - Clear sender identification: "Candor Foods"
  - Opt-out instructions: "Reply STOP to opt out"
  - Help instructions: "Reply HELP for assistance"
  - Business contact info when appropriate

Message Limits:
  - Character Limit: 160 characters (single SMS)
  - Long Message: Up to 1600 characters (segmented)
  - Frequency: Maximum 1 message per hour per recipient
```

### 3. Data Privacy
```python
# Implement data protection
class DataProtection:
    def hash_phone_number(self, phone):
        """Hash phone numbers for storage"""
        import hashlib
        return hashlib.sha256(phone.encode()).hexdigest()
    
    def encrypt_personal_data(self, data):
        """Encrypt personal information"""
        # Implement your encryption logic
        pass
```

---

## Campaign Approval Timeline

```yaml
Registration Process Timeline:
  Brand Registration: 1-5 business days
  Campaign Submission: 1-3 business days  
  Campaign Review: 2-7 business days
  Final Approval: 1-2 business days

Total Expected Time: 5-17 business days
```

### Expected A2P Registration Costs
```yaml
Twilio A2P Registration Fees:
  Brand Registration: $4 (one-time)
  Campaign Registration: $10 (one-time)
  Monthly Campaign Fee: $10/month per campaign
  
SMS Costs (after A2P approval):
  Toll-free SMS: $0.0075 per message
  Local SMS: $0.0075 per message
```

---

## Monitoring & Analytics

### Step 1: Message Tracking
```python
# Track message delivery and responses
class MessageTracking:
    def track_message(self, message_sid, visitor_id, message_type):
        """Track message delivery status"""
        message = client.messages(message_sid).fetch()
        
        tracking_data = {
            "sid": message.sid,
            "visitor_id": visitor_id,
            "status": message.status,
            "type": message_type,
            "sent_at": message.date_sent,
            "price": message.price,
            "error_code": message.error_code
        }
        
        # Save to database
        self.save_tracking_data(tracking_data)
```

### Step 2: Analytics Dashboard
```python
# Create analytics endpoint
@router.get("/sms/analytics")
async def get_sms_analytics():
    """Get SMS delivery analytics"""
    return {
        "total_sent": get_total_messages_sent(),
        "delivery_rate": calculate_delivery_rate(),
        "opt_out_rate": calculate_opt_out_rate(),
        "response_rate": calculate_response_rate()
    }
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. A2P Registration Delays
```yaml
Issue: Campaign approval taking longer than expected
Solutions:
  - Ensure all required documents are uploaded
  - Use clear, compliant message templates
  - Provide detailed use case descriptions
  - Contact Twilio support for status updates
```

#### 2. Message Delivery Failures
```python
# Debug message delivery issues
def debug_message_delivery(message_sid):
    """Debug failed message delivery"""
    message = client.messages(message_sid).fetch()
    
    print(f"Status: {message.status}")
    print(f"Error Code: {message.error_code}")
    print(f"Error Message: {message.error_message}")
    
    # Common error codes
    error_solutions = {
        "30008": "Unknown destination - verify phone number format",
        "30004": "Message blocked - number on DND list", 
        "30007": "Message blocked by carrier",
        "21211": "Invalid 'To' phone number"
    }
    
    if message.error_code in error_solutions:
        print(f"Solution: {error_solutions[message.error_code]}")
```

#### 3. Webhook Issues
```python
# Test webhook connectivity
@router.get("/test-webhook")
async def test_webhook():
    """Test webhook endpoint connectivity"""
    return {
        "status": "webhook_active",
        "timestamp": datetime.now(),
        "url": "https://yourapp.com/sms/webhook"
    }
```

---

## Production Deployment Checklist

```yaml
Pre-Production Checklist:
  ✓ Brand registration approved
  ✓ Campaign registration approved  
  ✓ Phone number purchased and configured
  ✓ Webhook endpoints deployed and tested
  ✓ SSL certificate installed
  ✓ Environment variables configured
  ✓ Message templates finalized
  ✓ Consent tracking implemented
  ✓ Error handling implemented
  ✓ Analytics tracking setup
  ✓ Rate limiting configured
  ✓ Backup phone number configured

Post-Production Monitoring:
  - Daily delivery rate monitoring
  - Weekly opt-out rate analysis  
  - Monthly cost analysis
  - Quarterly compliance review
```

---

## Support Contacts

```yaml
Twilio Support:
  - Console Support: help.twilio.com
  - Phone: Check console for your region
  - A2P Support: a2p-support@twilio.com
  - Technical Issues: support@twilio.com

Documentation:
  - A2P Registration: twilio.com/docs/messaging/a2p
  - SMS API: twilio.com/docs/messaging/api
  - Webhooks: twilio.com/docs/messaging/webhooks
```

---

## Next Steps

1. **Complete Brand Registration**: Submit all required documents
2. **Wait for Approval**: Monitor registration status daily
3. **Purchase Phone Number**: Buy toll-free number once brand is approved
4. **Submit Campaign**: Create detailed campaign with message samples
5. **Implement Integration**: Set up webhook and SMS service
6. **Test Thoroughly**: Verify all message types and responses
7. **Deploy to Production**: Launch visitor SMS notifications

**Important**: Start the A2P registration process immediately as it can take 2-3 weeks for full approval.