from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("admin:login"), permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("applications.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
