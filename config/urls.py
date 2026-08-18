from django.contrib import admin
from django.urls import include, path

from core.views import healthz


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    # Apps de domínio do sistema (ponto de integração 2 de 3 - D-34)
    path("exemplo/", include("apps.exemplo.urls")),
    # core.urls carrega o namespace "core" (login/logout/casca) — a rota ""
    # dela (`core:shell`) atende a raiz do Walking Skeleton desta fase.
    path("", include("core.urls")),
]
