from django.urls import path
from . import views
from . import api_views

app_name = "events"

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("events/", views.event_list, name="event_list"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("speakers/<int:speaker_id>/", views.speaker_detail, name="speaker_detail"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("system-status/", views.system_status, name="system_status"),
    path("login/", views.login_view, name="login"),
    
    # Event CRUD
    path("dashboard/events/add/", views.event_create, name="event_create"),
    path("dashboard/events/<int:event_id>/edit/", views.event_edit, name="event_edit"),
    path("dashboard/events/<int:event_id>/delete/", views.event_delete, name="event_delete"),
    
    # Speaker CRUD
    path("dashboard/speakers/add/", views.speaker_create, name="speaker_create"),
    path("dashboard/speakers/<int:speaker_id>/edit/", views.speaker_edit, name="speaker_edit"),
    path("dashboard/speakers/<int:speaker_id>/delete/", views.speaker_delete, name="speaker_delete"),
    
    # Session CRUD
    path("dashboard/sessions/add/", views.session_create, name="session_create"),
    path("dashboard/sessions/<int:session_id>/edit/", views.session_edit, name="session_edit"),
    path("dashboard/sessions/<int:session_id>/delete/", views.session_delete, name="session_delete"),

    # API Keys Admin Control
    path("dashboard/apikeys/add/", views.apikey_create, name="apikey_create"),
    path("dashboard/apikeys/<int:key_id>/delete/", views.apikey_delete, name="apikey_delete"),

    # Questions Admin Moderation
    path("dashboard/questions/<int:question_id>/delete/", views.question_delete, name="question_delete"),

    # Admin Profile
    path("dashboard/profile/", views.profile_view, name="profile_view"),

    # API REST Endpoints
    path("api/events/", api_views.EventListCreateAPIView.as_view(), name="api_events"),
    path("api/speakers/", api_views.SpeakerListCreateAPIView.as_view(), name="api_speakers"),
    path("api/sessions/", api_views.SessionListAPIView.as_view(), name="api_sessions"),
    path("api/sessions/<int:session_id>/questions/", api_views.SessionQuestionAPIView.as_view(), name="api_session_questions"),
    path("api/schema/", api_views.api_schema, name="api_schema"),
    path("api/docs/", api_views.swagger_docs, name="api_docs"),
]
