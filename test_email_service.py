#!/usr/bin/env python3
"""
Test Email Service - Test the email notification functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import email_service
from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_configuration():
    """Test email configuration"""
    print("📧 Email Service Configuration:")
    print(f"   Service Enabled: {'✓' if email_service.enabled else '✗'}")
    print(f"   SMTP Host: {email_service.smtp_host}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   SMTP User: {email_service.smtp_user}")
    print(f"   SMTP Password: {'✓ Set' if email_service.smtp_password else '✗ Not Set'}")
    print(f"   From Email: {email_service.from_email}")
    print()

    if not email_service.enabled:
        print("❌ Email service is disabled!")
        return False
    
    if not email_service.smtp_host or not email_service.smtp_port:
        print("❌ SMTP host/port not configured!")
        return False
    
    if not email_service.smtp_user or not email_service.smtp_password:
        print("❌ SMTP credentials not configured!")
        return False
    
    print("✅ Email service configuration looks good!")
    return True

def send_test_qr_email(email_address: str = "loharshubham31@gmail.com"):
    """Send a test QR email"""
    if not email_service.enabled:
        print("Email service is not enabled.")
        return False
    
    print(f"\nSending test QR email to: {email_address}")
    print("-" * 50)
    
    # Generate test QR code
    test_qr_code = "APT-20260210120001-TESTQR01"
    
    success = email_service.send_appointment_qr(
        to_email=email_address,
        visitor_name="Test Visitor",
        qr_code=test_qr_code,
        visitor_number="20260210120001",
        appointment_date="12 Feb 2026",
        appointment_time="2:00 PM - 3:00 PM",
        approver_name="Admin"
    )
    
    if success:
        print("✅ Test QR email sent successfully!")
        return True
    else:
        print("❌ Failed to send test QR email!")
        return False

def send_test_rejection_email(email_address: str = "loharshubham31@gmail.com"):
    """Send a test rejection email"""
    if not email_service.enabled:
        print("Email service is not enabled.")
        return False
    
    print(f"\nSending test rejection email to: {email_address}")
    print("-" * 50)
    
    success = email_service.send_appointment_rejection(
        to_email=email_address,
        visitor_name="Test Visitor",
        appointment_date="12 Feb 2026",
        appointment_time="2:00 PM - 3:00 PM",
        rejection_reason="Office capacity limit reached for this time slot"
    )
    
    if success:
        print("✅ Test rejection email sent successfully!")
        return True
    else:
        print("❌ Failed to send test rejection email!")
        return False

def main():
    print("CANDOR FOODS - EMAIL SERVICE TEST")
    print("=" * 60)
    
    # Test configuration
    config_success = test_email_configuration()
    
    if not config_success:
        print("\nConfiguration test failed. Cannot proceed with email test.")
        return
    
    # Test email address 
    test_email = "loharshubham31@gmail.com"
    print(f"🎯 Testing email functionality with: {test_email}")
    print("=" * 60)
    
    # Test 1: QR Code Email 
    print("\n1️⃣ Testing QR Code Email (Approval Notification)...")
    print("-" * 50)
    qr_result = send_test_qr_email(test_email)
    
    # Test 2: Rejection Email
    print("\n2️⃣ Testing Rejection Email...")
    print("-" * 50) 
    rejection_result = send_test_rejection_email(test_email)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EMAIL TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"QR Code Email (Approval): {'✅ SUCCESS' if qr_result else '❌ FAILED'}")
    print(f"Rejection Email:          {'✅ SUCCESS' if rejection_result else '❌ FAILED'}")
    
    total_tests = 2
    passed_tests = sum([qr_result, rejection_result])
    
    print(f"\n📈 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL EMAIL TESTS PASSED! Your email system is working perfectly!")
        print(f"📧 Check your email ({test_email}) for the test messages.")
        print("\n✅ Email Features Working:")
        print("   • QR code emails for approved appointments")
        print("   • Polite rejection emails for declined appointments")
        print("   • Professional email templates with Candor Foods branding")
        print("   • QR code image attachment for easy scanning")
    else:
        print("⚠️  Some email tests failed. Check the error messages above.")
        print("💡 Troubleshooting:")
        print("   • Verify SMTP credentials in .env file")
        print("   • For Gmail: Use App Password instead of regular password")
        print("   • Check firewall/network restrictions")
        print("   • Verify FROM_EMAIL is authorized to send from SMTP server")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()