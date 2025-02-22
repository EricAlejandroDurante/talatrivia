from django.contrib.auth.models import User

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status

from .serializers import UserSerializer

class UserCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        user_data = [{"username": user.username, "email": user.email} for user in users]
        return Response(user_data, status=status.HTTP_200_OK)