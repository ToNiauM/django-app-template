"""
Settings comuns a todos os ambientes (dev/prod).

Toda configuração sensível (SECRET_KEY, credenciais de banco, etc.) vem do
`.env` via django-environ — nunca hard-coded aqui (CFG-01).
"""

from datetime import timedelta
from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "core.apps.CoreConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django_htmx",
    "axes",
    "core",
]

# A ordem do MIDDLEWARE é normativa — não reordenar sem entender o motivo
# de cada posição (ver 01-RESEARCH.md, "ponto crítico desta fase").
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "core.middleware.HtmxRedirectMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
]

AUTH_USER_MODEL = "core.Usuario"

# Argon2 no topo — vencedor da Password Hashing Competition; PBKDF2 fica
# como fallback de leitura para hashes antigos (CFG-02).
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",  # sempre ANTES do ModelBackend padrão
    "django.contrib.auth.backends.ModelBackend",
]

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=env.int("AXES_COOLOFF_MINUTES", default=15))
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]  # nunca só "username"

# Django SEMPRE usa o kwarg literal "username" em authenticate(), mesmo com
# USERNAME_FIELD="email" no model customizado. Sem esta linha, o axes procura
# "email" no dict de credenciais — chave que nunca existe — e grava toda
# tentativa com username=None, quebrando o lockout por usuário+IP em silêncio.
AXES_USERNAME_FORM_FIELD = "username"

# Sem isto, AxesMiddleware substitui a resposta de QUALQUER view por uma
# página de bloqueio genérica sempre que axes_locked_out é True — mesmo
# quando a view já devolveu o fragmento HTMX correto em HTTP 200.
AXES_LOCKOUT_CALLABLE = "core.axes_lockout.resposta_bloqueio"

LOGIN_URL = "/login/"

SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=28800)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.usuario_atual",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Localização (CFG-03).
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Sempre o dict STORAGES — a chave de configuração de storage de estáticos
# de versões antigas do Django foi removida no Django 5.1.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
# htmx lê o cookie a cada requisição (htmx:configRequest); True quebraria
# 100% das escritas HTMX (CFG-04).
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_USE_SESSIONS = False
