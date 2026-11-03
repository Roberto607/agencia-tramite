from django.db import transaction
from rest_framework import serializers

from .models import Application, ApplicationDocument


class ApplicationSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True, write_only=True)
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
            "other_service",
            "photo",
            "created_at",
            "document_count",
            "documents",
        )
        read_only_fields = ("id", "created_at", "document_count")

    def validate(self, attrs):
        service_type = attrs.get("service_type")
        other_service = attrs.get("other_service", "")
        if service_type == "otros" and not other_service.strip():
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
