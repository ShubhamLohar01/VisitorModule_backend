#!/usr/bin/env python
"""Debug script to check what's being read from .env"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

print("=" * 80)
print("ENVIRONMENT CONFIGURATION DEBUG")
print("=" * 80)
print()

print("WhatsApp Configuration:")
print(f"  Enabled: {settings.whatsapp_enabled}")
print(f"  Token Length: {len(settings.whatsapp_access_token) if settings.whatsapp_access_token else 0}")
print(f"  Token value:")
print(f"  '{settings.whatsapp_access_token}'")
print()
print(f"  Phone Number ID: {settings.whatsapp_number_id}")
print()

# Check if there are any hidden characters
if settings.whatsapp_access_token:
    print("Token Analysis:")
    print(f"  First 50 chars: {settings.whatsapp_access_token[:50]}")
    print(f"  Last 50 chars: {settings.whatsapp_access_token[-50:]}")
    print(f"  Starts with 'EAA': {settings.whatsapp_access_token.startswith('EAA')}")
    
    # Check for hidden characters
    if any(ord(c) < 32 or ord(c) > 126 for c in settings.whatsapp_access_token):
        print("  ⚠️ WARNING: Token contains non-printable characters!")
        for i, c in enumerate(settings.whatsapp_access_token):
            if ord(c) < 32 or ord(c) > 126:
                print(f"  Non-printable char at position {i}: {ord(c)}")
    else:
        print("  ✓ Token contains only valid characters")
