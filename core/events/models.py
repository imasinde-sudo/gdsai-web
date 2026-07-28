from django.db import models
import secrets

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
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, help_text="e.g. Auditorium A, or Online")
    banner_image = models.ImageField(upload_to="events/", blank=True, null=True)

    def __str__(self):
        return self.title


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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Attendee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    is_registered = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=10,
        choices=[('PAID', 'Paid'), ('UNPAID', 'Unpaid')],
        default='UNPAID'
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendees")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees", null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

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
