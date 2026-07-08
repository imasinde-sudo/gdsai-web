from django import forms
from .models import Speaker, Event, Session, APIKey

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
        fields = ["event", "title", "description", "start_time", "end_time", "location", "speakers", "presentation_slides"]
        widgets = {
            "event": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Keynote Presentation", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Provide session details...", "class": "form-input", "rows": 4}),
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Room 104", "class": "form-input"}),
            "speakers": forms.SelectMultiple(attrs={"class": "form-select-multiple"}),
            "presentation_slides": forms.ClearableFileInput(attrs={"class": "form-input-file"}),
        }

class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Mobile App API Integration", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Specify key usage rules...", "class": "form-input", "rows": 4}),
        }
