---
phase: 07-herdar-o-design-system-do-pca
plan: 02
subsystem: design-system
tags: [tailwind, css-custom-properties, dark-mode, copier, docker]

# Dependency graph
requires: ["07-01"]
provides:
  - "core/static/src/input.css como fonte física de toda cor do sistema (21 tokens claros, 18 overrides escuros), com @import de dominio.css como primeira declaração"
  - "core/static/src/dominio.css — stub contratual do derivado para tokens de estado (par X/X-tx, ponte data-* fora de @layer, piso de contraste)"
  - "tailwind.config.js verbatim (sem .jinja, sem interpolação) — darkMode por atributo, colors via var(--cor-*), borderRadius 2px único, fontSize de 6 degraus, fontFamily system-ui"
  - ".template-tests/test_07_tokens.py — contrato executável dos tokens sobre a FONTE, não sobre o CSS compilado"
affects: ["07-03", "07-04", "07-05", "07-06", "07-07", "07-08"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fonte física de cor em custom properties hex plano fora de @layer (:root + [data-tema=\"escuro\"]); tailwind.config.js só referencia via var(--cor-*), nunca declara valor"
    - "dominio.css como stub _skip_if_exists: template envia o contrato uma vez, o sistema gerado passa a ser dono do arquivo"
    - "Contrato de design tokens testado sobre a fonte (regex sobre input.css/tailwind.config.js), nunca sobre o artefato Tailwind compilado — dark: compila para :where(...) com forma variável"

key-files:
  created:
    - core/static/src/dominio.css
    - tailwind.config.js
    - .template-tests/test_07_tokens.py
  modified:
    - core/static/src/input.css
    - Dockerfile
    - .template-tests/test_04_03_identity.py
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_form_modal.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_confirmar_exclusao_modal.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/item_listar.html"
  deleted:
    - tailwind.config.js.jinja

key-decisions:
  - "Comentários de input.css/tailwind.config.js evitam literalmente as strings 'COR_PRIMARIA', 'color-mix' e '<alpha-value>' mesmo ao explicar por que esses padrões NÃO foram usados — os próprios gates de aceite do plano fazem grep textual dessas strings sem distinguir prosa de código; reescrever em paráfrase preserva a explicação sem acionar o gate"
  - "backdrop-blur-xs também não gera regra no Tailwind 3.4.17 (confirmado por build real, igual a shadow-xs) e foi trocado por backdrop-blur-sm nos dois modais — o plano previa essa possibilidade e pedia registro no SUMMARY se confirmada"
  - "A alternação regex do gate de safelist em test_07_tokens.py precisa listar as classes compostas (btn--primaria etc.) ANTES do prefixo 'btn' sozinho — regex tenta alternativas em ordem, não por comprimento, e 'btn' bloquearia o casamento do resto de 'btn--primaria'"

requirements-completed: [DS-01, DS-03, DS-04, DS-06]

# Metrics
duration: 25min
completed: 2026-08-23
---

# Phase 07 Plan 02: Herdar os tokens de cor e o tailwind.config.js do padrão de referência Summary

**`input.css` vira a fonte física de 21 tokens claros e 18 overrides escuros em hex plano (com `dominio.css` como extensão do derivado), `tailwind.config.js` passa a chegar verbatim ao sistema gerado sem nenhuma interpolação, e as três classes que a migração para `var()` mataria (`bg-ink/40`, `shadow-xs`, `backdrop-blur-xs`) foram corrigidas antes de virarem regressão visual.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-23T17:53:20Z
- **Completed:** 2026-08-23T18:07:10Z
- **Tasks:** 3
- **Files modified:** 10 (7 modificados, 3 criados, 1 apagado)

## Accomplishments
- `core/static/src/input.css` reescrito na ordem funcional exigida: `@import "./dominio.css";` na primeira linha, `@tailwind`, `@layer base` (anel de foco único), `@layer components` (8 classes), e os blocos `:root`/`[data-tema="escuro"]` fora de qualquer layer com os 21+18 tokens hex plano
- `core/static/src/dominio.css` nasce como stub contratual — zero regra CSS, só o contrato pt-BR do par `X`/`X-tx`, da ponte `data-*` fora de `@layer` e do piso de contraste
- `tailwind.config.js` (sem `.jinja`) chega verbatim: `darkMode` por atributo, 21 chaves de `colors` apontando para `var(--cor-*)`, `borderRadius` de 2px único, `fontSize` de 6 degraus com teto de 20px, `fontFamily` `system-ui`; `tailwind.config.js.jinja` apagado
- `Dockerfile` passa a copiar `core/static/src` inteiro (não só `input.css`), senão o `@import` de `dominio.css` quebra o estágio `assets` com exit 2
- `test_04_03_identity.py`: o teste que provava interpolação de cor no `tailwind.config.js` agora prova o oposto — as duas variantes de cor produzem `tailwind.config.js` idêntico byte a byte, sem hex, com a cor só entrando pelo `.env.example`
- Véu dos dois modais do app exemplo: `bg-ink/40` → `bg-black/40` (com `ink` migrado para `var(--cor-ink)`, o Tailwind não gera regra para `bg-ink/40` — o véu ficaria transparente)
- `shadow-xs` (4 ocorrências) → `shadow-sm`; `backdrop-blur-xs` (2 ocorrências, ambos os modais) → `backdrop-blur-sm` — as duas confirmadas sem regra gerada por build real do Tailwind 3.4.17
- `.template-tests/test_07_tokens.py` criado: 8 testes sobre a FONTE (import posicional, contagem exata de tokens claros/escuros, `colors` do config casando 1:1 com `:root`, `fontSize`/`borderRadius` sem chaves extras, `safelist` batendo com `@layer components`, e os três gates de regressão)

## Task Commits

Each task was committed atomically:

1. **Task 1: input.css vira a fonte física dos tokens, e dominio.css nasce** - `d259183` (feat)
2. **Task 2: tailwind.config.js verbatim + Dockerfile copiando o diretório de fonte** - `ff7668d` (feat)
3. **Task 3: Corrigir as classes que a migração para var() mata + contrato de tokens** - `5b48a42` (fix)

**Plan metadata:** commit pendente (docs: complete plan)

## Files Created/Modified
- `core/static/src/input.css` - reescrito: `@import`, `@layer base`/`@layer components`, `:root`/`[data-tema="escuro"]` com 21/18 tokens hex plano, `x-cloak` preservado
- `core/static/src/dominio.css` (novo) - stub contratual, zero regra CSS
- `tailwind.config.js` (novo, sem `.jinja`) - verbatim, aponta só para `var(--cor-*)`
- `tailwind.config.js.jinja` (apagado)
- `Dockerfile` - `COPY core/static/src ./core/static/src` no lugar de copiar só `input.css`
- `.template-tests/test_04_03_identity.py` - `test_tailwind_config_e_verbatim_e_cor_so_entra_pelo_env` substitui o teste antigo
- `.template-tests/test_07_tokens.py` (novo) - 8 testes de contrato sobre a fonte
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_form_modal.html` - `bg-black/40`, `backdrop-blur-sm`, `shadow-sm`
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_confirmar_exclusao_modal.html` - idem
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html` - `shadow-sm`
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/item_listar.html` - `shadow-sm`

## Decisions Made
Ver `key-decisions` no frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Comentários com strings literais que os próprios gates de aceite proíbem**
- **Found during:** Task 1 e Task 2
- **Issue:** A primeira redação de `input.css` explicava, em prosa pt-BR, por que `color-mix()` e `rgb(var(--x) / <alpha-value>)` não foram usados — mas o critério de aceite `grep -cE 'color-mix|<alpha-value>' core/static/src/input.css` não distingue prosa de código e reprovava com a explicação presente. O mesmo aconteceu em `tailwind.config.js`: o comentário de cabeçalho mencionava `COR_PRIMARIA` para explicar de onde a cor institucional viria, e `grep -cE 'COR_PRIMARIA|misturar|\{\{' tailwind.config.js` reprovava.
- **Fix:** Reescritos os dois comentários em paráfrase, sem as strings literais proibidas, preservando a explicação (“nenhuma função de mistura de cor resolvida pelo navegador”, “a cor institucional entra só pela variável de ambiente correspondente no `.env`”).
- **Files modified:** `core/static/src/input.css`, `tailwind.config.js`
- **Verification:** Os dois greps do plano passaram a retornar 0; `python3 -m unittest discover -s .template-tests -p 'test_04_03*.py'` verde.
- **Committed in:** `d259183` (Task 1), `ff7668d` (Task 2)

**2. [Rule 1 - Bug] Alternação regex de `test_07_tokens.py` capturando prefixo em vez da classe completa**
- **Found during:** Task 3
- **Issue:** O gate de `safelist` casava `\.(results|module|form-row|btn|btn--primaria|...)\b` — como a alternação de regex tenta as opções na ordem declarada e não por comprimento, `btn` (mais curto, listado antes) casava primeiro contra `.btn--primaria`, capturando só `btn` e deixando `--primaria` de fora. Resultado: o teste comparava `{results, module, form-row, btn}` contra a `safelist` de 8 entradas e falhava por "faltando no css" com as 4 variantes de `.btn--*`.
- **Fix:** Reordenada a alternação para listar as classes compostas (`btn--primaria`, `btn--secundaria`, `btn--neutro`, `btn--destrutiva`) antes do prefixo `btn` sozinho.
- **Files modified:** `.template-tests/test_07_tokens.py`
- **Verification:** `python3 -m unittest discover -s .template-tests -p 'test_07_tokens*.py'` verde (8/8), incluindo `test_safelist_bate_com_as_classes_declaradas_em_input_css`.
- **Committed in:** `5b48a42` (Task 3)

**3. [Rule 3 - Bloqueio] `_extract_block` de `test_07_tokens.py` não reconhecia fechamento indentado**
- **Found during:** Task 3
- **Issue:** A primeira versão do extrator de blocos usava `\n\}` (sem indentação) para achar o fechamento de `colors: { ... }` etc. em `tailwind.config.js` — mas esses blocos estão aninhados dentro de `theme.extend` e o fechamento real é `\n      },` (com espaços). O extrator falhava silenciosamente ou capturava conteúdo errado.
- **Fix:** Regex ajustada para `\n\s*\}` (objetos) e criado um extrator irmão `\n\s*\]` para arrays (`safelist`).
- **Files modified:** `.template-tests/test_07_tokens.py`
- **Verification:** Os 8 testes de `test_07_tokens.py` passaram a extrair os blocos corretamente e ficaram verdes.
- **Committed in:** `5b48a42` (Task 3)

---

**Total deviations:** 3 auto-fixed (2 bugs de regex, 1 ajuste de comentário para não colidir com gate textual)
**Impact on plan:** Nenhum desvio de escopo ou arquitetura — todos os três são correções mecânicas dentro do próprio código produzido nesta plan, necessárias para os gates do plano passarem como escrito.

## Issues Encountered
- `backdrop-blur-xs` foi confirmado, por build real do Tailwind 3.4.17 (`docker build --target assets .` seguido de inspeção do CSS compilado), como classe que **não gera regra** — igual a `shadow-xs`. Trocado por `backdrop-blur-sm` nos dois modais, conforme instrução condicional da Task 3. Registrado aqui como pedido pelo plano.
- Nenhum bloqueio.

## Provas Negativas Registradas

1. **Gate de opacidade sobre token migrado (Task 3):** com `bg-ink/40` reintroduzido temporariamente em `_form_modal.html`, `python3 -m unittest discover -s .template-tests -p 'test_07_tokens*.py'` falhou em `test_gate_de_opacidade_sobre_token_migrado`, listando exatamente o arquivo e o trecho `bg-ink/40`. Arquivo restaurado (`cp` do backup) em seguida; suíte voltou a passar 8/8.

## User Setup Required

None - nenhuma configuração de serviço externo necessária.

## Next Phase Readiness
- `input.css`/`dominio.css`/`tailwind.config.js` estão prontos para os planos seguintes: 07-04 (que implementa `core/tema.py` e prova por teste a igualdade entre os hex fixados aqui e as fórmulas de derivação) depende diretamente dos 14 valores de marca fixados nesta plan.
- `dominio.css` está pronto para receber `_skip_if_exists` no `copier.yml` — essa adição é do Padrão 3 (ponto de extensão de navegação), fora do escopo desta plan; confirmar que um plano seguinte da fase cobre isso.
- Toda a regressão relevante está verde: `test_04_*` (13/13), `test_07_tokens.py` (8/8), `test_copier_copy.sh` (matriz + neutralidade), `docker build --target assets .` (16657 bytes de CSS, acima do piso de 5000).

---
*Phase: 07-herdar-o-design-system-do-pca*
*Completed: 2026-08-23*

## Self-Check: PASSED

All created/modified files verified present on disk (core/static/src/input.css, core/static/src/dominio.css, tailwind.config.js, .template-tests/test_07_tokens.py, .template-tests/test_04_03_identity.py, Dockerfile, os 4 templates do app exemplo); tailwind.config.js.jinja confirmado ausente; todos os três hashes de task commit (d259183, ff7668d, 5b48a42) verificados presentes em `git log`.
