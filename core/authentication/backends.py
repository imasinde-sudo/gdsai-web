from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend to allow users to log in using either their email address or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        lookup = kwargs.get('email', username)
        if not lookup:
            return None
        
        user = User.objects.filter(Q(email__iexact=lookup) | Q(username__iexact=lookup)).first()
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

