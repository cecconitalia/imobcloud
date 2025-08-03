# C:\wamp64\www\ImobCloud\core\views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer # Certifique-se de que core/serializers.py existe e está correto

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated] # Exige que o usuário esteja autenticado

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)