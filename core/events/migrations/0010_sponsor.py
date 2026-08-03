# Generated manually for the Sponsor model (Home Page sponsors section)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0009_seed_gdsai_2026_series"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sponsor",
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
                ("name", models.CharField(max_length=255)),
                (
                    "logo",
                    models.ImageField(blank=True, null=True, upload_to="sponsors/"),
                ),
                (
                    "website_url",
                    models.URLField(help_text="Link-through to the sponsor's site"),
                ),
                (
                    "tier",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("PLATINUM", "Platinum"),
                            ("GOLD", "Gold"),
                            ("PARTNER", "Partner"),
                        ],
                        help_text="Optional — higher tiers get a larger logo placement on the home page",
                        max_length=10,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Uncheck to hide from the home page without deleting",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
