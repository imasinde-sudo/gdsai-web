# Generated manually for registration / badge fields

from django.db import migrations, models
import uuid


def backfill_badge_codes(apps, schema_editor):
    Attendee = apps.get_model("events", "Attendee")
    for attendee in Attendee.objects.all():
        if not attendee.badge_code:
            attendee.badge_code = uuid.uuid4().hex[:16].upper()
            if attendee.is_registered and not attendee.receipt_no:
                attendee.receipt_no = f"ILAB-{attendee.badge_code}"
            attendee.save(update_fields=["badge_code", "receipt_no"])


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0006_ticket_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendee",
            name="organization",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="attendee",
            name="badge_code",
            field=models.CharField(blank=True, editable=False, max_length=32),
        ),
        migrations.AddField(
            model_name="attendee",
            name="badge_image",
            field=models.ImageField(blank=True, null=True, upload_to="badges/"),
        ),
        migrations.AddField(
            model_name="attendee",
            name="email_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_badge_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="attendee",
            name="badge_code",
            field=models.CharField(blank=True, editable=False, max_length=32, unique=True),
        ),
        migrations.AddConstraint(
            model_name="attendee",
            constraint=models.UniqueConstraint(
                fields=("event", "email"),
                name="unique_attendee_email_per_event",
            ),
        ),
    ]
