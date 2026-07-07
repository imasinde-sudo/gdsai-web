from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("events/", views.event_list, name="event_list"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("speakers/<int:speaker_id>/", views.speaker_detail, name="speaker_detail"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("system-status/", views.system_status, name="system_status"),
]
