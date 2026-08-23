---
phase: 07-herdar-o-design-system-do-pca
plan: 04
subsystem: design-system
tags: [django, colorsys, css-custom-properties, context-processor, docker-compose, copier]

# Dependency graph
requires:
  - phase: 07-01
    provides: ".template-tests/ensaio_django.sh — banco de ensaio reutilizável para rodar qualquer alvo Django dentro de uma cópia real do template"
  - phase: 07-02
    provides: "core/static/src/input.css como fonte física dos 21+18 tokens de cor, com a família de marca default derivada de #1e40af"
provides:
  - "core/tema.py — misturar(), com_hsl(), familia_marca(), css_da_marca(), COR_PAGE_CLARO, COR_PAGE_ESCURO, verificados byte a byte contra o padrão de referência"
  - "tema_css e cor_page_escuro expostos a todo template pelo context processor identidade, sem processor novo e sem tocar config/settings/base.py.jinja"
  - "<style>{{ tema_css|safe }}</style> em base.html, depois do <link> do Tailwind, sobrescrevendo os defaults de input.css nos dois temas por ordem de declaração"
  - ".template-tests/test_07_cor_runtime.sh — prova executável de D-80 (COR_PRIMARIA muda a paleta em runtime, docker compose up -d web, sem rebuild de imagem)"
  - "README.md.jinja sem a mentira do Pitfall 18 — COR_PRIMARIA descrita como runtime, não build"
affects: ["07-05", "07-06", "07-07", "07-08"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Derivação de paleta em Python no boot (core/tema.py), espelhando o precedente de core/admin_site.py:each_context — valor seguro para |safe porque validado #RRGGBB no boot"
    - "Convenção de chave dict para tema escuro: sufixo estável ':escuro' (ex.: 'brand:escuro'), documentada na docstring de familia_marca()"
    - "Amarração por teste (não por valor cravado): core/tests/test_tema.py lê input.css via regex e compara contra a derivação — divergência do CSS derruba a suíte"
    - "Depois de docker compose up -d <serviço>, NUNCA chamar de volta um subcomando de ensaio_django.sh (porta/subir) para redescobrir estado — garantir_banco() ali faz uma única tentativa de curl sem retry e, chamada logo após um recreate, interpreta o serviço-ainda-subindo como banco não saudável e detona uma recriação completa com porta nova. A porta é capturada uma vez e reaproveitada; quem espera é um laço de retry PRÓPRIO do chamador."

key-files:
  created:
    - core/tema.py
    - core/tests/test_tema.py
    - .template-tests/test_07_cor_runtime.sh
  modified:
    - core/views.py
    - core/context_processors.py
    - core/templates/base.html
    - README.md.jinja

key-decisions:
  - "css_da_marca() gera exatamente 14 linhas de declaração (--cor-<nome>: #hex;), verificadas por regex estrita em vez da leitura literal de 'sem aspas' da prosa do plano — os dois seletores (:root e [data-tema=\"escuro\"]) legitimamente usam aspas duplas, então o teste de segurança foca nos caracteres de risco real (<, >, ', @) e na forma exata de cada linha de declaração, não na ausência total de aspas na string inteira"
  - "test_07_cor_runtime.sh captura a porta do banco de ensaio UMA vez (passo 1, de ENSAIO_PORTA) e nunca mais chama ensaio_django.sh porta/subir depois de um up -d web — a espera por /healthz é um laço de retry próprio da suíte, não delegado ao helper (ver Deviations, Rule 1)"

requirements-completed: [DS-01, DS-06]

# Metrics
duration: 35min
completed: 2026-08-23
---

# Phase 07 Plan 04: COR_PRIMARIA comanda a família de marca inteira em runtime Summary

**`core/tema.py` deriva a família de marca inteira (14 valores, 2 temas) de uma única cor em Python no boot, `tema_css` chega a todo template via context processor e vence os defaults de `input.css` por ordem de declaração no `<style>` de `base.html`, e `.template-tests/test_07_cor_runtime.sh` prova executavelmente que trocar `COR_PRIMARIA` no `.env` e recriar só o `web` (`docker compose up -d web`, sem rebuild) muda a paleta nos dois temas — a afirmação central da Fase 7.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-08-23T15:39:00-03:00
- **Completed:** 2026-08-23T16:00:28-03:00
- **Tasks:** 4
- **Files modified:** 7 (4 criados, 3 modificados)

## Accomplishments

- `core/tema.py`: `misturar()`/`com_hsl()` portados para Python do antigo `tailwind.config.js.jinja`, verificados byte a byte contra os 12 valores de referência (`#003c71`) e contra os 14 valores do default do `copier.yml` (`#1e40af`) já escritos em `input.css` pelo plano 07-02 — todos batem exatamente
- `familia_marca()`/`css_da_marca()` com `lru_cache`, seguindo o precedente de segurança de `core/admin_site.py:each_context` (`|safe` seguro porque `COR_PRIMARIA` é validada `#RRGGBB` no boot)
- `COR_PAGE_CLARO`/`COR_PAGE_ESCURO` nomeados em Python e amarrados a `input.css` por teste; `core/views.py` não tem mais nenhum hex literal (o `background_color` do manifest usa `COR_PAGE_CLARO`)
- `core/context_processors.py` estende `identidade` (sem processor novo, `config/settings/base.py.jinja` intocado) com `tema_css` e `cor_page_escuro`; `base.html` ganha `<style>{{ tema_css|safe }}</style>` logo depois do `<link>` do Tailwind, com `{% comment %}` explicando posição, segurança do `|safe` e o comando de recarga correto
- `.template-tests/test_07_cor_runtime.sh`: 7 passos (linha de base → troca no `.env` → `up -d web` → cor nova → ID de imagem idêntico → restauração), `trap` com `codigo=$?`/`exit "$codigo"` preservando o código de saída original, `restaurar()` sem `set -e` ativo
- `README.md.jinja`: item "Cor primária" reescrito — `COR_PRIMARIA` é runtime, `docker compose up -d web` basta, `restart` explicitamente descartado com o motivo; `input.css`/`dominio.css` citados como donos dos tokens não parametrizados

## Task Commits

Each task was committed atomically:

1. **Task 1: core/tema.py — a família de marca derivada em Python e os dois --cor-page com nome** - `eecc3bd` (feat)
2. **Task 2: tema_css no contexto e o `<style>` de override em base.html** - `eb6c484` (feat)
3. **Task 3: Prova executável de D-80 — a cor troca em runtime, sem rebuild** - `77abd77` (feat)
4. **Task 4: O README do sistema gerado para de mentir sobre COR_PRIMARIA** - `f75eff6` (docs)

**Plan metadata:** commit pendente (docs: complete plan)

## Files Created/Modified

- `core/tema.py` (novo) - `_canais`/`_hex` (arredondamento meia-para-cima), `misturar`, `com_hsl`, `familia_marca` (lru_cache), `css_da_marca`, `COR_PAGE_CLARO`, `COR_PAGE_ESCURO`
- `core/tests/test_tema.py` (novo) - 8 casos de comportamento: primitivos, `familia_marca` do padrão e do default, formato hex, `css_da_marca` estrutural, amarração de `--cor-page`, manifest
- `core/views.py` - `background_color` do manifest usa `COR_PAGE_CLARO` (import de `core.tema`); zero hex literal restante
- `core/context_processors.py` - `identidade` ganha `tema_css` (`css_da_marca(settings.COR_PRIMARIA)`) e `cor_page_escuro` (`COR_PAGE_ESCURO`)
- `core/templates/base.html` - `<style>{{ tema_css|safe }}</style>` depois do `<link>` do Tailwind, com `{% comment %}` de racional
- `.template-tests/test_07_cor_runtime.sh` (novo) - prova executável de D-80, 141 linhas, executável
- `README.md.jinja` - item "Cor primária" reescrito; nota 1 distingue arquivo estático (exige `--build`) de `COR_PRIMARIA` (runtime)

## Decisions Made

Ver `key-decisions` no frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Regex de `css_da_marca` na Task 1 não aceitava dígitos no sufixo da variável**
- **Found during:** Task 1, primeira execução da suíte
- **Issue:** `test_css_da_marca_tem_dois_seletores_seguros_e_so_hex` usava `^--cor-[a-z-]+: #[0-9a-f]{6};$`, sem dígitos na classe de caracteres — falhava em `--cor-seq-600: #1e40af;` (o `600` do nome da variável).
- **Fix:** Classe de caracteres ampliada para `[a-z0-9-]+`.
- **Files modified:** `core/tests/test_tema.py`
- **Verification:** `bash .template-tests/ensaio_django.sh testar core.tests.test_tema core.tests.test_pwa` passou a sair 18/18 verde.
- **Committed in:** `eecc3bd` (Task 1)

**2. [Rule 1 - Bug] `test_07_cor_runtime.sh` redescobrindo a porta via `ensaio_django.sh porta` logo após um `up -d web` recriava o banco inteiro**
- **Found during:** Task 3, primeira execução real da suíte (ponta a ponta, com containers)
- **Issue:** A primeira versão chamava `bash "${ENSAIO}" compor up -d web` (recria só o `web`) e, na sequência imediata, `PORTA=$(bash "${ENSAIO}" porta)` para descobrir a porta antes de esperar `/healthz`. `garantir_banco()` (dentro de `ensaio_django.sh`) faz **uma única tentativa** de curl em `/healthz` (sem retry) para decidir se o banco está saudável; chamada nos milissegundos seguintes a um `up -d web` que acabou de recriar o container, quase sempre encontrava o serviço ainda subindo, interpretava isso como "banco não saudável ou impressão digital mudou" e disparava `derrubar_interno` + `criar_banco` — um `copier copy` + `docker compose up -d --build` do zero, com uma porta **nova**. A suíte então tentava curlar a `ENSAIO_URL` antiga (porta obsoleta) e falhava com "Failed to connect" no passo 5, mascarando a causa real.
- **Fix:** `WEB_PORT` nunca muda quando só `COR_PRIMARIA` é editada — a porta é capturada **uma única vez** no passo 1 (de `ENSAIO_PORTA`, na saída de `subir`) e reaproveitada em todos os passos seguintes. A espera por `/healthz` depois de cada `up -d web` passou a ser um laço de retry (`esperar_healthz()`) **próprio da suíte**, nunca delegado de volta a um subcomando de `ensaio_django.sh`.
- **Files modified:** `.template-tests/test_07_cor_runtime.sh`
- **Verification:** Execução completa (`bash .template-tests/test_07_cor_runtime.sh`) passou a sair 0 de forma repetível — confirmado em três execuções consecutivas, a segunda e a terceira em ~14s (sem recriação completa, só recriação do `web` nos passos 4 e 7, como esperado).
- **Committed in:** `77abd77` (Task 3)

---

**Total deviations:** 2 auto-fixed (2 bugs — um de regex no teste, um de timing/race no script de runtime)
**Impact on plan:** Ambos os desvios são correções mecânicas dentro do próprio código produzido nesta plan; nenhuma mudança de escopo ou arquitetura. O segundo é o mais relevante: sem ele, a suíte que prova a afirmação central da fase seria inerentemente instável (falha intermitente por corrida, não por defeito real na derivação de cor).

## Issues Encountered

Nenhum bloqueio não resolvido. A investigação da prova negativa da Task 3 (remover o `<style>` de `tema_css` de `base.html`) revelou que a expectativa de prosa do plano — "a suíte falha no passo 5" — não se confirma literalmente: como `curl` busca só o HTML de `/login/`, e o `tailwind.css` compilado é um arquivo **externo** referenciado por `<link>` (não inlinado na resposta), a **única** fonte de texto `--cor-brand:` no corpo HTML é o `<style>` injetado por `tema_css`. Removê-lo faz **zero** ocorrências aparecerem, e a suíte falha já no **passo 2** (linha de base), com a mensagem própria `'linha de base não contém --cor-brand: #1e40af...'` — mais cedo e mais direto do que o passo 5 previsto na prosa do plano, mas provando exatamente a mesma coisa (o canal depende inteiramente do `<style>`). Registrado aqui como divergência entre a prosa de planejamento e o comportamento real, sem alteração no comportamento do script (a suíte já falha corretamente, só que num passo anterior).

## Provas Negativas Registradas

1. **Divergência de `input.css` derruba a igualdade com `familia_marca()` (Task 1):** com `--cor-brand: #1e40af;` do bloco `:root` trocado temporariamente para `#123456`, `bash .template-tests/ensaio_django.sh testar core.tests.test_tema` falhou em `test_familia_marca_do_default_do_copier_igual_ao_input_css` com `AssertionError: '#1e40af' != '#123456'`. Arquivo restaurado (`cp` do backup) em seguida; `diff` confirmou identidade byte a byte; suíte voltou a passar 8/8.
2. **Divergência do `--cor-page` escuro derruba a amarração (Task 1):** com `--cor-page: #0f0e0d;` do bloco `[data-tema="escuro"]` trocado para `#ffffff`, `test_cor_page_claro_e_escuro_amarrados_ao_input_css` falhou com `AssertionError: '#0f0e0d' != '#ffffff'`. Arquivo restaurado; suíte voltou a passar 18/18 (`core.tests.test_tema` + `core.tests.test_pwa`).
3. **`<style>` de `tema_css` ausente derruba `test_07_cor_runtime.sh` (Task 3):** com a linha `<style>{{ tema_css|safe }}</style>` de `base.html` temporariamente comentada, a suíte falhou já no passo 2 (linha de base) com `FALHOU: linha de base não contém --cor-brand: #1e40af — o banco de ensaio não está respondendo ao default do copier.yml` (ver "Issues Encountered" acima para o porquê de ser o passo 2, não o 5 previsto na prosa do plano). Arquivo restaurado a partir de backup (`diff` confirmou identidade); a suíte voltou a sair `0` de forma repetível.

## User Setup Required

None - nenhuma configuração de serviço externo necessária.

## Next Phase Readiness

- `cor_page_escuro` está disponível em todo template para o plano 07-05, que escreve esse valor no `<meta id="meta-theme-cor">` do script de tema (síncrono, antes do CSS existir, D-99) — o canal já foi aberto e testado; o consumo é responsabilidade do 07-05.
- `test_07_cor_runtime.sh` restaura o banco de ensaio para `COR_PRIMARIA=#1e40af` mesmo em caso de falha (`trap`) — o plano 07-05 encontra o banco na mesma linha de base que o 07-04 recebeu.
- Toda a `<verification>` do plano está verde: `ensaio_django.sh testar core apps.exemplo` (91/91), `test_07_cor_runtime.sh` (0, três execuções consecutivas), `test_copier_copy.sh` (matriz completa), `python3 -m unittest discover -s .template-tests -p 'test_*.py'` (32/32).
- `README.md.jinja` não é mais editado por nenhum plano restante da fase até o 07-08 (fechamento do inventário de suítes, que só acrescenta `test_07_cor_runtime.sh` à lista — não toca na seção "Customização de marca" escrita aqui).

---
*Phase: 07-herdar-o-design-system-do-pca*
*Completed: 2026-08-23*

## Self-Check: PASSED

All created/modified files verified present on disk (core/tema.py, core/tests/test_tema.py,
.template-tests/test_07_cor_runtime.sh, core/views.py, core/context_processors.py,
core/templates/base.html, README.md.jinja); all four task-commit hashes (eecc3bd, eb6c484,
77abd77, f75eff6) verified present in `git log`.
