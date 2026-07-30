"""Professional event badge generation with embedded QR codes."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from .models import Attendee

# Brand handbook colours
ORANGE = (249, 101, 0)
BLUE = (70, 156, 214)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MUTED = (92, 92, 92)
LIGHT = (246, 246, 244)
GOLD = (203, 160, 82)

# Badge canvas — landscape conference badge at print-friendly resolution
WIDTH = 1200
HEIGHT = 750


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if draw.textlength(text, font=font) <= max_width:
        return text
    ellipsis = "…"
    while text and draw.textlength(text + ellipsis, font=font) > max_width:
        text = text[:-1]
    return text + ellipsis if text else ellipsis


def build_badge_verify_url(attendee: Attendee, request=None) -> str:
    path = reverse("events:badge_verify", kwargs={"badge_code": attendee.badge_code})
    if request is not None:
        return request.build_absolute_uri(path)
    base = getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
    return f"{base}{path}" if base else path


def generate_badge_image(attendee: Attendee, verify_url: str) -> Image.Image:
    """Return a professional brand-aligned badge as a Pillow image."""
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    # Top brand bar
    draw.rectangle((0, 0, WIDTH, 18), fill=ORANGE)
    # Left accent rail
    draw.rectangle((0, 0, 22, HEIGHT), fill=BLACK)
    draw.rectangle((22, 0, 30, HEIGHT), fill=ORANGE)

    # Header strip
    draw.rectangle((30, 18, WIDTH, 130), fill=BLACK)
    draw.text((60, 42), "@iLabAfrica Centre", font=_font(36, bold=True), fill=WHITE)
    draw.text((60, 88), "EVENT BADGE", font=_font(18, bold=True), fill=ORANGE)

    event = attendee.event
    ticket = attendee.ticket

    title_font = _font(42, bold=True)
    name_font = _font(54, bold=True)
    body_font = _font(26)
    small_font = _font(20)
    label_font = _font(16, bold=True)

    event_title = _fit_text(draw, event.title if event else "Event", title_font, 720)
    draw.text((60, 170), event_title, font=title_font, fill=BLACK)

    draw.rectangle((60, 230, 280, 234), fill=ORANGE)

    draw.text((60, 260), "ATTENDEE", font=label_font, fill=MUTED)
    attendee_name = _fit_text(draw, attendee.name, name_font, 720)
    draw.text((60, 285), attendee_name, font=name_font, fill=BLACK)

    y = 370
    if attendee.organization:
        draw.text((60, y), "ORGANISATION", font=label_font, fill=MUTED)
        draw.text((60, y + 28), _fit_text(draw, attendee.organization, body_font, 720), font=body_font, fill=MUTED)
        y += 90

    draw.text((60, y), "TICKET", font=label_font, fill=MUTED)
    ticket_label = ticket.name if ticket else "General Admission"
    if ticket and ticket.price == 0:
        ticket_label = f"{ticket.name} · Free"
    elif ticket:
        ticket_label = f"{ticket.name}"
    draw.text((60, y + 28), _fit_text(draw, ticket_label, body_font, 720), font=body_font, fill=BLACK)

    y += 90
    if event:
        draw.text((60, y), "WHEN / WHERE", font=label_font, fill=MUTED)
        when = event.start_date.strftime("%d %b %Y · %H:%M")
        where = event.location or ""
        draw.text((60, y + 28), _fit_text(draw, when, body_font, 720), font=body_font, fill=MUTED)
        if where:
            draw.text((60, y + 62), _fit_text(draw, where, small_font, 720), font=small_font, fill=MUTED)

    # QR panel
    qr_box = (860, 170, 1140, 520)
    draw.rounded_rectangle(qr_box, radius=18, fill=LIGHT, outline=BLUE, width=3)

    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=BLACK, back_color=WHITE).convert("RGB")
    qr_img = qr_img.resize((220, 220))
    img.paste(qr_img, (890, 200))

    draw.text((890, 440), "SCAN TO VERIFY", font=label_font, fill=MUTED)
    draw.text((890, 468), attendee.badge_code, font=_font(22, bold=True), fill=ORANGE)

    # Footer
    draw.rectangle((30, HEIGHT - 70, WIDTH, HEIGHT), fill=LIGHT)
    draw.text((60, HEIGHT - 48), "Strathmore University · ilabafrica.strathmore.edu", font=small_font, fill=MUTED)
    receipt = attendee.receipt_no or attendee.badge_code
    draw.text((860, HEIGHT - 48), f"ID {receipt}", font=small_font, fill=MUTED)

    return img


def badge_png_bytes(attendee: Attendee, verify_url: str) -> bytes:
    image = generate_badge_image(attendee, verify_url)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def save_badge_to_attendee(attendee: Attendee, verify_url: str) -> bytes:
    """Generate the badge, persist it on the attendee, and return PNG bytes."""
    png = badge_png_bytes(attendee, verify_url)
    filename = f"badge-{attendee.badge_code}.png"
    if attendee.badge_image:
        attendee.badge_image.delete(save=False)
    attendee.badge_image.save(filename, ContentFile(png), save=True)
    return png
