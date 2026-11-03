from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_names", models.CharField(max_length=120)),
                ("last_names", models.CharField(max_length=120)),
                (
                    "identification_type",
                    models.CharField(
                        choices=[
                            ("cedula", "Cédula de ciudadanía"),
                            ("extranjeria", "Cédula de extranjería"),
                            ("pasaporte", "Pasaporte"),
                            ("nit", "NIT"),
                            ("otro", "Otro"),
                        ],
                        max_length=20,
                    ),
                ),
                ("identification_number", models.CharField(max_length=40)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("photo", models.ImageField(blank=True, null=True, upload_to="applications/photos/%Y/%m/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ApplicationDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="applications/documents/%Y/%m/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="applications.application",
                    ),
                ),
            ],
            options={"ordering": ["uploaded_at", "pk"]},
        ),
    ]
