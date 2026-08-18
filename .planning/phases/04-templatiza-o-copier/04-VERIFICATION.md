---
phase: 04-templatiza-o-copier
verified: 2026-08-18T17:45:20Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 04: Templatização Copier — Verification Report

**Phase Goal:** O sistema-modelo vira template Copier: valores específicos de cada sistema são parametrizados, `copier copy` cria um projeto autocontido, `copier update` entrega evoluções do núcleo e `ops/` fornece operação portátil.

**Verified:** 2026-08-18T17:45:20Z  
**Status:** passed  
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | `copier copy` asks template questions and produces a complete, self-contained Django project. | ✓ VERIFIED | `copier.yml` declares the eight questions/validators and `sh .template-tests/test_copier_copy.sh` passed with both app variants, generated `.copier-answers.yml`, `.env.example`, `manage.py`, Django packages, Compose, and `ops/`. |
| 2 | Per-system name, slug, hostname, port, database, and primary colour are derived from Copier answers rather than generated hard-coding. | ✓ VERIFIED | `.env.example.jinja`, `compose.yml.jinja`, settings, Tailwind, nginx, and README consume the answer variables; the copy probe rendered two distinct identities and audited generated paths/content for legacy identifiers. |
| 3 | `copier update` applies core changes to an existing generated system. | ✓ VERIFIED | `sh .template-tests/test_copier_update.sh` exited `0` in this verification. It performs isolated Git tags A→B→C, proves `_commit` changes, commits clean A/B/C states, delivers B/C changes, and detects conflict markers after both updates. |
| 4 | Generated code contains no PCA or business-domain identity. | ✓ VERIFIED | The executed copy matrix scans every generated path and text case-insensitively for the explicit PCA/CFC/domain/prefix list in both variants and passed. Its only metadata normalization is `_src_path` in Copier answers, required for update. |
| 5 | Generated `ops/` contains backup plus nginx; web is loopback-only; the migration path is portable. | ✓ VERIFIED | Rendered Compose publishes only `${WEB_BIND_ADDRESS:-127.0.0.1}:${WEB_PORT:-8000}:8000`; copy probe validated Compose, shell syntax, mocked restore cleanup, TLS vhost, and migration runbook. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

## Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `copier.yml` | Copier contract, validators, exclusions | ✓ VERIFIED | Substantive 92-line config: Copier 9.17.1, StrictUndefined, eight questions, no `_tasks`, migrations, or extensions. |
| `.copier-answers.yml.jinja` | Copier-managed update metadata | ✓ VERIFIED | Renders `_copier_answers` directly; executed copy/update probes generated and advanced `_commit`. |
| `.env.example.jinja` | Rendered identity/connection defaults without secrets | ✓ VERIFIED | Contains variables for identity, PostgreSQL, loopback, R2 and backup; secrets remain non-usable `replace-with-*` placeholders. |
| `config/settings/base.py.jinja` / `tailwind.config.js.jinja` | Runtime identity from `.env`, build colour from Copier | ✓ VERIFIED | Settings require `SISTEMA_NOME`, `SISTEMA_SIGLA`, `COR_PRIMARIA`; Tailwind is the sole build-time interpolation. |
| `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/` | Optional example package | ✓ VERIFIED | Copy matrix rendered the complete true variant and absent false variant; four integration points were checked. |
| `compose.yml.jinja` and `ops/backup/*` | Isolated stack and containerized backup/retention | ✓ VERIFIED | `name: {{ sistema_slug }}`, managed `pgdata`, health-gated `backup`, `init: true`, custom `pg_dump`, and shared retention function. |
| `ops/backup/ensaio_restore_local.sh` | Confined restore | ✓ VERIFIED | Records only created container/network/volume flags; `testar_ensaio_restore.sh` passed success, failure, and interrupt cleanup cases without Docker/R2. |
| `ops/nginx/{{ sistema_slug }}.conf.jinja` and `ops/MIGRACAO.md.jinja` | TLS proxy and portable migration runbook | ✓ VERIFIED | Rendered TLS/HTTP redirect, trusted headers, loopback proxy, dump + `.env` + Compose + migrate + healthz + DNS/cert steps. |
| `.template-tests/test_copier_copy.sh` / `test_copier_update.sh` | Behavioral copy/update proof | ✓ VERIFIED | Both scripts are substantive, syntactically valid, and passed in isolated temporary repositories. |

## Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `copier.yml` | `.env.example.jinja` | answer variables | ✓ WIRED | All required values are declared and interpolated. |
| `.copier-answers.yml` | `copier update` | Copier metadata | ✓ WIRED | Update probe compares changing `_commit` at A/B/C. |
| `.env.example.jinja` | settings/icons/Compose | required environment values | ✓ WIRED | Runtime env reads and Compose substitutions are present; copy tests render concrete values. |
| `incluir_app_exemplo` | package, settings, URLs, navigation | identical conditional contract | ✓ WIRED | True/false rendered variants and second update prove all four destinations stay consistent. |
| `compose.yml.jinja` | backup entrypoint | health-gated internal service | ✓ WIRED | `depends_on: db: service_healthy`, `init: true`, and environment wiring inspected. |
| backup script | retention script | `manter_ultimos` | ✓ WIRED | `backup.sh` sources `retencao.sh` and invokes it for daily and weekly. |
| restore/vhost | Compose loopback contract | rendered ports and isolated resources | ✓ WIRED | Restore probe passed; vhost proxy target is `127.0.0.1:{{ sistema_porta }}`. |

## Data-Flow Trace (Level 4)

| Artifact | Data variable | Source | Produces real data | Status |
|---|---|---|---|---|
| Rendered `.env.example` | identity and connection values | Copier answers | Two distinct Copy variants were rendered and inspected | ✓ FLOWING |
| Rendered Compose/nginx | slug, port, hostname | Copier answers → `.env.example` / Jinja | `docker compose config` runs in the copy matrix; rendered vhost is checked | ✓ FLOWING |
| Optional application | `incluir_app_exemplo` | Copier boolean answer | True/false tree, settings, URLs, and nav verified | ✓ FLOWING |

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Copier installation and probe syntax | `.venv-template/bin/copier --version`; `sh -n ...` | `copier 9.17.1`; all scripts parsed | ✓ PASS |
| Identity / optional app / backup / operations | `python3 .template-tests/test_04_03_identity.py`, `test_04_04_optional_exemplo.py`, `test_04_05_backup.py`, `test_04_06_operations.py` | 3 + 3 + 4 + 2 tests passed | ✓ PASS |
| Confined restore cleanup | `timeout 30 sh ops/backup/testar_ensaio_restore.sh` | success/failure/interrupt mock passed | ✓ PASS |
| Copy matrix | `timeout 90 sh .template-tests/test_copier_copy.sh` | `OK: matriz Copier copy, exclusões, neutralidade e operação passou.` | ✓ PASS |
| Update lifecycle | `timeout 210 sh .template-tests/test_copier_update.sh` | exit `0` | ✓ PASS |

## Probe Execution

| Probe | Command | Result | Status |
|---|---|---|---|
| `.template-tests/test_copier_copy.sh` | `sh .template-tests/test_copier_copy.sh` | Valid true/false copies, invalid inputs, exclusions, audit and operations | PASS |
| `.template-tests/test_copier_update.sh` | `sh .template-tests/test_copier_update.sh` | A→B→C core update, `_commit` advancement, opt-out persistence | PASS |

## Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|---|---|---|---|---|
| TPL-01 | 04-02, 04-07 | Generate complete Django project via `copier copy` | ✓ SATISFIED | Executed two-variant copy matrix. |
| TPL-02 | 04-02, 03, 05, 07 | Parameterize per-system identity and infrastructure | ✓ SATISFIED | Validators, rendered env/configuration, and identity audit passed. |
| TPL-03 | 04-04, 04-07 | Pull core evolutions through `copier update` | ✓ SATISFIED | Executed A→B→C update probe exit `0`. |
| TPL-04 | 04-03 to 04-07 | No PCA or domain-business references in generated code | ✓ SATISFIED | Full case-insensitive generated tree audit passed for both variants. |
| INF-03 | 04-05 to 04-07 | Backup and nginx example in `ops/` | ✓ SATISFIED | Rendered backup, restore, retention and TLS nginx artifacts passed probes. |
| INF-04 | 04-05 to 04-07 | Loopback-only app and host-independent migration | ✓ SATISFIED | Rendered Compose, runbook and confined restore checks passed. |

No Phase 04 requirement is orphaned: all six IDs are declared by one or more plans and have executable evidence above.

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `README.md.jinja`, icon generator, probe assertions | various | “placeholder” text | ℹ️ Info | Describes deliberately non-secret configuration/icon placeholders or assertions; it does not flow to an incomplete feature. |
| Roadmap metadata | Phase 04 | `mode: mvp` goal is not valid User Story syntax | ⚠️ Warning | Process metadata discrepancy only. Per coordinator direction, it does not alter this technical verdict; reformat before relying on MVP-specific UAT framing. |

There are no unreferenced `TBD`, `FIXME`, or `XXX` markers in Phase 04 implementation artifacts. The intentional `pca` substring in the Portuguese word `interrupcao` is not a legacy-identity occurrence.

## Prohibition Review

All four Plan 04-07 negative controls are supported by independent code/probe evidence: no Copier post-generation task exists; secrets are neither questions nor answer fields and render as non-usable placeholders; the generated-tree auditor passes; and Compose/runbook use managed volumes plus containerized application tooling. No prohibition remains silently unverified.

## Gaps Summary

No implementation gap was found. Phase 5’s end-to-end system boot and user-flow validation remains future scope; it is not a missing Phase 04 deliverable because the roadmap explicitly assigns it to Phase 5.

---

_Verified: 2026-08-18T17:45:20Z_  
_Verifier: gsd-verifier_
