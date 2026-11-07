from django.contrib.auth import authenticate, get_user_model
from django.db import DatabaseError, connection
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import ClientProfile
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


class ClientLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        if not isinstance(email, str) or not isinstance(password, str) or not email.strip() or not password:
            return Response(
                {"detail": "Escribe tu correo electrónico y contraseña."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = email.strip()

        user_model = get_user_model()
        try:
            user = user_model.objects.get(email__iexact=email)
        except user_model.DoesNotExist:
            user = None

        if user is None:
            authenticated_user = None
        else:
            authenticated_user = authenticate(
                request,
                **{
                    user_model.USERNAME_FIELD: user.get_username(),
                    "password": password,
                },
            )
        if authenticated_user is None:
            return Response(
                {"detail": "El correo electrónico o la contraseña no son correctos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            profile = authenticated_user.client_profile
        except ClientProfile.DoesNotExist:
            return Response(
                {"detail": "El correo electrónico o la contraseña no son correctos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _created = Token.objects.get_or_create(user=authenticated_user)
        return Response(
            {
                "token": token.key,
                "profile": {
                    "first_names": authenticated_user.first_name,
                    "last_names": authenticated_user.last_name,
                    "identification_type": profile.identification_type,
                    "identification_number": profile.identification_number,
                    "country": profile.country,
                    "phone": profile.phone,
                    "email": authenticated_user.email,
                },
            }
        )


def health_check(request):
    try:
        connection.ensure_connection()
    except DatabaseError:
        return JsonResponse({"status": "unavailable", "database": "disconnected"}, status=503)
    return JsonResponse({"status": "ok", "database": "connected"})
