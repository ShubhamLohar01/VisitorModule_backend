#!/usr/bin/env python
"""
Check Twilio SMS usage and logs to understand where the $47 went
"""
from twilio.rest import Client
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_twilio_usage():
    """Check Twilio SMS usage for the last 30 days"""
    print("=" * 80)
    print("TWILIO SMS USAGE ANALYSIS")
    print("=" * 80)

    try:
        # Initialize Twilio client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        # Get account balance
        try:
            balance = client.api.v2010.balance.fetch()
            print(f"\nCurrent Balance: ${balance.balance} {balance.currency}")
        except Exception as e:
            print(f"\nCould not fetch balance: {e}")

        # Get messages from last 30 days
        date_from = datetime.now() - timedelta(days=30)

        print(f"\nFetching SMS messages sent since {date_from.date()}...")
        print("-" * 80)

        messages = client.messages.list(date_sent_after=date_from, limit=100)

        total_messages = 0
        successful = 0
        failed = 0
        undelivered = 0
        total_cost = 0.0

        # Group by phone number to detect spam
        phone_counts = {}
        error_messages = {}

        print(f"\n{'Date':<20} {'To':<15} {'Status':<12} {'Error':<40} {'Price':<10}")
        print("-" * 100)

        for msg in messages:
            total_messages += 1
            to_number = msg.to

            # Count by phone number
            phone_counts[to_number] = phone_counts.get(to_number, 0) + 1

            # Track status
            if msg.status == 'delivered':
                successful += 1
            elif msg.status == 'failed':
                failed += 1
            elif msg.status in ['undelivered', 'canceled']:
                undelivered += 1

            # Track errors
            if msg.error_code:
                error_key = f"{msg.error_code}: {msg.error_message}"
                error_messages[error_key] = error_messages.get(error_key, 0) + 1

            # Calculate cost
            if msg.price:
                price = float(msg.price) if msg.price else 0.0
                total_cost += abs(price)  # Price is negative, so take absolute

            # Print recent messages
            if total_messages <= 20:  # Show first 20 messages
                date_str = msg.date_sent.strftime("%Y-%m-%d %H:%M") if msg.date_sent else "N/A"
                status = msg.status or "unknown"
                error = msg.error_message[:40] if msg.error_message else "-"
                price = f"${abs(float(msg.price)):.4f}" if msg.price else "$0"
                print(f"{date_str:<20} {to_number:<15} {status:<12} {error:<40} {price:<10}")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Messages Sent: {total_messages}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Undelivered: {undelivered}")
        print(f"Estimated Total Cost: ${total_cost:.2f}")

        # Check for spam/repeated sends
        print("\n" + "=" * 80)
        print("MESSAGES PER PHONE NUMBER (Top 10)")
        print("=" * 80)
        sorted_phones = sorted(phone_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for phone, count in sorted_phones:
            print(f"{phone}: {count} messages")
            if count > 10:
                print(f"  ⚠️  WARNING: {count} messages to same number - possible loop!")

        # Show error summary
        if error_messages:
            print("\n" + "=" * 80)
            print("ERROR SUMMARY")
            print("=" * 80)
            for error, count in sorted(error_messages.items(), key=lambda x: x[1], reverse=True):
                print(f"{error}: {count} occurrences")

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        if failed > successful:
            print("❌ More FAILED than SUCCESSFUL messages!")
            print("   - Check if phone numbers are in correct format (+91XXXXXXXXXX)")
            print("   - Check if Twilio account is verified")
            print("   - Check if numbers are on DND list")

        if any(count > 10 for count in phone_counts.values()):
            print("⚠️  Some numbers received 10+ messages - POSSIBLE INFINITE LOOP!")
            print("   - Check if appointments/check-ins are being submitted multiple times")
            print("   - Review backend logs for duplicate visitor creations")

        if undelivered > 0:
            print(f"⚠️  {undelivered} messages undelivered - carrier/DND issues")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("1. Invalid Twilio credentials")
        print("2. Account SID or Auth Token incorrect")
        print("3. Network connectivity issue")

if __name__ == "__main__":
    check_twilio_usage()
