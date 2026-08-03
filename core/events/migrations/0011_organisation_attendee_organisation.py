# Generated manually for the Organisation Registration path

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0010_sponsor"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organisation",
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
                ("name", models.CharField(max_length=255, verbose_name="Organisation name")),
                (
                    "contact_email",
                    models.EmailField(
                        help_text="Primary point of contact for the group", max_length=254
                    ),
                ),
                (
                    "localisation",
                    models.CharField(
                        choices=[("LOCAL", "Local"), ("INTERNATIONAL", "International")],
                        max_length=20,
                    ),
                ),
                (
                    "registration_option",
                    models.CharField(
                        choices=[
                            ("PAY_NOW", "Pay now"),
                            ("INVITATION_LETTER", "Request invitation letter"),
                        ],
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organisations",
                        to="events.event",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="attendee",
            name="organisation",
            field=models.ForeignKey(
                blank=True,
                help_text="Set when this attendee was registered as part of a group/organisation registration",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="attendees",
                to="events.organisation",
            ),
        ),
        migrations.AddConstraint(
            model_name="organisation",
            constraint=models.UniqueConstraint(
                fields=("event", "contact_email"),
                name="unique_organisation_contact_email_per_event",
            ),
        ),
    ]
