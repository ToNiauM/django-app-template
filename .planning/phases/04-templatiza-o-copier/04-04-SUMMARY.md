---
phase: 04-templatiza-o-copier
plan: 04
subsystem: template-copier
tags: [copier, jinja, django, optional-app, integration-testing]

requires:
  - phase: 04-templatiza-o-copier
    provides: "Copier 9.17.1 isolado, respostas validadas e runtime Django neutro renderizável."
provides:
  - "apps/exemplo condicional, sem _skip_if_exists, para permitir opt-out persistente em updates futuros."
  - "Os três acoplamentos D-34/D-54 condicionais: settings, rota e navegação."
  - "README do app exemplo renderizado, neutro e orientado ao opt-out pelo Copier."
affects: [04-05, 04-06, 04-07, template-copier]

actuals:
  tokens: 5009
  tasks: 2
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Diretórios opcionais usam caminho Jinja no Copier, sem _skip_if_exists."
    - "Templates Django migrados para .jinja preservam suas tags em blocos raw do Copier."
    - "A opcionalidade é provada por cópias reais true/false, não apenas por inspeção do template."

key-files:
  created:
    - .template-tests/test_04_04_optional_exemplo.py
    - config/urls.py.jinja
    - core/templates/core/_nav.html.jinja
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/README.md.jinja"
  modified:
    - config/settings/base.py.jinja
    - .template-tests/test_04_03_identity.py
  removed:
    - config/urls.py
    - core/templates/core/_nav.html
    - apps/exemplo/README.md

key-decisions:
  - "A resposta incluir_app_exemplo cobre exatamente o pacote e os três acoplamentos D-34/D-54."
  - "O partial de navegação usa raw do Copier para preservar a linguagem de template do Django."
  - "O README do app é renderizado somente com o app e orienta copier update em vez de remoção manual."

patterns-established:
  - "Todo caminho que acompanha o app opcional fica dentro do diretório condicionado; não há lista de exclusões que impeça remoções em update."
  - "Integrações do Copier usam dados explícitos não-default em ambas as variantes para validar estrutura, compilação e segurança."

requirements-completed: [TPL-03, TPL-04]

coverage:
  - id: D1
    description: "A cópia com incluir_app_exemplo=false omite o pacote, ExemploConfig e rota, preservando admin, healthz, core e cookies seguros."
    requirement: TPL-03
    verification:
      - kind: integration
        ref: ".template-tests/test_04_04_optional_exemplo.py#test_false_omits_only_the_example_app_integrations"
        status: pass
      - kind: integration
        ref: "copier copy false + compileall config + evidências ASVS L1"
        status: pass
    human_judgment: false
  - id: D2
    description: "A cópia com incluir_app_exemplo=true contém o pacote, a config, a rota, os links e o README interpolado sem identidade legada."
    requirement: TPL-04
    verification:
      - kind: integration
        ref: ".template-tests/test_04_04_optional_exemplo.py#test_true_renders_app_settings_and_route"
        status: pass
      - kind: integration
        ref: ".template-tests/test_04_04_optional_exemplo.py#test_navigation_and_readme_follow_the_same_boolean_contract"
        status: pass
    human_judgment: false
  - id: D3
    description: "A variante sem app não resolve namespaces ausentes e a documentação instrui o opt-out persistente pelo Copier."
    requirement: TPL-03
    verification:
      - kind: integration
        ref: "copier copy true/false + inspeção de _nav.html e README.md renderizados"
        status: pass
    human_judgment: false

metrics:
  duration: 10min
  completed: 2026-08-18
status: complete
---

# Phase 04 Plan 04: Opcionalidade persistente do app exemplo Summary

**O Copier agora renderiza `apps/exemplo` e somente seus três acoplamentos como uma unidade opcional, com navegação Django preservada e opt-out documentado.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-18T16:38:19Z
- **Completed:** 2026-08-18T16:48:07Z
- **Tasks:** 2/2
- **Files modified:** 31

## Accomplishments

- Movido o pacote para `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/`, sem `_skip_if_exists`, e condicionados `ExemploConfig` e a rota `/exemplo/`.
- Migrado o partial de navegação para Jinja Copier, mantendo o item Início intacto e renderizando resoluções/links do exemplo como um bloco único.
- Migrado o README do app para variante renderizada que inclui o nome do sistema, o fluxo `copier update --data incluir_app_exemplo=false` e o protocolo de banco/check/testes.
- Adicionadas integrações reais do Copier para as variantes true/false, mais a correção da integração de identidade anterior após a migração de caminho.

## Task Commits

1. **Task 1: Condicionar diretório, settings e URLs do app exemplo** — `86a46df` (RED), `1815b4e` (GREEN)
2. **Task 2: Condicionar navegação e documentar opt-out persistente** — `7b1481f` (RED), `c8a3002` (GREEN)
3. **Correção direta causada pela migração de caminho** — `6692f57` (fix)

## Files Created/Modified

- `config/settings/base.py.jinja` — torna o `ExemploConfig` dependente da resposta Copier.
- `config/urls.py.jinja` — renderiza o include de `/exemplo/` somente na variante completa.
- `core/templates/core/_nav.html.jinja` — preserva tags Django em raw e condiciona ambos os links do exemplo.
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/` — pacote inteiro opcional, incluindo o README renderizado.
- `.template-tests/test_04_04_optional_exemplo.py` — matriz de integração true/false no destino gerado.

## Decisions Made

- A condicional está limitada ao pacote e aos três pontos D-34/D-54; core, auth, healthz, shell e infraestrutura permanecem fora dela.
- Tags Django no partial foram encapsuladas por `{% raw %}` do Copier para evitar colisão entre os dois motores de template.
- O README gerado é parte do pacote opcional e apresenta `copier update` como fluxo primário, sem referências a sistemas ou domínios reais.

## Verification Evidence

- `.venv-template/bin/python .template-tests/test_04_04_optional_exemplo.py` passou com 3 testes de integração Copier.
- A matriz final gerou árvores `false` e `true` com dados explícitos; ambas compilaram `config/`, a variante false não contém `apps.exemplo` nem namespaces do exemplo, e a variante true contém pacote, config, rota, navegação e README interpolado.
- Evidências ASVS L1 passaram: admin, healthz, core, `SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` permanecem na variante false; a variante true não contém identificadores legados no app ou na navegação.
- Não existe `_skip_if_exists` no contrato do app opcional.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Atualizar integração de identidade para o novo caminho condicional**
- **Found during:** Verificação completa após Task 2.
- **Issue:** O teste de identidade do Plano 04-03 ainda lia `apps/exemplo/...`; o caminho deixou de existir após a migração necessária desta tarefa.
- **Fix:** Centralizado o caminho-fonte opcional no teste e ajustadas as leituras do seed e do README `.jinja`.
- **Files modified:** `.template-tests/test_04_03_identity.py`.
- **Verification:** A integração de identidade e a matriz de opcionalidade executam cópias reais sem erro de caminho.
- **Committed in:** `6692f57`.

---

**Total deviations:** 1 auto-fixed (Rule 1 - regressão de teste diretamente causada pela migração de caminho).
**Impact on plan:** Mantém a suíte existente alinhada ao novo contrato de diretório, sem ampliar os quatro destinos opcionais.

## Known Stubs

None.

## Issues Encountered

Nenhum bloqueio. O Copier 9.17.1 emite `DirtyLocalWarning` durante cópias de validação da árvore de trabalho em edição; as cópias incluíram as mudanças intencionalmente e todas as evidências passaram.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- O Plano 04-07 pode executar o ensaio A→B→C de `copier update`; este plano garante que nenhum caminho opcional usa `_skip_if_exists`.
- As variantes completas e sem exemplo já estão estruturalmente válidas para os planos de operação e de atualização.

## Self-Check: PASSED

- Os seis arquivos-chave existem nos caminhos condicionais/renderizáveis esperados.
- Os cinco commits de RED, GREEN e correção de regressão estão presentes no histórico.
- A única exclusão rastreada desta etapa é o README-fonte substituído pelo README `.jinja`, documentada como migração intencional.

---
*Phase: 04-templatiza-o-copier*
*Completed: 2026-08-18*
