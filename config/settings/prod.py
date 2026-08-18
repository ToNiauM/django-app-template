from .base import *  # noqa: F403


DEBUG = False

# 127.0.0.1 sempre presente — é quem o healthz interno do compose usa.
ALLOWED_HOSTS = list(set(env.list("ALLOWED_HOSTS", default=[]) + ["127.0.0.1"]))  # noqa: F405

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
# Sem isto o healthcheck do compose (HTTP puro, interno) entra em loop de
# redirect contra o SECURE_SSL_REDIRECT acima.
SECURE_REDIRECT_EXEMPT = [r"^healthz$"]
USE_X_FORWARDED_HOST = False

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# W005/W021 correspondem exatamente às duas flags de HSTS acima
# (SECURE_HSTS_INCLUDE_SUBDOMAINS / SECURE_HSTS_PRELOAD), deliberadamente
# False: opt-in em subdomínios/preload é decisão de operação real, fora do
# escopo deste template genérico.
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]

AXES_IPWARE_PROXY_COUNT = 2
AXES_IPWARE_META_PRECEDENCE_ORDER = ("HTTP_X_FORWARDED_FOR", "REMOTE_ADDR")
