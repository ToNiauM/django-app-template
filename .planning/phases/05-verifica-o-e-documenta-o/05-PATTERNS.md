# Phase 5: Verificação e Documentação - Pattern Map

**Mapped:** 2026-08-18  
**Files analyzed:** 2  
**Analogs found:** 2 / 2

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.template-tests/test_05_nascimento.sh` | test / orchestration script | batch + file-I/O + request-response | `.template-tests/test_copier_copy.sh` | exact role-match |
| `README.md` | documentation / runbook | request-response operational workflow | `README.md.jinja` | role-match |

## Pattern Assignments

### `.template-tests/test_05_nascimento.sh` (test/orchestration script, batch + file-I/O + request-response)

**Primary analog:** `.template-tests/test_copier_copy.sh`  
**Supporting analog:** `.template-tests/test_copier_update.sh`

Create a POSIX shell rehearsal, not a Django test or a second Copier matrix. It must render one temporary `incluir_app_exemplo=true` project, make only disposable `.env` substitutions inside that destination, and tear down only the Compose project/resources it created. The existing copy matrix deliberately stops at static/contract validation, so preserve it and add the real boot path separately.

**Bootstrap, cleanup, and failure helpers** (`.template-tests/test_copier_copy.sh:1-23`):

```sh
#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
COPIER="${ROOT}/.venv-template/bin/copier"
TMP=$(mktemp -d)

limpar() {
    rm -rf "${TMP}"
}
trap limpar 0 HUP INT TERM

falhar() {
    printf 'FALHOU: %s\n' "$1" >&2
    exit 1
}
```

Copy this containment convention. Add the generated destination and Compose project name beneath `${TMP}`; in the trap, run the scoped `docker compose ... down` before deleting `${TMP}`. Do not use `docker system prune`, unscoped `down`, a host directory, or real secrets.

**Pinned Copier invocation with deterministic answers** (`.template-tests/test_copier_copy.sh:19-45`):

```sh
exigir_copier() {
    [ -x "${COPIER}" ] || falhar "Copier aprovado ausente: ${COPIER}"
    "${COPIER}" --version | grep -Fx 'copier 9.17.1' >/dev/null || \
        falhar 'é obrigatório usar Copier 9.17.1 na .venv-template'
}

"${COPIER}" copy --defaults \
    --data "sistema_nome=${nome}" \
    --data "sistema_slug=${slug}" \
    --data "sistema_hostname=${hostname}" \
    --data "sistema_porta=${porta}" \
    --data "sistema_banco=${banco}" \
    --data "sistema_sigla=${sigla}" \
    --data "cor_primaria=${cor}" \
    --data "incluir_app_exemplo=${exemplo}" \
    "${ROOT}" "${destino}" >/dev/null
```

Use this exact answer shape, with a unique temporary slug, database name, port, and `incluir_app_exemplo=true`. Keep Copier's approved executable/version check rather than calling a global CLI.

**Generated-project configuration and static Compose validation** (`.template-tests/test_copier_copy.sh:121-140`):

```sh
cp "${destino}/.env.example" "${destino}/.env"
(
    cd "${destino}"
    docker compose --env-file .env config >/dev/null
)
```

Follow this order before booting. The new test may replace only placeholder values in the copied `.env` (including Django/PostgreSQL test secrets); it must not alter the template source or `.copier-answers.yml`.

**Automation-safe Docker/Django commands** (`ops/MIGRACAO.md.jinja:72-83` and `README.md.jinja:21-32`):

```sh
docker compose up -d --build
docker compose exec -T web python manage.py migrate --noinput
curl -fsS "http://127.0.0.1:${WEB_PORT}/healthz"
```

After `config -q`, start only `db` and `web` (the birth rehearsal must not require the placeholder-configured `backup` service). Wait with a bounded retry loop for `web` health/HTTP; on timeout print scoped `docker compose ps` and `docker compose logs --tail=100 web db`, then fail. Use `exec -T` for all noninteractive commands, including the explicit idempotent migration, an environment-injected disposable `createsuperuser --noinput`, and:

```sh
docker compose exec -T web python manage.py test core apps.exemplo --noinput
curl -fsS "http://127.0.0.1:${WEB_PORT}/healthz"
curl -fsS "http://127.0.0.1:${WEB_PORT}/login/" >/dev/null
```

The test suite is the proof for login, shell, CRUD, modal behavior, and dashboard; `/healthz` and `/login/` are real-process HTTP smoke checks only. This implements the UI contract without introducing browser automation or UI files.

**Scoped, visible diagnostics** (`.template-tests/test_copier_update.sh:16-24` and `ops/MIGRACAO.md.jinja:82-83`):

```sh
falhar() {
    printf 'FALHOU: %s\n' "$1" >&2
    exit 1
}

docker compose logs --tail=100 web db backup
```

Retain the `FALHOU:` convention. Diagnostics belong on failure and must name only the rehearsal's project/services; never echo generated passwords.

---

### `README.md` (documentation/runbook, request-response operational workflow)

**Primary analog:** `README.md.jinja`  
**Supporting analog:** `ops/MIGRACAO.md.jinja`

Modify the root README in place: it is the canonical template runbook, while `README.md.jinja` remains the generated-system operations guide and `ops/MIGRACAO.md.jinja` remains the detailed VM/restore/TLS runbook. Put the full birth path in root README instead of delegating steps 5 onward to the generated README.

**Template boundary and Copier installation** (`README.md:1-21`):

```markdown
Este repositório é o **template-fonte** de uma família de sistemas Django. Ele
não deve ser executado diretamente: use o Copier para criar um repositório
derivado e execute os comandos Django e Docker somente nele.

```bash
python3 -m venv .venv-template
.venv-template/bin/pip install 'copier==9.17.1'
.venv-template/bin/copier --version
```
```

Keep this safety boundary and pinned Copier command at the beginning. The root README must never instruct the operator to run Django or Compose against the Jinja source tree.

**Rendered-system boot sequence** (`README.md.jinja:8-32`):

```markdown
```bash
cp .env.example .env
docker compose up -d --build
docker compose logs -f web
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Confirme a saúde em `http://127.0.0.1:{{ sistema_porta }}/healthz`.
```

Use this command ordering in the root README, strengthening automation-oriented examples with `-T` and `--noinput` where appropriate. Explain that secrets are local `.env` values, never Copier answers; give the existing `secrets.token_urlsafe(50)` command and list the needed values. Include the generated URLs: login, shell/home, CRUD and dashboard when the example app was selected.

**Layered production handoff** (`README.md.jinja:34-43`):

```markdown
Para levar o sistema a uma VM limpa, restaurar um dump e publicar o hostname com
TLS, siga o [runbook de migração](ops/MIGRACAO.md). Ele mantém a aplicação em
loopback, configura o vhost Nginx e documenta DNS, certificado e validação de
`/healthz`.
```

Root README should summarize the production order (DNS record, ports 80/443, Certbot, generated Nginx vhost, `nginx -t`, external HTTPS health check) and link to `ops/MIGRACAO.md` for exact restore and recovery steps. Do not duplicate unsafe restore internals.

**Proxy/TLS/DNS concrete commands** (`ops/MIGRACAO.md.jinja:85-101`):

```sh
sudo certbot certonly --standalone -d {{ sistema_hostname }}
sudo install -m 0644 ops/nginx/{{ sistema_slug }}.conf /etc/nginx/sites-available/{{ sistema_slug }}.conf
sudo ln -sf /etc/nginx/sites-available/{{ sistema_slug }}.conf /etc/nginx/sites-enabled/{{ sistema_slug }}.conf
sudo nginx -t
sudo systemctl restart nginx
```

Document loopback as an invariant: Compose publishes `${WEB_BIND_ADDRESS:-127.0.0.1}:${WEB_PORT:-8000}:8000` (`compose.yml.jinja:31-39`), and only Nginx terminates public TLS.

**Regression command listing** (`README.md:134-142`):

```markdown
```bash
.template-tests/test_copier_copy.sh
.template-tests/test_copier_update.sh
```
```

Extend this same block with `.template-tests/test_05_nascimento.sh`, explaining that it renders a disposable copy, validates Compose, boots `db`/`web`, runs `core` plus `apps.exemplo` tests, performs HTTP smoke checks, and removes its own resources. This links documentation and executable proof without claiming browser automation.

## Shared Patterns

### Source-tree versus generated-project boundary

**Sources:** `README.md:1-6`, `.template-tests/test_copier_copy.sh:36-45`  
**Apply to:** the rehearsal and all README command examples.

All runtime commands operate only after Copier writes a destination. The rehearsal source checkout is read-only except for its own untracked temporary directory; root documentation says the same explicitly.

### Ephemeral-resource ownership and cleanup

**Sources:** `.template-tests/test_copier_copy.sh:5-17`, `.template-tests/test_copier_update.sh:5-19`  
**Apply to:** `.template-tests/test_05_nascimento.sh`.

Use `mktemp -d`, `set -eu`, a named cleanup function, `trap ... 0 HUP INT TERM`, and a single `falhar` helper. Compose resources must receive a unique project name and be stopped through that exact project; cleanup must never target shared Docker resources.

### Compose readiness, diagnostics, and noninteractive commands

**Sources:** `compose.yml.jinja:14-39`, `ops/MIGRACAO.md.jinja:72-83`  
**Apply to:** the birth rehearsal and root README.

Validate resolved config before `up`; `db` becomes healthy before `web` due to `depends_on`, but the test must still use a bounded readiness loop. On failure surface scoped `ps` and logs. Shell automation always uses `docker compose exec -T`; interactive operator documentation may retain the normal `exec` form for `createsuperuser`.

### Behavioral and UI verification boundary

**Sources:** `core/tests/test_login_flow.py:22-214`, `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:27-231`, `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:25-143`, `05-UI-SPEC.md:108-158`  
**Apply to:** the birth rehearsal and README regression explanation.

Run `manage.py test core apps.exemplo --noinput` in the rendered project. This reuses the existing authenticated login, shell, CRUD/HTMX, and dashboard tests. The UI contract explicitly keeps browser inspection as complementary evidence and introduces neither a new visual-test framework nor frontend files in this phase.

### Local-secret handling

**Sources:** `README.md:68-79`, `.env.example.jinja:1-4,34-44`  
**Apply to:** the birth rehearsal and README.

Secrets remain only in a generated `.env` or process environment. Do not add them to Copier answers, version control, logs, README literals, or the template source.

## No Analog Found

None. The phase extends established shell-rehearsal and layered-runbook patterns; it does not introduce an application component, runtime service, or browser test harness.

## Metadata

**Analog search scope:** `.template-tests/`, `ops/`, root `README.md`, generated README/runbook templates, Compose and environment templates, existing core/example tests  
**Files scanned:** 14  
**Pattern extraction date:** 2026-08-18
