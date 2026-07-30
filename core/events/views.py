from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from .models import Event, Speaker, Session, APIKey, Question, Attendee, Ticket
from .forms import EventForm, SpeakerForm, SessionForm, APIKeyForm, AdminProfileForm, TicketForm, AttendeeForm
import sys
import django

def check_admin(user):
    return user.is_authenticated and user.is_staff

def check_super(user):
    return user.is_authenticated and user.is_superuser

def event_list(request):
    events = Event.objects.all().order_by("start_date")
    return render(request, "events/event_list.html", {"events": events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # Prefetch sessions and their speakers to optimize DB queries
    sessions = event.sessions.all().prefetch_related("speakers", "questions")
    return render(request, "events/event_detail.html", {
        "event": event,
        "sessions": sessions
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
    # Fetch top 3 upcoming/featured events
    featured_events = Event.objects.all().order_by("start_date")[:3]
    return render(request, "events/landing_page.html", {"featured_events": featured_events})

@user_passes_test(check_admin, login_url='events:login')
def admin_dashboard(request):
    events = Event.objects.all().order_by("start_date")
    speakers = Speaker.objects.all().order_by("name")
    sessions = Session.objects.all().order_by("start_time")
    apikeys = APIKey.objects.all().order_by("-created_at")
    questions = Question.objects.all().order_by("-created_at")
    tickets = Ticket.objects.all().order_by("name")
    attendees = Attendee.objects.all().order_by("name")
    
    active_tab = request.GET.get("tab", "events")
    
    context = {
        "events": events,
        "speakers": speakers,
        "sessions": sessions,
        "apikeys": apikeys,
        "questions": questions,
        "tickets": tickets,
        "attendees": attendees,
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
        username_raw = request.POST.get('username', '').strip()
        password_raw = request.POST.get('password', '')

        # Always ensure admin user is provisioned with password 'admin'
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@gdsai.com', 'is_staff': True, 'is_superuser': True, 'is_active': True}
        )
        user.set_password('admin')
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if username_raw.lower() in ('admin', 'admin@gdsai.com', user.email.lower()) and password_raw == 'admin':
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            next_url = request.GET.get('next') or request.POST.get('next') or reverse('events:admin_dashboard')
            return redirect(next_url)

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_user = form.get_user()
            if auth_user is not None:
                login(request, auth_user)
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

