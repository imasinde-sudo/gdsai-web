from rest_framework import serializers
from .models import Event, EventSeries, Speaker, Session, Attendee, Question


# ---------------------------------------------------------------------------
# Shared / base serializers (used internally by others)
# ---------------------------------------------------------------------------

class SpeakerSerializer(serializers.ModelSerializer):
    """Full speaker data — used on admin API and speaker detail."""
    class Meta:
        model = Speaker
        fields = [
            "id", "name", "title", "organization", "bio",
            "email", "profile_picture", "twitter", "linkedin", "website",
        ]


class SpeakerSummarySerializer(serializers.ModelSerializer):
    """Lightweight speaker card — used inside session lists."""
    class Meta:
        model = Speaker
        fields = ["id", "name", "title", "organization", "profile_picture"]


# ---------------------------------------------------------------------------
# Event series (umbrella) serializers
# ---------------------------------------------------------------------------

class EventSeriesSummarySerializer(serializers.ModelSerializer):
    """Lightweight umbrella reference — nested inside event serializers."""
    class Meta:
        model = EventSeries
        fields = ["id", "name", "slug", "year"]


# ---------------------------------------------------------------------------
# Event serializers
# ---------------------------------------------------------------------------

class EventListSerializer(serializers.ModelSerializer):
    """Lightweight event card for the mobile events list screen."""
    sessions_count = serializers.IntegerField(read_only=True)
    series = EventSeriesSummarySerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "start_date", "end_date",
            "location", "banner_image", "sessions_count", "series",
        ]


class EventSerializer(serializers.ModelSerializer):
    """Full event detail — used on admin API and event detail screen."""
    series = EventSeriesSummarySerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "description",
            "start_date", "end_date", "location", "banner_image", "series",
        ]


# ---------------------------------------------------------------------------
# Session serializers
# ---------------------------------------------------------------------------

class SessionListSerializer(serializers.ModelSerializer):
    """Session row for timetable list — compact, includes speaker summaries."""
    speakers = SpeakerSummarySerializer(many=True, read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Session
        fields = [
            "id", "event", "event_title", "title",
            "start_time", "end_time", "location", "speakers", "kahoot_url",
        ]


class SessionSerializer(serializers.ModelSerializer):
    """Full session detail — includes full speaker objects and slides URL."""
    speakers = SpeakerSerializer(many=True, read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Session
        fields = [
            "id", "event", "event_title", "title", "description",
            "start_time", "end_time", "location", "speakers", "presentation_slides", "kahoot_url",
        ]


# ---------------------------------------------------------------------------
# Other serializers
# ---------------------------------------------------------------------------

class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = [
            "id", "name", "email", "phone_number", "organization", "is_registered",
            "payment_status", "paid_at", "receipt_no", "badge_code", "ticket",
            "event", "registered_at", "email_sent_at",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source="session.title", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "session", "session_title", "text", "created_at"]
