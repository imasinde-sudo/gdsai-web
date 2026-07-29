from rest_framework import serializers
from .models import Event, Speaker, Session, Attendee, Question


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
# Event serializers
# ---------------------------------------------------------------------------

class EventListSerializer(serializers.ModelSerializer):
    """Lightweight event card for the mobile events list screen."""
    sessions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "start_date", "end_date",
            "location", "banner_image", "sessions_count",
        ]


class EventSerializer(serializers.ModelSerializer):
    """Full event detail — used on admin API and event detail screen."""
    class Meta:
        model = Event
        fields = [
            "id", "title", "description",
            "start_date", "end_date", "location", "banner_image",
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
        fields = ["id", "name", "email", "phone_number", "is_registered", "payment_status", "paid_at", "receipt_no", "ticket", "event", "registered_at"]


class QuestionSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source="session.title", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "session", "session_title", "text", "created_at"]
