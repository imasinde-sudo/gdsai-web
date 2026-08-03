# Generated manually for the EventSeries umbrella (nest events under a year brand)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0007_attendee_registration_badge"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventSeries",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(help_text="e.g. GDSAI 2026", max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255, unique=True)),
                ("year", models.PositiveIntegerField(help_text="e.g. 2026")),
                ("tagline", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "banner_image",
                    models.ImageField(blank=True, null=True, upload_to="series/"),
                ),
                (
                    "is_current",
                    models.BooleanField(
                        default=False,
                        help_text="Show as the featured umbrella on the landing page",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Event series",
                "ordering": ["-year"],
            },
        ),
        migrations.AddField(
            model_name="event",
            name="series",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="events",
                to="events.eventseries",
            ),
        ),
    ]
