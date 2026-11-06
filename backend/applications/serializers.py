from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from .models import (
    Application,
    ApplicationDocument,
    ApplicationFileType,
    ClientProfile,
)


class ClientRegistrationSerializer(serializers.Serializer):
    first_names = serializers.CharField(max_length=120)
    last_names = serializers.CharField(max_length=120)
    identification_type = serializers.ChoiceField(choices=Application._meta.get_field("identification_type").choices)
    identification_number = serializers.CharField(max_length=40)
    phone = serializers.CharField(max_length=40)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False, min_length=8)

    def validate_email(self, value):
        email = value.strip().lower()
        user_model = get_user_model()
        username_field = user_model.USERNAME_FIELD
        if user_model.objects.filter(
            Q(email__iexact=email) | Q(**{f"{username_field}__iexact": email})
        ).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error
        return value

    @transaction.atomic
    def create(self, validated_data):
        user_model = get_user_model()
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        first_names = validated_data.pop("first_names")
        last_names = validated_data.pop("last_names")
        user = user_model.objects.create_user(
            **{
                user_model.USERNAME_FIELD: email,
                "email": email,
                "first_name": first_names,
                "last_name": last_names,
                "password": password,
            }
        )
        ClientProfile.objects.create(user=user, **validated_data)
        return user


class ApplicationSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True, write_only=True)
    selected_services = serializers.JSONField(required=False)
    selected_options = serializers.JSONField(required=False)
    documents = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            "id",
            "first_names",
            "last_names",
            "identification_type",
            "identification_number",
            "email",
            "phone",
            "service_type",
            "selected_services",
            "selected_options",
            "other_service",
            "photo",
            "created_at",
            "document_count",
            "documents",
        )
        read_only_fields = ("id", "created_at", "document_count")

    def validate(self, attrs):
        selected_services = attrs.get("selected_services")
        if selected_services is None:
            selected_services = [attrs.get("service_type", Application._meta.get_field("service_type").default)]
        if (
            not isinstance(selected_services, list)
            or not selected_services
            or any(not isinstance(service, str) for service in selected_services)
        ):
            raise serializers.ValidationError(
                {"selected_services": "Selecciona al menos un trámite válido."}
            )

        valid_services = {value for value, _label in Application._meta.get_field("service_type").choices}
        invalid_services = [service for service in selected_services if service not in valid_services]
        if invalid_services:
            raise serializers.ValidationError(
                {"selected_services": "La selección contiene un trámite no válido."}
            )

        selected_services = list(dict.fromkeys(selected_services))
        attrs["selected_services"] = selected_services
        attrs["service_type"] = selected_services[0]

        selected_options = attrs.get("selected_options", [])
        if not isinstance(selected_options, list) or any(
            not isinstance(option, dict)
            or not isinstance(option.get("service"), str)
            or option["service"] not in selected_services
            or any(
                not isinstance(option.get(field), str)
                for field in ("service_label", "group", "option", "time")
            )
            or (
                option.get("price") is not None
                and (
                    not isinstance(option["price"], (int, float))
                    or isinstance(option["price"], bool)
                )
            )
            or (
                option.get("currency") is not None
                and not isinstance(option["currency"], str)
            )
            for option in selected_options
        ):
            raise serializers.ValidationError(
                {"selected_options": "Las opciones deben corresponder a los trámites seleccionados."}
            )
        attrs["selected_options"] = selected_options

        request = self.context.get("request")
        if request is not None:
            valid_service_types = {
                service for service, _label in Application._meta.get_field("service_type").choices
            }
            invalid_attachment_fields = []
            for key in request.FILES:
                if key.startswith("documents_"):
                    service_type = key.removeprefix("documents_")
                elif key.startswith("photos_"):
                    service_type = key.removeprefix("photos_")
                else:
                    continue
                if service_type not in valid_service_types or service_type not in selected_services:
                    invalid_attachment_fields.append(key)

            if invalid_attachment_fields:
                raise serializers.ValidationError(
                    {"documents": "Solo puedes adjuntar archivos a los trámites seleccionados."}
                )

        other_service = attrs.get("other_service", "")
        if "otros" in selected_services and not other_service.strip():
            raise serializers.ValidationError({"other_service": "Debes describir el trámite solicitado en 'Otros'."})
        return attrs

    def create(self, validated_data):
        uploaded_documents = validated_data.pop("documents", [])
        request = self.context.get("request")
        selected_services = validated_data["selected_services"]
        with transaction.atomic():
            if request is not None and request.user.is_authenticated:
                client_profile = ClientProfile.objects.filter(user=request.user).first()
                validated_data["user"] = request.user
                if client_profile is not None:
                    validated_data.update(
                        first_names=request.user.first_name,
                        last_names=request.user.last_name,
                        identification_type=client_profile.identification_type,
                        identification_number=client_profile.identification_number,
                        email=request.user.email,
                        phone=client_profile.phone,
                    )
            application = Application.objects.create(**validated_data)
            for uploaded_file in uploaded_documents:
                ApplicationDocument.objects.create(application=application, file=uploaded_file)
            if request is not None:
                for service_type in selected_services:
                    for uploaded_file in request.FILES.getlist(f"photos_{service_type}"):
                        ApplicationDocument.objects.create(
                            application=application,
                            file=uploaded_file,
                            service_type=service_type,
                            file_type=ApplicationFileType.PHOTO,
                        )
                    for uploaded_file in request.FILES.getlist(f"documents_{service_type}"):
                        ApplicationDocument.objects.create(
                            application=application,
                            file=uploaded_file,
                            service_type=service_type,
                            file_type=ApplicationFileType.DOCUMENT,
                        )
        return application

    def get_document_count(self, application):
        return application.documents.count()
