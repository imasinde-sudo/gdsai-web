from django.contrib import admin
from .models import Speaker, Event, Session

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "organization", "email")
    search_fields = ("name", "title", "organization", "bio")
    list_filter = ("organization",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "location")
    search_fields = ("title", "description", "location")
    list_filter = ("start_date", "location")
    ordering = ("start_date",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "start_time", "end_time", "location")
    search_fields = ("title", "description", "location", "event__title")
    list_filter = ("event", "start_time", "location")
    filter_horizontal = ("speakers",)
    ordering = ("start_time",)
