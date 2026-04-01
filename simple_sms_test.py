#!/usr/bin/env python3
"""
Simple SMS Test - Direct test without input
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.sms_service import sms_service
from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("CANDOR FOODS - SMS FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Check configuration
    print("📋 Configuration Check:")
    print(f"   TWILIO_ACCOUNT_SID: {'✓' if settings.twilio_account_sid else '✗'}")
    print(f"   TWILIO_AUTH_TOKEN: {'✓' if settings.twilio_auth_token else '✗'}")
    print(f"   TWILIO_ENABLED: {settings.twilio_enabled}")
    print(f"   TWILIO_SMS_ENABLED: {settings.twilio_sms_enabled}")
    print(f"   SMS Service Ready: {'✓' if sms_service.enabled else '✗'}")
    print()
    
    if not sms_service.enabled:
        print("❌ SMS Service is not enabled!")
        return
    
    # Test phone number
    test_phone = "8856056214"
    print(f"📱 Testing SMS to: {test_phone}")
    print("-" * 50)
    
    # Send test SMS
    success = sms_service.send_visitor_notification(
        to_phone=test_phone,
        visitor_name="Test User",
        visitor_mobile="9999999999",
        visitor_email="test@example.com", 
        visitor_company="Test Company",
        reason_for_visit="SMS Configuration Test",
        visitor_id="TEST001",
        warehouse="W202",
        person_to_meet_name="Admin"
    )
    
    print("=" * 50)
    if success:
        print("✅ SMS TEST SUCCESSFUL!")
        print("📱 Check your phone for the test message.")
        print(f"   Message sent to: +91{test_phone}")
    else:
        print("❌ SMS TEST FAILED!")
        print("   Check the error logs above.")
    print("=" * 50)

if __name__ == "__main__":
    main()