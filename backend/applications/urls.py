from django.urls import path

from .views import ApplicationCreateView, health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("applications/", ApplicationCreateView.as_view(), name="application-create"),
]
