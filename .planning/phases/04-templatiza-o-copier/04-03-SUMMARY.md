---
phase: 04-templatiza-o-copier
plan: 03
subsystem: template-copier
tags: [copier, jinja, environment, tailwind, runtime-identity, security]

requires:
  - phase: 04-templatiza-o-copier
    provides: "Copier 9.17.1, respostas validadas e .env.example renderizado."
provides:
  - "Identidade obrigatória em runtime por .env, com cor de marca interpolada somente no build Tailwind."
  - "Entrypoint neutro, seed genérico e ícones que leem identidade obrigatória do .env."
  - "Auditoria de cópia real com localização de ocorrências, limites léxicos e verificação de exclusões."
affects: [04-04, 04-05, 04-06, 04-07, template-copier]

tech-stack:
  added: []
  patterns:
    - ".env primeiro no runtime; Jinja somente para a constante Tailwind resolvida no build."
    - "Auditoria de conteúdo e caminhos reporta todas as localizações antes de falhar."

key-files:
  created:
    - .template-tests/test_04_03_identity.py
    - tailwind.config.js.jinja
    - config/settings/base.py.jinja
  modified:
    - apps/exemplo/templates/exemplo/dashboard.html
    - entrypoint.sh
    - apps/exemplo/management/commands/seed_exemplo.py
    - apps/exemplo/README.md
    - ops/gerar_icones_pwa.py
    - apps/exemplo/models.py
    - apps/exemplo/migrations/0001_initial.py
  removed:
    - tailwind.config.js
    - config/settings/base.py

decisions:
  - "Runtime exige SISTEMA_NOME, SISTEMA_SIGLA e COR_PRIMARIA no .env; somente Tailwind recebe cor via Jinja."
  - "Gunicorn conserva 0.0.0.0:8000; WEB_PORT permanece exclusivamente no bind/proxy do host."
  - "Auditoria usa limites léxicos e remove somente o campo _src_path da inspeção, pois ele é metadata indispensável do Copier update."

actuals:
  tokens: 8272
  tasks: 2
  commits: 5

metrics:
  duration: 22min
  completed: 2026-08-18
status: complete
---

# Phase 04 Plan 03: Runtime neutro e identidade via ambiente Summary

**O sistema gerado obtém identidade obrigatória do `.env`, limita Jinja à cor do build Tailwind e passa por auditoria integral da árvore Copier.**

## Accomplishments

- Migrados `tailwind.config.js` e `config/settings/base.py` para variantes `.jinja`; o Python renderizado não varia entre cópias e mantém a validação `#RRGGBB`.
- Removido o fallback de cor do dashboard e mantido o contexto obrigatório de identidade.
- Documentado o bind interno fixo do Gunicorn, neutralizado o seed e feito o gerador de ícones exigir `COR_PRIMARIA` e `SISTEMA_SIGLA` do `.env` quando não recebe overrides explícitos.
- Neutralizados termos de domínio legado no app, migração e testes para cumprir a auditoria de toda a árvore gerada.
- Criados testes TDD de integração que renderizam cópias com respostas distintas, checam exclusões e acumulam todas as ocorrências com arquivo, linha e coluna.

## Task Commits

1. **Task 1: Parametrizar identidade obrigatória e cor de build** — `423503d` (RED), `a63adc5` (GREEN)
2. **Task 2: Neutralizar entrypoint, seed, ícones e árvore gerada** — `3493799` (RED), `863294a` (auditoria), `dfac852` (GREEN)

## Verification Evidence

- `.venv-template/bin/python .template-tests/test_04_03_identity.py` passou: 3 testes, incluindo duas cores renderizadas e Python idêntico.
- `copier copy` com respostas Aurora passou na auditoria de caminhos/conteúdo por limites léxicos; `.planning`, `.template-tests`, `copier.yml`, venv, documentos internos e fontes `.jinja` não chegaram ao destino.
- `compileall` dos diretórios `config`, `apps` e do gerador de ícones do destino passou; `sh -n entrypoint.sh` também passou.
- O gerador de ícones do sistema gerado executou com `.env.example` copiado para `.env` e produziu os três PNGs esperados.

## Deviations from Plan

### Approved audit interpretation

**1. [Explicit auto decision] Preservar metadata do Copier e cores neutras herdadas**
- **Found during:** Task 2
- **Issue:** A busca literal encontrava `sistema_base` em `_src_path` do `.copier-answers.yml`, indispensável para `copier update`, e `CFC` como substring de `#fcfcfb`.
- **Resolution:** Auditoria passou a usar limites léxicos, remover somente o valor `_src_path` antes da inspeção e continuar reportando todas as demais ocorrências com localização.
- **Impact:** Mantém o contrato de atualização do Copier e a paleta neutra byte a byte.

### Auto-fixed Issues

**1. [Rule 2 - Information disclosure] Neutralizar referências de domínio fora da lista inicial de arquivos**
- **Found during:** Task 2
- **Issue:** A auditoria obrigatória encontrou termos proibidos em `CategoriaChoices`, migração e testes do app exemplo.
- **Fix:** Categoria e fixtures foram generalizadas para `RECURSOS` e domínios de teste `exemplo.test`.
- **Files modified:** `apps/exemplo/models.py`, migração inicial e três testes do app.
- **Commit:** `dfac852`

**2. [Rule 3 - Blocking] Corrigir permissão da migração existente**
- **Found during:** Task 2
- **Issue:** `apps/exemplo/migrations/0001_initial.py` pertencia a outro usuário e não podia receber a correção exigida.
- **Fix:** A propriedade foi transferida ao usuário do workspace antes da edição.
- **Commit:** `dfac852`

## Known Stubs

None.

## Self-Check: PASSED

- Arquivos renderizáveis, scripts neutros e o resumo existem nos caminhos esperados.
- Os cinco commits de TDD e implementação estão presentes no histórico.

---
*Phase: 04-templatiza-o-copier*
*Completed: 2026-08-18*
