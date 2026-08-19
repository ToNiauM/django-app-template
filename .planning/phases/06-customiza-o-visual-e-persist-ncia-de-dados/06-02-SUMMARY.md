---
phase: 06-customiza-o-visual-e-persist-ncia-de-dados
plan: 02
subsystem: ui
tags: [logos, svg, static, whitenoise, favicon, django-templates]

# Dependency graph
requires:
  - phase: 06-01
    provides: "Tracer de nascimento corrigido (copier copy --vcs-ref=HEAD e limpeza uid 999) usado como prova de execução"
provides:
  - "Contrato de logo por arquivo fixo: core/static/img/logo-entidade.svg e logo-subsistema.svg — trocar = substituir o arquivo, sem editar código (D-65)"
  - "Logo do subsistema no cabeçalho da aside e no header mobile do shell (D-68)"
  - "Logo da entidade na tela de login e discreto no rodapé da aside (D-69)"
  - "Favicon via ícone PWA existente (icon-192.png) no base.html (D-72)"
  - "Regressão core/tests/test_logos.py que viaja com todo sistema gerado"
affects:
  - "06-03 (documentação da seção Customização de marca referencia os caminhos fixos criados aqui)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Arquivo fixo → {% static %}: extensão do padrão de identidade dos ícones PWA (D-20) para logos"
    - "{% load static %} explícito em templates filhos (o load do base.html não é herdado)"

key-files:
  created:
    - core/static/img/logo-entidade.svg
    - core/static/img/logo-subsistema.svg
    - core/tests/test_logos.py
  modified:
    - core/templates/core/shell.html
    - core/templates/core/login.html
    - core/templates/base.html

key-decisions:
  - "Comentário XML dos SVGs sem hífen duplo: 'docker compose build && docker compose up -d' no lugar de 'up -d --build' (XML proíbe -- dentro de comentário)"
  - "Formas distintas entre placeholders: círculo+cruz (entidade) vs quadrado arredondado+losango (subsistema) para diferenciação de relance"
  - "Favicon reaproveita icon-192.png — zero arquivo novo, mesmo contrato de substituição (D-72)"

patterns-established:
  - "alt de logo sempre derivado do context processor identidade (sistema_sigla), nunca literal de marca"

# Metrics
duration: 9min
completed: 2026-08-19
---

# Phase 06 Plan 02: Logos por arquivo fixo e favicon Summary

**Placeholders SVG neutros em caminhos fixos do core, inseridos via {% static %} nos quatro pontos travados (aside, header mobile, login, rodapé), favicon via ícone PWA e regressão Django que congela o contrato — tudo verde no tracer de nascimento.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-08-19T11:43:05Z
- **Completed:** 2026-08-19T11:52:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Contrato D-65 entregue: trocar qualquer logo = substituir UM arquivo de nome fixo em `core/static/img/`, sem editar código
- Placeholders neutros (D-66): SVGs com viewBox, sem width/height, paleta gray-400, zero marca de domínio — passam o scan de identidade do sistema gerado
- Logos nos quatro pontos travados: subsistema na aside + header mobile (D-68); entidade no login + rodapé discreto da aside (D-69)
- `alt` sempre derivado da identidade (`{{ sistema_sigla }}`) — logo complementa o texto, não o substitui (D-67)
- Favicon via `icon-192.png` existente no `base.html` — elimina o 302 ruidoso de `/favicon.ico` no LoginRequiredMiddleware
- Admin intocado (D-70) e `core/views.py` intocado (D-71) — confirmado por diff do plano inteiro
- `core/tests/test_logos.py` com 5 comportamentos, executado dentro da cópia gerada pelo tracer de nascimento (verde)

## Task Commits

Each task was committed atomically:

1. **Task 1: Placeholders SVG neutros em caminhos fixos** - `229a7bd` (feat)
2. **Task 2: Inserir logos nos templates e favicon no base.html** - `8d0ca19` (feat)
3. **Task 3: Regressão Django dos logos e prova ponta a ponta via tracer** - `7da09aa` (test)

**Plan metadata:** (final commit) - docs: SUMMARY + STATE + ROADMAP

## Files Created/Modified

- `core/static/img/logo-entidade.svg` - Placeholder neutro: círculo com cruz interna (identidade "da casa")
- `core/static/img/logo-subsistema.svg` - Placeholder neutro: quadrado arredondado com losango (identidade "deste sistema")
- `core/templates/core/shell.html` - `{% load static %}` + logo do subsistema (aside h-8, header mobile h-6) + logo da entidade no rodapé (h-5, opacity-60)
- `core/templates/core/login.html` - `{% load static %}` + logo da entidade acima do `<h1>Entrar</h1>` (h-12, mx-auto)
- `core/templates/base.html` - `<link rel="icon">` apontando para `{% static 'img/icon-192.png' %}`
- `core/tests/test_logos.py` - 5 testes: static() no shell e login, alt via SISTEMA_SIGLA, favicon, SVGs válidos nos caminhos fixos

## Decisions Made

- Comentário XML dos SVGs reformulado para `docker compose build && docker compose up -d` — o texto planejado (`up -d --build`) continha `--`, proibido dentro de comentário XML (arquivo não parseava)
- Formas geométricas distintas entre os dois placeholders para o operador diferenciá-los de relance (discretion do plano)
- Favicon adotado conforme recomendação do research (Open Question 2 resolvida): reaproveita o ícone PWA, mesmo contrato de substituição

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Comentário XML com hífen duplo quebrava o parse dos SVGs**
- **Found during:** Task 1 (verificação automatizada)
- **Issue:** O texto de comentário especificado no plano continha `--build`; XML proíbe `--` dentro de comentários e o `ET.parse` falhava
- **Fix:** Reformulado para `docker compose build && docker compose up -d` (semanticamente equivalente), com nota explicando a forma expandida
- **Files modified:** core/static/img/logo-entidade.svg, core/static/img/logo-subsistema.svg
- **Commit:** 229a7bd

**Nota sobre TDD (Task 3):** a task tem `tdd="true"`, mas o próprio plano ordena a implementação (Task 2) antes dos testes (Task 3) e os settings do template são `.jinja` (a suíte só roda na cópia gerada). O ciclo RED estrito não é aplicável — os testes nasceram como regressão e a prova de execução é o tracer de nascimento, exatamente como o plano prescreve.

## Verification Results

- `.template-tests/test_05_nascimento.sh` — **verde**: "OK: nascimento completo da cópia Copier passou." (suíte da cópia inclui test_logos.py)
- `python3 -m unittest discover -s .template-tests -p 'test_04_03_identity.py'` — **verde** (3 testes OK): nenhum arquivo do sistema gerado contém identidade proibida
- `git diff --name-only 31a1194..HEAD` — nenhum arquivo de admin nem `core/views.py` (D-70/D-71)
- `grep -E 'CFC|Sistema Base' core/tests/test_logos.py` — vazio (nenhum literal de marca nos asserts)

## Known Stubs

Nenhum — os placeholders SVG são o produto do plano (contrato D-66: neutros e substituíveis por design), não stubs pendentes.

## Next Phase Readiness

- Plano 06-03 (documentação) pode referenciar os caminhos fixos `core/static/img/logo-entidade.svg` e `logo-subsistema.svg` na seção "Customização de marca" do README gerado
- Contrato congelado por regressão que roda em todo sistema nascido

## Self-Check: PASSED
