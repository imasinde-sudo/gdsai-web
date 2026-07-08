from rest_framework import serializers
from .models import Event, Speaker, Session, Attendee, Question

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ["id", "name", "title", "organization", "bio", "email", "profile_picture", "twitter", "linkedin", "website"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "description", "start_date", "end_date", "location", "banner_image"]


class SessionSerializer(serializers.ModelSerializer):
    speakers = SpeakerSerializer(many=True, read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Session
        fields = ["id", "event", "event_title", "title", "description", "start_time", "end_time", "location", "speakers", "presentation_slides"]


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ["id", "name", "email", "event", "registered_at"]


class QuestionSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source="session.title", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "session", "session_title", "text", "created_at"]
