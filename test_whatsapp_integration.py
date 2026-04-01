#!/usr/bin/env python
"""
WhatsApp Integration Test Script
Sends a sample visitor notification message to test the integration.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from app.services.whatsapp_service import whatsapp_service

def test_whatsapp_integration():
    """Test WhatsApp service with sample visitor notification."""
    
    print("=" * 80)
    print("WHATSAPP INTEGRATION TEST")
    print("=" * 80)
    print()
    
    # Check credentials
    print("📋 Checking Configuration:")
    print(f"  • WhatsApp Enabled: {settings.whatsapp_enabled}")
    print(f"  • Access Token: {'✓ Set' if settings.whatsapp_access_token else '✗ Missing'}")
    print(f"  • Phone Number ID: {settings.whatsapp_number_id if settings.whatsapp_number_id else '✗ Missing'}")
    print()
    
    if not settings.whatsapp_enabled:
        print("❌ WhatsApp service is disabled in settings!")
        return False
    
    if not settings.whatsapp_access_token or not settings.whatsapp_number_id:
        print("❌ WhatsApp credentials not configured!")
        return False
    
    # Test parameters
    test_phone = "8856056214"  # Your test number
    
    print(f"📱 Sending test message to: {test_phone}")
    print()
    
    # Test 1: Visitor Notification (for approver)
    print("1️⃣ Test: Visitor Approval Notification")
    print("-" * 50)
    print("Simulating: New visitor check-in notification to approver")
    print()
    
    result1 = whatsapp_service.send_visitor_notification(
        to_phone=test_phone,
        visitor_name="Kaushal Patil",
        person_to_meet_name="Ramesh Kumar",
        visitor_company="Reliance Retail Ltd",
        reason_for_visit="Business Meeting"
    )
    
    status1 = "✅ SUCCESS" if result1 else "❌ FAILED"
    print(f"Result: {status1}")
    print()
    
    # Test 2: Approval Notification (for visitor)
    print("2️⃣ Test: Visitor Approved Notification")
    print("-" * 50)
    print("Simulating: Visitor approval confirmation")
    print()
    
    result2 = whatsapp_service.send_approval_notification(
        to_phone=test_phone,
        visitor_name="Kaushal Patil",
        person_to_meet_name="Ramesh Kumar"
    )
    
    status2 = "✅ SUCCESS" if result2 else "❌ FAILED"
    print(f"Result: {status2}")
    print()
    
    # Test 3: Rejection Notification
    print("3️⃣ Test: Visitor Rejected Notification")
    print("-" * 50)
    print("Simulating: Visitor rejection notification")
    print()
    
    result3 = whatsapp_service.send_rejection_notification(
        to_phone=test_phone,
        visitor_name="Kaushal Patil"
    )
    
    status3 = "✅ SUCCESS" if result3 else "❌ FAILED"
    print(f"Result: {status3}")
    print()
    
    # Test 4: OTP Notification
    print("4️⃣ Test: OTP for Revisit Verification")
    print("-" * 50)
    print("Simulating: OTP code for returning visitor")
    print()
    
    result4 = whatsapp_service.send_otp_notification(
        to_phone=test_phone,
        otp_code="123456",
        visitor_name="Kaushal Patil"
    )
    
    status4 = "✅ SUCCESS" if result4 else "❌ FAILED"
    print(f"Result: {status4}")
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Visitor Notification:    {status1}")
    print(f"Approval Notification:   {status2}")
    print(f"Rejection Notification:  {status3}")
    print(f"OTP Notification:        {status4}")
    print()
    
    all_success = result1 and result2 and result3 and result4
    
    if all_success:
        print("✅ All tests PASSED!")
        print()
        print("Messages should appear shortly on WhatsApp at: +91" + test_phone)
        print()
    else:
        print("⚠️ Some tests failed. Check logs for details.")
        print()
        print("Common issues:")
        print("  • Message templates not approved in Meta Manager")
        print("  • Invalid access token or phone number ID")
        print("  • WhatsApp API connectivity issues")
        print()
    
    return all_success


if __name__ == "__main__":
    try:
        success = test_whatsapp_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
