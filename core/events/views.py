from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Event, Speaker, Session
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

@user_passes_test(check_admin, login_url='/admin/login/')
def admin_dashboard(request):
    events = Event.objects.all().order_by("start_date")
    speakers = Speaker.objects.all().order_by("name")
    sessions = Session.objects.all().order_by("start_time")
    
    context = {
        "events": events,
        "speakers": speakers,
        "sessions": sessions,
        "total_events": events.count(),
        "total_speakers": speakers.count(),
        "total_sessions": sessions.count(),
    }
    return render(request, "events/admin_dashboard.html", context)

@user_passes_test(check_super, login_url='/admin/login/')
def system_status(request):
    context = {
        "python_version": sys.version,
        "django_version": django.get_version(),
    }
    return render(request, "events/system_status.html", context)


