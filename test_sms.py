#!/usr/bin/env python3
"""
SMS Test Script - Test Twilio SMS functionality
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

def test_sms_configuration():
    """Test SMS service configuration and credentials"""
    print("=" * 60)
    print("SMS SERVICE CONFIGURATION TEST")
    print("=" * 60)
    
    # Check environment variables
    print(f"TWILIO_ACCOUNT_SID: {'✓ Set' if settings.twilio_account_sid else '✗ Missing'}")
    print(f"TWILIO_AUTH_TOKEN: {'✓ Set' if settings.twilio_auth_token else '✗ Missing'}")
    print(f"TWILIO_CUSTOM_PHONE_NUMBER: {settings.twilio_custom_phone_number or 'Not Set'}")
    print(f"TWILIO_MESSAGING_SERVICE_SID: {settings.twilio_messaging_service_sid or 'Not Set'}")
    print(f"TWILIO_ENABLED: {settings.twilio_enabled}")
    print(f"TWILIO_SMS_ENABLED: {settings.twilio_sms_enabled}")
    print(f"SMS Service Enabled: {sms_service.enabled}")
    print(f"SMS Client Initialized: {'✓' if sms_service.client else '✗'}")
    
    print("\n" + "=" * 60)
    
    if not sms_service.enabled:
        print("❌ SMS Service is not enabled!")
        print("Check your configuration and credentials.")
        return False
    
    if not sms_service.client:
        print("❌ Twilio client not initialized!")
        print("Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
        return False
    
    print("✅ SMS Service is properly configured!")
    return True

def send_test_sms(phone_number: str = "8856056214"):
    """Send a test SMS to verify functionality"""
    if not test_sms_configuration():
        return False
    
    print(f"\nSending test SMS to: {phone_number}")
    print("-" * 40)
    
    # Test visitor notification (main SMS function)
    success = sms_service.send_visitor_notification(
        to_phone=phone_number,
        visitor_name="Test Visitor",
        visitor_mobile="9999999999",
        visitor_email="test@example.com",
        visitor_company="Test Company",
        reason_for_visit="SMS Testing",
        visitor_id="TEST-SMS-001",
        warehouse="Test Warehouse",
        person_to_meet_name="Admin",
        date_of_visit=None,
        time_slot=None
    )
    
    if success:
        print("✅ Test SMS sent successfully!")
        print(f"📱 Check your phone ({phone_number}) for the SMS message.")
        return True
    else:
        print("❌ Failed to send test SMS!")
        print("Check the logs above for error details.")
        return False

def send_test_approval_sms(phone_number: str = "8856056214"):
    """Send a test approval SMS"""
    if not sms_service.enabled:
        print("SMS service is not enabled.")
        return False
    
    print(f"\nSending test approval SMS to: {phone_number}")
    print("-" * 40)
    
    success = sms_service.send_approval_notification(
        to_phone=phone_number,
        visitor_name="Test Visitor",
        person_to_meet_name="Admin",
        visitor_id="TEST-APPROVAL-001",
        is_appointment=False
    )
    
    if success:
        print("✅ Test approval SMS sent successfully!")
        return True
    else:
        print("❌ Failed to send test approval SMS!")
        return False

def test_phone_formatting():
    """Test phone number formatting"""
    print("\n" + "=" * 60)
    print("PHONE NUMBER FORMATTING TEST")
    print("=" * 60)
    
    test_numbers = [
        "8856056214",
        "+918856056214", 
        "918856056214",
        "08856056214",
        "+91 88560 56214",
        "88560-56214",
        "(91) 8856056214"
    ]
    
    for number in test_numbers:
        formatted = sms_service.format_phone_number(number)
        print(f"'{number}' -> '{formatted}'")

if __name__ == "__main__":
    print("CANDOR FOODS VISITOR MANAGEMENT SYSTEM")
    print("SMS Service Testing Script")
    print("=" * 60)
    
    # Test phone formatting first
    test_phone_formatting()
    
    # Test configuration
    if not test_sms_configuration():
        print("\nConfiguration test failed. Cannot proceed with SMS test.")
        sys.exit(1)
    
    # Ask user for phone number
    test_number = input(f"\nEnter phone number to test SMS (default: 8856056214): ").strip()
    if not test_number:
        test_number = "8856056214"
    
    print(f"\nTesting SMS functionality with number: {test_number}")
    print("=" * 60)
    
    # Send test visitor notification
    print("\n1. Testing Visitor Notification SMS...")
    visitor_result = send_test_sms(test_number)
    
    # Send test approval notification  
    print("\n2. Testing Approval Notification SMS...")
    approval_result = send_test_approval_sms(test_number)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Visitor Notification SMS: {'✅ SUCCESS' if visitor_result else '❌ FAILED'}")
    print(f"Approval Notification SMS: {'✅ SUCCESS' if approval_result else '❌ FAILED'}")
    
    if visitor_result and approval_result:
        print("\n🎉 All SMS tests passed!")
        print("Your SMS configuration is working correctly.")
    else:
        print("\n⚠️  Some SMS tests failed.")
        print("Check the error messages above for troubleshooting.")
    
    print("\nNote: Check your phone for received messages.")
    print("=" * 60)