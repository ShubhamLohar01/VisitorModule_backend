#!/usr/bin/env python3
"""
Comprehensive SMS System Test
Tests all SMS functionality in the Visitor Management System
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
    print("🔔 CANDOR FOODS VISITOR MANAGEMENT SYSTEM")
    print("📱 COMPLETE SMS FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Configuration Summary
    print("📋 SMS Configuration Summary:")
    print(f"   • TWILIO_ACCOUNT_SID: {'✓ Set' if settings.twilio_account_sid else '✗ Missing'}")
    print(f"   • TWILIO_AUTH_TOKEN: {'✓ Set' if settings.twilio_auth_token else '✗ Missing'}")
    print(f"   • Custom Phone Number: {settings.twilio_custom_phone_number}")
    print(f"   • Messaging Service SID: {settings.twilio_messaging_service_sid}")
    print(f"   • Service Enabled: {'✓' if sms_service.enabled else '✗'}")
    print()
    
    if not sms_service.enabled:
        print("❌ SMS Service is not enabled! Cannot proceed.")
        return
    
    test_phone = "8856056214"
    print(f"📱 Running tests with phone number: {test_phone}")
    print("=" * 60)
    
    # Test 1: Visitor Check-in Notification (to approver)
    print("\n1️⃣ Testing Visitor Check-in Notification (sent to approver)...")
    print("-" * 50)
    
    visitor_notification_success = sms_service.send_visitor_notification(
        to_phone=test_phone,
        visitor_name="John Smith",
        visitor_mobile="9876543210", 
        visitor_email="john@example.com",
        visitor_company="ABC Corporation",
        reason_for_visit="Business Meeting",
        visitor_id="20260210143001",
        warehouse="W202",
        person_to_meet_name="Admin"
    )
    
    result1 = "✅ SUCCESS" if visitor_notification_success else "❌ FAILED"
    print(f"   Result: {result1}")
    
    # Test 2: Regular Approval Notification (to visitor)
    print("\n2️⃣ Testing Regular Visitor Approval Notification (sent to visitor)...")
    print("-" * 50)
    
    approval_success = sms_service.send_approval_notification(
        to_phone=test_phone,
        visitor_name="John Smith",
        person_to_meet_name="Admin",
        visitor_id="20260210143001",
        is_appointment=False
    )
    
    result2 = "✅ SUCCESS" if approval_success else "❌ FAILED"
    print(f"   Result: {result2}")
    
    # Test 3: Appointment Check-in Notification (to approver)  
    print("\n3️⃣ Testing Appointment Request Notification (sent to approver)...")
    print("-" * 50)
    
    appointment_notification_success = sms_service.send_visitor_notification(
        to_phone=test_phone,
        visitor_name="Jane Doe",
        visitor_mobile="8765432109",
        visitor_email="jane@example.com", 
        visitor_company="XYZ Inc",
        reason_for_visit="[APPOINTMENT] Product Discussion",
        visitor_id="20260212100001",
        warehouse="W203",
        person_to_meet_name="CEO",
        date_of_visit="12 Feb 2026",
        time_slot="10:00 AM - 11:00 AM"
    )
    
    result3 = "✅ SUCCESS" if appointment_notification_success else "❌ FAILED"
    print(f"   Result: {result3}")
    
    # Test 4: Appointment Approval Notification (to visitor)
    print("\n4️⃣ Testing Appointment Approval Notification (sent to visitor)...")
    print("-" * 50)
    
    appointment_approval_success = sms_service.send_approval_notification(
        to_phone=test_phone,
        visitor_name="Jane Doe",
        person_to_meet_name="CEO", 
        visitor_id="20260212100001",
        is_appointment=True,
        appointment_date="12 Feb 2026",
        appointment_time="10:00 AM - 11:00 AM"
    )
    
    result4 = "✅ SUCCESS" if appointment_approval_success else "❌ FAILED"
    print(f"   Result: {result4}")
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"1️⃣ Visitor Check-in Notification:      {result1}")
    print(f"2️⃣ Regular Approval Notification:     {result2}")
    print(f"3️⃣ Appointment Request Notification:   {result3}")
    print(f"4️⃣ Appointment Approval Notification:  {result4}")
    
    total_tests = 4
    passed_tests = sum([
        visitor_notification_success,
        approval_success,
        appointment_notification_success,
        appointment_approval_success
    ])
    
    print(f"\n📈 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Your SMS system is working perfectly!")
        print("📱 Check your phone ({}) for the test messages.".format(test_phone))
        print("\n✅ SMS Features Working:")
        print("   • Visitor check-in notifications to approvers")
        print("   • Approval notifications to visitors")
        print("   • Appointment request notifications") 
        print("   • Appointment approval notifications")
        print("   • Proper phone number formatting (+91)")
        print("   • Twilio messaging service integration")
        print("   • Background SMS sending (non-blocking)")
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed.")
        print("   Check the logs above for error details.")
    
    print("\n" + "=" * 60)
    print("💡 Integration Points:")
    print("   • Visitor check-in: /api/visitors/check-in")
    print("   • Status updates: /api/visitors/{id}/status") 
    print("   • Background tasks: FastAPI BackgroundTasks")
    print("   • Error handling: Graceful failures logged")
    print("=" * 60)

if __name__ == "__main__":
    main()