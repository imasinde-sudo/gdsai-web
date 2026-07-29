from django import forms
from django.contrib.auth.models import User
from .models import Speaker, Event, Session, APIKey, Ticket, Attendee


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start_date", "end_date", "location", "banner_image"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. AI Innovation Summit 2026", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Provide a descriptive overview...", "class": "form-input", "rows": 4}),
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Hall C / Online", "class": "form-input"}),
            "banner_image": forms.ClearableFileInput(attrs={"class": "form-input-file"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and end <= start:
            raise forms.ValidationError("End date must be after the start date.")
        return cleaned_data


class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = ["name", "title", "organization", "bio", "email", "profile_picture", "twitter", "linkedin", "website"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Dr. Kalanza", "class": "form-input"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Senior Staff AI Engineer", "class": "form-input"}),
            "organization": forms.TextInput(attrs={"placeholder": "e.g. Google DeepMind", "class": "form-input"}),
            "bio": forms.Textarea(attrs={"placeholder": "Tell us about the speaker's background...", "class": "form-input", "rows": 4}),
            "email": forms.EmailInput(attrs={"placeholder": "e.g. contact@example.com", "class": "form-input"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-input-file"}),
            "twitter": forms.URLInput(attrs={"placeholder": "e.g. https://x.com/username", "class": "form-input"}),
            "linkedin": forms.URLInput(attrs={"placeholder": "e.g. https://linkedin.com/in/username", "class": "form-input"}),
            "website": forms.URLInput(attrs={"placeholder": "e.g. https://example.com", "class": "form-input"}),
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["event", "title", "description", "start_time", "end_time", "location", "speakers", "presentation_slides", "kahoot_url"]
        widgets = {
            "event": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Keynote Presentation", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Provide session details...", "class": "form-input", "rows": 4}),
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Room 104", "class": "form-input"}),
            "speakers": forms.SelectMultiple(attrs={"class": "form-select-multiple"}),
            "presentation_slides": forms.ClearableFileInput(attrs={"class": "form-input-file"}),
            "kahoot_url": forms.URLInput(attrs={"placeholder": "e.g. https://kahoot.it/challenge/...", "class": "form-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after the start time.")
        return cleaned_data


class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Mobile App API Integration", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Specify key usage rules...", "class": "form-input", "rows": 4}),
        }


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First Name", "class": "form-input"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name", "class": "form-input"}),
            "email": forms.EmailInput(attrs={"placeholder": "e.g. admin@eventhub.com", "class": "form-input"}),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["event", "name", "price"]
        widgets = {
            "event": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g. General Admission", "class": "form-input"}),
            "price": forms.NumberInput(attrs={"placeholder": "e.g. 29.99", "class": "form-input", "step": "0.01"}),
        }


class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ["name", "email", "phone_number", "is_registered", "payment_status", "paid_at", "ticket", "event"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Jane Doe", "class": "form-input"}),
            "email": forms.EmailInput(attrs={"placeholder": "e.g. jane@example.com", "class": "form-input"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "e.g. +1234567890", "class": "form-input"}),
            "is_registered": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "payment_status": forms.Select(attrs={"class": "form-select"}),
            "paid_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input", "required": False}),
            "ticket": forms.Select(attrs={"class": "form-select"}),
            "event": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        payment_status = cleaned_data.get("payment_status")
        paid_at = cleaned_data.get("paid_at")
        
        # If paid and no timestamp provided, auto-set to now
        from django.utils import timezone
        if payment_status == "PAID" and not paid_at:
            cleaned_data["paid_at"] = timezone.now()
        elif payment_status == "UNPAID":
            cleaned_data["paid_at"] = None
            
        return cleaned_data
