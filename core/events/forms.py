from django import forms
from django.contrib.auth.models import User
from .models import Speaker, Event, EventSeries, Session, APIKey, Ticket, Attendee, Sponsor, Organisation


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["series", "title", "description", "start_date", "end_date", "location", "banner_image"]
        widgets = {
            "series": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Conference", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Provide a descriptive overview...", "class": "form-input", "rows": 4}),
            "start_date": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={"type": "datetime-local", "step": "1", "class": "form-input"}),
            "end_date": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={"type": "datetime-local", "step": "1", "class": "form-input"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Hall C / Online", "class": "form-input"}),
            "banner_image": forms.ClearableFileInput(attrs={"class": "form-input-file"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["series"].queryset = EventSeries.objects.order_by("-year", "name")
        self.fields["series"].required = False

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and end <= start:
            raise forms.ValidationError("End date must be after the start date.")
        return cleaned_data


class EventSeriesForm(forms.ModelForm):
    class Meta:
        model = EventSeries
        fields = ["name", "slug", "year", "tagline", "description", "banner_image", "is_current"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. GDSAI 2026", "class": "form-input"}),
            "slug": forms.TextInput(attrs={"placeholder": "e.g. gdsai-2026 (auto-filled if left blank)", "class": "form-input"}),
            "year": forms.NumberInput(attrs={"placeholder": "e.g. 2026", "class": "form-input"}),
            "tagline": forms.TextInput(attrs={"placeholder": "e.g. Where research, innovation and enterprise meet.", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Provide an overview of this year's umbrella brand...", "class": "form-input", "rows": 4}),
            "banner_image": forms.ClearableFileInput(attrs={"class": "form-input-file"}),
            "is_current": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False


class OrganisationForm(forms.ModelForm):
    """Admin-side create/edit of an organisation registration record itself."""

    class Meta:
        model = Organisation
        fields = ["event", "name", "contact_email", "localisation", "registration_option"]
        widgets = {
            "event": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g. Strathmore University", "class": "form-input"}),
            "contact_email": forms.EmailInput(attrs={"placeholder": "e.g. contact@strathmore.edu", "class": "form-input"}),
            "localisation": forms.Select(attrs={"class": "form-select"}),
            "registration_option": forms.Select(attrs={"class": "form-select"}),
        }


class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = ["name", "logo", "website_url", "tier", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Acme Corp", "class": "form-input"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-input-file"}),
            "website_url": forms.URLInput(attrs={"placeholder": "e.g. https://acme.example.com", "class": "form-input"}),
            "tier": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
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
        fields = ["event", "title", "description", "start_time", "end_time", "location", "speakers", "presentation_slides", "kahoot_url"]
        widgets = {
            "event": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Keynote Presentation", "class": "form-input"}),
            "description": forms.Textarea(attrs={"placeholder": "Provide session details...", "class": "form-input", "rows": 4}),
            "start_time": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={"type": "datetime-local", "step": "1", "class": "form-input"}),
            "end_time": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={"type": "datetime-local", "step": "1", "class": "form-input"}),

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
            "email": forms.EmailInput(attrs={"placeholder": "e.g. admin@ilabafrica.strathmore.edu", "class": "form-input"}),
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
        fields = ["name", "email", "phone_number", "organization", "organisation", "is_registered", "payment_status", "paid_at", "ticket", "event"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Jane Doe", "class": "form-input"}),
            "email": forms.EmailInput(attrs={"placeholder": "e.g. jane@example.com", "class": "form-input"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "e.g. +1234567890", "class": "form-input"}),
            "organization": forms.TextInput(attrs={"placeholder": "e.g. Strathmore University", "class": "form-input"}),
            "organisation": forms.Select(attrs={"class": "form-select"}),
            "is_registered": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "payment_status": forms.Select(attrs={"class": "form-select"}),
            "paid_at": forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={"type": "datetime-local", "step": "1", "class": "form-input", "required": False}),

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


class EventRegistrationForm(forms.Form):
    """Public self-service registration — no payment step."""

    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Full name", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com", "autocomplete": "email"}),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "+254 …", "autocomplete": "tel"}),
    )
    organization = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Organisation (optional)"}),
    )
    ticket = forms.ModelChoiceField(
        queryset=Ticket.objects.none(),
        empty_label=None,
        widget=forms.RadioSelect(attrs={"class": "ticket-radio"}),
    )

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        if event is not None:
            self.fields["ticket"].queryset = Ticket.objects.filter(event=event).order_by("price", "name")
            if self.fields["ticket"].queryset.count() == 1:
                self.fields["ticket"].initial = self.fields["ticket"].queryset.first()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if self.event and Attendee.objects.filter(event=self.event, email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered for this event. "
                "Check your inbox for your badge, or contact the organisers."
            )
        return email

    def clean_ticket(self):
        ticket = self.cleaned_data["ticket"]
        if self.event and ticket.event_id != self.event.id:
            raise forms.ValidationError("Please select a ticket for this event.")
        return ticket


class OrganisationRegistrationForm(forms.ModelForm):
    """Public self-service group registration — the organisation-level fields."""

    class Meta:
        model = Organisation
        fields = ["name", "contact_email", "localisation", "registration_option"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Organisation / institution name"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "contact@organisation.com", "autocomplete": "email"}),
            "localisation": forms.RadioSelect(attrs={"class": "localisation-radio"}),
            "registration_option": forms.RadioSelect(attrs={"class": "registration-option-radio"}),
        }

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

    def clean_contact_email(self):
        contact_email = self.cleaned_data["contact_email"].strip().lower()
        if self.event and Organisation.objects.filter(event=self.event, contact_email__iexact=contact_email).exists():
            raise forms.ValidationError(
                "An organisation has already registered with this contact email for this event."
            )
        return contact_email


class OrgAttendeeForm(forms.Form):
    """One row in the organisation registration's attendee formset.

    All fields are optional at the field level so a blank trailing row (used
    to let an organisation register more than the minimum without needing
    JavaScript to add rows) doesn't raise errors — clean() enforces that a
    row with *any* data in it has all of name/email/ticket filled in.
    """

    name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Full name"}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com"}),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "+254 … (optional)"}),
    )
    ticket = forms.ModelChoiceField(
        queryset=Ticket.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        if event is not None:
            self.fields["ticket"].queryset = Ticket.objects.filter(event=event).order_by("price", "name")

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        email = cleaned_data.get("email")
        ticket = cleaned_data.get("ticket")

        if not any([name, email, ticket]):
            # Fully blank row — a spare slot the organisation didn't need.
            return cleaned_data

        if not name:
            self.add_error("name", "Name is required.")
        if not email:
            self.add_error("email", "Email is required.")
        if not ticket:
            self.add_error("ticket", "Please select a ticket.")
        elif self.event and ticket.event_id != self.event.id:
            self.add_error("ticket", "Please select a ticket for this event.")

        if email and self.event and Attendee.objects.filter(event=self.event, email__iexact=email).exists():
            self.add_error("email", "This email is already registered for this event.")

        return cleaned_data


class BaseOrgAttendeeFormSet(forms.BaseFormSet):
    """Enforces the spec's 'minimum block of 5 people' rule across the formset."""

    MIN_ATTENDEES = 5

    def clean(self):
        if any(self.errors):
            return
        filled_forms = [form for form in self.forms if form.cleaned_data]
        if len(filled_forms) < self.MIN_ATTENDEES:
            raise forms.ValidationError(
                f"Organisation registration requires a minimum of {self.MIN_ATTENDEES} people "
                f"— you've filled in {len(filled_forms)}."
            )
        emails = [
            form.cleaned_data["email"].strip().lower()
            for form in filled_forms
            if form.cleaned_data.get("email")
        ]
        if len(emails) != len(set(emails)):
            raise forms.ValidationError("Each person in the group must have a unique email address.")


OrgAttendeeFormSet = forms.formset_factory(
    OrgAttendeeForm,
    formset=BaseOrgAttendeeFormSet,
    extra=10,
)
