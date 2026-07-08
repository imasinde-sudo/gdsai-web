from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from .models import Event, Speaker, Session, APIKey, Question, Attendee
from .forms import EventForm, SpeakerForm, SessionForm, APIKeyForm, AdminProfileForm
import sys
import django

def check_admin(user):
    if user.is_authenticated:
        if user.is_staff:
            return True
    return False

def check_super(user):
    if user.is_authenticated:
        if user.is_superuser:
            return True
    return False

def event_list(request):
    events = Event.objects.all().order_by("start_date")
    return render(request, "events/event_list.html", {"events": events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # Prefetch sessions and their speakers to optimize DB queries
    sessions = event.sessions.all().prefetch_related("speakers")
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

@user_passes_test(check_admin, login_url='/login/')
def admin_dashboard(request):
    events = Event.objects.all().order_by("start_date")
    speakers = Speaker.objects.all().order_by("name")
    sessions = Session.objects.all().order_by("start_time")
    apikeys = APIKey.objects.all().order_by("-created_at")
    questions = Question.objects.all().order_by("-created_at")
    
    active_tab = request.GET.get("tab", "events")
    
    context = {
        "events": events,
        "speakers": speakers,
        "sessions": sessions,
        "apikeys": apikeys,
        "questions": questions,
        "total_events": events.count(),
        "total_speakers": speakers.count(),
        "total_sessions": sessions.count(),
        "total_apikeys": apikeys.count(),
        "total_questions": questions.count(),
        "active_tab": active_tab,
    }
    return render(request, "events/admin_dashboard.html", context)

@user_passes_test(check_super, login_url='/login/')
def system_status(request):
    context = {
        "python_version": sys.version,
        "django_version": django.get_version(),
    }
    return render(request, "events/system_status.html", context)

# --- Events CRUD Views ---
@user_passes_test(check_admin, login_url='/login/')
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/?tab=events")
    else:
        form = EventForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Event", "active_tab": "events"})

@user_passes_test(check_admin, login_url='/login/')
def event_edit(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/?tab=events")
    else:
        form = EventForm(instance=event)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Event", "active_tab": "events"})

@user_passes_test(check_admin, login_url='/login/')
def event_delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "POST":
        event.delete()
        return redirect("/dashboard/?tab=events")
    return render(request, "events/dashboard_confirm_delete.html", {"object": event, "title": "Delete Event", "cancel_url": "/dashboard/?tab=events"})

# --- Speakers CRUD Views ---
@user_passes_test(check_admin, login_url='/login/')
def speaker_create(request):
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/?tab=speakers")
    else:
        form = SpeakerForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Speaker", "active_tab": "speakers"})

@user_passes_test(check_admin, login_url='/login/')
def speaker_edit(request, speaker_id):
    speaker = get_object_or_404(Speaker, pk=speaker_id)
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/?tab=speakers")
    else:
        form = SpeakerForm(instance=speaker)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Speaker", "active_tab": "speakers"})

@user_passes_test(check_admin, login_url='/login/')
def speaker_delete(request, speaker_id):
    speaker = get_object_or_404(Speaker, pk=speaker_id)
    if request.method == "POST":
        speaker.delete()
        return redirect("/dashboard/?tab=speakers")
    return render(request, "events/dashboard_confirm_delete.html", {"object": speaker, "title": "Delete Speaker", "cancel_url": "/dashboard/?tab=speakers"})

# --- Sessions CRUD Views ---
@user_passes_test(check_admin, login_url='/login/')
def session_create(request):
    if request.method == "POST":
        form = SessionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/?tab=sessions")
    else:
        form = SessionForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Create Session", "active_tab": "sessions"})

@user_passes_test(check_admin, login_url='/login/')
def session_edit(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    if request.method == "POST":
        form = SessionForm(request.POST, request.FILES, instance=session)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/?tab=sessions")
    else:
        form = SessionForm(instance=session)
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Edit Session", "active_tab": "sessions"})

@user_passes_test(check_admin, login_url='/login/')
def session_delete(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    if request.method == "POST":
        session.delete()
        return redirect("/dashboard/?tab=sessions")
    return render(request, "events/dashboard_confirm_delete.html", {"object": session, "title": "Delete Session", "cancel_url": "/dashboard/?tab=sessions"})

# --- Authentication Views ---
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/dashboard/')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, "events/login.html", {"form": form})


# --- API Key Management Views ---
@user_passes_test(check_admin, login_url='/login/')
def apikey_create(request):
    if request.method == "POST":
        form = APIKeyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/?tab=apikeys")
    else:
        form = APIKeyForm()
    return render(request, "events/dashboard_form.html", {"form": form, "title": "Generate API Key", "active_tab": "apikeys"})


@user_passes_test(check_admin, login_url='/login/')
def apikey_delete(request, key_id):
    key = get_object_or_404(APIKey, pk=key_id)
    if request.method == "POST":
        key.delete()
        return redirect("/dashboard/?tab=apikeys")
    return render(request, "events/dashboard_confirm_delete.html", {"object": key, "title": "Revoke API Key", "cancel_url": "/dashboard/?tab=apikeys"})


# --- Q&A Moderation Views ---
@user_passes_test(check_admin, login_url='/login/')
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        question.delete()
        return redirect("/dashboard/?tab=questions")
    return render(request, "events/dashboard_confirm_delete.html", {"object": question, "title": "Delete Q&A Question", "cancel_url": "/dashboard/?tab=questions"})


# --- Admin Profile View ---
@user_passes_test(check_admin, login_url='/login/')
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

