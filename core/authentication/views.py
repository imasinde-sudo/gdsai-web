from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserSerializer, EmailTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    """
    Endpoint for user registration.
    """
    queryset = RegisterSerializer.Meta.model.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        
        # Optionally, generate tokens immediately upon registration
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            "user": user_data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

class LogoutView(APIView):
    """
    Endpoint to blacklist a refresh token, effectively logging the user out.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Invalid or missing token."}, status=status.HTTP_400_BAD_REQUEST)

class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint that accepts 'email' instead of 'username'.
    Returns JWT access and refresh tokens on successful authentication.
    """
    serializer_class = EmailTokenObtainPairSerializer