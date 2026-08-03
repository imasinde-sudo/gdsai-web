# Generated manually — seed the GDSAI 2026 umbrella and nest existing events under it

from django.db import migrations


GDSAI_2026_EVENT_TITLES = [
    "GDSAI Summit 2026",
    "Masterclass",
]


def seed_series(apps, schema_editor):
    EventSeries = apps.get_model("events", "EventSeries")
    Event = apps.get_model("events", "Event")

    series, _ = EventSeries.objects.get_or_create(
        slug="gdsai-2026",
        defaults={
            "name": "GDSAI 2026",
            "year": 2026,
            "tagline": "Where research, innovation and enterprise meet.",
            "is_current": True,
        },
    )

    for title in GDSAI_2026_EVENT_TITLES:
        Event.objects.filter(title__iexact=title, series__isnull=True).update(series=series)


def unseed_series(apps, schema_editor):
    EventSeries = apps.get_model("events", "EventSeries")
    Event = apps.get_model("events", "Event")

    series = EventSeries.objects.filter(slug="gdsai-2026").first()
    if series is not None:
        Event.objects.filter(series=series).update(series=None)
        series.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0008_eventseries_event_series"),
    ]

    operations = [
        migrations.RunPython(seed_series, unseed_series),
    ]
