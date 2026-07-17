import uuid
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Generate a unique username since the default User model requires one
        username = str(uuid.uuid4())[:30]
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that accepts 'email' instead of 'username'
    as the login credential field.

    Setting username_field = 'email' causes the parent class to declare
    the input field as 'email' automatically, so no __init__ override is needed.
    The validate() method authenticates via the EmailAuthBackend which accepts
    an email kwarg.
    """
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if user is None:
            raise AuthenticationFailed(
                "No active account found with the given credentials",
                "no_active_account",
            )

        self.user = user
        refresh = self.get_token(self.user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
