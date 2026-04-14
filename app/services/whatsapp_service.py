"""
WhatsApp Service for sending notifications via Meta WhatsApp Business Cloud API.
Uses pre-approved message templates for structured communications.
"""
from typing import Optional, List
import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service for sending WhatsApp messages via Meta WhatsApp Business API.
    Uses pre-approved message templates for compliance and better delivery.
    """

    # Fallback image used as header when visitor selfie is unavailable
    DEFAULT_VISITOR_IMAGE = "https://visitor-selfie-image.s3.ap-south-1.amazonaws.com/default-visitor.jpg"

    TEMPLATES = {
        "visitor_approval_emp": "visitor_approval_emp",   # New visitor → approver
        "visitor_approved": "visitor_approved",            # Approval confirmation → visitor
        "visitor_revisit_otp": "visitor_revisit_otp",     # OTP for revisit → visitor
        "visitor_rejected": "visitor_rejected",            # Rejection → visitor
    }

    # Language codes per template
    TEMPLATE_LANGUAGES = {
        "visitor_approval_emp": "en",
        "visitor_approved": "en",
        "visitor_rejected": "en",
        "visitor_revisit_otp": "en_US",
    }

    def __init__(self):
        self.enabled = settings.whatsapp_enabled
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.api_url = settings.whatsapp_api_url

        if not self.enabled:
            logger.warning("WhatsApp service is disabled")
            return

        if not self.access_token or not self.phone_number_id:
            logger.error(
                f"WhatsApp credentials missing: "
                f"access_token={'SET' if self.access_token else 'MISSING'}, "
                f"phone_number_id={'SET' if self.phone_number_id else 'MISSING'}"
            )
            self.enabled = False
            return

        logger.info(f"WhatsApp service initialized: phone_id={self.phone_number_id}, api={self.api_url}")

    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number to E.164 format (e.g. 919876543210)."""
        if not phone_number:
            return ""

        digits = ''.join(filter(str.isdigit, phone_number))

        if digits.startswith('0'):
            digits = digits[1:]

        if len(digits) == 10:
            return f"91{digits}"
        elif len(digits) == 12 and digits.startswith('91'):
            return digits
        elif len(digits) > 10:
            return digits
        else:
            return f"91{digits}"

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_messages_url(self) -> str:
        return f"{self.api_url}/{self.phone_number_id}/messages"

    def _send_template_message(
        self,
        to_phone: str,
        template_name: str,
        body_params: List[str],
        header_image_url: Optional[str] = None,
        button_params: Optional[List[dict]] = None,
    ) -> bool:
        """
        Send a WhatsApp message using a pre-approved template.

        Args:
            to_phone: Recipient phone number
            template_name: Name of the approved template
            body_params: List of body parameter strings
            header_image_url: Optional URL for image header component
            button_params: Optional list of button component dicts
        """
        if not self.enabled:
            logger.warning("WhatsApp service is disabled")
            return False

        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp credentials not configured")
            return False

        try:
            formatted_phone = self.format_phone_number(to_phone)
            if not formatted_phone:
                logger.warning(f"Invalid phone number: {to_phone}")
                return False

            components = []

            if header_image_url:
                components.append({
                    "type": "header",
                    "parameters": [{"type": "image", "image": {"link": header_image_url}}],
                })

            components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in body_params],
            })

            if button_params:
                components.extend(button_params)

            lang_code = self.TEMPLATE_LANGUAGES.get(template_name, "en")

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": lang_code},
                    "components": components,
                },
            }

            logger.info(f"Sending WhatsApp '{template_name}' to {formatted_phone}")

            with httpx.Client(timeout=10) as client:
                response = client.post(
                    self._get_messages_url(),
                    headers=self._get_headers(),
                    json=payload,
                )

            if response.status_code == 200:
                message_id = response.json().get("messages", [{}])[0].get("id", "unknown")
                logger.info(f"WhatsApp message sent. ID: {message_id}")
                return True
            else:
                logger.error(f"WhatsApp API error {response.status_code}: {response.text}")
                return False

        except httpx.TimeoutException:
            logger.error("WhatsApp API request timed out")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {e}")
            return False

    def send_text_message(self, to_phone: str, text: str) -> bool:
        """Send a plain text WhatsApp message (for webhook confirmations)."""
        if not self.enabled:
            return False

        try:
            formatted_phone = self.format_phone_number(to_phone)
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "text",
                "text": {"body": text},
            }

            with httpx.Client(timeout=10) as client:
                response = client.post(
                    self._get_messages_url(),
                    headers=self._get_headers(),
                    json=payload,
                )

            if response.status_code == 200:
                logger.info(f"WhatsApp text message sent to {formatted_phone}")
                return True
            else:
                logger.error(f"WhatsApp text error {response.status_code}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending WhatsApp text: {e}")
            return False

    def send_visitor_notification(
        self,
        to_phone: str,
        visitor_name: str,
        visitor_id: str,
        person_to_meet_name: Optional[str] = None,
        visitor_company: Optional[str] = None,
        reason_for_visit: Optional[str] = None,
        visit_time: Optional[str] = None,
        reference_no: Optional[str] = None,
        visitor_image_url: Optional[str] = None,
    ) -> bool:
        """
        Send WhatsApp notification to approver about new visitor.
        Template 'visitor_approval_emp' (lang: en):
          header = visitor selfie image
          {{1}} = visitor name, {{2}} = company, {{3}} = purpose
          {{4}} = time,         {{5}} = reference number
          Buttons: [Approve] payload=approve_{visitor_id}
                   [Reject]  payload=reject_{visitor_id}
        """
        try:
            params = [
                visitor_name,
                visitor_company or "Not specified",
                reason_for_visit or "Business visit",
                visit_time or "N/A",
                reference_no or visitor_id,
            ]

            button_params = [
                {
                    "type": "button",
                    "sub_type": "quick_reply",
                    "index": "0",
                    "parameters": [{"type": "payload", "payload": f"approve_{visitor_id}"}],
                },
                {
                    "type": "button",
                    "sub_type": "quick_reply",
                    "index": "1",
                    "parameters": [{"type": "payload", "payload": f"reject_{visitor_id}"}],
                },
            ]

            header_img = visitor_image_url or self.DEFAULT_VISITOR_IMAGE
            logger.info(f"[WhatsApp] Sending visitor notification to {to_phone} for visitor {visitor_id}")

            return self._send_template_message(
                to_phone=to_phone,
                template_name=self.TEMPLATES["visitor_approval_emp"],
                body_params=params,
                header_image_url=header_img,
                button_params=button_params,
            )
        except Exception as e:
            logger.error(f"Error sending visitor notification: {e}")
            return False

    def send_approval_notification(
        self,
        to_phone: str,
        visitor_name: str,
        person_to_meet_name: Optional[str] = None,
        cn_number: Optional[str] = None,
    ) -> bool:
        """
        Send WhatsApp approval confirmation to visitor.
        Template 'visitor_approved' (lang: en): {{1}} = CN number
        """
        try:
            params = [cn_number or visitor_name]
            logger.info(f"[WhatsApp] Sending approval notification to visitor {to_phone}")
            return self._send_template_message(
                to_phone=to_phone,
                template_name=self.TEMPLATES["visitor_approved"],
                body_params=params,
            )
        except Exception as e:
            logger.error(f"Error sending approval notification: {e}")
            return False

    def send_rejection_notification(
        self,
        to_phone: str,
        visitor_name: str,
        cn_number: Optional[str] = None,
    ) -> bool:
        """
        Send WhatsApp rejection notification to visitor.
        Template 'visitor_rejected' (lang: en): {{1}} = CN number
        """
        try:
            params = [cn_number or visitor_name]
            logger.info(f"[WhatsApp] Sending rejection notification to visitor {to_phone}")
            return self._send_template_message(
                to_phone=to_phone,
                template_name=self.TEMPLATES["visitor_rejected"],
                body_params=params,
            )
        except Exception as e:
            logger.error(f"Error sending rejection notification: {e}")
            return False

    def send_otp_notification(
        self,
        to_phone: str,
        otp_code: str,
        visitor_name: Optional[str] = None,
    ) -> bool:
        """
        Send WhatsApp OTP for revisit verification.
        Template 'visitor_revisit_otp' (authentication, lang: en_US):
          body {{1}} = OTP, button COPY_CODE = OTP
        """
        try:
            button_params = [
                {
                    "type": "button",
                    "sub_type": "COPY_CODE",
                    "index": "0",
                    "parameters": [{"type": "coupon_code", "coupon_code": otp_code}],
                }
            ]
            logger.info(f"[WhatsApp] Sending OTP to {to_phone}")
            return self._send_template_message(
                to_phone=to_phone,
                template_name=self.TEMPLATES["visitor_revisit_otp"],
                body_params=[otp_code],
                button_params=button_params,
            )
        except Exception as e:
            logger.error(f"Error sending OTP notification: {e}")
            return False


# Global instance
whatsapp_service = WhatsAppService()
