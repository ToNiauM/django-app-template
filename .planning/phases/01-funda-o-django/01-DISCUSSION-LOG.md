# Phase 1: Fundação Django - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-17
**Phase:** 1-Fundação Django
**Areas discussed:** Estratégia de templatização, Identificador de login, Organização dos settings, Build do Tailwind, Gestão de dependências

**Mode:** `--auto` — todas as áreas cinzentas foram selecionadas e resolvidas automaticamente com a opção recomendada (ancorada na PCA, fonte de extração). Nenhuma pergunta interativa foi feita.

---

## Estratégia de templatização

| Option | Description | Selected |
|--------|-------------|----------|
| Sistema-modelo plano primeiro | Desenvolver projeto Django executável na raiz; templatizar via Copier só na Fase 4 | ✓ |
| Copier desde o início | Desenvolver já dentro de estrutura jinja/`copier.yml` | |

**User's choice:** [auto] Sistema-modelo plano primeiro (recommended default)
**Notes:** Permite validar cada fase rodando o sistema de verdade; templatização é transformação mecânica ao final.

---

## Identificador de login

| Option | Description | Selected |
|--------|-------------|----------|
| E-mail (padrão PCA) | `USERNAME_FIELD = "email"`, sem `username`, manager customizado | ✓ |
| Username (AbstractUser padrão) | Manter username como identificador | |

**User's choice:** [auto] E-mail (recommended default)
**Notes:** Extraído de `/opt/web/pca/core/models.py` — `UsuarioManager` com `use_in_migrations = True`.

---

## Organização dos settings

| Option | Description | Selected |
|--------|-------------|----------|
| Módulos por ambiente (padrão PCA) | `config/settings/{base,dev,prod}.py` via `DJANGO_SETTINGS_MODULE` | ✓ |
| Arquivo único | `settings.py` único com toggles de env | |

**User's choice:** [auto] Módulos por ambiente (recommended default)

---

## Build do Tailwind

| Option | Description | Selected |
|--------|-------------|----------|
| Multi-stage Docker (padrão PCA) | Estágio `node:20-alpine` com `npx tailwindcss@3.4.17` + guarda de tamanho do CSS | ✓ |
| Standalone CLI no host | Binário tailwindcss fora do Docker | |
| CDN | Tailwind via CDN (descartado: proibido em produção) | |

**User's choice:** [auto] Multi-stage Docker (recommended default)
**Notes:** Padrão comentado no próprio `Dockerfile` da PCA (falha o build se só o preflight for emitido).

---

## Gestão de dependências

| Option | Description | Selected |
|--------|-------------|----------|
| requirements.txt (padrão PCA) | Pip + requirements.txt | ✓ |
| pyproject.toml + uv | Toolchain moderna | |

**User's choice:** [auto] requirements.txt (recommended default)

---

## Claude's Discretion

- Detalhes de `compose.yml`, `entrypoint.sh` e healthchecks (extrair da PCA e generalizar)
- Tela de login mínima nesta fase (identidade visual completa é a Fase 2)
- Versões exatas de dependências (partir do `requirements.txt` da PCA)

## Deferred Ideas

None.
