from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.schemas.openapi import SchemaGenerator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Event, Speaker, Session, Attendee, Question, APIKey
from .serializers import EventSerializer, SpeakerSerializer, SessionSerializer, AttendeeSerializer, QuestionSerializer


# Custom API Key Authentication
class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            # Allow Swagger schema view to be accessed freely, or other public requests
            # In our case, we protect regular resource endpoints.
            raise AuthenticationFailed("API key is required in X-API-KEY header.")
        
        try:
            key_record = APIKey.objects.get(key=api_key, is_active=True)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive API key.")
        
        return (None, key_record)


# API Endpoints
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
    GET: List all questions asked for a session.
    POST: Submit a new question for a session. (Public endpoint, no API key required for attendees)
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
            return Response({"error": "text field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        question = Question.objects.create(session=session, text=text)
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# API Schema and Swagger views
def api_schema(request):
    generator = SchemaGenerator(title="EventHub Platform API", description="API endpoints for managing events, sessions, speakers, and Q&A.")
    schema = generator.get_schema(request=None)
    return JsonResponse(schema)


def swagger_docs(request):
    return render(request, "events/swagger_docs.html")
