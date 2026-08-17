# Phase 1: Fundação Django - Research

**Researched:** 2026-08-17
**Domain:** Projeto Django 5.2 LTS "plano" (não-Copier ainda) com PostgreSQL 17 em Docker Compose, usuário customizado por e-mail, settings por ambiente com invariantes de segurança/localização da PCA, e convenção CSRF/HTMX
**Confidence:** HIGH (todo o núcleo técnico foi extraído de `/opt/web/pca`, sistema em produção que roda exatamente esta combinação de versões; pacotes confirmados no PyPI e via `slopcheck`)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

*(Modo `--auto`: decisões selecionadas automaticamente com a opção recomendada, ancoradas na PCA — fonte de extração declarada em PROJECT.md.)*

**Estratégia de desenvolvimento**
- **D-01:** O repositório é desenvolvido como projeto Django "plano" e executável na raiz (`manage.py`, `config/`, `core/`, `apps/`). A parametrização Copier (jinja, `copier.yml`) só entra na Fase 4. Motivo: permite validar cada fase rodando o sistema de verdade, e a templatização é uma transformação mecânica no final.

**Autenticação**
- **D-02:** Login por **e-mail** — `USERNAME_FIELD = "email"`, sem campo `username`. Espelha a PCA (`/opt/web/pca/core/models.py`): `UsuarioManager(BaseUserManager)` com `use_in_migrations = True`, `create_user`/`create_superuser` recebendo `email` como primeiro argumento posicional.
- **D-03:** `AUTH_USER_MODEL = "core.Usuario"` definido desde a migração 0001 do `core` (invariante para não inviabilizar SSO futuro).
- **D-04:** `django-axes` configurado com lockout customizado (a PCA tem `core/axes_lockout.py` e nota em `base.py` sobre `USERNAME_FIELD="email"` — replicar o padrão).

**Settings e configuração**
- **D-05:** Settings em módulos por ambiente: `config/settings/base.py` + `dev.py` + `prod.py`, selecionados por `DJANGO_SETTINGS_MODULE`, com `django-environ` lendo tudo do `.env`. Espelha a PCA.
- **D-06:** Dependências via `requirements.txt` (padrão da PCA; sem poetry/uv/pyproject nesta fase).

**Docker e assets**
- **D-07:** Tailwind compilado em **estágio multi-stage do Dockerfile** (`node:20-alpine` rodando `npx tailwindcss@3.4.17 --minify`), com guarda de tamanho do CSS gerado (falha o build se só o preflight for emitido — padrão comentado no Dockerfile da PCA). Nenhuma dependência de node no host.
- **D-08:** Runtime `python:3.12-slim`, Gunicorn atrás do proxy, app escutando só em `127.0.0.1` no host (publicação de porta restrita), WhiteNoise para estáticos.

### Claude's Discretion

- Detalhes de `compose.yml`, `entrypoint.sh` e healthchecks: extrair o padrão da PCA e generalizar (remover qualquer menção a PCA/domínio).
- Estrutura exata da tela de login desta fase: mínima e funcional; a identidade visual completa (shell, navegação) é a Fase 2.
- Versões exatas de dependências: partir do `requirements.txt` da PCA, atualizando patches quando seguro.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope (modo auto, sem novas capacidades sugeridas).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| CFG-01 | `config/` com settings por ambiente via `django-environ` — toda config sensível vem do `.env` | Pattern 1 (Settings por ambiente), Code Examples (`.env.example` completo) |
| CFG-02 | Settings de produção aplicam Argon2 no topo de `PASSWORD_HASHERS`, `django-axes`, cookies `Secure`/`HttpOnly`/`SameSite=Lax`, HSTS/`SECURE_PROXY_SSL_HEADER`, `DEBUG=False`, `ALLOWED_HOSTS` restrito | Pattern 3 (`django-axes` + email), Pitfalls 3/4/6, Security Domain (V2/V3/V6) |
| CFG-03 | Localização padrão: pt-br, America/Sao_Paulo, `USE_TZ=True`, datas DD/MM/AAAA, moeda R$ | Pitfall 7 (collation ICU pt-BR), Pitfall 8 (`localdate()`), Pattern 6 (`POSTGRES_INITDB_ARGS`) |
| CFG-04 | `CSRF_COOKIE_HTTPONLY = False` com CSRF do HTMX via `htmx:configRequest` (nunca `hx-headers`) | Pattern 4 (CSRF via `htmx:configRequest`), Anti-Patterns, Pitfalls 1/2 |
| CORE-01 | `Usuario` customizado (AbstractUser) com manager próprio, desde a primeira migração | Pattern 2 (Usuario + UsuarioManager), Recommended Project Structure |
| CORE-02 | Login e logout pela tela de login | Pattern 3 (view de login/axes), Pitfalls 1/2/9, Code Examples (`LoginFlowTests`) |
| INF-01 | `docker compose up -d` sobe app + PostgreSQL 17 via `Dockerfile`/`compose.yml`/`entrypoint.sh` | Pattern 5 (Dockerfile multi-stage), Pattern 6 (compose.yml + healthcheck), Pitfall 10, Environment Availability |
| INF-02 | `.env.example` completo cobrindo todas as variáveis | Code Examples (`.env.example` desta fase) |
</phase_requirements>

## Summary

Esta fase reproduz, de forma generalizada e sem menção a "PCA", o kernel de fundação que já está provado em produção em `/opt/web/pca`: `config/settings/{base,dev,prod}.py` com `django-environ`, um `Usuario` customizado por e-mail (`AbstractUser` + `UsuarioManager` próprio) presente desde a migração `0001` do app `core`, `django-axes` com o callable de lockout que preserva a convenção HTTP 200 do HTMX, e a leitura do token CSRF via `htmx:configRequest` no cookie (nunca `hx-headers`). A infraestrutura é um `Dockerfile` multi-stage (Node 20 só para compilar Tailwind, descartado; runtime `python:3.12-slim` com Gunicorn) e um `compose.yml` com `db` (Postgres 17, collation ICU pt-BR) + `web`, ambos com healthcheck, e o app escutando só em `127.0.0.1`.

O ponto crítico desta fase não é nenhuma peça isolada — é a **ordem e a interação** entre elas: middleware (`AuthenticationMiddleware` → `HistoryRequestMiddleware`* → `HtmxMiddleware` → `HtmxRedirectMiddleware` → `AxesMiddleware` → `LoginRequiredMiddleware`), a resolução de `USERNAME_FIELD="email"` dentro do `axes` (que exige `AXES_USERNAME_FORM_FIELD = "username"`, um detalhe nada óbvio), e o fato de `STORAGES`/`collectstatic` terem que rodar **no build da imagem**, nunca no entrypoint, para não violar o invariante de portabilidade. (*`HistoryRequestMiddleware`/`simple_history` só entram na Fase 2 junto com `django-simple-history`; nesta fase o middleware fica sem essa linha.)

Todos os pacotes Python recomendados são bibliotecas antigas e amplamente usadas (8–18 anos de existência no PyPI, todas com repositório-fonte público), verificadas tanto no índice do PyPI quanto pelo `slopcheck` (10/10 `[OK]`, nenhum `[SLOP]`/`[SUS]`).

**Primary recommendation:** Copiar literalmente a topologia de settings/middleware/axes/CSRF da PCA (ela já resolveu as armadilhas), mas **reduzir o escopo de pacotes ao que a Fase 1 realmente usa** — sem `django-simple-history` (entra na Fase 2 com `CORE-06`) e sem `openpyxl` (não há import de planilha no escopo deste template) — e **não tornar o volume do Postgres `external`** neste estágio, para que `docker compose up -d` funcione sozinho no primeiro clone, sem passo manual (`docker volume create`) que quebraria o critério de sucesso 1.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Orquestração `app` + PostgreSQL 17 | Infra / Docker Compose | Database | `compose.yml` define os dois serviços, rede e volumes; nenhuma dependência do host além do Docker |
| `Usuario` customizado + migração 0001 | Database / Backend (Django ORM) | — | Modelo + manager vivem em `core/models.py`; a migração é a fonte de verdade do schema |
| Settings por ambiente (`django-environ`) | Backend Server (Django settings) | — | `config/settings/{base,dev,prod}.py` — carregado no processo Django, nunca no cliente |
| Invariantes de segurança (Argon2, axes, cookies, HSTS) | Backend Server | Browser (cookies `Secure`/`SameSite`) | Hashers e axes rodam no processo Django; cookies são o contrato com o browser |
| Localização (pt-br/America/Sao_Paulo) | Backend Server | Browser (renderização de datas nos templates) | `LANGUAGE_CODE`/`TIME_ZONE` no settings; efeito visível nos templates renderizados no servidor |
| Login/Logout (view + template) | Backend Server (view) | Browser (formulário HTMX) | View faz `authenticate()`/`login()`; o HTML é servido pelo Django, HTMX só troca fragmentos |
| CSRF via `htmx:configRequest` | Browser / Client | Backend Server (`CSRF_COOKIE_HTTPONLY=False`) | O JS síncrono em `base.html` lê o cookie a cada request; o settings só precisa não bloquear a leitura |
| Estáticos (Tailwind compilado) | CDN / Static (WhiteNoise) | Build (Docker multi-stage) | Compilado uma vez no build, servido por `WhiteNoiseMiddleware` com hashing/gzip |
| Migração + subida do container | Infra / Docker | Backend Server | `entrypoint.sh` roda `migrate` antes de `exec gunicorn`; `healthcheck` depende disso |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `Django` | `5.2.17` [VERIFIED: PyPI/pip index] | Framework web | LTS até ~abr/2028; PCA roda `5.2.16` em produção — `5.2.17` é o patch mais recente da mesma LTS (Django 5.2 release notes, `docs.djangoproject.com`) |
| `psycopg[binary]` | `3.3.4` [VERIFIED: PyPI/pip index] | Driver PostgreSQL | psycopg3, extra `[binary]` evita exigir `libpq-dev` na imagem runtime; mesma versão validada em produção na PCA |
| `django-environ` | `0.14.0` [VERIFIED: PyPI/pip index] | Settings via `.env` (`env.db`, `env.list`, `env.bool`) | CFG-01 exige toda config sensível vinda do `.env`; é a lib usada pela PCA |
| `django-axes` | `8.3.1` [VERIFIED: PyPI/pip index] | Lockout de login por tentativas | CFG-02; compatível com Django 5.2 (comprovado em produção na PCA) |
| `django-htmx` | `1.29.0` [VERIFIED: PyPI/pip index] | Middleware `HtmxMiddleware` (popula `request.htmx`), `HttpResponseClientRedirect` | Necessário para o padrão `HX-Redirect` (nunca `redirect()` puro em view HTMX) e para o `HtmxRedirectMiddleware` |
| `argon2-cffi` | `25.1.0` [VERIFIED: PyPI/pip index] | Backend do `Argon2PasswordHasher` | CFG-02 exige Argon2 no topo de `PASSWORD_HASHERS`; sem este pacote o hasher não fica disponível (Django docs, `password_hashers`) |
| `whitenoise` | `6.12.0` [VERIFIED: PyPI/pip index] | Serve estáticos direto do processo Gunicorn | D-08; `CompressedManifestStaticFilesStorage` precisa do dict `STORAGES` (Django ≥4.2; `STATICFILES_STORAGE` foi **removido** no 5.1) |
| `gunicorn` | `26.0.0` [VERIFIED: PyPI/pip index] | Servidor WSGI de produção | D-08, atrás do proxy do host |
| `django-ipware` | `7.0.1` [VERIFIED: PyPI/pip index] | Resolução de IP real atrás de proxy (`AXES_IPWARE_*`) | Sem ele, `AXES_IPWARE_PROXY_COUNT` é um no-op silencioso e o lockout por usuário+IP colapsa para "só por usuário" atrás do proxy |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `tailwindcss` (npm, estágio de build) | `3.4.17` [CITED: decisão D-07 do CONTEXT.md, ancorada no `Dockerfile` da PCA] | Compilação do CSS utilitário | Só dentro do estágio `node:20-alpine` do Dockerfile; nunca como dependência do host |
| `htmx.org` | `1.9.12` (recomendado) ou `2.0.10` (mais recente) [ASSUMED — ver Open Questions] | Interatividade sem SPA | Vendorizado em `core/static/vendor/htmx.min.js`, baixado uma vez e commitado — nunca via CDN em runtime (offline-first / portabilidade) |
| `alpinejs` | `3.16.2` [ASSUMED — última 3.x estável, ver Open Questions] | Estado reativo leve nos templates | Vendorizado do mesmo jeito que o htmx |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `django-axes` | Rate limiting manual (cache + middleware próprio) | Reinventa lockout, throttling e IP-resolution que o axes já resolve e testa; fora de escopo do "não hand-roll" |
| `psycopg[binary]` | `psycopg2-binary` | psycopg3 é o driver atual recomendado pelo Django ≥4.2 e é o que a PCA já valida em produção; psycopg2 é legado |
| `WhiteNoise` | Servir estáticos via Nginx do host | Quebraria o invariante de portabilidade (container autossuficiente); Nginx do host é reverse proxy, não deve conhecer o filesystem do app |
| Vendorizar htmx/alpine | `django-htmx`/CDN em runtime | CDN em runtime quebra o offline-first e adiciona dependência de rede externa em cada boot; vendorizar é o padrão já usado pela PCA |

**Installation:**
```bash
pip install \
  "Django==5.2.17" \
  "psycopg[binary]==3.3.4" \
  "django-environ==0.14.0" \
  "django-axes==8.3.1" \
  "django-htmx==1.29.0" \
  "argon2-cffi==25.1.0" \
  "whitenoise==6.12.0" \
  "gunicorn==26.0.0" \
  "django-ipware==7.0.1"
```

**Version verification:** Todas as versões acima foram confirmadas via `pip index versions <pkg>` contra o PyPI nesta sessão de pesquisa (2026-08-17). `Django==5.2.17` é o patch mais recente da série 5.2 LTS (a PCA está em `5.2.16`, um patch atrás — seguro atualizar, é a mesma LTS). **Não incluído nesta fase, de propósito:** `django-simple-history` (entra na Fase 2, requisito `CORE-06`) e `openpyxl` (a PCA usa para import de planilha; este template não tem essa funcionalidade em `apps/exemplo`).

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| `django` | PyPI | ~16 anos (primeiro release 2010) | muito alto (framework major) | github.com/django/django | [OK] | Approved |
| `psycopg[binary]` | PyPI | ~5 anos (psycopg3, sucessor do psycopg2 de 2010) | alto | github.com/psycopg/psycopg | [OK] | Approved |
| `django-environ` | PyPI | ~13 anos | alto | github.com/joke2k/django-environ | [OK] | Approved |
| `django-axes` | PyPI | ~18 anos (projeto Jazzband) | alto | github.com/jazzband/django-axes | [OK] | Approved |
| `django-htmx` | PyPI | ~6 anos | alto | github.com/adamchainz/django-htmx | [OK] | Approved |
| `argon2-cffi` | PyPI | ~11 anos | alto | github.com/hynek/argon2-cffi | [OK] | Approved |
| `whitenoise` | PyPI | ~13 anos | alto | github.com/evansd/whitenoise | [OK] | Approved |
| `gunicorn` | PyPI | ~16 anos | muito alto | github.com/benoitc/gunicorn | [OK] | Approved |
| `django-ipware` | PyPI | ~13 anos | médio-alto | github.com/un33k/django-ipware | [OK] | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** nenhum.
**Packages flagged as suspicious [SUS]:** nenhum.

Todos os 9 pacotes passaram por `slopcheck install <pkgs>` nesta sessão (rodado contra o índice do PyPI) com veredito `[OK]` para os 9 — nenhum `[SLOP]`/`[SUS]`. Idade e presença de repositório-fonte foram confirmadas via a API JSON do PyPI (primeira data de upload de qualquer release). Nomes de pacote também batem com os já usados em produção em `/opt/web/pca/requirements.txt` (fonte de extração declarada), o que reduz o risco de confusão de nome a praticamente zero.

## Architecture Patterns

### System Architecture Diagram

```
Cliente (browser)
    │  GET /login/          POST /login/ (form, hx-post)
    ▼                             │
┌─────────────────────────────────┼───────────────────────────────┐
│  Container "web" (Gunicorn, 127.0.0.1:8000)                     │
│                                                                   │
│  entrypoint.sh: migrate --noinput  →  exec gunicorn              │
│                                                                   │
│  MIDDLEWARE (ordem importa):                                     │
│   SecurityMiddleware → XFrameOptionsMiddleware →                 │
│   SessionMiddleware → WhiteNoiseMiddleware → CommonMiddleware →  │
│   CsrfViewMiddleware → AuthenticationMiddleware →                │
│   HtmxMiddleware → HtmxRedirectMiddleware →                      │
│   AxesMiddleware → MessageMiddleware → LoginRequiredMiddleware   │
│                                                                   │
│  core.views.login_view                                           │
│    ├─ authenticate(request, username=email, password=senha)      │
│    │     └─ AXES_USERNAME_FORM_FIELD="username" (não é o email!) │
│    ├─ falha → TemplateResponse 200 (nunca 4xx) com fragmento erro │
│    └─ sucesso → login(request, user) + HttpResponseClientRedirect│
│                                                                   │
│  core.models.Usuario (AbstractUser, USERNAME_FIELD="email")      │
│    └─ UsuarioManager.create_user/create_superuser(email, senha)  │
│                                                                   │
│  WhiteNoiseMiddleware serve /static/dist/tailwind.css            │
│  (compilado no build da imagem, nunca no entrypoint)             │
└──────────────────────┬───────────────────────────────────────────┘
                        │  DATABASE_URL (django-environ → env.db)
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  Container "db" — postgres:17, locale ICU pt-BR                │
│  Volume nomeado (não-external nesta fase) → dados persistem    │
│  entre `docker compose down` / `up`, mas NÃO sobrevivem a       │
│  `down -v` (aceitável: ainda não há dado de produção a proteger)│
└───────────────────────────────────────────────────────────────┘

Navegador, depois do <body> carregar (base.html):
  document.body.addEventListener("htmx:configRequest", (e) => {
    e.detail.headers["X-CSRFToken"] = lerCookie("csrftoken");
  });
  → todo POST/PUT/DELETE feito pelo htmx carrega o token FRESCO,
    lido do cookie a cada requisição — nunca congelado em hx-headers.
```

### Recommended Project Structure
```
/ (raiz do repo, projeto Django "plano" — D-01, sem Copier ainda)
├── manage.py
├── requirements.txt
├── Dockerfile                  # multi-stage: node:20-alpine (tailwind) → python:3.12-slim
├── compose.yml                 # serviços: db (postgres:17) + web
├── entrypoint.sh                # migrate --noinput && exec gunicorn
├── tailwind.config.js
├── .env.example                 # cobre TODAS as variáveis (INF-02)
├── config/
│   ├── __init__.py
│   ├── urls.py                  # inclui core.urls
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py               # comum: apps, middleware, axes, localização
│       ├── dev.py                 # from .base import *; DEBUG=True; storage sem manifest
│       └── prod.py                # from .base import *; DEBUG=False; proxy/HSTS/ALLOWED_HOSTS
├── core/                          # app kernel agnóstico de domínio
│   ├── apps.py
│   ├── models.py                   # Usuario + UsuarioManager
│   ├── migrations/
│   │   └── 0001_initial.py          # Usuario já aqui — invariante SSO
│   ├── views.py                     # login_view, logout_view, healthz
│   ├── urls.py                      # app_name="core"
│   ├── axes_lockout.py              # AXES_LOCKOUT_CALLABLE
│   ├── context_processors.py        # usuario_atual (mínimo desta fase)
│   ├── templates/
│   │   ├── base.html                 # <script> htmx:configRequest aqui
│   │   └── core/
│   │       ├── login.html
│   │       └── _login_form.html      # fragmento reusado no erro/bloqueio
│   ├── static/
│   │   ├── src/input.css              # @tailwind base/components/utilities
│   │   ├── dist/                       # gerado no build, gitignored
│   │   └── vendor/                     # htmx.min.js, alpine.min.js (commitados)
│   └── tests/
│       ├── test_auth.py
│       └── test_login_flow.py
```

### Pattern 1: Settings por ambiente com `django-environ`

**What:** `base.py` lê `.env` uma vez e define tudo comum; `dev.py`/`prod.py` fazem `from .base import *` e sobrescrevem só o que diverge.

**When to use:** Sempre — é a única forma de satisfazer CFG-01 (toda config sensível do `.env`) sem duplicar `INSTALLED_APPS`/`MIDDLEWARE` entre ambientes.

**Example:**
```python
# Source: /opt/web/pca/config/settings/base.py (produção, extraído e generalizado)
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DATABASES = {"default": env.db("DATABASE_URL")}
```
```python
# config/settings/dev.py
from .base import *  # noqa: F403
DEBUG = env.bool("DEBUG", default=True)  # noqa: F405
ALLOWED_HOSTS = ["*"]
```
```python
# config/settings/prod.py
from .base import *  # noqa: F403
DEBUG = False
ALLOWED_HOSTS = list(set(env.list("ALLOWED_HOSTS", default=[]) + ["127.0.0.1"]))  # noqa: F405
```
`DJANGO_SETTINGS_MODULE` no `.env` (`config.settings.dev` ou `config.settings.prod`) seleciona o módulo — `manage.py`/`wsgi.py` usam `config.settings.dev` como default local.

### Pattern 2: Usuario customizado por e-mail desde a migração 0001

**What:** `AbstractUser` sem `username`, `USERNAME_FIELD="email"`, manager próprio com `use_in_migrations = True`.

**When to use:** Único caminho aceitável para CORE-01/D-02/D-03 — trocar o modelo de usuário depois da primeira migração é uma operação destrutiva em Django (o invariante de SSO futuro do PROJECT.md exige isto **desde o início**).

**Example:**
```python
# Source: /opt/web/pca/core/models.py (verbatim — sem nada específico de domínio)
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    username = None
    email = models.EmailField("e-mail", unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UsuarioManager()

    def __str__(self):
        return self.email
```
**Diferença importante em relação à migração `0001` da PCA:** a PCA já registra `django-simple-history` desde a 0001 (fora do escopo desta fase — `CORE-06` é Fase 2). A migração `0001` gerada nesta fase deve conter **só** `Usuario` (sem `HistoricalUsuario`); a Fase 2 adiciona o histórico numa migração nova (`0002` ou posterior), sem quebrar dado nenhum — `simple_history.register()`/`HistoricalRecords` sempre podem ser adicionados depois, é uma migração aditiva.

### Pattern 3: `django-axes` com usuário customizado por e-mail

**What:** Três ajustes não-óbvios para o axes funcionar corretamente com `USERNAME_FIELD="email"`.

**When to use:** Sempre que o `User` customizado não usa `username` — é exatamente este projeto.

**Example:**
```python
# Source: /opt/web/pca/config/settings/base.py (comentários explicam o "porquê")
from datetime import timedelta

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",   # sempre ANTES do ModelBackend padrão
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
```
```python
# core/axes_lockout.py
def resposta_bloqueio(request, original_response, credentials=None):
    return original_response
```
E na view (`authenticate` de alto nível **nunca propaga** o `PermissionDenied` do axes — só devolve `None`; distinga "bloqueado" de "senha errada" via `request.axes_locked_out`):
```python
# Source: /opt/web/pca/core/views.py (padrão de view, generalizado)
user = authenticate(request, username=email, password=senha)
if user is None:
    bloqueado = bool(getattr(request, "axes_locked_out", False))
    return TemplateResponse(request, "core/_login_form.html",
                             {"email": email, "bloqueado": bloqueado, "erro": not bloqueado},
                             status=200)  # nunca 4xx puro — HTMX não faz swap por padrão
login(request, user)
return HttpResponseClientRedirect(request.GET.get("next") or "/")
```

### Pattern 4: CSRF do HTMX via `htmx:configRequest` (CFG-04)

**What:** Ler o cookie `csrftoken` a cada requisição HTMX, nunca injetar num `hx-headers` estático.

**When to use:** Sempre — é invariante do projeto, não uma opção.

**Example:**
```javascript
// Source: /opt/web/pca/core/templates/base.html (verbatim, sem nada de domínio)
function csrfCookie(nome) {
  const match = document.cookie.match("(^|;)\\s*" + nome + "\\s*=\\s*([^;]+)");
  return match ? decodeURIComponent(match.pop()) : null;
}
document.body.addEventListener("htmx:configRequest", (evento) => {
  evento.detail.headers["X-CSRFToken"] = csrfCookie("csrftoken");
});
```
```python
# config/settings/base.py — consequência obrigatória do padrão acima
CSRF_COOKIE_HTTPONLY = False  # htmx lê o cookie; True quebra 100% das escritas
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_USE_SESSIONS = False
```

### Pattern 5: Dockerfile multi-stage com guarda de tamanho do CSS

**What:** Estágio `node:20-alpine` compila o Tailwind e falha o build se o CSS gerado for pequeno demais (sinal de que os `content` globs não casaram com nenhum template).

**When to use:** Sempre que o build depende de purge de classes usadas em templates — é o único jeito barato de pegar "esqueci de apontar o glob" antes do deploy.

**Example:**
```dockerfile
# Source: /opt/web/pca/Dockerfile (generalizado — sem paths específicos de domínio)
FROM node:20-alpine AS assets
WORKDIR /build
COPY tailwind.config.js ./
COPY core/static/src/input.css ./core/static/src/input.css
COPY core/templates ./core/templates
RUN npx --yes tailwindcss@3.4.17 \
    -i ./core/static/src/input.css -o ./core/static/dist/tailwind.css --minify \
    && CSS_BYTES=$(wc -c < ./core/static/dist/tailwind.css) \
    && echo "tailwind.css gerado: ${CSS_BYTES} bytes" \
    && if [ "$CSS_BYTES" -lt 6000 ]; then \
         echo "ERRO: CSS pequeno demais — os content globs não casaram com nenhum template." >&2; \
         exit 1; \
       fi

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=assets /build/core/static/dist/tailwind.css ./core/static/dist/tailwind.css
RUN SECRET_KEY=build DATABASE_URL=sqlite:///tmp/build.db DJANGO_SETTINGS_MODULE=config.settings.prod \
    python manage.py collectstatic --noinput
RUN chmod +x /app/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
```
**Nota sobre o limiar de bytes:** a PCA usa `10000` (10 KB) porque o template dela já carrega um design system completo. Nesta fase, com só `base.html` + `login.html` (poucas classes utilitárias), o CSS "sem estilo" (só preflight) fica em ~4,7 KB — um limiar de **6000** é um piso seguro para pegar a falha real sem exigir volume de classes que a Fase 1 ainda não tem. **Recalibrar este número após o primeiro build real** (ver Pitfall abaixo) e novamente na Fase 2, quando o shell visual completo aumentar o volume de classes usadas.

### Pattern 6: `compose.yml` com healthcheck e `start_period` cobrindo o `migrate`

**What:** `db` com `healthcheck` de `pg_isready`; `web` depende de `db: condition: service_healthy`; `entrypoint.sh` roda `migrate --noinput` **antes** de `exec gunicorn`; `healthcheck` do `web` com `start_period` generoso.

**Example:**
```yaml
# Source: /opt/web/pca/compose.yml (generalizado — sem imagem pinada em registry,
# sem volume external, sem o serviço `backup` que é INF-03/Fase 4)
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--locale-provider=icu --icu-locale=pt-BR --encoding=UTF8"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 30s

  web:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - .env
    ports:
      - "${WEB_BIND_ADDRESS}:${WEB_PORT}:8000"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://127.0.0.1:8000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 120s

volumes:
  pgdata:
    # NÃO external nesta fase (diferente da PCA): o critério de sucesso 1
    # exige que `docker compose up -d` funcione sozinho no primeiro clone.
    # Um volume `external: true` falharia com "volume not found" sem o passo
    # manual `docker volume create` — acoplamento indevido para esta fase.
```
```bash
#!/bin/sh
# entrypoint.sh — Source: /opt/web/pca/entrypoint.sh (verbatim)
set -eu
python manage.py migrate --noinput
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Anti-Patterns to Avoid
- **`redirect()` puro em view acessada via HTMX:** o XHR segue o 302 de forma transparente e injeta a página inteira (com `<html>`/sidebar) dentro do alvo do swap. Use `django_htmx.http.HttpResponseClientRedirect` + `HtmxRedirectMiddleware` para o caso genérico (ex.: expiração de sessão).
- **`hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'` no `<body>`:** congela o token no momento do render; Django gira o token (`rotate_token()`) no login/logout e `hx-boost` não reescreve `<body>` — o token fica obsoleto. Leia sempre do cookie via `htmx:configRequest`.
- **`CSRF_COOKIE_HTTPONLY = True` como "hardening":** quebra 100% das escritas HTMX (não é vulnerabilidade real — a doc do Django não recomenda isso como proteção prática — é indisponibilidade).
- **`collectstatic` no `entrypoint.sh`:** torna o container dependente de rodar isso toda vez que sobe, adiciona tempo de boot e — pior — quebra o invariante de portabilidade (a imagem deixa de ser autossuficiente). Rode sempre no **build**.
- **Trocar `AUTH_USER_MODEL` depois da migração 0001:** operação destrutiva em Django; é exatamente o que este fase existe para evitar (D-03, invariante de SSO futuro).
- **Publicar a porta do `web` sem `WEB_BIND_ADDRESS=127.0.0.1`:** expõe o Django direto na rede, sem TLS/proxy — viola D-08 e o invariante de portabilidade (deploy = proxy do host cuida de TLS).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Lockout de tentativas de login | Contador manual em cache/Redis | `django-axes` (`AXES_FAILURE_LIMIT`, `AXES_LOCKOUT_PARAMETERS`) | Já resolve IP-resolution atrás de proxy, cooloff, reset em login bem-sucedido, e tem `AXES_LOCKOUT_CALLABLE` para integrar com a convenção HTTP 200 do HTMX |
| Hash de senha | Wrapper próprio sobre `hashlib` | `argon2-cffi` + `PASSWORD_HASHERS` do Django | Argon2 é o vencedor da Password Hashing Competition; Django já tem suporte de primeira classe via `Argon2PasswordHasher` |
| Servir estáticos com cache-busting | Nome de arquivo com hash manual | `whitenoise.storage.CompressedManifestStaticFilesStorage` (via `STORAGES`) | Já faz gzip/brotli, hash de conteúdo e manifest — reimplementar é retrabalho puro |
| Leitura de config por ambiente | `os.environ.get(...)` espalhado + parsing manual de listas/bools | `django-environ` (`env.db`, `env.list`, `env.bool`, `env.int`) | Parsing de `DATABASE_URL`, listas separadas por vírgula e booleans já testado; espalhar `os.environ.get` pelo código é o oposto de CFG-01 |
| Redirect que funcione tanto para navegação normal quanto HTMX | `if request.htmx: ... else: redirect(...)` em cada view | `django_htmx.http.HttpResponseClientRedirect` + `HtmxRedirectMiddleware` central | Um middleware cobre TODAS as views automaticamente; view por view é fonte garantida de esquecimento |

**Key insight:** Nada nesta fase é "problema novo" — é reprodução deliberada de decisões já validadas em produção na PCA. O risco real não é escolher a lib errada, é **desviar da ordem/composição exata** (middleware, `AUTHENTICATION_BACKENDS`, settings de CSRF) que a PCA já descobriu, na marra, que precisa ser assim.

## Common Pitfalls

### Pitfall 1: HTMX não faz swap de respostas 4xx — erro de login "desaparece"

**What goes wrong:** Se a view de login devolver `401`/`403`/`422` no caminho de erro, o fragmento HTML nunca é trocado na tela — o usuário reclica achando que "não fez nada".
**Why it happens:** A config padrão do htmx é literal: `4xx`/`5xx` não fazem swap (`www/content/QUIRKS.md` do htmx).
**How to avoid:** `login_view` sempre devolve **HTTP 200** no caminho de erro, com o fragmento re-renderizado (`erro`/`bloqueado` no contexto). Status não-200 é reservado para falhas de infraestrutura reais.
**Warning signs:** Teste que só afere `status_code` e nunca o HTML no corpo — passa verde com a UI quebrada.

### Pitfall 2: `redirect()` dentro de uma view acessada via HTMX aninha a página inteira

**What goes wrong:** POST de login bem-sucedido com `redirect("/")` faz o htmx seguir o 302 de forma transparente e trocar o alvo pelo `<html>` inteiro.
**Why it happens:** XHR/fetch seguem redirects sem expor o 302 ao JS que disparou a requisição.
**How to avoid:** `django_htmx.http.HttpResponseClientRedirect(destino)` em toda view acessada via HTMX; `HtmxRedirectMiddleware` cobre o caso genérico (ex.: sessão expirada no meio de uma navegação).
**Warning signs:** Formulário de login aninhado dentro de outro elemento; `assertRedirects` passando (servidor certo) enquanto a UI está quebrada — teste com `headers={"HX-Request": "true"}` e afira `response["HX-Redirect"]`.

### Pitfall 3: `AXES_USERNAME_FORM_FIELD` não configurado — lockout nunca dispara

**What goes wrong:** Com `USERNAME_FIELD="email"` no model customizado, o axes por padrão tenta ler a credencial pela chave `"email"` no dict passado a `authenticate()` — mas Django **sempre** usa o kwarg literal `username=` nessa chamada, mesmo com email. O axes nunca encontra a chave certa, grava toda tentativa com `username=None`, e o lockout por usuário+IP nunca dispara (nenhum erro visível).
**Why it happens:** Comportamento documentado, mas não-óbvio, de como `authenticate()` interage com backends customizados e `USERNAME_FIELD`.
**How to avoid:** `AXES_USERNAME_FORM_FIELD = "username"` explícito em `base.py`, com o comentário explicando o motivo (é fácil um desenvolvedor "corrigir" isso para `"email"` achando que está errado).
**Warning signs:** Testar a 6ª tentativa de login errado e o axes **não** bloquear — sintoma silencioso, só aparece com teste dedicado (ver `core/tests/test_auth.py` da PCA).

### Pitfall 4: `AxesMiddleware` sobrescreve a resposta 200 já correta da view

**What goes wrong:** Sem `AXES_LOCKOUT_CALLABLE`, o `AxesMiddleware` substitui a resposta de **qualquer** view por uma página de bloqueio genérica (status default `AXES_HTTP_RESPONSE_CODE`, tipicamente 429) sempre que `request.axes_locked_out` é `True` — mesmo quando `login_view` já devolveu o fragmento HTMX correto em HTTP 200.
**How to avoid:** `AXES_LOCKOUT_CALLABLE = "core.axes_lockout.resposta_bloqueio"` retornando `original_response` sem modificação.
**Warning signs:** A tela de bloqueio genérica do axes aparecendo em vez do fragmento com a mensagem de bloqueio do sistema; só visível testando a 6ª tentativa via HTTP real (`Client().post(...)`), não via `AxesBackend` isolado.

### Pitfall 5: `STATICFILES_STORAGE` de tutorial antigo é silenciosamente ignorado

**What goes wrong:** `STATICFILES_STORAGE` foi removido no Django 5.1 — um `settings.py` copiado de material desatualizado que ainda usa essa chave não gera erro nenhum, só não aplica compressão/hash. Sintoma pior: `ValueError: Missing staticfiles manifest entry` em produção se `collectstatic` não rodar **no build**.
**How to avoid:** Sempre o dict `STORAGES` (não `STATICFILES_STORAGE`); `collectstatic` roda no `Dockerfile`, nunca no `entrypoint.sh`.
**Warning signs:** CSS certo em dev, sem estilo em produção; `grep -r STATICFILES_STORAGE config/` retornando algo.

### Pitfall 6: `SECURE_SSL_REDIRECT` sem `SECURE_PROXY_SSL_HEADER` = loop de redirect atrás do proxy

**What goes wrong:** Com `SECURE_SSL_REDIRECT=True` e nada mais, o Django recebe HTTP do proxy do host, conclui que a requisição é insegura e redireciona para HTTPS; o proxy devolve HTTP de novo → loop infinito. Cada sistema gerado a partir deste template terá seu próprio proxy — a settings de `prod.py` precisa estar pronta para essa topologia desde a Fase 1, mesmo que o proxy real só exista mais tarde no ciclo de vida do sistema derivado.
**How to avoid:** `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` + `ALLOWED_HOSTS` incluindo `127.0.0.1` (necessário para o próprio `/healthz` interno do compose) + `CSRF_TRUSTED_ORIGINS` **com esquema** (`https://...`, exigido desde Django 4.0) + `SECURE_REDIRECT_EXEMPT = [r"^healthz$"]` (senão o healthcheck interno em HTTP puro recebe 301 e o container fica marcado unhealthy).
**Warning signs:** `curl -I` retornando 301 repetido para a mesma URL; container `web` reiniciando em loop com log limpo (é o healthcheck batendo em `DisallowedHost` ou redirect).

### Pitfall 7: collation do Postgres decidida só no primeiro `initdb` — não dá para corrigir depois sem downtime

**What goes wrong:** Se o cluster Postgres subir sem `POSTGRES_INITDB_ARGS` explícito, a collation default (`C`/`POSIX` em muitas imagens) ordena por byte — "Órgão" depois de "Zebra". Corrigir depois de dados existirem exige `pg_dump` + `initdb` novo + `pg_restore` + `REINDEX` (janela de indisponibilidade).
**How to avoid:** `POSTGRES_INITDB_ARGS: "--locale-provider=icu --icu-locale=pt-BR --encoding=UTF8"` no `compose.yml` **desde o primeiro `docker compose up`** — decisão que satisfaz CFG-03 (localização pt-BR) e precisa estar certa no dia 1 do template, pois todo sistema derivado herda esse `compose.yml`.
**Warning signs:** `SHOW lc_collate;` retornando `C`/`POSIX`; ordenação de nomes com acento visivelmente errada.

### Pitfall 8: `timezone.now().date()` erra o "hoje" em `America/Sao_Paulo` (UTC−3)

**What goes wrong:** Com `USE_TZ=True`, `timezone.now()` sempre retorna UTC, independente de `TIME_ZONE`. Às 21h de um dia em Brasília, `timezone.now().date()` já retorna o dia seguinte. Ainda que a Fase 1 não tenha modelos de domínio com datas, os testes de sessão/expiração e qualquer lógica futura de "hoje" herdam essa armadilha se a convenção não for fixada agora.
**How to avoid:** Documentar em `core/` (comentário ou `README` interno) que **toda** lógica de "hoje" usa `django.utils.timezone.localdate()`, nunca `timezone.now().date()` nem `datetime.date.today()` (este último usa o fuso do SO — dentro do container Docker é UTC, mesmo com `TIME_ZONE="America/Sao_Paulo"` no settings).
**Warning signs:** Teste que passa de manhã e falha à noite/madrugada.

### Pitfall 9: `LoginRequiredMiddleware` (Django 5.1+) tem comportamento diferente do decorator antigo

**What goes wrong:** Com `LoginRequiredMiddleware` no `MIDDLEWARE`, toda view exige login por padrão — inclusive uma view nova esquecida sem `@login_not_required`. É o comportamento **desejado** (fecha o buraco de "esqueci o decorator"), mas surpreende quem espera o antigo padrão opt-in (`@login_required` só onde precisa).
**How to avoid:** `/login/`, `/logout/`, `/healthz` (e futuramente `/manifest.json`, `/sw.js` na Fase 2) precisam de `@login_not_required` explícito. Documentar essa convenção em `core/views.py`.
**Warning signs:** Página nova redirecionando para login sem que ninguém tenha adicionado `@login_required` de propósito (é o middleware fazendo seu trabalho, não um bug) — ou o inverso: `/healthz` redirecionando para `/login/` porque esqueceram o decorator, quebrando o healthcheck do Compose.

### Pitfall 10: Guarda de tamanho do CSS do Tailwind com limiar copiado sem recalibrar

**What goes wrong:** O limiar de bytes que detecta "só o preflight foi emitido" (PCA usa 10 KB) foi calibrado para um design system completo. Copiado literalmente para a Fase 1 — que só tem `login.html` + `base.html`, com poucas classes — o build real pode gerar um CSS legitimamente menor que 10 KB e falhar por um falso positivo, ou o limiar pode ficar baixo demais e não pegar o problema real.
**How to avoid:** Rodar o build uma vez, observar o tamanho real do CSS gerado para os templates desta fase, e fixar o limiar um pouco abaixo desse valor real (nunca abaixo de ~5 KB, que é a faixa do preflight puro). Recalibrar de novo na Fase 2 quando o shell visual completo entrar.
**Warning signs:** Build falhando com CSS "pequeno" que na verdade está correto para o conteúdo atual; ou build passando com CSS que na prática só tem preflight.

## Code Examples

### `.env.example` completo para esta fase (INF-02)
```bash
# Django
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=true
DJANGO_SETTINGS_MODULE=config.settings.dev
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
SESSION_COOKIE_AGE=28800
AXES_COOLOFF_MINUTES=15
WEB_BIND_ADDRESS=127.0.0.1
WEB_PORT=8000
SECURE_SSL_REDIRECT=true
SECURE_HSTS_SECONDS=3600

# PostgreSQL
POSTGRES_DB=sistema_base
POSTGRES_USER=sistema_base
POSTGRES_PASSWORD=replace-with-a-database-password
DATABASE_URL=postgres://sistema_base:replace-with-a-database-password@db:5432/sistema_base
```
*(Sem `PGDATA_VOLUME`/`R2_*` nesta fase — o volume não é `external` aqui, e o serviço `backup`/R2 é `INF-03`, Fase 4.)*

### Teste vivo das três convenções de fundação (HTMX/CSRF/axes)
```python
# Source: adaptado de /opt/web/pca/core/tests/test_login_flow.py — mesma convenção,
# sem nada de domínio.
from django.test import Client, TestCase, override_settings
from core.models import Usuario


@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class LoginFlowTests(TestCase):
    def setUp(self):
        self.email = "usuario@exemplo.org"
        self.password = "correta"
        self.user = Usuario.objects.create_user(email=self.email, password=self.password)

    def test_login_logout_login_then_htmx_post_succeeds_csrf_round_trip(self):
        client = Client(enforce_csrf_checks=True)
        client.get("/login/")
        csrf_token = client.cookies["csrftoken"].value
        response = client.post("/login/", {"email": self.email, "password": self.password},
                                headers={"HX-Request": "true", "X-CSRFToken": csrf_token})
        self.assertEqual(response["HX-Redirect"], "/")

    def test_invalid_credentials_return_200_never_4xx(self):
        client = Client()
        response = client.post("/login/", {"email": "errado@x.com", "password": "errado"})
        self.assertEqual(response.status_code, 200)

    def test_five_wrong_attempts_lock_out_on_the_sixth(self):
        client = Client()
        for _ in range(5):
            client.post("/login/", {"email": self.email, "password": "errada"})
        response = client.post("/login/", {"email": self.email, "password": "errada"})
        self.assertEqual(response.status_code, 200)  # nunca 4xx — Pitfall 1
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `STATICFILES_STORAGE` | dict `STORAGES` | Removido no Django 5.1 | Settings de tutoriais antigos falham silenciosamente — usar sempre `STORAGES` |
| `@login_required` decorator por view | `LoginRequiredMiddleware` + `@login_not_required` opt-out | Django 5.1 | Inverte o padrão: default é autenticado, exceção é explícita |
| `hx-headers` global estático para CSRF | `htmx:configRequest` lendo o cookie por requisição | Prática recomendada desde sempre no htmx (não é uma mudança recente, é um erro comum) | Token sempre fresco, sobrevive a `rotate_token()` no login/logout |
| `psycopg2` | `psycopg` (psycopg3) | Driver recomendado desde Django 4.2+ | `psycopg[binary]` evita `libpq-dev` na imagem |

**Deprecated/outdated:**
- `STATICFILES_STORAGE`/`DEFAULT_FILE_STORAGE`: removidos no Django 5.1 (a versão-alvo desta fase é 5.2, então nem existe a opção de usar a forma antiga).
- htmx 1.x: ainda mantido e usado em produção pela PCA, mas o htmx 2.0 é a linha atual do projeto (ver Open Questions — decisão de qual linha vendorizar fica para o planejamento).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | Vendorizar `htmx.org` 1.9.12 (linha 1.x, paridade com a PCA) em vez de migrar para 2.0.10 | Standard Stack / Supporting | Baixo — a API de `htmx:configRequest`/`hx-post`/`hx-target` usada nesta fase é estável entre as duas linhas major; se o planner preferir 2.x, é só trocar o arquivo vendorizado, sem mudança de settings Django |
| A2 | Vendorizar `alpinejs` 3.16.2 (última 3.x estável) | Standard Stack / Supporting | Baixo — Alpine não é usado em nenhum comportamento crítico desta fase (tela de login mínima); qualquer patch 3.x serve |
| A3 | Limiar de 6000 bytes para a guarda de CSS do Tailwind nesta fase (em vez dos 10000 da PCA) | Pattern 5 / Pitfall 10 | Baixo-médio — se calibrado errado, ou o build falha por falso positivo, ou deixa passar um CSS quase vazio; recomendação explícita é recalibrar após o primeiro build real |
| A4 | Volume do Postgres **não** `external` nesta fase (diferente da PCA) | Pattern 6 | Médio — decisão deliberada para satisfazer o critério de sucesso 1 (`docker compose up -d` funciona sozinho); se o time preferir replicar o padrão `external` da PCA desde já, precisa documentar o passo extra `docker volume create` no README, o que technically viola "zero passo extra" só para o *primeiro* boot |
| A5 | `django.contrib.admin` fica com o `AdminSite` **padrão** do Django nesta fase (sem customização de `PcaAdminSite`) | Recommended Project Structure | Baixo — `CORE-03` (admin customizado com identidade visual) é explicitamente Fase 2; manter o admin padrão nesta fase não bloqueia nada e evita acoplar Fase 1 a decisões de UI que ainda não foram tomadas |

## Open Questions

1. **htmx 1.x vs 2.x para o vendor inicial**
   - What we know: a PCA (fonte de extração) roda htmx 1.x; a linha atual do projeto é 2.0.10 (estável) — 4.0 está em beta e não deve ser usado. A API usada nesta fase (`htmx:configRequest`, `hx-post`, `hx-target`, `HX-Redirect`) é idêntica nas duas linhas.
   - What's unclear: se "atualizando patches quando seguro" (CONTEXT.md, Claude's Discretion) deve ser lido como "só patch da mesma major" (ficar em 1.x) ou como liberdade geral de escolher a versão mais nova disponível para um projeto greenfield.
   - Recommendation: usar 1.9.12 por paridade e menor risco nesta fase de fundação; documentar a decisão explicitamente no PLAN para que fique rastreável e revisitável.

2. **Exato ponto de corte da migração 0001 do `core`**
   - What we know: CORE-01 exige `Usuario` desde a 0001; CORE-06 (simple-history) é Fase 2.
   - What's unclear: se a Fase 2 deve criar uma migração `0002_alter_usuario...` (registrando `simple_history.register(Usuario)`, que gera `HistoricalUsuario` numa migração posterior) ou se compensa antecipar campos/estrutura nesta fase para simplificar a Fase 2.
   - Recommendation: não antecipar nada — deixar a 0001 limpa e mínima (só `Usuario`), a Fase 2 adiciona o histórico como migração aditiva, sem risco de dado.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | `docker compose up -d` (critério de sucesso 1) | ✓ | 29.5.2 | — |
| Docker Compose (plugin `compose`) | `compose.yml` | ✓ | v5.1.4 | — |
| Python (host) | Não necessário — tudo roda em container | ✓ (3.14.4, irrelevante) | — | Container usa `python:3.12-slim`, independente da versão do host |
| Node.js (host) | Não necessário — Tailwind compila só dentro do estágio Docker | ✓ (v22.22.2, mas não deve ser usado diretamente) | — | Confirma D-07: mesmo com Node disponível no host, o build deve rodar só dentro do `Dockerfile` |
| Git | Versionamento do repo | ✓ | 2.53.0 | — |

**Missing dependencies with no fallback:** nenhuma.
**Missing dependencies with fallback:** nenhuma — todas as dependências necessárias já estão disponíveis no ambiente.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | yes | `django.contrib.auth` + `Usuario`/`UsuarioManager` (senha via `set_password`, nunca texto plano); `django-axes` para força bruta |
| V3 Session Management | yes | `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_SAMESITE="Lax"`, `SESSION_COOKIE_AGE` configurável via `.env`, `SESSION_EXPIRE_AT_BROWSER_CLOSE=True` |
| V4 Access Control | yes | `LoginRequiredMiddleware` (Django 5.1+) — nega por padrão, `@login_not_required` explícito nas exceções |
| V5 Input Validation | parcial nesta fase | Formulário de login processado via `request.POST.get` direto (sem `django.forms.Form` — escopo mínimo desta fase); Django escapa automaticamente output em templates (proteção XSS por padrão) |
| V6 Cryptography | yes | `Argon2PasswordHasher` no topo de `PASSWORD_HASHERS` (via `argon2-cffi`), `PBKDF2PasswordHasher` como fallback de leitura para hashes antigos |

### Known Threat Patterns for Django + HTMX + PostgreSQL

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Força bruta de login | Spoofing | `django-axes` (`AXES_FAILURE_LIMIT=5`, lockout por usuário+IP) |
| CSRF em POST/PUT/DELETE via HTMX | Tampering | `CsrfViewMiddleware` + token lido por `htmx:configRequest` a cada request (Pattern 4) |
| Clickjacking | Tampering | `XFrameOptionsMiddleware` com `X_FRAME_OPTIONS="DENY"` (default Django) — sistema é 100% HTMX/server-rendered, nunca embutido em iframe |
| Sessão sequestrada via cookie sem flag `Secure`/`HttpOnly` | Information Disclosure | `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY` (default `True` do Django, não sobrescrever) |
| Downgrade de HTTPS / MITM atrás do proxy | Tampering / Information Disclosure | `SECURE_PROXY_SSL_HEADER` + `SECURE_SSL_REDIRECT` + `SECURE_HSTS_SECONDS` (Pitfall 6) |
| Enumeração de host via `Host` header forjado | Spoofing | `ALLOWED_HOSTS` restrito em produção (CFG-02); `DisallowedHost` rejeita hosts não listados |
| SQL Injection | Tampering | Django ORM parametriza queries por padrão; nenhuma query raw nesta fase |
| Exposição de `DEBUG=True`/stack trace em produção | Information Disclosure | `DEBUG=False` fixo em `prod.py`, nunca vindo do `.env` nesse módulo |

## Sources

### Primary (HIGH confidence)
- `/opt/web/pca/config/settings/base.py`, `dev.py`, `prod.py` — settings de produção, extraídos e generalizados
- `/opt/web/pca/core/models.py`, `axes_lockout.py`, `middleware.py`, `context_processors.py`, `views.py`, `urls.py`, `apps.py` — kernel replicável
- `/opt/web/pca/Dockerfile`, `compose.yml`, `entrypoint.sh`, `requirements.txt`, `tailwind.config.js` — infra replicável
- `/opt/web/pca/core/tests/test_auth.py`, `test_login_flow.py` — provas vivas das convenções (HTMX/CSRF/axes)
- `/opt/web/pca/.planning/research/PITFALLS.md` — pesquisa de pitfalls da própria PCA, com citações de fontes oficiais (htmx `QUIRKS.md`, Django docs, django-axes/django-htmx/whitenoise docs) — Pitfalls 1, 2, 3, 6 (equivalente ao Pitfall 18 da PCA), 5 (equivalente ao 19), 7 (equivalente ao 21), 8, 9 (equivalente ao 16) desta pesquisa são derivados diretamente de lá
- `pip index versions <pkg>` contra o PyPI (2026-08-17) — todas as versões da tabela Standard Stack
- `slopcheck install <9 pacotes>` (2026-08-17) — 10/10 `[OK]`
- API JSON do PyPI (`pypi.org/pypi/<pkg>/json`) — idade e repositório-fonte de cada pacote

### Secondary (MEDIUM confidence)
- Django 5.2 release notes (`docs.djangoproject.com`) — confirmação de LTS até ~abril/2028, via WebSearch
- htmx.org / npm registry — confirmação de que 2.0.10 é a última estável (4.0 em beta) e Alpine 3.16.2 é a última 3.x

### Tertiary (LOW confidence)
- Nenhuma — todo o núcleo técnico desta pesquisa foi ancorado em código de produção real ou em verificação de registry/slopcheck.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versões confirmadas no PyPI, pacotes já validados em produção na PCA com Django 5.2
- Architecture: HIGH — topologia de settings/middleware/CSRF/axes extraída verbatim de sistema em produção
- Pitfalls: HIGH — documentados com fonte oficial (htmx docs, Django docs) no `PITFALLS.md` da própria PCA, e comprovados por testes reais (`core/tests/`)

**Research date:** 2026-08-17
**Valid until:** 2026-09-16 (30 dias — stack estável, mas checar `pip index versions` de novo antes de instalar, por segurança de patches)
