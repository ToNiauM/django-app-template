from django.contrib.auth.decorators import login_not_required
from django.db import connection
from django.http import JsonResponse


@login_not_required
def healthz(request):
    """Rota de healthcheck (usada pelo `compose.yml` — Plan 01-03).

    Sem `@login_not_required`, o `LoginRequiredMiddleware` (Pitfall 9)
    redirecionaria toda requisição sem sessão para `/login/`, quebrando o
    healthcheck do container.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})
