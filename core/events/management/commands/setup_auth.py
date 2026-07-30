import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Cleans up existing users and provisions a fresh superuser and authentication system."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "admin@gdsai.com")
        password = os.environ.get("ADMIN_PASSWORD", "admin")

        self.stdout.write(self.style.WARNING("Performing clean slate authentication setup..."))

        # Delete existing superusers or admin users to guarantee clean slate
        deleted_count, _ = User.objects.filter(is_superuser=True).delete()
        self.stdout.write(f"Removed {deleted_count} stale superuser account(s).")

        # Create/reset primary superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created fresh superuser '{username}' ({email})."
            )
        )
