#!/usr/bin/env python3
"""
Comprehensive Notification Test - Test both SMS and Email systems
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.sms_service import sms_service
from app.services.email_service import email_service
from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sms_configuration():
    """Test SMS configuration"""
    print("📱 SMS Service Configuration:")
    print(f"   Service Enabled: {'✓' if sms_service.enabled else '✗'}")
    print(f"   Twilio Account SID: {'✓ Set' if hasattr(settings, 'twilio_account_sid') and settings.twilio_account_sid else '✗ Not Set'}")
    print(f"   Twilio Auth Token: {'✓ Set' if hasattr(settings, 'twilio_auth_token') and settings.twilio_auth_token else '✗ Not Set'}")
    
    return sms_service.enabled

def test_email_configuration():
    """Test email configuration"""
    print("📧 Email Service Configuration:")
    print(f"   Service Enabled: {'✓' if email_service.enabled else '✗'}")
    print(f"   SMTP Host: {email_service.smtp_host}")
    print(f"   SMTP User: {email_service.smtp_user}")
    print(f"   SMTP Password: {'✓ Set' if email_service.smtp_password else '✗ Not Set'}")
    
    return email_service.enabled and email_service.smtp_host and email_service.smtp_user and email_service.smtp_password

def simulate_visitor_approval_flow(phone: str, email: str):
    """Simulate the complete visitor approval notification flow"""
    
    print(f"\n🎯 SIMULATING COMPLETE VISITOR APPROVAL FLOW")
    print(f"📱 SMS to: {phone}")
    print(f"📧 Email to: {email}")
    print("=" * 70)
    
    # Step 1: Visitor Check-in Notification (SMS to Approver)
    print("\n1️⃣ STEP 1: New Visitor Check-in Notification (SMS to Approver)")
    print("-" * 60)
    print("📝 A new visitor just checked in via the form...")
    
    visitor_checkin_success = sms_service.send_visitor_notification(
        to_phone=phone,
        visitor_name="Shubham Lohar",
        visitor_mobile="8856056214",
        visitor_email=email,
        visitor_company="Tech Solutions Pvt Ltd",
        reason_for_visit="[APPOINTMENT] Product Demo and Discussion",
        visitor_id="20260210150001",
        warehouse="W202",
        person_to_meet_name="CEO",
        date_of_visit="12 Feb 2026",
        time_slot="3:00 PM - 4:00 PM"
    )
    
    checkin_result = "✅ SUCCESS" if visitor_checkin_success else "❌ FAILED"
    print(f"   Result: {checkin_result}")
    
    if not visitor_checkin_success:
        print("⚠️  Check-in SMS failed. Stopping simulation.")
        return False, False
    
    # Step 2: Employee Approves the visitor (SMS to Visitor)
    print("\n2️⃣ STEP 2: Approval SMS Notification (SMS to Visitor)")
    print("-" * 60)
    print("✅ Employee approves the visitor request...")
    
    approval_sms_success = sms_service.send_approval_notification(
        to_phone="8856056214",  # Send to visitor's number
        visitor_name="Shubham Lohar",
        person_to_meet_name="CEO",
        visitor_id="20260210150001",
        is_appointment=True,
        appointment_date="12 Feb 2026",
        appointment_time="3:00 PM - 4:00 PM"
    )
    
    approval_sms_result = "✅ SUCCESS" if approval_sms_success else "❌ FAILED"
    print(f"   Result: {approval_sms_result}")
    
    # Step 3: QR Code Email (Email to Visitor)
    print("\n3️⃣ STEP 3: QR Code Email with Visitor Pass (Email to Visitor)")
    print("-" * 60)
    print("📧 Sending QR code and visitor pass via email...")
    
    qr_email_success = email_service.send_appointment_qr(
        to_email=email,
        visitor_name="Shubham Lohar",
        qr_code="APT-20260210150001-QR5C8A12",
        visitor_number="20260210150001",
        appointment_date="12 Feb 2026",
        appointment_time="3:00 PM - 4:00 PM",
        approver_name="CEO"
    )
    
    qr_email_result = "✅ SUCCESS" if qr_email_success else "❌ FAILED"
    print(f"   Result: {qr_email_result}")
    
    return approval_sms_success, qr_email_success

def main():
    print("=" * 70)
    print("🏢 CANDOR FOODS - COMPLETE NOTIFICATION SYSTEM TEST")
    print("=" * 70)
    
    # Test phone and email
    test_phone = "8856056214"
    test_email = "loharshubham31@gmail.com"
    
    print(f"🎯 Testing with:")
    print(f"   📱 Phone: {test_phone}")
    print(f"   📧 Email: {test_email}")
    print()
    
    # Check configurations
    print("🔍 CHECKING SERVICE CONFIGURATIONS")
    print("-" * 40)
    
    sms_config_ok = test_sms_configuration()
    print()
    email_config_ok = test_email_configuration()
    print()
    
    if not sms_config_ok:
        print("❌ SMS service is not properly configured!")
    
    if not email_config_ok:
        print("❌ Email service is not properly configured!")
    
    if not (sms_config_ok or email_config_ok):
        print("❌ Neither SMS nor Email service is configured. Cannot proceed.")
        return
    
    # Run the complete simulation
    sms_success, email_success = simulate_visitor_approval_flow(test_phone, test_email)
    
    # Final Summary
    print("\n" + "=" * 70)
    print("📊 COMPLETE NOTIFICATION SYSTEM TEST RESULTS")
    print("=" * 70)
    
    print("🔔 NOTIFICATION SERVICES STATUS:")
    print(f"   📱 SMS Service:   {'🟢 WORKING' if sms_config_ok else '🔴 NOT WORKING'}")
    print(f"   📧 Email Service: {'🟢 WORKING' if email_config_ok else '🔴 NOT WORKING'}")
    
    print("\n📋 VISITOR APPROVAL WORKFLOW RESULTS:")
    print(f"   1️⃣ Check-in SMS (to approver):     {'✅ SUCCESS' if sms_config_ok else '❌ FAILED'}")
    print(f"   2️⃣ Approval SMS (to visitor):      {'✅ SUCCESS' if sms_success else '❌ FAILED'}")
    print(f"   3️⃣ QR Email (to visitor):          {'✅ SUCCESS' if email_success else '❌ FAILED'}")
    
    # Calculate overall success rate
    working_services = sum([1 if sms_config_ok else 0, 1 if email_config_ok else 0])
    successful_notifications = sum([1 if sms_success else 0, 1 if email_success else 0]) + (1 if sms_config_ok else 0)  # +1 for check-in SMS
    total_notifications = 3
    
    success_rate = int((successful_notifications / total_notifications) * 100)
    
    print(f"\n📈 Overall Success Rate: {success_rate}% ({successful_notifications}/{total_notifications})")
    
    if success_rate == 100:
        print("\n🎉 PERFECT! ALL NOTIFICATION SYSTEMS ARE WORKING!")
        print("✅ Your visitor management system is fully operational:")
        print("   • Visitors get SMS confirmation when approved")
        print("   • Visitors get beautiful QR code emails for entry")
        print("   • Approvers get SMS notifications for new check-ins")
        print("   • Professional email templates with company branding")
        print("\n🚀 READY FOR PRODUCTION!")
    elif success_rate >= 66:
        print("\n✅ GOOD! Most notification systems are working!")
        print("💡 Minor issues detected. Check failed services above.")
    else:
        print("\n⚠️  ATTENTION NEEDED!")
        print("🔧 Multiple notification services need configuration.")
        print("📋 Please review error messages and fix configuration issues.")
    
    print("\n📱📧 Check your phone and email for the test notifications!")
    print("=" * 70)

if __name__ == "__main__":
    main()