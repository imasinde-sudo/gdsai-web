from django.urls import path
from . import views
from . import api_views

app_name = "events"

urlpatterns = [
    path("auth-diag/", views.auth_diagnostic, name="auth_diagnostic"),  # TEMPORARY
    path("", views.landing_page, name="landing_page"),
    path("schedule/pdf/", views.download_timetable_pdf, name="download_timetable_pdf"),
    path("series/", views.series_list, name="series_list"),
    path("series/<slug:slug>/", views.series_detail, name="series_detail"),
    path("events/", views.event_list, name="event_list"),

    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("events/<int:event_id>/register/", views.event_register, name="event_register"),
    path("register/success/<str:badge_code>/", views.registration_success, name="registration_success"),
    path("badges/<str:badge_code>/", views.badge_verify, name="badge_verify"),
    path("badges/<str:badge_code>/image.png", views.badge_image, name="badge_image"),
    path("badges/<str:badge_code>/download/", views.badge_download, name="badge_download"),
    path("speakers/<int:speaker_id>/", views.speaker_detail, name="speaker_detail"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("system-status/", views.system_status, name="system_status"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Event Series (umbrella) CRUD
    path("dashboard/series/add/", views.series_create, name="series_create"),
    path("dashboard/series/<int:series_id>/edit/", views.series_edit, name="series_edit"),
    path("dashboard/series/<int:series_id>/delete/", views.series_delete, name="series_delete"),

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

    # Ticket CRUD
    path("dashboard/tickets/add/", views.ticket_create, name="ticket_create"),
    path("dashboard/tickets/<int:ticket_id>/edit/", views.ticket_edit, name="ticket_edit"),
    path("dashboard/tickets/<int:ticket_id>/delete/", views.ticket_delete, name="ticket_delete"),

    # Attendee CRUD
    path("dashboard/attendees/add/", views.attendee_create, name="attendee_create"),
    path("dashboard/attendees/<int:attendee_id>/edit/", views.attendee_edit, name="attendee_edit"),
    path("dashboard/attendees/<int:attendee_id>/delete/", views.attendee_delete, name="attendee_delete"),

    # Admin Profile
    path("dashboard/profile/", views.profile_view, name="profile_view"),

    # API REST Endpoints (Admin — protected by X-API-KEY header)
    path("api/events/", api_views.EventListCreateAPIView.as_view(), name="api_events"),
    path("api/speakers/", api_views.SpeakerListCreateAPIView.as_view(), name="api_speakers"),
    path("api/sessions/", api_views.SessionListAPIView.as_view(), name="api_sessions"),
    path("api/sessions/<int:session_id>/questions/", api_views.SessionQuestionAPIView.as_view(), name="api_session_questions"),
    path("api/schema/", api_views.api_schema, name="api_schema"),
    path("api/docs/", api_views.swagger_docs, name="api_docs"),

    # Mobile API v1 — Public read-only content endpoints
    path("api/v1/events/", api_views.MobileEventListView.as_view(), name="v1_event_list"),
    path("api/v1/events/<int:pk>/", api_views.MobileEventDetailView.as_view(), name="v1_event_detail"),
    path("api/v1/events/<int:event_id>/sessions/", api_views.MobileEventSessionsView.as_view(), name="v1_event_sessions"),
    path("api/v1/speakers/", api_views.MobileSpeakerListView.as_view(), name="v1_speaker_list"),
    path("api/v1/speakers/<int:pk>/", api_views.MobileSpeakerDetailView.as_view(), name="v1_speaker_detail"),
    path("api/v1/sessions/<int:pk>/", api_views.MobileSessionDetailView.as_view(), name="v1_session_detail"),
    path("api/v1/sessions/<int:session_id>/questions/", api_views.MobileSessionQuestionsView.as_view(), name="v1_session_questions"),
]

