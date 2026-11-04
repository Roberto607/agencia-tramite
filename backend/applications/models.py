from django.db import models
from django.conf import settings


class IdentificationType(models.TextChoices):
    CITIZENSHIP = "cedula", "Cédula de ciudadanía"
    FOREIGNER = "extranjeria", "Cédula de extranjería"
    PASSPORT = "pasaporte", "Pasaporte"
    TAX_ID = "nit", "NIT"
    OTHER = "otro", "Otro"


class ServiceType(models.TextChoices):
    BIRTH_CERTIFICATE = "certificacion_nacimiento", "Certificación de Nacimiento"
    CRIMINAL_RECORD = "certificacion_antecedentes_penales", "Certificación de antecedentes penales"
    MARRIAGE_DIVORCE_SINGLE = "certificacion_matrimonio_divorcio_solteria", "Certificación de matrimonio, divorcio, Fe de soltería"
    WIDOWHOOD = "certificacion_viudez", "Certificación de viudez"
    DEATH_CERTIFICATE = "certificacion_defuncion", "Certificación de defunción"
    STUDY_CERTIFICATE = "titulos_estudio_certificacion_notas_plan_tematico", "Títulos de estudio, certificación de notas y plan temático"
    LEGAL_REPRESENTATION = "representacion_juridica", "Representación jurídica (abogados)"
    CERTIFIED_TRANSLATIONS = "traducciones_certificadas", "Traducciones certificadas"
    APOSTILLE_CONSULATE = "apostillamiento_consulado", "Apostillamiento Consulado"
    BUSINESS_ADVISORY = "asesoramiento_empresarial", "Asesoramiento empresarial: Pymes, TCP, CNA y otros actores económicos"
    OTHER = "otros", "Otros"


class ApplicationFileType(models.TextChoices):
    PHOTO = "photo", "Fotografía"
    DOCUMENT = "document", "Documento"


class Application(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="applications",
        blank=True,
        null=True,
    )
    first_names = models.CharField(max_length=120)
    last_names = models.CharField(max_length=120)
    identification_type = models.CharField(max_length=20, choices=IdentificationType.choices)
    identification_number = models.CharField(max_length=40)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    service_type = models.CharField(max_length=80, choices=ServiceType.choices, default=ServiceType.APOSTILLE_CONSULATE)
    selected_services = models.JSONField(default=list)
    other_service = models.CharField(max_length=255, blank=True, default="")
    photo = models.ImageField(upload_to="applications/photos/%Y/%m/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "solicitud"
        verbose_name_plural = "lista de trámites"

    def __str__(self):
        return f"Solicitud #{self.pk}"


class ApplicationDocument(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="applications/documents/%Y/%m/")
    service_type = models.CharField(
        max_length=80,
        choices=ServiceType.choices,
        blank=True,
        default="",
    )
    file_type = models.CharField(
        max_length=12,
        choices=ApplicationFileType.choices,
        default=ApplicationFileType.DOCUMENT,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at", "pk"]
        verbose_name = "archivo adjunto"
        verbose_name_plural = "archivos adjuntos"

    def __str__(self):
        return self.file.name


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    identification_type = models.CharField(max_length=20, choices=IdentificationType.choices)
    identification_number = models.CharField(max_length=40)
    phone = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.identification_number})"
