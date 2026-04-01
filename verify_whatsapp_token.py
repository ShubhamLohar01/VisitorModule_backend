#!/usr/bin/env python
"""
Quick verification of WhatsApp API access token validity.
"""
import requests
from app.core.config import settings

print("=" * 80)
print("WHATSAPP API TOKEN VERIFICATION")
print("=" * 80)
print()

if not settings.whatsapp_access_token:
    print("❌ No access token configured")
    exit(1)

# Test token by trying to fetch user info
url = f"https://graph.instagram.com/v18.0/me?fields=name,email&access_token={settings.whatsapp_access_token}"

print(f"Testing token validity by calling Meta API...")
print(f"URL: {url[:80]}...")
print()

try:
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        print("✅ Token is VALID!")
        data = response.json()
        print(f"Account: {data}")
    else:
        print(f"❌ Token is INVALID!")
        print(f"Status Code: {response.status_code}")
        print(f"Error: {response.text}")
        print()
        print("SOLUTION:")
        print("Your access token has likely EXPIRED or is invalid.")
        print()
        print("Steps to fix:")
        print("1. Go to: https://business.facebook.com/")
        print("2. Navigate to: Settings → Business Apps")
        print("3. Find your WhatsApp app → Settings")
        print("4. Go to: Tools → System Users")
        print("5. Delete the old system user and create a new one")
        print("6. Generate a fresh Access Token")
        print("7. Copy the FULL token (usually 200+ characters)")
        print("8. Update your .env file with the new token")
        print("9. Restart the backend server")
        
except Exception as e:
    print(f"❌ Network error: {e}")
    print("Could not reach Meta API")
