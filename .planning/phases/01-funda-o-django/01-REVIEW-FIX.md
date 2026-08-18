---
phase: 01-funda-o-django
fixed_at: 2026-08-18T00:29:36Z
review_path: .planning/phases/01-funda-o-django/01-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 01: Code Review Fix Report — Fundação Django

**Fixed at:** 2026-08-18T00:29:36Z
**Source review:** .planning/phases/01-funda-o-django/01-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (CR-01, CR-02, WR-01..WR-04, IN-01, IN-02)
- Fixed: 8
- Skipped: 0

## Fixed Issues

### CR-01: `?next=` nunca é propagado — redirecionamento pós-login está quebrado na prática

**Files modified:** `core/views.py`, `core/templates/core/_login_form.html`, `core/tests/test_login_flow.py`
**Commit:** 3b4ed50
**Applied fix:** GET agora propaga `next` da querystring para o contexto do template (`{"next": request.GET.get("next", "")}`); `_login_form.html` ganhou um campo oculto `<input type="hidden" name="next" ...>` que carrega o valor no POST; o branch de erro/bloqueio também preserva `next` no contexto para não se perder numa segunda tentativa; `destino_bruto` agora lê primeiro `request.POST.get("next")` (o que o ciclo real produz) com fallback em `request.GET.get("next")` para POSTs diretos. O teste `test_next_open_redirect_nunca_aponta_para_host_externo` foi reescrito para exercitar o ciclo real GET→extrair campo oculto→POST (em vez de forjar a querystring do POST diretamente), e um novo teste `test_next_legitimo_sobrevive_ao_ciclo_completo_get_form_post` cobre o caminho de sucesso com um `next` legítimo. Suite completa validada em container (`docker run ... manage.py test core -v 1`): 13/13 passando.

### CR-02: Menção explícita a "PCA" dentro do código-fonte

**Files modified:** `core/tests/test_login_flow.py`
**Commit:** dfe1031
**Applied fix:** Removida a linha "Fonte: adaptado de /opt/web/pca/..." do docstring do módulo, mantendo o restante da descrição. Confirmado via `grep -rn "pca" --include="*.py" -i .` que não resta nenhuma menção no código-fonte Python.

### WR-01: Container de produção roda como root

**Files modified:** `Dockerfile`
**Commit:** c6823b1
**Applied fix:** Adicionado `RUN groupadd -r app && useradd -r -g app -d /app app && chown -R app:app /app` seguido de `USER app`, inserido depois do `chmod +x`/`collectstatic` (que precisam de root) e antes do `ENTRYPOINT`. Validado com rebuild completo (`docker build`) + `docker run`: `whoami` dentro do container retorna `app`, `/healthz` responde 200, migrações rodam normalmente.

### WR-02: `WEB_BIND_ADDRESS`/`WEB_PORT` sem valor padrão seguro

**Files modified:** `compose.yml`
**Commit:** 3e7c312
**Applied fix:** Porta alterada para `"${WEB_BIND_ADDRESS:-127.0.0.1}:${WEB_PORT:-8000}:8000"`. Validado com `docker compose config` usando um `.env` sem essas duas variáveis definidas: o mapeamento resolvido mostra `host_ip: 127.0.0.1`, `published: "8000"` — confirma o comportamento seguro por padrão.

### WR-03: `AxesMiddleware` fora da posição recomendada, sem justificativa registrada

**Files modified:** `config/settings/base.py`
**Commit:** 303ec1f
**Applied fix:** Adicionado comentário explicativo acima de `"axes.middleware.AxesMiddleware"` documentando que a posição não-canônica é segura hoje porque `AXES_LOCKOUT_CALLABLE` neutraliza a substituição de resposta, e que o item deve ser movido para o final da lista se o callable for removido/alterado no futuro (opção "comentário" preferida pelo próprio finding, por manter o diff pequeno e o comportamento já testado).

### WR-04: `SILENCED_SYSTEM_CHECKS` sem comentário em `prod.py`

**Files modified:** `config/settings/prod.py`
**Commit:** 8972395
**Applied fix:** Adicionado comentário acima de `SILENCED_SYSTEM_CHECKS` ligando explicitamente `security.W005`/`security.W021` às duas flags `SECURE_HSTS_INCLUDE_SUBDOMAINS = False` / `SECURE_HSTS_PRELOAD = False` já presentes no mesmo arquivo.

### IN-01: `HtmxRedirectMiddleware` assume header `Location` sempre presente

**Files modified:** `core/middleware.py`
**Commit:** ab4a2d6
**Applied fix:** Trocado `response["Location"]` por `response.get("Location")` com fallback: se o header não existir, o middleware devolve a resposta original em vez de estourar `KeyError`. Suite completa revalidada em container: 13/13 passando (nenhum fluxo de redirect existente foi afetado).

### IN-02: `{% csrf_token %}` duplicado sem documentação do motivo

**Files modified:** `core/templates/core/_login_form.html`, `core/templates/core/shell.html`
**Commit:** b824562
**Applied fix:** Adicionado comentário Django (`{# ... #}`) acima de cada `{% csrf_token %}` explicando que o campo oculto é redundante com o header `X-CSRFToken` injetado via `htmx:configRequest`, mas deliberado como fallback para um POST tradicional sem JS/htmx.

## Skipped Issues

None — all findings were fixed.

---

_Fixed: 2026-08-18T00:29:36Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
