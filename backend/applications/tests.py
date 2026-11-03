import os
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import CommandError, call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Application, ApplicationDocument


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
        )
        document = ApplicationDocument.objects.create(
            application=application,
            file=SimpleUploadedFile("soporte.pdf", b"private document", content_type="application/pdf"),
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

        self.assertEqual(inbox.status_code, status.HTTP_200_OK)
        self.assertContains(inbox, "Ana María Pérez López")
        self.assertContains(inbox, "ana@example.com")
        self.assertContains(inbox, "Descargar TXT")
        self.assertContains(inbox, 'class="application-search"', html=False)
        self.assertContains(inbox, 'id="application-search-suggestions"', html=False)
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
        self.assertEqual(download.status_code, status.HTTP_200_OK)
        self.assertEqual(b"".join(download.streaming_content), b"private document")

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
                    "label": f"#{application.pk} · Ana Pérez · Apostillamiento Consulado",
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
        self.assertIn("Documentos adjuntos: 1", export)
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
