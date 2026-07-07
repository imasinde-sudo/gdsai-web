from django.db import models

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

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.title} ({self.event.title})"
