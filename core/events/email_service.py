"""Brevo transactional email helpers for badge delivery."""

from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

import requests
from django.conf import settings
from django.utils import timezone

if TYPE_CHECKING:
    from .models import Attendee

logger = logging.getLogger(__name__)

BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"


def send_badge_email(attendee: Attendee, badge_png: bytes, verify_url: str) -> bool:
    """
    Email the attendee their badge PNG via Brevo.

    Returns True on success. When BREVO_API_KEY is unset, logs and returns False
    so registration still completes without email.
    """
    api_key = getattr(settings, "BREVO_API_KEY", "") or ""
    sender_email = getattr(settings, "BREVO_SENDER_EMAIL", "") or ""
    sender_name = getattr(settings, "BREVO_SENDER_NAME", "@iLabAfrica Centre")

    if not api_key or not sender_email:
        logger.warning(
            "Brevo is not configured (BREVO_API_KEY / BREVO_SENDER_EMAIL). "
            "Skipping badge email for %s.",
            attendee.email,
        )
        return False

    event = attendee.event
    event_title = event.title if event else "the event"
    ticket_name = attendee.ticket.name if attendee.ticket else "General Admission"

    html = f"""
    <div style="font-family: Arial, Helvetica, sans-serif; color: #2B2B2B; line-height: 1.6; max-width: 600px; margin: 0 auto;">
      <div style="background:#000000; padding:20px 24px; border-top:4px solid #F96500;">
        <p style="margin:0; color:#FFFFFF; font-size:18px; font-weight:700;">@iLabAfrica Centre</p>
        <p style="margin:6px 0 0; color:#F96500; font-size:12px; letter-spacing:0.12em; text-transform:uppercase;">Registration confirmed</p>
      </div>
      <div style="padding:28px 24px; border:1px solid #DDDDD8; border-top:0;">
        <p style="margin:0 0 12px;">Dear {attendee.name},</p>
        <p style="margin:0 0 12px;">
          You are registered for <strong>{event_title}</strong>
          ({ticket_name}).
        </p>
        <p style="margin:0 0 12px;">
          Your event badge is attached to this email. Please bring it
          (printed or on your phone) for check-in. The QR code on the badge
          can be scanned to verify your registration.
        </p>
        <p style="margin:0 0 8px; font-size:13px; color:#5C5C5C;">
          Badge ID: <strong style="color:#F96500;">{attendee.badge_code}</strong>
        </p>
        <p style="margin:0 0 20px; font-size:13px;">
          <a href="{verify_url}" style="color:#3C5A9A;">Verify your badge online</a>
        </p>
        <p style="margin:0; color:#5C5C5C; font-size:13px;">
          — @iLabAfrica Centre, Strathmore University
        </p>
      </div>
    </div>
    """

    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": attendee.email, "name": attendee.name}],
        "subject": f"Your badge for {event_title}",
        "htmlContent": html,
        "attachment": [
            {
                "content": base64.b64encode(badge_png).decode("ascii"),
                "name": f"badge-{attendee.badge_code}.png",
            }
        ],
    }

    try:
        response = requests.post(
            BREVO_ENDPOINT,
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        if response.status_code >= 400:
            logger.error(
                "Brevo badge email failed for %s: %s %s",
                attendee.email,
                response.status_code,
                response.text[:500],
            )
            return False
    except requests.RequestException:
        logger.exception("Brevo badge email request failed for %s", attendee.email)
        return False

    attendee.email_sent_at = timezone.now()
    attendee.save(update_fields=["email_sent_at"])
    return True
