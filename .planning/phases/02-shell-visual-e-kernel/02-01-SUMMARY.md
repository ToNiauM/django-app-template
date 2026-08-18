---
phase: 02-shell-visual-e-kernel
plan: 01
subsystem: identidade-visual
tags: [django, settings, context-processor, tailwind, css]
requires: []
provides:
  - "Settings SISTEMA_NOME/SISTEMA_SIGLA/COR_PRIMARIA lidos do .env com defaults e COR_PRIMARIA validada como #RRGGBB no boot (D-16, T-02-01)"
  - "Context processor core.context_processors.identidade expondo sistema_nome/sistema_sigla/cor_primaria a todo template"
  - "Paleta Tailwind semântica: neutros (page, surface, surface-2, ink, ink-2, muted, grid) + marca (brand, brand-hover, brand-ink, brand-tint) derivada de um único literal (D-17)"
  - "Regra [x-cloak] { display: none !important } no CSS final (pré-requisito do shell da wave 2)"
affects: [02-02, 02-03, 02-04, fase-4-copier]
tech-stack:
  added: []
  patterns:
    - "Validação de settings no boot com ImproperlyConfigured (fail-fast contra .env malformado)"
    - "Derivação de tints/shades em JS puro dentro do tailwind.config.js (função misturar) — sem CSS vars"
key-files:
  created:
    - core/tests/test_identidade.py
  modified:
    - config/settings/base.py
    - core/context_processors.py
    - .env.example
    - tailwind.config.js
    - core/static/src/input.css
decisions:
  - "COR_PRIMARIA validada com re.fullmatch(r'#[0-9a-fA-F]{6}') no boot — ImproperlyConfigured é a barreira contra CSS injection via .env (T-02-01), já que a plan 02-03 interpolará o valor em <style> com |safe"
  - "Tokens de marca derivados por misturar(hex, alvo, fator) em JS puro — tailwind.config.js mantém um ÚNICO hex literal de identidade (D-17); Fase 4 (Copier) parametrizará exatamente essa linha + o .env"
  - "Neutros de template (page/surface/ink/etc.) são literais fixos do template, NÃO identidade — fora dos dois touchpoints por design"
metrics:
  duration: 4min
  completed: 2026-08-18
---

# Phase 2 Plan 01: Identidade Parametrizada (settings + paleta Tailwind) Summary

Identidade via `.env` → settings → context processor com validação #RRGGBB no boot, e paleta Tailwind completa (neutros + marca derivada de um único literal), fechando o Pitfall 6 (bg-page/bg-surface/text-ink ignorados pelo JIT) e prevenindo o Pitfall 7 ([x-cloak] inerte).

## O que foi construído

### Task 1 — Settings de identidade + context processor + teste (commit 17f71c9)

- `config/settings/base.py`: `SISTEMA_NOME` (default "Sistema Base"), `SISTEMA_SIGLA` (default "SB") e `COR_PRIMARIA` (default "#1e40af") lidos do `.env` via django-environ, após o bloco de localização. `COR_PRIMARIA` fora do formato `#RRGGBB` derruba o boot com `ImproperlyConfigured` e mensagem em pt-BR (mitigação T-02-01 — o valor será interpolado em CSS com `|safe` na plan 02-03). Comentário documenta que estes 3 settings + o literal do `tailwind.config.js` são os DOIS únicos touchpoints de identidade da Fase 4 (Copier).
- `core/context_processors.py`: `identidade(request)` retorna `{sistema_nome, sistema_sigla, cor_primaria}`; registrado em `TEMPLATES[0]["OPTIONS"]["context_processors"]` após `usuario_atual`.
- `.env.example`: bloco "Identidade do sistema" documentando as 3 variáveis (formato `#RRGGBB` obrigatório; futuras variáveis Copier). As mesmas 3 linhas foram adicionadas ao `.env` local (não versionado) para exercitar o caminho `.env` → settings.
- `core/tests/test_identidade.py`: 3 testes — formato de `COR_PRIMARIA`, identidade presente no `response.context` de GET `/login/` (prova de registro do context processor) e presença literal do processor nos settings. Suíte roda no container com bind-mount pontual: 3/3 OK.

### Task 2 — Paleta Tailwind + regra [x-cloak] (commit 009c162)

- `tailwind.config.js`: `const COR_PRIMARIA = "#1e40af"` como ÚNICO literal de identidade; função `misturar(hex, alvo, fator)` em JS puro deriva `brand-hover` (clareado 12%), `brand-ink` (escurecido 18%) e `brand-tint` (fundo tênue, 90% para o branco). Neutros de template: `page #f9f9f7`, `surface #fcfcfb`, `surface-2 #f3f2ef`, `ink #0b0b0b`, `ink-2 #52514e`, `muted #77756f`, `grid #e4e2dd`. Sintaxe Tailwind 3.4 mantida (stack fechada).
- `core/static/src/input.css`: regra `[x-cloak] { display: none !important; }` com comentário explicando o porquê (gaveta mobile do shell da wave 2 piscaria aberta antes do Alpine iniciar — Pitfall 7).
- Imagem reconstruída (`docker compose build web` passou na guarda de 5000 bytes) e containers no ar (`web` healthy). CSS final no container contém `bg-page` e `x-cloak`.

## Verificação

- `manage.py test core.tests -v 2` no container: **16/16 OK** (13 da Fase 1 + 3 novos).
- `manage.py check`: sem erros.
- `grep` no CSS gerado dentro do container: `bg-page` ≥ 1, `x-cloak` ≥ 1 (Pitfalls 6 e 7 fechados).
- Tela de login agora renderiza com fundo `#f9f9f7` (bg-page) e card `#fcfcfb` (bg-surface).

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

Nenhum — todos os valores fluem do `.env`/settings reais; nenhum placeholder ou dado vazio hard-coded.

## Self-Check: PASSED

- Todos os 6 arquivos criados/modificados existem no disco.
- Commits 17f71c9 e 009c162 presentes no histórico.
- Suíte completa e `check` passando no container.
