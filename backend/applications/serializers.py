from django.db import transaction
from rest_framework import serializers

from .models import Application, ApplicationDocument


class ApplicationSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True, write_only=True)
    selected_services = serializers.JSONField(required=False)
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

        other_service = attrs.get("other_service", "")
        if "otros" in selected_services and not other_service.strip():
            raise serializers.ValidationError({"other_service": "Debes describir el trámite solicitado en 'Otros'."})
        return attrs

    def create(self, validated_data):
        uploaded_documents = validated_data.pop("documents", [])
        with transaction.atomic():
            application = Application.objects.create(**validated_data)
            for uploaded_file in uploaded_documents:
                ApplicationDocument.objects.create(application=application, file=uploaded_file)
        return application

    def get_document_count(self, application):
        return application.documents.count()
