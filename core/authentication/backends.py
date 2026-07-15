from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend to allow users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # We can accept either username or email in the 'username' parameter
        email = kwargs.get('email', username)
        if not email:
            return None
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
