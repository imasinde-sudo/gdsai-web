from django.db import models
from django.utils.text import slugify
import secrets
import uuid


class EventSeries(models.Model):
    name = models.CharField(max_length=255, help_text="e.g. GDSAI 2026")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    year = models.PositiveIntegerField(help_text="e.g. 2026")
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    banner_image = models.ImageField(upload_to="series/", blank=True, null=True)
    is_current = models.BooleanField(default=False, help_text="Show as the featured umbrella on the landing page")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Event series"
        ordering = ["-year"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Speaker(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, help_text="e.g. Senior Software Engineer")
    organization = models.CharField(max_length=255, blank=True, help_text="e.g. Google")
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    profile_picture = models.ImageField(upload_to="speakers/", blank=True, null=True)
    twitter = models.URLField(blank=True, verbose_name="Twitter / X URL")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn URL")
    website = models.URLField(blank=True, verbose_name="Personal Website URL")

    def __str__(self):
        return f"{self.name} ({self.organization})" if self.organization else self.name


class Event(models.Model):
    series = models.ForeignKey(
        EventSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="events"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, help_text="e.g. Auditorium A, or Online")
    banner_image = models.ImageField(upload_to="events/", blank=True, null=True)

    def __str__(self):
        return self.title


class Organisation(models.Model):
    LOCAL = "LOCAL"
    INTERNATIONAL = "INTERNATIONAL"
    LOCALISATION_CHOICES = [
        (LOCAL, "Local"),
        (INTERNATIONAL, "International"),
    ]

    PAY_NOW = "PAY_NOW"
    INVITATION_LETTER = "INVITATION_LETTER"
    REGISTRATION_OPTION_CHOICES = [
        (PAY_NOW, "Pay now"),
        (INVITATION_LETTER, "Request invitation letter"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="organisations")
    name = models.CharField(max_length=255, verbose_name="Organisation name")
    contact_email = models.EmailField(help_text="Primary point of contact for the group")
    localisation = models.CharField(max_length=20, choices=LOCALISATION_CHOICES)
    registration_option = models.CharField(max_length=20, choices=REGISTRATION_OPTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "contact_email"],
                name="unique_organisation_contact_email_per_event",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.event.title})"


class Session(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sessions")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, help_text="Specific room or venue section")
    speakers = models.ManyToManyField(Speaker, related_name="sessions", blank=True)
    presentation_slides = models.FileField(upload_to="slides/", blank=True, null=True)
    kahoot_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to external Kahoot or Slido quiz")

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.title} ({self.event.title})"

class Ticket(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Attendee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    is_registered = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=10,
        choices=[('PAID', 'Paid'), ('UNPAID', 'Unpaid')],
        default='UNPAID'
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_no = models.CharField(max_length=100, blank=True, null=True)
    badge_code = models.CharField(max_length=32, unique=True, blank=True, editable=False)
    badge_image = models.ImageField(upload_to="badges/", blank=True, null=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendees")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees", null=True, blank=True)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendees",
        help_text="Set when this attendee was registered as part of a group/organisation registration",
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "email"],
                name="unique_attendee_email_per_event",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.badge_code:
            self.badge_code = uuid.uuid4().hex[:16].upper()
        if not self.receipt_no and self.is_registered:
            self.receipt_no = f"ILAB-{self.badge_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — {self.email}"


class APIKey(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.key[:8]}...)"


class Question(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q for {self.session.title}: {self.text[:30]}..."


class Sponsor(models.Model):
    TIER_PLATINUM = "PLATINUM"
    TIER_GOLD = "GOLD"
    TIER_PARTNER = "PARTNER"
    TIER_CHOICES = [
        (TIER_PLATINUM, "Platinum"),
        (TIER_GOLD, "Gold"),
        (TIER_PARTNER, "Partner"),
    ]

    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="sponsors/", blank=True, null=True)
    website_url = models.URLField(help_text="Link-through to the sponsor's site")
    tier = models.CharField(
        max_length=10,
        choices=TIER_CHOICES,
        blank=True,
        help_text="Optional — higher tiers get a larger logo placement on the home page",
    )
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide from the home page without deleting")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})" if self.tier else self.name
