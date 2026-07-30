from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "events"

    def ready(self):
        import sys
        if "migrate" in sys.argv or "collectstatic" in sys.argv or "test" in sys.argv:
            return
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # 1. Update/create username='admin'
            user, _ = User.objects.get_or_create(
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

            # 2. Update/create email='admin'
            email_user, _ = User.objects.get_or_create(
                email='admin',
                defaults={
                    'username': 'admin_email_user',
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
        except Exception:
            pass

