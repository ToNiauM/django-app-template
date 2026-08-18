---
phase: 02-shell-visual-e-kernel
plan: 03
subsystem: admin-auditoria
tags: [django, admin, adminsite, simple-history, auditoria, historical]
requires:
  - "02-01: settings.SISTEMA_NOME/SISTEMA_SIGLA/COR_PRIMARIA (COR_PRIMARIA validada #RRGGBB no boot — pré-requisito do |safe do tema)"
provides:
  - "core.admin_site.SistemaAdminSite: site default do projeto via SistemaAdminConfig.default_site (config/urls.py intocado — D-13); identidade via settings; each_context injeta admin_tema_css com --primary/--header-bg/--link-fg"
  - "core/templates/admin/base_site.html: override cirúrgico só do bloco extrastyle (D-14) — nenhum outro aspecto do admin tocado"
  - "core/admin.py: simple_history.register(Usuario) (exceção oficial para user model swappable — D-22) + UsuarioAdmin por e-mail sem campo de login padrão"
  - "Tabela core_historicalusuario (migração 0002) gravando com history_user via HistoryRequestMiddleware"
  - "Convenção D-23 documentada em core/README.md: modelos de domínio declaram history = HistoricalRecords(); alerta queryset.update() sem histórico"
affects: [02-04, fase-3-apps-exemplo, fase-4-copier]
tech-stack:
  added: [django-simple-history==3.13.0]
  patterns:
    - "AdminSite isolado em módulo sem nenhum register (reentrância do LazyObject._setup() apaga registros em silêncio)"
    - "AdminConfig com import aliased + default = False para blindar o autodiscovery da entrada core"
    - "Tema do admin por 3 CSS vars nativas do Django 5.2 via bloco extrastyle — sobrevive a upgrades"
    - "Auditoria: HistoricalRecords() no modelo para domínio; register() só para o user model"
key-files:
  created:
    - core/admin_site.py
    - core/admin.py
    - core/templates/admin/base_site.html
    - core/migrations/0002_historicalusuario.py
    - core/tests/test_admin.py
    - core/tests/test_auditoria.py
  modified:
    - requirements.txt
    - config/settings/base.py
    - core/apps.py
    - core/README.md
key-decisions:
  - "A1 mantida: has_permission NÃO sobrescrito — gate padrão do Django (is_active and is_staff), travado por teste para que qualquer mudança de semântica de acesso seja explícita"
  - "D-15 respeitada: zero agrupamento custom do índice do admin (sem admin_grupo/get_app_list) — só identidade visual + registro do Usuario"
  - "HistoryRequestMiddleware imediatamente após AuthenticationMiddleware e antes de HtmxMiddleware (ordem da PCA; doc oficial só exige 'depois do auth')"
patterns-established:
  - "Override cirúrgico de template do admin: extends recursivo resolvido pelo loader DIRS antes do APP_DIRS"
  - "Escritas em massa auditadas usam bulk_update_with_history (nunca queryset.update())"
requirements-completed: [CORE-03, CORE-06]
duration: 6min
completed: 2026-08-18
---

# Phase 2 Plan 03: Admin com identidade + auditoria padrão Summary

**Admin servido por `SistemaAdminSite` isolado (header/título/cor via settings, sem tocar urls.py) e auditoria django-simple-history gravando `HistoricalUsuario` com autor — tudo provado por 9 testes novos.**

## Performance

- **Duration:** 6min
- **Started:** 2026-08-18T03:59:36Z
- **Completed:** 2026-08-18T04:05:36Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- `/admin/` exibe "Sistema Base — Administração" e a cor primária (#1e40af) nos 3 tokens nativos do Django 5.2 (`--primary`, `--header-bg`, `--link-fg`), injetados por `each_context` + override cirúrgico do `extrastyle` (CORE-03)
- `django-simple-history==3.13.0` instalado, migrado (`core_historicalusuario`) e gravando: criação via ORM gera registro `+`; edição via admin registra `history_user` (CORE-06)
- `Usuario` editável no admin com `UsuarioAdmin` adaptado a login por e-mail (fieldsets reescritos sem o campo de login padrão do Django)
- Convenção de auditoria D-23 documentada como 4ª convenção do `core/README.md`, incluindo a exceção do user model e o alerta de `queryset.update()`
- Suíte completa verde: 30 testes, 0 falhas

## Task Commits

Each task was committed atomically:

1. **Task 1: Dependência simple-history + settings + AdminSite isolado** - `8451c91` (feat)
2. **Task 2: core/admin.py + override do template + migração HistoricalUsuario** - `ba8bd87` (feat)
3. **Task 3: Testes de admin e auditoria + convenção no README** - `c431a92` (test)

## Files Created/Modified

- `core/admin_site.py` - `SistemaAdminSite` isolado (zero register — D-13); identidade via settings no `__init__`; `admin_tema_css` em `each_context`; `has_permission` padrão mantido (A1)
- `core/apps.py` - `SistemaAdminConfig(AdminConfig)` com import aliased, `default_site` e `default = False`
- `core/admin.py` - `simple_history.register(Usuario)` no topo + `UsuarioAdmin(UserAdmin)` por e-mail, sem ações em massa (D-15)
- `core/templates/admin/base_site.html` - override só do bloco `extrastyle` com `{{ block.super }}` + `<style>{{ admin_tema_css|safe }}</style>`
- `core/migrations/0002_historicalusuario.py` - `CreateModel` de `HistoricalUsuario` (nome gerado exatamente como previsto no plano)
- `config/settings/base.py` - app admin plain substituído por `core.apps.SistemaAdminConfig`; `simple_history` entre `django_htmx` e `axes`; `HistoryRequestMiddleware` entre auth e htmx
- `requirements.txt` - `django-simple-history==3.13.0` (única dependência nova da fase)
- `core/README.md` - convenção nº 4: auditoria com HistoricalRecords()/register()/bulk_update_with_history
- `core/tests/test_admin.py` - default_site honrado, header e `--primary` no HTML, changelist do Usuario, gate A1 (staff acessa, anônimo 302)
- `core/tests/test_auditoria.py` - criação gera histórico `+`, edição via admin grava `history_user`, ordem auth → HistoryRequestMiddleware assertada

## Decisions Made

- Gate de acesso ao admin mantido no padrão do Django (`is_active and is_staff`) — decisão A1, deliberada e travada por teste; o gate superuser da PCA é política de domínio, não do template
- Nenhum agrupamento custom do índice do admin (D-15) — o template entrega só identidade visual e o registro do Usuario
- Comentários/docstrings redigidos sem os literais que os greps de aceitação proíbem (`username`, entrada plain do app admin), mantendo o conteúdo explicativo

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `makemigrations` via bind-mount falhou com PermissionError**
- **Found during:** Task 2
- **Issue:** o usuário interno do container não tem permissão de escrita no diretório do host montado em `/app` — `PermissionError` ao gravar `core/migrations/0002_historicalusuario.py`
- **Fix:** reexecutado com `docker compose run --rm --user "$(id -u):$(id -g)" ...` (UID/GID do host), gerando a migração com dono correto
- **Files modified:** nenhum arquivo de código — só a forma de invocação
- **Commit:** `ba8bd87` (migração incluída no commit da task)

Nenhuma outra deviation — plano executado como escrito.

## Verification Notes

- `docker compose exec -T web python manage.py test core.tests -v 2` — 30 testes, OK
- `grep -rn "PCA\|pca"` nos arquivos novos do admin — zero menção a domínio
- `web` healthy; migração `0002_historicalusuario` aplicada (`[X]`)
- **Human check pendente (não bloqueante):** conferir no navegador `/admin/` com header azul `#1e40af`, edição de Usuário e aba "Histórico" — coberto por testes automatizados, verificação visual fica para o checkpoint da fase (plan 02-04/verifier)

## Next Phase Readiness

- Contrato de auditoria pronto para a Fase 3: `apps/exemplo` só precisa declarar `history = HistoricalRecords()` (convenção nº 4 do README)
- Identidade do admin deriva 100% dos settings — pronta para parametrização Copier da Fase 4 (D-16/D-17)

## Self-Check: PASSED

- 6 arquivos criados verificados no disco
- 3 commits de task verificados no git log (8451c91, ba8bd87, c431a92)
