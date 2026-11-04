from django.urls import path

from .views import (
    ApplicationCreateView,
    ClientLoginView,
    ClientRegistrationView,
    health_check,
)

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("register/", ClientRegistrationView.as_view(), name="client-registration"),
    path("login/", ClientLoginView.as_view(), name="client-login"),
    path("applications/", ApplicationCreateView.as_view(), name="application-create"),
]
