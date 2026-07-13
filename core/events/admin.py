from django.contrib import admin
from .models import Speaker, Event, Session, APIKey, Question, Attendee


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


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    readonly_fields = ("key", "created_at")


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "event", "registered_at")
    search_fields = ("name", "email")
    list_filter = ("event",)
    readonly_fields = ("registered_at",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("session", "text", "created_at")
    list_filter = ("session__event", "session")
    search_fields = ("text",)
    readonly_fields = ("created_at",)
