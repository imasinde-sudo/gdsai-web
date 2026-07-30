from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.schemas.openapi import SchemaGenerator, AutoSchema
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Count

from .models import Event, Speaker, Session, Attendee, Question, APIKey
from .serializers import (
    EventSerializer, EventListSerializer,
    SpeakerSerializer, SpeakerSummarySerializer,
    SessionSerializer, SessionListSerializer,
    AttendeeSerializer, QuestionSerializer,
)


# ---------------------------------------------------------------------------
# Mobile v1 API Schema — prefixes operationIds to avoid Swagger duplicates
# ---------------------------------------------------------------------------

class MobileV1Schema(AutoSchema):
    """Custom AutoSchema that prefixes all v1 operationIds with 'mobile_'.
    This prevents duplicate operationId warnings when both the admin API
    (/api/speakers/) and the mobile API (/api/v1/speakers/) share the same
    resource name in the OpenAPI schema.
    """
    def get_operation_id(self, path, method):
        return f"mobile_{super().get_operation_id(path, method)}"


# ---------------------------------------------------------------------------
# Admin API — Custom API Key Authentication (unchanged)
# ---------------------------------------------------------------------------

class APIKeyAuthentication(BaseAuthentication):
    """Header-based API key auth for admin/integration consumers."""
    def authenticate(self, request):
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            raise AuthenticationFailed("API key is required in X-API-KEY header.")
        try:
            key_record = APIKey.objects.get(key=api_key, is_active=True)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive API key.")
        return (None, key_record)


# ---------------------------------------------------------------------------
# Admin API Endpoints (protected by X-API-KEY header)
# ---------------------------------------------------------------------------

class EventListCreateAPIView(ListCreateAPIView):
    queryset = Event.objects.all().order_by("start_date")
    serializer_class = EventSerializer
    authentication_classes = [APIKeyAuthentication]


class SpeakerListCreateAPIView(ListCreateAPIView):
    queryset = Speaker.objects.all().order_by("name")
    serializer_class = SpeakerSerializer
    authentication_classes = [APIKeyAuthentication]


class SessionListAPIView(ListAPIView):
    queryset = Session.objects.all().order_by("start_time")
    serializer_class = SessionSerializer
    authentication_classes = [APIKeyAuthentication]


class SessionQuestionAPIView(APIView):
    """
    GET:  List all questions for a session.
    POST: Submit a new question for a session. (Public — no auth required)
    """
    def get(self, request, session_id):
        session = get_object_or_404(Session, pk=session_id)
        questions = session.questions.all().order_by("-created_at")
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request, session_id):
        session = get_object_or_404(Session, pk=session_id)
        text = request.data.get("text")
        if not text:
            return Response(
                {"error": "text field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        question = Question.objects.create(session=session, text=text)
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# API Schema and Swagger views
# ---------------------------------------------------------------------------

def api_schema(request):
    generator = SchemaGenerator(
        title="@iLabAfrica Centre Events API",
        description="API endpoints for managing events, sessions, speakers, and Q&A.",
    )
    schema = generator.get_schema(request=None)
    return JsonResponse(schema)


def swagger_docs(request):
    return render(request, "events/swagger_docs.html")


# ===========================================================================
# Mobile API v1 — Public read-only endpoints (no API key required)
# ===========================================================================

# ---------------------------------------------------------------------------
# v1 Event Views
# ---------------------------------------------------------------------------

class MobileEventListView(ListAPIView):
    """
    GET /api/v1/events/
    Lightweight event list for the mobile events screen.
    Annotates sessions_count so the card can show how many sessions are in the event.
    """
    serializer_class = EventListSerializer
    schema = MobileV1Schema()

    def get_queryset(self):
        return Event.objects.annotate(
            sessions_count=Count("sessions")
        ).order_by("start_date")


class MobileEventDetailView(RetrieveAPIView):
    """
    GET /api/v1/events/<id>/
    Full event details for the mobile event detail screen.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    schema = MobileV1Schema()


class MobileEventSessionsView(ListAPIView):
    """
    GET /api/v1/events/<event_id>/sessions/
    All sessions for a specific event ordered by start time.
    This is the primary endpoint for rendering the in-app timetable schedule.
    """
    serializer_class = SessionListSerializer
    schema = MobileV1Schema()

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        get_object_or_404(Event, pk=event_id)  # Return 404 if event doesn't exist
        return Session.objects.filter(
            event_id=event_id
        ).prefetch_related("speakers").order_by("start_time")


# ---------------------------------------------------------------------------
# v1 Speaker Views
# ---------------------------------------------------------------------------

class MobileSpeakerListView(ListAPIView):
    """
    GET /api/v1/speakers/
    Lightweight speaker directory list for the mobile speakers screen.
    """
    serializer_class = SpeakerSummarySerializer
    queryset = Speaker.objects.all().order_by("name")
    schema = MobileV1Schema()


class MobileSpeakerDetailView(RetrieveAPIView):
    """
    GET /api/v1/speakers/<id>/
    Full speaker profile including their scheduled sessions.
    """
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    schema = MobileV1Schema()


# ---------------------------------------------------------------------------
# v1 Session Views
# ---------------------------------------------------------------------------

class MobileSessionDetailView(RetrieveAPIView):
    """
    GET /api/v1/sessions/<id>/
    Full session detail including speakers and slides download URL.
    """
    queryset = Session.objects.all().prefetch_related("speakers")
    serializer_class = SessionSerializer
    schema = MobileV1Schema()


class MobileSessionQuestionsView(SessionQuestionAPIView):
    """
    GET  /api/v1/sessions/<session_id>/questions/  — List Q&A for a session.
    POST /api/v1/sessions/<session_id>/questions/  — Submit a question (public write).
    Inherits all logic from SessionQuestionAPIView; only the schema is overridden
    to ensure a unique operationId in the OpenAPI/Swagger schema.
    """
    schema = MobileV1Schema()

