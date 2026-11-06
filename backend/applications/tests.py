import os
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import CommandError, call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Application,
    ApplicationDocument,
    ApplicationNotification,
    ApplicationStatus,
)


class BootstrapSuperuserTests(APITestCase):
    def test_bootstrap_skips_when_environment_is_unset(self):
        with patch.dict(
            os.environ,
            {
                "DJANGO_SUPERUSER_USERNAME": "",
                "DJANGO_SUPERUSER_EMAIL": "",
                "DJANGO_SUPERUSER_PASSWORD": "",
            },
        ):
            call_command("bootstrap_superuser")

        self.assertFalse(get_user_model().objects.exists())

    def test_bootstrap_requires_all_environment_values(self):
        with patch.dict(
            os.environ,
            {
                "DJANGO_SUPERUSER_USERNAME": "site-admin",
                "DJANGO_SUPERUSER_EMAIL": "",
                "DJANGO_SUPERUSER_PASSWORD": "",
            },
        ):
            with self.assertRaisesMessage(
                CommandError, "Set DJANGO_SUPERUSER_USERNAME"
            ):
                call_command("bootstrap_superuser")

        self.assertFalse(get_user_model().objects.exists())

    def test_bootstrap_creates_superuser_once_without_logging_password(self):
        password = "temporary-secret-for-test-only"
        environment = {
            "DJANGO_SUPERUSER_USERNAME": "site-admin",
            "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": password,
        }
        output = StringIO()

        with patch.dict(os.environ, environment):
            call_command("bootstrap_superuser", stdout=output)
            call_command("bootstrap_superuser", stdout=output)

        user = get_user_model().objects.get(username="site-admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password(password))
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertNotIn(password, output.getvalue())

    def test_bootstrap_rejects_existing_non_superuser(self):
        get_user_model().objects.create_user(
            username="site-admin",
            email="admin@example.com",
            password="existing-password",
        )
        with patch.dict(
            os.environ,
            {
                "DJANGO_SUPERUSER_USERNAME": "site-admin",
                "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
                "DJANGO_SUPERUSER_PASSWORD": "temporary-secret-for-test-only",
            },
        ):
            with self.assertRaisesMessage(
                CommandError, "already exists and is not a superuser"
            ):
                call_command("bootstrap_superuser")


class ApplicationApiTests(APITestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.addCleanup(self.media_directory.cleanup)
        media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

    def test_registration_authenticates_client_and_attaches_documents_to_services(self):
        registration_data = {
            "first_names": "Ana María",
            "last_names": "Pérez López",
            "identification_type": "cedula",
            "identification_number": "123456789",
            "phone": "+53 58049659",
            "email": "ana@example.com",
            "password": "V3ry-Strong-Account-Password-892!",
        }
        registration = self.client.post(
            reverse("client-registration"),
            registration_data,
            format="json",
        )

        self.assertEqual(registration.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", registration.data)
        user = get_user_model().objects.get(email="ana@example.com")
        self.assertTrue(user.check_password(registration_data["password"]))
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {registration.data['token']}")

        application_response = self.client.post(
            reverse("application-create"),
            {
                "first_names": "Nombre manipulado",
                "last_names": "Apellido manipulado",
                "identification_type": "otro",
                "identification_number": "999",
                "email": "otra@example.com",
                "phone": "+1 555 000 0000",
                "selected_services": '["certificacion_nacimiento","traducciones_certificadas"]',
                "photos_certificacion_nacimiento": SimpleUploadedFile(
                    "nacimiento.jpg",
                    b"birth photo",
                    content_type="image/jpeg",
                ),
                "documents_traducciones_certificadas": SimpleUploadedFile(
                    "traduccion.pdf",
                    b"translation document",
                    content_type="application/pdf",
                ),
            },
            format="multipart",
        )

        self.assertEqual(application_response.status_code, status.HTTP_201_CREATED)
        application = Application.objects.get(pk=application_response.data["id"])
        self.assertEqual(application.user, user)
        self.assertEqual(application.first_names, "Ana María")
        self.assertEqual(application.last_names, "Pérez López")
        self.assertEqual(application.identification_number, "123456789")
        self.assertEqual(application.email, "ana@example.com")
        self.assertEqual(
            list(application.documents.values_list("service_type", "file_type")),
            [
                ("certificacion_nacimiento", "photo"),
                ("traducciones_certificadas", "document"),
            ],
        )
        self.client.force_login(
            get_user_model().objects.create_superuser(
                "attachment-admin",
                "attachments@example.com",
                "attachment-admin-password-for-test",
            )
        )
        detail = self.client.get(
            reverse("admin:applications_application_change", args=(application.pk,))
        )
        self.assertContains(detail, "Fotografía")
        self.assertContains(detail, "Documento")
        self.assertContains(detail, "Certificación de Nacimiento")
        self.assertContains(detail, "Traducciones certificadas")

    def test_registration_rejects_an_existing_email(self):
        registration_data = {
            "first_names": "Ana",
            "last_names": "Pérez",
            "identification_type": "cedula",
            "identification_number": "123456789",
            "phone": "+53 58049659",
            "email": "ana@example.com",
            "password": "V3ry-Strong-Account-Password-892!",
        }
        first_response = self.client.post(
            reverse("client-registration"),
            registration_data,
            format="json",
        )
        duplicate_response = self.client.post(
            reverse("client-registration"),
            registration_data,
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", duplicate_response.data)

    def test_client_can_log_in_and_receives_profile_and_token(self):
        registration_data = {
            "first_names": "Ana María",
            "last_names": "Pérez López",
            "identification_type": "cedula",
            "identification_number": "123456789",
            "phone": "+53 58049659",
            "email": "ana@example.com",
            "password": "V3ry-Strong-Account-Password-892!",
        }
        self.client.post(reverse("client-registration"), registration_data, format="json")

        response = self.client.post(
            reverse("client-login"),
            {"email": "ANA@example.com", "password": registration_data["password"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["token"])
        self.assertEqual(
            response.data["profile"],
            {
                "first_names": "Ana María",
                "last_names": "Pérez López",
                "identification_type": "cedula",
                "identification_number": "123456789",
                "phone": "+53 58049659",
                "email": "ana@example.com",
            },
        )

    def test_client_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("client-login"),
            {"email": "unknown@example.com", "password": "incorrect"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_root_redirects_to_admin_login(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.headers["Location"], "/admin/login/")

    def test_admin_login_uses_agency_branding(self):
        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Administración de LB&amp;A Consulter")
        self.assertContains(response, "/static/applications/logo-lba.png")
        self.assertNotContains(response, '<header id="header">', html=False)
        self.assertNotContains(response, 'aria-label="Breadcrumbs"', html=False)
        self.assertContains(response, 'id="login-form"', html=False)

    def test_create_application_with_multiple_documents(self):
        documents = [
            SimpleUploadedFile("identificacion.pdf", b"pdf contents", content_type="application/pdf"),
            SimpleUploadedFile("soporte.pdf", b"more pdf contents", content_type="application/pdf"),
        ]
        response = self.client.post(
            reverse("application-create"),
            {
                "first_names": "Ana María",
                "last_names": "Pérez López",
                "identification_type": "cedula",
                "identification_number": "123456789",
                "email": "ana@example.com",
                "phone": "+57 300 123 4567",
                "documents": documents,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["document_count"], 2)
        self.assertNotIn("photo", response.data)
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(ApplicationDocument.objects.count(), 2)

    def test_create_application_with_multiple_selected_services(self):
        response = self.client.post(
            reverse("application-create"),
            {
                "first_names": "Ana",
                "last_names": "Pérez",
                "identification_type": "cedula",
                "identification_number": "123456789",
                "email": "ana@example.com",
                "selected_services": '["certificacion_nacimiento","traducciones_certificadas"]',
                "selected_options": (
                    '[{"service":"certificacion_nacimiento",'
                    '"service_label":"Certificación de Nacimiento",'
                    '"group":"Obtención","option":"Obtención",'
                    '"time":"1–5 días","price":6000,"currency":"CUP"}]'
                ),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["selected_services"],
            ["certificacion_nacimiento", "traducciones_certificadas"],
        )
        application = Application.objects.get(pk=response.data["id"])
        self.assertEqual(
            application.selected_services,
            ["certificacion_nacimiento", "traducciones_certificadas"],
        )
        self.assertEqual(application.service_type, "certificacion_nacimiento")
        self.assertEqual(
            application.selected_options[0]["price"],
            6000,
        )

    def test_create_application_requires_details_when_other_service_is_selected(self):
        response = self.client.post(
            reverse("application-create"),
            {
                "first_names": "Ana",
                "last_names": "Pérez",
                "identification_type": "cedula",
                "identification_number": "123456789",
                "email": "ana@example.com",
                "selected_services": '["certificacion_nacimiento","otros"]',
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("other_service", response.data)

    def test_admin_inbox_lists_submissions_and_allows_staff_file_download(self):
        admin_user = get_user_model().objects.create_superuser(
            username="inbox-admin",
            email="inbox-admin@example.com",
            password="test-admin-password-123",
        )
        application = Application.objects.create(
            first_names="Ana María",
            last_names="Pérez López",
            identification_type="cedula",
            identification_number="123456789",
            email="ana@example.com",
            phone="+57 300 123 4567",
            selected_options=[{
                "service": "certificacion_nacimiento",
                "service_label": "Certificación de Nacimiento",
                "group": "Obtención",
                "option": "Obtención",
                "time": "1–5 días",
                "price": 6000,
                "currency": "CUP",
            }, {
                "service": "certificacion_nacimiento",
                "service_label": "Certificación de Nacimiento",
                "group": "Legalización",
                "option": "Vía express",
                "time": "15–20 días",
                "price": 70,
                "currency": "USD",
            }],
        )
        document = ApplicationDocument.objects.create(
            application=application,
            file=SimpleUploadedFile("soporte.pdf", b"private document", content_type="application/pdf"),
            service_type="certificacion_nacimiento",
            file_type="document",
        )
        photo = ApplicationDocument.objects.create(
            application=application,
            file=SimpleUploadedFile("nacimiento.jpg", b"private photo", content_type="image/jpeg"),
            service_type="certificacion_nacimiento",
            file_type="photo",
        )
        self.client.force_login(admin_user)

        inbox = self.client.get(reverse("admin:applications_application_changelist"))
        detail = self.client.get(reverse("admin:applications_application_change", args=(application.pk,)))
        download = self.client.get(
            reverse(
                "admin:applications_application_document_download",
                args=(application.pk, document.pk),
            )
        )
        photo_download = self.client.get(
            reverse(
                "admin:applications_application_document_download",
                args=(application.pk, photo.pk),
            )
        )

        self.assertEqual(inbox.status_code, status.HTTP_200_OK)
        self.assertContains(inbox, "Ana María Pérez López")
        self.assertContains(inbox, "ana@example.com")
        self.assertContains(inbox, "Descargar TXT")
        self.assertNotContains(inbox, "Aceptar solicitud")
        self.assertNotContains(inbox, "Rechazar solicitud")
        self.assertContains(inbox, 'class="application-search"', html=False)
        self.assertContains(inbox, 'id="application-search-suggestions"', html=False)
        self.assertContains(inbox, "form.requestSubmit();", html=False)
        self.assertContains(
            inbox,
            'data-suggestions-url="/admin/applications/application/search-suggestions/"',
            html=False,
        )
        self.assertNotContains(inbox, 'id="changelist-filter"', html=False)
        self.assertContains(inbox, 'input.addEventListener("input"', html=False)
        self.assertNotContains(inbox, "Inicio", html=False)
        self.assertContains(inbox, "#0c2851", html=False)
        self.assertContains(inbox, 'id="user-tools"', html=False)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertContains(detail, "soporte.pdf")
        self.assertContains(detail, "nacimiento.jpg")
        self.assertContains(detail, "Fotografía")
        self.assertContains(detail, "Certificación de Nacimiento")
        self.assertContains(detail, "Opciones, tiempos y precios seleccionados")
        self.assertContains(detail, 'class="application-selected-service__title"', html=False)
        self.assertEqual(
            detail.content.count(b'class="application-selected-option__row"'),
            2,
        )
        self.assertContains(detail, "Legalización: Vía express")
        self.assertNotContains(detail, "Obtención: Obtención")
        self.assertContains(detail, "6,000 CUP")
        self.assertNotContains(detail, "&lt;br&gt;", html=False)
        self.assertContains(detail, "Total estimado")
        self.assertContains(detail, "Aceptar solicitud")
        self.assertContains(detail, "Rechazar solicitud")
        self.assertContains(detail, "Eliminar")
        self.assertNotContains(detail, 'name="_save"', html=False)
        self.assertNotContains(detail, 'name="_addanother"', html=False)
        self.assertNotContains(detail, 'name="_continue"', html=False)
        self.assertNotContains(detail, "applications/documents/")
        self.assertNotContains(detail, "<h2>Fotografía</h2>", html=False)
        self.assertEqual(download.status_code, status.HTTP_200_OK)
        self.assertEqual(b"".join(download.streaming_content), b"private document")
        self.assertEqual(photo_download.status_code, status.HTTP_200_OK)
        self.assertEqual(b"".join(photo_download.streaming_content), b"private photo")
        self.assertEqual(str(photo), "nacimiento.jpg")

    def test_admin_can_approve_or_reject_and_open_whatsapp_with_a_message(self):
        admin_user = get_user_model().objects.create_superuser(
            "review-admin",
            "review-admin@example.com",
            "review-admin-password-for-test",
        )
        application = Application.objects.create(
            first_names="Ana María",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="123456789",
            email="ana@example.com",
            phone="+53 58049659",
            selected_services=["certificacion_nacimiento"],
        )
        self.client.force_login(admin_user)

        approve_url = reverse(
            "admin:applications_application_review_status",
            args=(application.pk, ApplicationStatus.APPROVED),
        )
        confirmation = self.client.get(approve_url)
        self.assertEqual(confirmation.status_code, status.HTTP_200_OK)
        self.assertContains(confirmation, "Confirmar y abrir WhatsApp")
        self.assertContains(confirmation, "Certificación de Nacimiento")

        approved = self.client.post(approve_url)
        application.refresh_from_db()
        self.assertEqual(application.status, ApplicationStatus.APPROVED)
        self.assertEqual(approved.status_code, status.HTTP_302_FOUND)
        self.assertTrue(approved.headers["Location"].startswith("https://wa.me/5358049659?text="))
        approve_message = parse_qs(urlsplit(approved.headers["Location"]).query)["text"][0]
        self.assertIn("fue aprobada", approve_message)
        self.assertIn("Ana María", approve_message)

        reject_url = reverse(
            "admin:applications_application_review_status",
            args=(application.pk, ApplicationStatus.REJECTED),
        )
        rejected = self.client.post(reject_url)
        application.refresh_from_db()
        self.assertEqual(application.status, ApplicationStatus.REJECTED)
        self.assertTrue(rejected.headers["Location"].startswith("https://wa.me/5358049659?text="))
        reject_message = parse_qs(urlsplit(rejected.headers["Location"]).query)["text"][0]
        self.assertIn("no fue aprobada", reject_message)

        notifications = self.client.get(
            reverse("admin:applications_applicationnotification_changelist")
        )
        notification_search_url = reverse(
            "admin:applications_applicationnotification_changelist"
        )
        matching_notifications = self.client.get(
            notification_search_url,
            {"q": "Ana María"},
        )
        rejected_notifications = self.client.get(
            notification_search_url,
            {"q": "rechazada"},
        )
        approved_notifications = self.client.get(
            notification_search_url,
            {"q": "aPrObAdA"},
        )
        self.assertEqual(
            ApplicationNotification.objects.filter(application=application).count(),
            2,
        )
        self.assertEqual(matching_notifications.status_code, status.HTTP_200_OK)
        self.assertEqual(matching_notifications.context["cl"].result_count, 2)
        self.assertEqual(rejected_notifications.context["cl"].result_count, 1)
        self.assertEqual(approved_notifications.context["cl"].result_count, 1)
        self.assertContains(rejected_notifications, "Rechazada")
        self.assertEqual(
            [
                notification.status
                for notification in approved_notifications.context["cl"].result_list
            ],
            [ApplicationStatus.APPROVED],
        )
        self.assertContains(notifications, "Aprobada")
        self.assertContains(notifications, "Rechazada")
        self.assertContains(notifications, "Preparada para WhatsApp")
        self.assertContains(notifications, "Ana María Pérez")
        self.assertContains(notifications, "form.requestSubmit();", html=False)
        self.assertNotContains(notifications, 'id="changelist-filter"', html=False)

    def test_admin_review_does_not_change_status_without_a_valid_phone(self):
        admin_user = get_user_model().objects.create_superuser(
            "review-no-phone-admin",
            "review-no-phone@example.com",
            "review-no-phone-password-for-test",
        )
        application = Application.objects.create(
            first_names="Luis",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="123456789",
            email="luis@example.com",
            phone="555",
        )
        self.client.force_login(admin_user)
        review_url = reverse(
            "admin:applications_application_review_status",
            args=(application.pk, ApplicationStatus.APPROVED),
        )

        response = self.client.post(review_url)
        application.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(application.status, ApplicationStatus.PENDING)
        self.assertFalse(ApplicationNotification.objects.exists())
        self.assertEqual(
            response.headers["Location"],
            reverse("admin:applications_application_changelist"),
        )
        inbox = self.client.get(response.headers["Location"])
        self.assertContains(inbox, "el teléfono del solicitante")

    def test_admin_list_collapses_additional_services_behind_ellipsis(self):
        admin_user = get_user_model().objects.create_superuser(
            "compact-services-admin",
            "compact-services@example.com",
            "compact-services-password-for-test",
        )
        Application.objects.create(
            first_names="Ana",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="12345",
            email="ana@example.com",
            service_type="certificacion_nacimiento",
            selected_services=[
                "certificacion_nacimiento",
                "traducciones_certificadas",
                "apostillamiento_consulado",
            ],
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:applications_application_changelist")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Certificación de Nacimiento")
        self.assertContains(response, 'class="service-types-more"', html=False)
        self.assertContains(response, "Ver 2 trámites más", html=False)
        self.assertContains(response, "<li>Traducciones certificadas</li>", html=False)
        self.assertContains(response, "<li>Apostillamiento Consulado</li>", html=False)

    def test_admin_search_filters_applications_by_query(self):
        admin_user = get_user_model().objects.create_superuser(
            "search-admin",
            "search-admin@example.com",
            "search-password-for-test",
        )
        Application.objects.create(
            first_names="Ana",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="12345",
            email="ana@example.com",
        )
        Application.objects.create(
            first_names="Luis",
            last_names="Gómez",
            identification_type="cedula",
            identification_number="67890",
            email="luis@example.com",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:applications_application_changelist"),
            {"q": "ana"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Ana Pérez")
        self.assertNotContains(response, "Luis Gómez")
        self.assertContains(response, 'value="ana"', html=False)

    def test_cleared_admin_search_returns_full_application_list(self):
        admin_user = get_user_model().objects.create_superuser(
            "clear-search-admin",
            "clear-search-admin@example.com",
            "clear-search-password-for-test",
        )
        Application.objects.create(
            first_names="Ana",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="12345",
            email="ana@example.com",
        )
        Application.objects.create(
            first_names="Luis",
            last_names="Gómez",
            identification_type="nit",
            identification_number="900123",
            email="luis@example.com",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:applications_application_changelist"),
            {"q": ""},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Ana Pérez")
        self.assertContains(response, "Luis Gómez")
        self.assertContains(response, 'value=""', html=False)

    def test_admin_search_suggestions_return_matching_application_links(self):
        admin_user = get_user_model().objects.create_superuser(
            "suggestion-admin",
            "suggestion-admin@example.com",
            "suggestion-password-for-test",
        )
        application = Application.objects.create(
            first_names="Ana",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="12345",
            email="ana@example.com",
            service_type="apostillamiento_consulado",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:applications_application_search_suggestions"),
            {"q": "ana"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["results"],
            [
                {
                    "id": application.pk,
                    "label": (
                        f"#{application.pk} · Ana Pérez · Cédula de ciudadanía: "
                        "12345 · Apostillamiento Consulado"
                    ),
                    "url": reverse(
                        "admin:applications_application_change",
                        args=(application.pk,),
                    ),
                }
            ],
        )
        multiword_response = self.client.get(
            reverse("admin:applications_application_search_suggestions"),
            {"q": "ana pé"},
        )
        self.assertEqual(multiword_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(multiword_response.json()["results"]), 1)

    def test_admin_search_matches_displayed_identification_and_service_labels(self):
        admin_user = get_user_model().objects.create_superuser(
            "exact-search-admin",
            "exact-search-admin@example.com",
            "exact-search-password-for-test",
        )
        nit_application = Application.objects.create(
            first_names="Ana",
            last_names="Pérez",
            identification_type="nit",
            identification_number="900123",
            email="ana@example.com",
            service_type="apostillamiento_consulado",
            selected_services=[
                "apostillamiento_consulado",
                "traducciones_certificadas",
                "asesoramiento_empresarial",
            ],
        )
        Application.objects.create(
            first_names="Luis",
            last_names="Gómez",
            identification_type="cedula",
            identification_number="12345",
            email="luis@example.com",
            service_type="certificacion_nacimiento",
        )
        self.client.force_login(admin_user)

        nit_suggestions = self.client.get(
            reverse("admin:applications_application_search_suggestions"),
            {"q": "NIT"},
        )
        nit_list = self.client.get(
            reverse("admin:applications_application_changelist"),
            {"q": "NIT"},
        )
        service_suggestions = self.client.get(
            reverse("admin:applications_application_search_suggestions"),
            {"q": "Traducciones certificadas"},
        )
        service_list = self.client.get(
            reverse("admin:applications_application_changelist"),
            {"q": "Traducciones certificadas"},
        )
        advisory_suggestions = self.client.get(
            reverse("admin:applications_application_search_suggestions"),
            {"q": "Asesoramiento empresarial Pymes"},
        )

        self.assertEqual(nit_suggestions.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [result["id"] for result in nit_suggestions.json()["results"]],
            [nit_application.pk],
        )
        self.assertContains(nit_list, "Ana Pérez")
        self.assertNotContains(nit_list, "Luis Gómez")
        self.assertEqual(service_suggestions.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [result["id"] for result in service_suggestions.json()["results"]],
            [nit_application.pk],
        )
        self.assertContains(service_list, "Apostillamiento Consulado")
        self.assertContains(service_list, 'class="service-types-more"', html=False)
        self.assertContains(service_list, "Traducciones certificadas")
        self.assertContains(
            service_list,
            "Asesoramiento empresarial: Pymes, TCP, CNA y otros actores económicos",
        )
        self.assertEqual(advisory_suggestions.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [result["id"] for result in advisory_suggestions.json()["results"]],
            [nit_application.pk],
        )

    def test_txt_export_contains_only_selected_application_without_attachments(self):
        admin_user = get_user_model().objects.create_superuser(
            username="export-admin",
            email="export-admin@example.com",
            password="test-admin-password-123",
        )
        Application.objects.create(
            first_names="María",
            last_names="Gómez",
            identification_type="pasaporte",
            identification_number="P-98765",
            email="maria@example.com",
            phone="+57 300 555 0101",
            photo=SimpleUploadedFile("private-photo.jpg", b"private photo contents", content_type="image/jpeg"),
        )
        application = Application.objects.create(
            first_names="Luis",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="123456789",
            email="luis@example.com",
        )
        ApplicationDocument.objects.create(
            application=application,
            file=SimpleUploadedFile("private-document.pdf", b"private document contents", content_type="application/pdf"),
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:applications_application_export_txt", args=(application.pk,))
        )
        export = response.content.decode("utf-8")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertIn(f'attachment; filename="tramite-{application.pk}-lba.txt"', response["Content-Disposition"])
        self.assertIn("luis@example.com", export)
        self.assertIn("123456789", export)
        self.assertIn("Archivos adjuntos: 1", export)
        self.assertNotIn("maria@example.com", export)
        self.assertNotIn("P-98765", export)
        self.assertNotIn("private-photo", export)
        self.assertNotIn("private document", export)
        self.assertNotIn("private-document", export)

    def test_txt_export_requires_admin_login(self):
        application = Application.objects.create(
            first_names="Luis",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="123456789",
            email="luis@example.com",
        )
        response = self.client.get(
            reverse("admin:applications_application_export_txt", args=(application.pk,))
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("/admin/login/", response["Location"])

    def test_txt_export_requires_application_permission(self):
        staff_user = get_user_model().objects.create_user(
            username="limited-staff",
            email="limited-staff@example.com",
            password="test-staff-password-123",
            is_staff=True,
        )
        application = Application.objects.create(
            first_names="Luis",
            last_names="Pérez",
            identification_type="cedula",
            identification_number="123456789",
            email="luis@example.com",
        )
        self.client.force_login(staff_user)

        response = self.client.get(
            reverse("admin:applications_application_export_txt", args=(application.pk,))
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_menu_shows_applications_instead_of_groups(self):
        admin_user = get_user_model().objects.create_superuser(
            username="menu-admin",
            email="menu-admin@example.com",
            password="test-admin-password-123",
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Trámites")
        self.assertContains(response, "Lista de trámites")
        self.assertNotContains(response, "Grupos")
        self.assertContains(response, reverse("admin:applications_application_changelist"))

    def test_health_check_reports_database_connection(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["database"], "connected")
