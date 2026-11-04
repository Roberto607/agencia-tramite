from django.db import migrations, models


def copy_existing_service(apps, schema_editor):
    Application = apps.get_model("applications", "Application")
    for application in Application.objects.only("pk", "service_type").iterator():
        application.selected_services = [application.service_type]
        application.save(update_fields=("selected_services",))


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0003_application_service_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="selected_services",
            field=models.JSONField(default=list),
        ),
        migrations.RunPython(copy_existing_service, migrations.RunPython.noop),
    ]
