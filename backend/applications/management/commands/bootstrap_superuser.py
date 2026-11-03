import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the initial admin account from environment variables, if configured."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
        values = (username, email, password)

        if not any(values):
            return
        if not all(values):
            raise CommandError(
                "Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, "
                "and DJANGO_SUPERUSER_PASSWORD together."
            )

        user_model = get_user_model()
        username_field = user_model.USERNAME_FIELD
        try:
            existing_user = user_model._default_manager.get(
                **{username_field: username}
            )
        except user_model.DoesNotExist:
            user_model._default_manager.create_superuser(
                **{username_field: username},
                email=email,
                password=password,
            )
            self.stdout.write("Initial admin account created.")
            return

        if not existing_user.is_superuser:
            raise CommandError(
                "The configured admin username already exists and is not a superuser."
            )
        self.stdout.write("Configured admin account already exists; no changes made.")
