from django.conf import settings


def usuario_atual(request):
    """Expõe o usuário autenticado ao template — usado no layout base (ex.:
    nome/e-mail no cabeçalho) sem cada view precisar passá-lo explicitamente."""
    return {"usuario_atual": getattr(request, "user", None)}


def identidade(request):
    """Expõe a identidade parametrizada do sistema (D-16) a todo template —
    shell, login, admin e PWA consomem nome/sigla/cor daqui, para que a
    identidade tenha uma única fonte (`.env` → settings) em vez de valores
    espalhados pelos templates."""
    return {
        "sistema_nome": settings.SISTEMA_NOME,
        "sistema_sigla": settings.SISTEMA_SIGLA,
        "cor_primaria": settings.COR_PRIMARIA,
    }
