#!/usr/bin/env python3
"""
Test Approval SMS - Test the approval notification flow
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
    print("CANDOR FOODS - APPROVAL SMS TEST")
    print("=" * 50)
    
    # Check configuration
    print("📋 SMS Configuration:")
    print(f"   Service Ready: {'✓' if sms_service.enabled else '✗'}")
    print()
    
    if not sms_service.enabled:
        print("❌ SMS Service is not enabled!")
        return
    
    # Test the approval SMS
    test_phone = "8856056214"
    print(f"📱 Testing approval SMS to: {test_phone}")
    print("-" * 50)
    
    # Send approval SMS
    success = sms_service.send_approval_notification(
        to_phone=test_phone,
        visitor_name="Test User",
        person_to_meet_name="Admin",
        visitor_id="20260210120001",
        is_appointment=False,
        appointment_date=None,
        appointment_time=None
    )
    
    print("=" * 50)
    if success:
        print("✅ APPROVAL SMS TEST SUCCESSFUL!")
        print("📱 Check your phone for the approval message.")
    else:
        print("❌ APPROVAL SMS TEST FAILED!")
        print("   Check the error logs above.")
    
    print("\n" + "=" * 50)
    print("Testing appointment approval SMS...")
    
    # Test appointment approval
    appointment_success = sms_service.send_approval_notification(
        to_phone=test_phone,
        visitor_name="Test User", 
        person_to_meet_name="Admin",
        visitor_id="20260210120002",
        is_appointment=True,
        appointment_date="12 Feb 2026",
        appointment_time="2:00 PM - 3:00 PM"
    )
    
    print("=" * 50)
    if appointment_success:
        print("✅ APPOINTMENT APPROVAL SMS TEST SUCCESSFUL!")
        print("📱 Check your phone for the appointment approval message.")
    else:
        print("❌ APPOINTMENT APPROVAL SMS TEST FAILED!")
    
    print("=" * 50)

if __name__ == "__main__":
    main()