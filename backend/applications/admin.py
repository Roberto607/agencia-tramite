import re
from urllib.parse import urlencode
from pathlib import Path

from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q, TextField
from django.db.models.functions import Cast
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.dateparse import parse_date
from django.utils.html import format_html, format_html_join
from django.utils import timezone

from .models import (
    Application,
    ApplicationDocument,
    ApplicationNotification,
    ApplicationStatus,
    IdentificationType,
    ServiceType,
)


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    fields = ("service_label", "file_type_label", "file_name", "uploaded_at", "download_link")
    readonly_fields = fields
    extra = 0
    can_delete = False

    @admin.display(description="Archivo")
    def file_name(self, document):
        return Path(document.file.name).name

    @admin.display(description="Trámite")
    def service_label(self, document):
        return document.get_service_type_display() if document.service_type else "General"

    @admin.display(description="Tipo")
    def file_type_label(self, document):
        return document.get_file_type_display()

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
    change_form_template = "admin/applications/application/change_form.html"
    list_display = (
        "id",
        "full_name",
        "identification_type",
        "identification_number",
        "email",
        "phone",
        "service_types_summary",
        "status_display",
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
        ("Trámite", {"fields": ("service_types_display", "other_service")}),
        ("Estado de la solicitud", {"fields": ("status_display",)}),
        ("Registro", {"fields": ("created_at",)}),
    )
    readonly_fields = (
        "first_names",
        "last_names",
        "identification_type",
        "identification_number",
        "email",
        "phone",
        "service_types_display",
        "other_service",
        "status_display",
        "created_at",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(document_total=Count("documents", distinct=True))

    @admin.display(description="Solicitante")
    def full_name(self, application):
        return f"{application.first_names} {application.last_names}"

    @admin.display(description="Archivos", ordering="document_total")
    def document_count(self, application):
        return application.document_total

    @admin.display(description="Trámites solicitados")
    def service_types_display(self, application):
        selected_services = application.selected_services or [application.service_type]
        labels = dict(Application._meta.get_field("service_type").choices)
        return ", ".join(labels.get(service, service) for service in selected_services)

    @admin.display(description="Trámites solicitados")
    def service_types_summary(self, application):
        selected_services = application.selected_services or [application.service_type]
        labels = dict(Application._meta.get_field("service_type").choices)
        service_labels = [labels.get(service, service) for service in selected_services]
        if len(service_labels) == 1:
            return service_labels[0]

        additional_services = format_html_join(
            "",
            "<li>{}</li>",
            ((label,) for label in service_labels[1:]),
        )
        return format_html(
            '<span>{}</span> <details class="service-types-more">'
            '<summary aria-label="Ver {} trámites más" title="Ver otros trámites">…</summary>'
            "<ul>{}</ul></details>",
            service_labels[0],
            len(service_labels) - 1,
            additional_services,
        )

    @admin.display(description="Estado")
    def status_display(self, application):
        return application.get_status_display()

    def _review_message(self, application, target_status):
        action_text = (
            "fue aprobada"
            if target_status == ApplicationStatus.APPROVED
            else "no fue aprobada"
        )
        return (
            f"Hola {application.first_names}, te contactamos sobre tu solicitud "
            f"#{application.pk} para {self.service_types_display(application)}. "
            f"Tu solicitud {action_text}. Por favor, responde este mensaje "
            "para conversar sobre los siguientes pasos."
        )

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
                "<int:object_id>/review/<str:target_status>/",
                self.admin_site.admin_view(self.review_status),
                name="applications_application_review_status",
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

    def review_status(self, request, object_id, target_status):
        application = get_object_or_404(Application, pk=object_id)
        if not self.has_change_permission(request, application):
            raise PermissionDenied
        if target_status not in {
            ApplicationStatus.APPROVED,
            ApplicationStatus.REJECTED,
        }:
            raise Http404

        status_label = dict(ApplicationStatus.choices)[target_status]
        if request.method == "POST":
            phone_digits = re.sub(r"\D", "", application.phone)
            if phone_digits.startswith("00"):
                phone_digits = phone_digits[2:]
            if not 8 <= len(phone_digits) <= 15:
                messages.error(
                    request,
                    "No se pudo notificar: el teléfono del solicitante no parece tener un código de país válido.",
                )
                return HttpResponseRedirect(
                    reverse("admin:applications_application_changelist")
                )

            message = self._review_message(application, target_status)
            with transaction.atomic():
                application.status = target_status
                application.save(update_fields=("status",))
                ApplicationNotification.objects.create(
                    application=application,
                    application_reference=f"Solicitud #{application.pk}",
                    applicant_name=f"{application.first_names} {application.last_names}",
                    phone=application.phone,
                    status=target_status,
                    message=message,
                    created_by=request.user,
                )
            return HttpResponseRedirect(
                f"https://wa.me/{phone_digits}?{urlencode({'text': message})}"
            )

        if request.method != "GET":
            return HttpResponseNotAllowed(("GET", "POST"))

        context = {
            **self.admin_site.each_context(request),
            "title": f"Confirmar solicitud {status_label.lower()}",
            "application": application,
            "target_status": target_status,
            "status_label": status_label,
            "service_types": self.service_types_display(application),
            "message": self._review_message(application, target_status),
        }
        return TemplateResponse(
            request,
            "admin/applications/application/confirm_status.html",
            context,
        )

    def search_suggestions(self, request):
        if not self.has_view_or_change_permission(request):
            return JsonResponse({"detail": "No tienes permiso para consultar trámites."}, status=403)

        query = request.GET.get("q", "").strip()
        if not query:
            return JsonResponse({"results": []})

        matching_applications = self._filter_search_queryset(self.get_queryset(request), query)
        results = [
            {
                "id": application.pk,
                "label": (
                    f"#{application.pk} · {application.first_names} "
                    f"{application.last_names} · "
                    f"{application.get_identification_type_display()}: "
                    f"{application.identification_number} · "
                    f"{self.service_types_display(application)}"
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
    def _choice_values_matching(choices, term):
        term = term.casefold()
        return [
            value
            for value, label in choices
            if term in str(value).casefold() or term in str(label).casefold()
        ]

    def _filter_search_queryset(self, queryset, query):
        queryset = queryset.annotate(
            selected_services_text=Cast("selected_services", TextField())
        )
        for term in query.split():
            search_term = Q(first_names__icontains=term)
            search_term |= Q(last_names__icontains=term)
            search_term |= Q(identification_number__icontains=term)
            search_term |= Q(email__icontains=term)
            search_term |= Q(phone__icontains=term)
            search_term |= Q(other_service__icontains=term)

            identification_types = self._choice_values_matching(
                IdentificationType.choices,
                term,
            )
            if identification_types:
                search_term |= Q(identification_type__in=identification_types)

            service_types = self._choice_values_matching(ServiceType.choices, term)
            if service_types:
                search_term |= Q(service_type__in=service_types)
                selected_services_text = Cast("selected_services", TextField())
                for service_type in service_types:
                    search_term |= Q(
                        selected_services_text__icontains=f'"{service_type}"'
                    )

            record_id = term.removeprefix("#")
            if record_id.isdecimal():
                search_term |= Q(pk=int(record_id))
                search_term |= Q(document_total=int(record_id))

            date_value = parse_date(term)
            if date_value:
                search_term |= Q(created_at__date=date_value)

            queryset = queryset.filter(search_term)
        return queryset

    def get_search_results(self, request, queryset, search_term):
        return self._filter_search_queryset(queryset, search_term), False

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
            f"Trámites solicitados: {self._txt_value(self.service_types_display(application))}",
            f"Detalle del trámite: {self._txt_value(application.other_service) if application.service_type == 'otros' else '-'}",
            f"Fecha de solicitud: {timezone.localtime(application.created_at):%Y-%m-%d %H:%M:%S}",
            f"Archivos adjuntos: {application.documents.count()}",
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


@admin.register(ApplicationNotification)
class ApplicationNotificationAdmin(admin.ModelAdmin):
    change_list_template = "admin/applications/applicationnotification/change_list.html"
    list_display = (
        "application_link",
        "applicant_name",
        "status_display",
        "notification_state",
        "phone",
        "created_by",
        "created_at",
    )
    list_display_links = None
    list_filter = ("status", "created_at")
    search_fields = (
        "application_reference",
        "applicant_name",
        "phone",
        "application__identification_number",
        "message",
    )
    ordering = ("-created_at", "-pk")
    readonly_fields = (
        "application_link",
        "application_reference",
        "applicant_name",
        "phone",
        "status_display",
        "notification_state",
        "message",
        "created_by",
        "created_at",
    )
    fields = readonly_fields

    @admin.display(description="Solicitud")
    def application_link(self, notification):
        if notification.application_id:
            url = reverse(
                "admin:applications_application_change",
                args=(notification.application_id,),
            )
            return format_html('<a href="{}">{}</a>', url, notification.application_reference)
        return notification.application_reference

    @admin.display(description="Resultado")
    def status_display(self, notification):
        return notification.get_status_display()

    @admin.display(description="Notificación")
    def notification_state(self, notification):
        return "Preparada para WhatsApp"

    def get_search_results(self, request, queryset, search_term):
        for term in search_term.split():
            matching_statuses = ApplicationAdmin._choice_values_matching(
                ApplicationStatus.choices,
                term,
            )
            if matching_statuses:
                queryset = queryset.filter(status__in=matching_statuses)
                continue

            matching_term = Q(application_reference__icontains=term)
            matching_term |= Q(applicant_name__icontains=term)
            matching_term |= Q(phone__icontains=term)
            matching_term |= Q(message__icontains=term)
            matching_term |= Q(application__identification_number__icontains=term)
            matching_term |= Q(created_by__username__icontains=term)
            queryset = queryset.filter(matching_term)
        return queryset, False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "LB&A Consulter"
admin.site.site_title = "Administración de LB&A Consulter"
admin.site.index_title = "Bandeja de solicitudes"
admin.site.unregister(Group)
