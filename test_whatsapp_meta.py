"""
Test: send a sample visitor_approval_emp WhatsApp message
to 8856056214 using Meta WhatsApp Business API.
"""
import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("Whatsapp_access_token")
PHONE_NUMBER_ID = os.getenv("Whatsapp_number_id")
TO_PHONE = "918856056214"

BASE_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

now = datetime.now()
visit_time = now.strftime("%I:%M %p")
reference_no = now.strftime("%Y%m%d%H%M%S")

# Sample visitor selfie placeholder (replace with real S3 URL in production)
SAMPLE_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Gatto_europeo4.jpg/320px-Gatto_europeo4.jpg"

payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": TO_PHONE,
    "type": "template",
    "template": {
        "name": "visitor_approval_emp",
        "language": {"code": "en"},
        "components": [
            {
                "type": "header",
                "parameters": [{"type": "image", "image": {"link": SAMPLE_IMAGE_URL}}],
            },
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": "Rahul Sharma"},    # visitor name
                    {"type": "text", "text": "Candor Foods Ltd"},# company
                    {"type": "text", "text": "Business Meeting"},# purpose
                    {"type": "text", "text": visit_time},        # time
                    {"type": "text", "text": reference_no},      # reference no
                ],
            },
        ],
    },
}

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

print(f"Sending visitor approval notification to: {TO_PHONE}")
print(f"Template: visitor_approval_emp  |  Lang: en")
print(f"Reference No: {reference_no}   Time: {visit_time}")
print()

response = requests.post(BASE_URL, json=payload, headers=headers, timeout=15)

print(f"HTTP Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    msg_id = response.json().get("messages", [{}])[0].get("id", "?")
    print(f"\nMessage sent successfully! ID: {msg_id}")
    sys.exit(0)
else:
    print("\nFailed. Check token/number_id or template approval status.")
    sys.exit(1)
