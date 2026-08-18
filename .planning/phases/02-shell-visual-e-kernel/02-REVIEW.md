---
phase: 02-shell-visual-e-kernel
reviewed: 2026-08-18T04:18:50Z
depth: standard
files_reviewed: 25
files_reviewed_list:
  - config/settings/base.py
  - core/README.md
  - core/admin.py
  - core/admin_site.py
  - core/apps.py
  - core/context_processors.py
  - core/migrations/0002_historicalusuario.py
  - core/static/offline.html
  - core/static/src/input.css
  - core/templates/admin/base_site.html
  - core/templates/base.html
  - core/templates/core/_breadcrumbs.html
  - core/templates/core/_nav.html
  - core/templates/core/login.html
  - core/templates/core/shell.html
  - core/tests/test_admin.py
  - core/tests/test_auditoria.py
  - core/tests/test_identidade.py
  - core/tests/test_pwa.py
  - core/tests/test_shell.py
  - core/urls.py
  - core/views.py
  - ops/gerar_icones_pwa.py
  - tailwind.config.js
  - .env.example
findings:
  critical: 1
  warning: 2
  info: 7
  total: 10
fixes:
  fixed_at: 2026-08-18T04:35:00Z
  CR-01: 9fa7d87
  WR-01: "9532245"
  WR-02: 011d4c6
status: fixes_applied
---

# Phase 2: Code Review Report

**Reviewed:** 2026-08-18T04:18:50Z
**Depth:** standard
**Files Reviewed:** 25
**Status:** fixes_applied (CR-01, WR-01 and WR-02 fixed on 2026-08-18; Info findings deliberately left open — original findings text preserved below for audit)

## Summary

Review of the Phase 2 kernel: parameterized identity (settings + context processor), custom admin site, HTMX/Alpine/Tailwind shell, PWA (manifest/service worker/icons), and simple-history auditing. The architecture is well-documented and most house invariants hold (CSRF via `htmx:configRequest`, `CSRF_COOKIE_HTTPONLY=False`, Argon2, boot-time `COR_PRIMARIA` validation, service worker restricted to `/static/`, no domain/PCA mentions).

Three substantive problems were found. The most serious: the "no-JS fallback" documented on the login/logout forms (IN-02 of the previous review cycle) does not exist — the forms have no `method`/`action`, so a native submit degrades to a **GET with the password (login) or CSRF token (logout) in the query string**. Second, the historical user table snapshots the **password hash on every save** (including the `last_login` write on every login), retaining superseded hashes indefinitely. Third, the desktop sidebar is invisible until Alpine initializes — a flash on every full-page navigation (and permanent with JS unavailable), because desktop visibility is JS state instead of CSS.

## Critical Issues

### CR-01: "No-JS fallback" claim is false — native form submit sends credentials via GET in the query string

> **fixed:** commit `9fa7d87` (2026-08-18) — `method="post"`/`action` added to both forms; `_redirecionar()` in `core/views.py` branches on `request.htmx` (htmx keeps `HX-Redirect`, plain POST gets a real 302); non-htmx login error renders the full `core/login.html` page instead of the bare fragment; new tests lock the form attributes and both response paths.

**File:** `core/templates/core/shell.html:85-92` (logout form); `core/templates/core/login.html:10` (includes `core/_login_form.html`, which has the same defect at its `<form>` on line 1); `core/views.py:31-99` (docstrings/flow assume the fallback works)

**Issue:** Both forms declare only `hx-post` — no `method="post"` and no `action`. The comment chain (shell.html line 87 → `_login_form.html` lines 3-7, added as the IN-02 "fix" of the previous review) claims the hidden `csrfmiddlewaretoken` field "faz o form funcionar em um POST tradicional sem JS/htmx". That is false. Without `method`, the HTML default is **GET to the current URL**. Concretely, if htmx fails to load (blocked script, broken static, no-JS client):

- Login form: submits `GET /login/?csrfmiddlewaretoken=...&next=...&email=...&password=...` — the **plaintext password lands in the URL**, i.e., in browser history, proxy logs, and the reverse-proxy access logs of the very host the app sits behind (127.0.0.1 proxy per house invariant). `login_view` treats the GET as a page render, so the user just sees the form again with the password now persisted in logs/history.
- Logout form: submits `GET /?csrfmiddlewaretoken=...` — logout silently never happens and the CSRF token leaks into the URL.

Additionally, even with `method="post"` added, `login_view`/`logout_view` respond with `HttpResponseClientRedirect` (HTTP 200 + `HX-Redirect` header, empty body) unconditionally — a non-htmx POST client would see a blank page, so the fallback would still be half-broken.

**Fix:**
```html
<!-- _login_form.html -->
<form id="login-form" method="post" action="{% url 'core:login' %}"
      hx-post="{% url 'core:login' %}" hx-target="#login-form" hx-swap="outerHTML" ...>

<!-- shell.html -->
<form method="post" action="{% url 'core:logout' %}"
      hx-post="{% url 'core:logout' %}" hx-target="body" class="inline"
      hx-on::before-request="limparCachePwa()">
```
And in `core/views.py`, branch the redirect on `request.htmx` so plain POSTs get a real 302:
```python
def _redirecionar(request, destino):
    if request.htmx:
        return HttpResponseClientRedirect(destino)
    return redirect(destino)
```
Alternatively, if no-JS support is explicitly out of contract, delete the false "fallback deliberado no-JS" comments in `shell.html` and `_login_form.html` and still add `method="post"` — it costs nothing and removes the credentials-in-URL failure mode. Update the related docstrings in `core/views.py` accordingly.

## Warnings

### WR-01: `HistoricalUsuario` snapshots the password hash on every save — including one row per login

> **fixed:** commit `9532245` (2026-08-18) — `simple_history.register(Usuario, excluded_fields=["password", "last_login"])` + migration `0003` removing both columns; test locks the absence of the fields on the historical model. Residual note (verified against simple-history 3.13.0 source): `post_save` ignores `update_fields`, so each login still inserts one `~` history row — but it no longer carries any sensitive data (no hash, no `last_login`). Consequence 1 (hash retention) is fully eliminated; consequence 2 (login noise) is only defanged, not removed.

**File:** `core/admin.py:13`; `core/migrations/0002_historicalusuario.py:21-22`

**Issue:** `simple_history.register(Usuario)` tracks all fields, so the historical table carries a `password` column (migration line 21). Two consequences:

1. **Retention of superseded password hashes.** Every password change leaves the old Argon2 hash readable in `core_historicalusuario` forever. A DB dump then exposes the user's full hash history for offline cracking — old (possibly weaker/reused) passwords remain attackable long after being rotated. This defeats part of the purpose of forcing rotation.
2. **One audit row per login.** Django's `user_logged_in` signal runs `update_last_login`, which calls `user.save(update_fields=["last_login"])`; simple-history records every `post_save`, so **each successful login inserts a `HistoricalUsuario` row** (each duplicating the current password hash). The audit trail for real profile changes drowns in login noise.

**Fix:**
```python
simple_history.register(Usuario, excluded_fields=["password", "last_login"])
```
Then regenerate the historical migration (or add a follow-up migration removing the two columns). If a "password was changed" audit signal is desired, keep the event derivable by other means (e.g., `history_change_reason`), never the hash itself.

### WR-02: Desktop sidebar visibility driven by Alpine state — invisible flash on every page load; permanently hidden without JS

> **fixed:** commit `011d4c6` (2026-08-18) — aside gets `md:!flex` (CSS-owned desktop visibility, wins over the inline `display: none` a false `x-show` writes); the `desktop` Alpine state and its MediaQueryList listener were removed entirely — `x-show="sidebarAberta"` now drives only the mobile drawer, with overlay and close button made mobile-only via `md:hidden`; the `[x-cloak]` rule in `input.css` is scoped to `max-width: 767px`. Generated CSS verified in the built image; regression test locks `md:!flex` and the absence of the JS-gated desktop state.

**File:** `core/templates/core/shell.html:50-51` (aside `x-show="sidebarAberta || desktop"` + `x-cloak`); `core/static/src/input.css:9-11`

**Issue:** The `<aside>` starts with `x-cloak` (`display: none !important`) and only becomes visible after Alpine (loaded with `defer`) initializes and evaluates `x-show`. Because D-09 forbids htmx boost, **every navigation is a full page load**, so on desktop the sidebar blinks out and back in on every single click — `<main>` keeps its `md:ml-[232px]`, leaving a visible 232px dead strip during each load. Worse, if JS fails to run (blocked, parse error, extension), the aside — which contains the entire navigation, the user identity, and the logout button — never renders at all, on any viewport. Desktop visibility is a pure CSS concern (`min-width: 768px`) and should not be gated on JS.

**Fix:** Make the desktop state CSS-owned and keep Alpine only for the mobile drawer:
```html
<aside x-show="sidebarAberta || desktop" x-cloak
       class="max-md:x-cloak-target fixed inset-y-0 left-0 z-50 ... md:!flex">
```
i.e., add `md:!flex` (or restructure so `x-show` applies only below `md:`), and scope the cloak rule to mobile:
```css
@media (max-width: 767px) {
  [x-cloak] { display: none !important; }
}
```
This preserves the anti-flash behavior for the drawer/overlay (both are `md:hidden` anyway) while the desktop aside renders in the first paint with no JS dependency.

## Info

### IN-01: `core/static` discovered twice — STATICFILES_DIRS duplicates the app static dir

**File:** `config/settings/base.py:163`

**Issue:** `STATICFILES_DIRS = [BASE_DIR / "core" / "static"]` while `core` is an installed app, so `AppDirectoriesFinder` also serves `core/static/`. Every asset is found twice; `collectstatic` emits a "Found another file with the destination path" warning per file, which will mask real collision warnings later.

**Fix:** Drop `STATICFILES_DIRS` (app-dir discovery already covers `core/static/`), or reserve it for a future project-level `static/` dir outside apps.

### IN-02: `admin_tema_css` `|safe` relies solely on import-time validation

**File:** `core/admin_site.py:48-50`; `core/templates/admin/base_site.html:11`

**Issue:** The `#RRGGBB` regex runs only when `config/settings/base.py` is imported. Any later change of `COR_PRIMARIA` (e.g., `override_settings` in tests of a generated system, or a future settings refactor that moves the assignment) bypasses the barrier while the template still applies `|safe`.

**Fix:** Defense-in-depth — revalidate at render:
```python
if not re.fullmatch(r"#[0-9a-fA-F]{6}", cor):
    raise ImproperlyConfigured(...)
```
in `each_context`, or build the CSS with the value passed through `django.utils.html.escape` semantics (validation is cleaner given CSS context).

### IN-03: Authenticated user visiting `/login/` gets the login form again

**File:** `core/views.py:43-51`

**Issue:** `login_view` never checks `request.user.is_authenticated` on GET; a logged-in user landing on `/login/` (bookmark, back button) sees the login form instead of the shell. Logging in again works, but it is confusing and pointlessly re-runs authentication.

**Fix:** At the top of the GET branch: `if request.user.is_authenticated: return redirect("/")`.

### IN-04: Nothing detects divergence between the Tailwind brand literal and `COR_PRIMARIA` from `.env`

**File:** `tailwind.config.js:6`; `config/settings/base.py:150`

**Issue:** The two identity touchpoints (D-17) can silently disagree today: setting `COR_PRIMARIA=#0f766e` in `.env` changes the admin theme, manifest, and `theme-color` meta, while every `bg-brand`/`brand-tint` token in the shell stays `#1e40af`. Until Phase 4 (Copier) wires both, a generated/dev system can run visually split-brained with no warning or test.

**Fix:** Add a lightweight guard until Phase 4 — e.g., a test that reads `tailwind.config.js`, extracts `COR_PRIMARIA = "#..."`, and asserts equality with `settings.COR_PRIMARIA`; or a startup log warning on mismatch.

### IN-05: `static-v1` cache never evicts stale hashed assets — the "manual bump" has no trigger

**File:** `core/views.py:183-232`

**Issue:** WhiteNoise's manifest storage gives every deploy new hashed filenames; the SW cache-first branch stores each under `static-v1`, and the `activate` handler only deletes *other* cache names. Old hashes are never requested again but never removed, so `static-v1` accumulates every asset version ever served until someone remembers to bump the suffix — and no code path or checklist item forces that bump.

**Fix:** Either derive `CACHE_NAME` from something that changes per deploy (e.g., interpolate the hashed URL of a sentinel asset, or a `STATIC_VERSION` setting), or add expiration logic in `activate` that drops entries not matching current manifest URLs.

### IN-06: `gerar_icones_pwa.py` — unguarded Pillow ≥ 10.1 API and unvalidated color argument

**File:** `ops/gerar_icones_pwa.py:47,61`

**Issue:** `ImageFont.load_default(size=...)` only accepts `size` from Pillow 10.1.0; on older host Pillow it raises `TypeError: load_default() got an unexpected keyword argument` with no hint. Also, the `cor` CLI argument is not validated as `#RRGGBB`, unlike the settings-side barrier — `Image.new("RGB", ..., "#12")` fails with a generic `ValueError`, and a named color like `"blue"` silently succeeds and diverges from the settings contract.

**Fix:** Validate `sys.argv[1]` with the same `re.fullmatch(r"#[0-9a-fA-F]{6}", cor)` and exit with a clear message; document/verify `Pillow>=10.1` (try/except around `load_default(size=...)` with an actionable error).

### IN-07: `healthz` swallows the failure cause

**File:** `core/views.py:25-27`

**Issue:** The bare `except Exception` returns 503 with `{"status": "error"}` and discards the exception — when the container starts flapping, the operator gets no signal (log line) about *why* the DB check failed.

**Fix:** `except Exception: logger.exception("healthz: falha na checagem do banco")` before returning 503 (keep the broad catch — appropriate for a healthcheck).

---

_Reviewed: 2026-08-18T04:18:50Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
