from django.shortcuts import render, get_object_or_404
from .models import Event, Speaker, Session

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

