from django.db import DatabaseError, connection
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import ApplicationSerializer


class ApplicationCreateView(CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [AllowAny]


def health_check(request):
    try:
        connection.ensure_connection()
    except DatabaseError:
        return JsonResponse({"status": "unavailable", "database": "disconnected"}, status=503)
    return JsonResponse({"status": "ok", "database": "connected"})
