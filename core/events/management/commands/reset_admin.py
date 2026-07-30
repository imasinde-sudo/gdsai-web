from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Resets or creates the admin superuser with username 'admin' and password 'admin'"

    def handle(self, *args, **options):
        User = get_user_model()
        
        # 1. User with username='admin'
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@gdsai.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        user.set_password('admin')
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        # 2. User with email='admin' in case email lookup is used
        email_user, _ = User.objects.get_or_create(
            email='admin',
            defaults={
                'username': 'admin_email',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        email_user.set_password('admin')
        email_user.is_staff = True
        email_user.is_superuser = True
        email_user.is_active = True
        email_user.save()

        # 3. Ensure all superusers have password 'admin'
        for su in User.objects.filter(is_superuser=True):
            su.set_password('admin')
            su.is_active = True
            su.save()

        self.stdout.write(self.style.SUCCESS("Successfully configured superuser admin with password 'admin'."))
