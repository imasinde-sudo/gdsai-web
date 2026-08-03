from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.db.models import Prefetch
from .models import Event, EventSeries, Speaker, Session, APIKey, Question, Attendee, Ticket
from .forms import (
    EventForm, EventSeriesForm, SpeakerForm, SessionForm, APIKeyForm, AdminProfileForm,
    TicketForm, AttendeeForm, EventRegistrationForm,
)
from .badges import build_badge_verify_url, badge_png_bytes, save_badge_to_attendee
from .email_service import send_badge_email
import sys
import django
import logging
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)



# TEMPORARY DIAGNOSTIC VIEW — Remove after debugging
def auth_diagnostic(request):
    """Unauthenticated diagnostic endpoint to inspect auth state on Render."""
    from django.contrib.auth import get_user_model
    from django.conf import settings
    User = get_user_model()

    diag = {
        'backends': settings.AUTHENTICATION_BACKENDS,
        'total_users': User.objects.count(),
        'superusers': list(User.objects.filter(is_superuser=True).values('id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser')),
        'admin_user_exists': User.objects.filter(username='admin').exists(),
    }

    # Check if admin user can authenticate
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        diag['admin_user'] = {
            'id': admin_user.id,
            'username': admin_user.username,
            'email': admin_user.email,
            'is_active': admin_user.is_active,
            'is_staff': admin_user.is_staff,
            'is_superuser': admin_user.is_superuser,
            'has_usable_password': admin_user.has_usable_password(),
            'check_password_admin': admin_user.check_password('admin'),
        }
        # Test authenticate()
        auth_result = authenticate(request=request, username='admin', password='admin')
        diag['authenticate_username_admin'] = str(auth_result)
        auth_result2 = authenticate(request=request, username='admin@gdsai.com', password='admin')
        diag['authenticate_email_admin'] = str(auth_result2)
    else:
        diag['admin_user'] = 'NOT FOUND'

    return JsonResponse(diag, json_dumps_params={'indent': 2})

def check_admin(user):
    return user.is_authenticated and user.is_staff

def check_super(user):
    return user.is_authenticated and user.is_superuser

def event_list(request):
    series_list = EventSeries.objects.prefetch_related(
        Prefetch("events", queryset=Event.objects.order_by("start_date"))
    ).order_by("-year", "name")
    ungrouped_events = Event.objects.filter(series__isnull=True).order_by("start_date")
    return render(request, "events/event_list.html", {
        "series_list": series_list,
        "ungrouped_events": ungrouped_events,
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # Prefetch sessions and their speakers to optimize DB queries
    sessions = event.sessions.all().prefetch_related("speakers", "questions")
    tickets = event.tickets.all().order_by("price", "name")
    return render(request, "events/event_detail.html", {
        "event": event,
        "sessions": sessions,
        "tickets": tickets,
        "can_register": tickets.exists(),
    })

def speaker_detail(request, speaker_id):
    speaker = get_object_or_404(Speaker, pk=speaker_id)
    # Get all sessions for this speaker, ordered by start time
    sessions = speaker.sessions.all().select_related("event").order_by("start_time")
    return render(request, "events/speaker_detail.html", {
        "speaker": speaker,
        "sessions": sessions
    })

def landing_page(request):
    current_series = EventSeries.objects.filter(is_current=True).prefetch_related(
        Prefetch("events", queryset=Event.objects.order_by("start_date"))
    ).first()
    if current_series is not None:
        featured_events = current_series.events.all()
    else:
        # No umbrella marked current yet — fall back to the old flat top-3 behaviour.
        featured_events = Event.objects.all().order_by("start_date")[:3]
    # Fetch all scheduled conference sessions ordered by start time
    sessions = Session.objects.select_related("event").prefetch_related("speakers").order_by("start_time")
    return render(request, "events/landing_page.html", {
        "current_series": current_series,
        "featured_events": featured_events,
        "sessions": sessions,
    })


def download_timetable_pdf(request):
    """Generate and stream a PDF timetable of all conference sessions."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold',
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        fontName='Helvetica',
        spaceAfter=14
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        fontName='Helvetica'
    )

    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold'
    )

    story.append(Paragraph("GDSAI Summit — Official Timetable & Schedule", title_style))
    story.append(Paragraph("Includes session start/end times, room locations, and keynote speakers.", subtitle_style))
    story.append(Spacer(1, 10))

    sessions = Session.objects.select_related("event").prefetch_related("speakers").order_by("start_time")

    data = [
        [
            Paragraph("Time", table_header_style),
            Paragraph("Session Title & Event", table_header_style),
            Paragraph("Room / Location", table_header_style),
            Paragraph("Speakers", table_header_style),
        ]
    ]

    for s in sessions:
        time_str = f"{s.start_time.strftime('%b %d, %H:%M')} - {s.end_time.strftime('%H:%M')}"
        event_name = s.event.title if s.event else "GDSAI Summit"
        title_content = f"<b>{s.title}</b><br/><font color='#64748B' size=8>{event_name}</font>"
        location_str = s.location if s.location else "Main Auditorium"
        speaker_names = ", ".join([sp.name for sp in s.speakers.all()]) if s.speakers.exists() else "—"

        data.append([
            Paragraph(time_str, cell_bold),
            Paragraph(title_content, cell_style),
            Paragraph(location_str, cell_style),
            Paragraph(speaker_names, cell_style),
        ])

    if len(data) == 1:
        data.append([
            Paragraph("—", cell_style),
            Paragraph("No sessions currently scheduled.", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
        ])

    col_widths = [110, 193, 110, 110]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))

    story.append(t)
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="GDSAI_Conference_Schedule.pdf"'
    response.write(pdf)
    return response


def series_list(request):
    all_series = EventSeries.objects.prefetch_related(
        Prefetch("events", queryset=Event.objects.order_by("start_date"))
    ).order_by("-year", "name")
    return render(request, "events/series_list.html", {"series_list": all_series})


def series_detail(request, slug):
    series = get_object_or_404(
        EventSeries.objects.prefetch_related(
            Prefetch("events", queryset=Event.objects.order_by("start_date"))
        ),
        slug=slug,
    )
    return render(request, "events/series_detail.html", {
        "series": series,
        "events": series.events.all(),
    })


@user_passes_test(check_admin, login_url='events:login')
def admin_dashboard(request):
    series = EventSeries.objects.all().order_by("-year", "name")
    events = Event.objects.all().order_by("start_date")
    speakers = Speaker.objects.all().order_by("name")
    sessions = Session.objects.all().order_by("start_time")
    apikeys = APIKey.objects.all().order_by("-created_at")
    questions = Question.objects.all().order_by("-created_at")
    tickets = Ticket.objects.all().order_by("name")
    attendees = Attendee.objects.select_related("ticket", "event").order_by("-registered_at")

    active_tab = request.GET.get("tab", "events")

    context = {
        "series": series,
        "events": events,
        "speakers": speakers,
        "sessions": sessions,
        "apikeys": apikeys,
        "questions": questions,
        "tickets": tickets,
        "attendees": attendees,
        "total_series": series.count(),
        "total_events": events.count(),
        "total_speakers": speakers.count(),
        "total_sessions": sessions.count(),
        "total_apikeys": apikeys.count(),
        "total_questions": questions.count(),
        "total_tickets": tickets.count(),
        "total_attendees": attendees.count(),
        "active_tab": active_tab,
    }
    return render(request, "events/admin_dashboard.html", context)

@user_passes_test(check_super, login_url='events:login')
def system_status(request):
    from django.conf import settings as django_settings
    context = {
        "python_version": sys.version,
        "django_version": django.get_version(),
        "database_engine": django_settings.DATABASES["default"]["ENGINE"],
        "debug_mode": django_settings.DEBUG,
    }
    return render(request, "events/system_status.html", context)

# --- Event Series (umbrella) CRUD Views ---
@user_passes_test(check_admin, login_url='events:login')
def series_create(request):
    if request.method == "POST":
        form = EventSeriesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=series")
    else:
        form = EventSeriesForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Event Series", "active_tab": "series"})

@user_passes_test(check_admin, login_url='events:login')
def series_edit(request, series_id):
    series = get_object_or_404(EventSeries, pk=series_id)
    if request.method == "POST":
        form = EventSeriesForm(request.POST, request.FILES, instance=series)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=series")
    else:
        form = EventSeriesForm(instance=series)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Event Series", "active_tab": "series"})

@user_passes_test(check_admin, login_url='events:login')
def series_delete(request, series_id):
    series = get_object_or_404(EventSeries, pk=series_id)
    if request.method == "POST":
        series.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=series")
    return render(request, "events/dashboard_confirm_delete.html", {"object": series, "title": "Delete Event Series", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=series"})


# --- Events CRUD Views ---
@user_passes_test(check_admin, login_url='events:login')
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=events")
    else:
        form = EventForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Event", "active_tab": "events"})

@user_passes_test(check_admin, login_url='events:login')
def event_edit(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=events")
    else:
        form = EventForm(instance=event)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Event", "active_tab": "events"})

@user_passes_test(check_admin, login_url='events:login')
def event_delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "POST":
        event.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=events")
    return render(request, "events/dashboard_confirm_delete.html", {"object": event, "title": "Delete Event", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=events"})

# --- Speakers CRUD Views ---
@user_passes_test(check_admin, login_url='events:login')
def speaker_create(request):
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=speakers")
    else:
        form = SpeakerForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Speaker", "active_tab": "speakers"})

@user_passes_test(check_admin, login_url='events:login')
def speaker_edit(request, speaker_id):
    speaker = get_object_or_404(Speaker, pk=speaker_id)
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=speakers")
    else:
        form = SpeakerForm(instance=speaker)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Speaker", "active_tab": "speakers"})

@user_passes_test(check_admin, login_url='events:login')
def speaker_delete(request, speaker_id):
    speaker = get_object_or_404(Speaker, pk=speaker_id)
    if request.method == "POST":
        speaker.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=speakers")
    return render(request, "events/dashboard_confirm_delete.html", {"object": speaker, "title": "Delete Speaker", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=speakers"})

# --- Sessions CRUD Views ---
@user_passes_test(check_admin, login_url='events:login')
def session_create(request):
    if request.method == "POST":
        form = SessionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=sessions")
    else:
        form = SessionForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Session", "active_tab": "sessions"})

@user_passes_test(check_admin, login_url='events:login')
def session_edit(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    if request.method == "POST":
        form = SessionForm(request.POST, request.FILES, instance=session)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=sessions")
    else:
        form = SessionForm(instance=session)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Session", "active_tab": "sessions"})

@user_passes_test(check_admin, login_url='events:login')
def session_delete(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    if request.method == "POST":
        session.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=sessions")
    return render(request, "events/dashboard_confirm_delete.html", {"object": session, "title": "Delete Session", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=sessions"})

# --- Authentication Views ---
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next') or reverse('events:admin_dashboard')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, "events/login.html", {"form": form})






# --- API Key Management Views ---
@user_passes_test(check_admin, login_url='events:login')
def apikey_create(request):
    if request.method == "POST":
        form = APIKeyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=apikeys")
    else:
        form = APIKeyForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Generate API Key", "active_tab": "apikeys"})


@user_passes_test(check_admin, login_url='events:login')
def apikey_delete(request, key_id):
    key = get_object_or_404(APIKey, pk=key_id)
    if request.method == "POST":
        key.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=apikeys")
    return render(request, "events/dashboard_confirm_delete.html", {"object": key, "title": "Revoke API Key", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=apikeys"})


# --- Q&A Moderation Views ---
@user_passes_test(check_admin, login_url='events:login')
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        question.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=questions")
    return render(request, "events/dashboard_confirm_delete.html", {"object": question, "title": "Delete Q&A Question", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=questions"})


# --- Admin Profile View ---
@user_passes_test(check_admin, login_url='events:login')
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = AdminProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("events:profile_view")
    else:
        form = AdminProfileForm(instance=user)
    return render(request, "events/admin_profile.html", {"form": form, "user": user, "active_tab": "profile"})


def logout_view(request):
    logout(request)
    return redirect("events:landing_page")


# --- Tickets CRUD Views ---
@user_passes_test(check_admin, login_url='events:login')
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=tickets")
    else:
        form = TicketForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Ticket", "active_tab": "tickets"})


@user_passes_test(check_admin, login_url='events:login')
def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=tickets")
    else:
        form = TicketForm(instance=ticket)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Ticket", "active_tab": "tickets"})


@user_passes_test(check_admin, login_url='events:login')
def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == "POST":
        ticket.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=tickets")
    return render(request, "events/dashboard_confirm_delete.html", {"object": ticket, "title": "Delete Ticket", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=tickets"})


# --- Attendees CRUD Views ---
@user_passes_test(check_admin, login_url='events:login')
def attendee_create(request):
    if request.method == "POST":
        form = AttendeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=attendees")
    else:
        form = AttendeeForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Attendee", "active_tab": "attendees"})


@user_passes_test(check_admin, login_url='events:login')
def attendee_edit(request, attendee_id):
    attendee = get_object_or_404(Attendee, pk=attendee_id)
    if request.method == "POST":
        form = AttendeeForm(request.POST, instance=attendee)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('events:admin_dashboard')}?tab=attendees")
    else:
        form = AttendeeForm(instance=attendee)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Attendee", "active_tab": "attendees"})


@user_passes_test(check_admin, login_url='events:login')
def attendee_delete(request, attendee_id):
    attendee = get_object_or_404(Attendee, pk=attendee_id)
    if request.method == "POST":
        attendee.delete()
        return redirect(f"{reverse('events:admin_dashboard')}?tab=attendees")
    return render(request, "events/dashboard_confirm_delete.html", {"object": attendee, "title": "Delete Attendee", "cancel_url": f"{reverse('events:admin_dashboard')}?tab=attendees"})


# --- Public event registration (no payment) ---

def event_register(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    tickets = event.tickets.all().order_by("price", "name")
    if not tickets.exists():
        return render(request, "events/event_register.html", {
            "event": event,
            "form": None,
            "no_tickets": True,
        })

    if request.method == "POST":
        form = EventRegistrationForm(request.POST, event=event)
        if form.is_valid():
            try:
                attendee = Attendee(
                    name=form.cleaned_data["name"].strip(),
                    email=form.cleaned_data["email"],
                    phone_number=form.cleaned_data.get("phone_number", "").strip(),
                    organization=form.cleaned_data.get("organization", "").strip(),
                    ticket=form.cleaned_data["ticket"],
                    event=event,
                    is_registered=True,
                    payment_status="UNPAID",
                )
                attendee.save()
            except IntegrityError:
                form.add_error("email", "This email is already registered for this event.")
            else:
                verify_url = build_badge_verify_url(attendee, request)
                try:
                    badge_png = save_badge_to_attendee(attendee, verify_url)
                except Exception:
                    logger.exception("Badge generation failed for attendee %s", attendee.pk)
                    badge_png = badge_png_bytes(attendee, verify_url)

                email_sent = send_badge_email(attendee, badge_png, verify_url)
                request.session["registration_email_sent"] = email_sent
                return redirect("events:registration_success", badge_code=attendee.badge_code)
    else:
        form = EventRegistrationForm(event=event)

    return render(request, "events/event_register.html", {
        "event": event,
        "form": form,
        "no_tickets": False,
    })


def registration_success(request, badge_code):
    attendee = get_object_or_404(
        Attendee.objects.select_related("event", "ticket"),
        badge_code=badge_code,
    )
    email_sent = request.session.pop("registration_email_sent", None)
    return render(request, "events/registration_success.html", {
        "attendee": attendee,
        "event": attendee.event,
        "email_sent": email_sent,
    })


def badge_image(request, badge_code):
    """Serve / regenerate the badge PNG so QR links work without relying on MEDIA_URL."""
    attendee = get_object_or_404(
        Attendee.objects.select_related("event", "ticket"),
        badge_code=badge_code,
    )
    verify_url = build_badge_verify_url(attendee, request)
    png = badge_png_bytes(attendee, verify_url)
    response = HttpResponse(png, content_type="image/png")
    response["Content-Disposition"] = f'inline; filename="badge-{badge_code}.png"'
    response["Cache-Control"] = "private, max-age=300"
    return response


def badge_download(request, badge_code):
    attendee = get_object_or_404(
        Attendee.objects.select_related("event", "ticket"),
        badge_code=badge_code,
    )
    verify_url = build_badge_verify_url(attendee, request)
    png = badge_png_bytes(attendee, verify_url)
    response = HttpResponse(png, content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="badge-{badge_code}.png"'
    return response


def badge_verify(request, badge_code):
    """Public verification page encoded into the badge QR code."""
    attendee = get_object_or_404(
        Attendee.objects.select_related("event", "ticket"),
        badge_code=badge_code,
    )
    return render(request, "events/badge_verify.html", {
        "attendee": attendee,
        "event": attendee.event,
        "valid": attendee.is_registered,
    })

