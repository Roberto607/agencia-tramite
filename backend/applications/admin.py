from pathlib import Path

from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils import timezone

from .models import Application, ApplicationDocument


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    fields = ("file_name", "uploaded_at", "download_link")
    readonly_fields = fields
    extra = 0
    can_delete = False

    @admin.display(description="Documento")
    def file_name(self, document):
        return Path(document.file.name).name

    @admin.display(description="Archivo")
    def download_link(self, document):
        url = reverse(
            "admin:applications_application_document_download",
            args=(document.application_id, document.pk),
        )
        return format_html('<a href="{}">Descargar</a>', url)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    change_list_template = "admin/applications/application/change_list.html"
    list_display = (
        "id",
        "full_name",
        "identification_type",
        "identification_number",
        "email",
        "phone",
        "service_type",
        "document_count",
        "txt_download_link",
        "created_at",
    )
    list_display_links = ("id", "full_name")
    list_filter = ()
    search_fields = ("first_names", "last_names", "identification_number", "email", "phone", "other_service")
    ordering = ("-created_at",)
    list_per_page = 25
    inlines = (ApplicationDocumentInline,)
    fieldsets = (
        ("Datos del solicitante", {"fields": ("first_names", "last_names", "identification_type", "identification_number")}),
        ("Contacto", {"fields": ("email", "phone")}),
        ("Trámite", {"fields": ("service_type", "other_service")}),
        ("Fotografía", {"fields": ("photo_name", "photo_download")}),
        ("Registro", {"fields": ("created_at",)}),
    )
    readonly_fields = ("photo_name", "photo_download", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(document_total=Count("documents", distinct=True))

    @admin.display(description="Solicitante")
    def full_name(self, application):
        return f"{application.first_names} {application.last_names}"

    @admin.display(description="Documentos", ordering="document_total")
    def document_count(self, application):
        return application.document_total

    @admin.display(description="Exportar")
    def txt_download_link(self, application):
        url = reverse(
            "admin:applications_application_export_txt",
            args=(application.pk,),
        )
        return format_html('<a href="{}">Descargar TXT</a>', url)

    @admin.display(description="Archivo de foto")
    def photo_name(self, application):
        return Path(application.photo.name).name if application.photo else "Sin foto"

    @admin.display(description="Acceso a la foto")
    def photo_download(self, application):
        if not application.photo:
            return "-"
        url = reverse("admin:applications_application_photo_download", args=(application.pk,))
        return format_html('<a href="{}">Descargar fotografía</a>', url)

    def get_urls(self):
        custom_urls = [
            path(
                "search-suggestions/",
                self.admin_site.admin_view(self.search_suggestions),
                name="applications_application_search_suggestions",
            ),
            path(
                "<int:object_id>/export-txt/",
                self.admin_site.admin_view(self.export_txt),
                name="applications_application_export_txt",
            ),
            path(
                "<int:object_id>/photo/download/",
                self.admin_site.admin_view(self.download_photo),
                name="applications_application_photo_download",
            ),
            path(
                "<int:object_id>/documents/<int:document_id>/download/",
                self.admin_site.admin_view(self.download_document),
                name="applications_application_document_download",
            ),
        ]
        return custom_urls + super().get_urls()

    def search_suggestions(self, request):
        if not self.has_view_permission(request):
            return JsonResponse({"detail": "No tienes permiso para consultar trámites."}, status=403)

        query = request.GET.get("q", "").strip()
        if len(query) < 2:
            return JsonResponse({"results": []})

        matching_applications = self.get_queryset(request)
        for term in query.split():
            matching_applications = matching_applications.filter(
                Q(first_names__icontains=term)
                | Q(last_names__icontains=term)
                | Q(identification_number__icontains=term)
                | Q(email__icontains=term)
                | Q(phone__icontains=term)
                | Q(other_service__icontains=term)
            )
        results = [
            {
                "id": application.pk,
                "label": (
                    f"#{application.pk} · {application.first_names} "
                    f"{application.last_names} · "
                    f"{application.get_service_type_display()}"
                ),
                "url": reverse(
                    "admin:applications_application_change",
                    args=(application.pk,),
                ),
            }
            for application in matching_applications.order_by("-created_at", "-pk")[:8]
        ]
        return JsonResponse({"results": results})

    @staticmethod
    def _txt_value(value):
        return str(value or "No registrado").replace("\r", " ").replace("\n", " ").strip()

    def export_txt(self, request, object_id):
        application = get_object_or_404(Application, pk=object_id)
        self._check_download_permission(request, application)
        lines = [
            "LB&A CONSULTER - DATOS DEL TRÁMITE",
            f"Radicado: #{application.pk}",
            f"Nombre: {self._txt_value(application.first_names)} {self._txt_value(application.last_names)}",
            f"Tipo de identificación: {self._txt_value(application.get_identification_type_display())}",
            f"Número de identificación: {self._txt_value(application.identification_number)}",
            f"Correo: {self._txt_value(application.email)}",
            f"Teléfono: {self._txt_value(application.phone)}",
            f"Trámite solicitado: {self._txt_value(application.get_service_type_display())}",
            f"Detalle del trámite: {self._txt_value(application.other_service) if application.service_type == 'otros' else '-'}",
            f"Fecha de solicitud: {timezone.localtime(application.created_at):%Y-%m-%d %H:%M:%S}",
            f"Documentos adjuntos: {application.documents.count()}",
        ]
        response = HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="tramite-{application.pk}-lba.txt"'
        return response

    def _check_download_permission(self, request, application):
        if not self.has_view_or_change_permission(request, application):
            raise PermissionDenied

    def download_photo(self, request, object_id):
        application = get_object_or_404(Application, pk=object_id)
        self._check_download_permission(request, application)
        if not application.photo:
            raise Http404
        return FileResponse(
            application.photo.open("rb"),
            as_attachment=True,
            filename=Path(application.photo.name).name,
        )

    def download_document(self, request, object_id, document_id):
        document = get_object_or_404(
            ApplicationDocument.objects.select_related("application"),
            pk=document_id,
            application_id=object_id,
        )
        self._check_download_permission(request, document.application)
        return FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=Path(document.file.name).name,
        )


admin.site.site_header = "LB&A Consulter"
admin.site.site_title = "Administración de LB&A Consulter"
admin.site.index_title = "Bandeja de solicitudes"
admin.site.unregister(Group)
