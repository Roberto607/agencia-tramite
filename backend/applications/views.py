from django.db import DatabaseError, connection
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .serializers import ApplicationSerializer, ClientRegistrationSerializer


class ApplicationCreateView(CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]


class ClientRegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ClientRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key},
            status=status.HTTP_201_CREATED,
        )


def health_check(request):
    try:
        connection.ensure_connection()
    except DatabaseError:
        return JsonResponse({"status": "unavailable", "database": "disconnected"}, status=503)
    return JsonResponse({"status": "ok", "database": "connected"})
