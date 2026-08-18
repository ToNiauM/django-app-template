from django.contrib import admin
from django.urls import include, path

from core.views import healthz


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    # core.urls carrega o namespace "core" (login/logout/casca) — a rota ""
    # dela (`core:shell`) atende a raiz do Walking Skeleton desta fase.
    path("", include("core.urls")),
]
