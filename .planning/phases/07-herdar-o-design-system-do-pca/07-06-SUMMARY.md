---
phase: 07-herdar-o-design-system-do-pca
plan: 06
subsystem: design-system
tags: [django, echarts, tailwind-dark-mode, json_script, getComputedStyle]

# Dependency graph
requires:
  - phase: 07-04
    provides: "core.tema.familia_marca() — a mesma função que alimenta o <style> de base.html; este plano consome as chaves seq-600/seq-450/seq-300/brand-tint (e os equivalentes :escuro) para montar a rampa sequencial do donut"
  - phase: 07-05
    provides: "evento tema:alterado disparado pelo script síncrono de base.html — este plano é o primeiro consumidor real do evento fora do core"
provides:
  - "apps/…/exemplo/views.py — paleta_graficos no contexto do dashboard, derivado de core.tema.familia_marca(settings.COR_PRIMARIA), nos dois temas, zero hex literal em Python"
  - "dashboard.html — zero hex de cor: PALETA carregada por json_script, chrome do ECharts (surface/grid/ink/ink-2/surface-2/brand) lido de getComputedStyle a cada montarGraficos(), reconstrução completa (dispose+init) no evento tema:alterado"
  - "Os 3 níveis de elevação aplicados aos 6 consumidores do exemplo (4 KPIs + 2 cards de gráfico em dashboard.html) e aos 2 modais (_form_modal.html, _confirmar_exclusao_modal.html)"
  - "Gate executável 'zero hex em core/templates + apps/**/*.html' — critério 3 do ROADMAP fechado"
affects: ["07-07", "07-08"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Paleta CATEGÓRICA de gráfico é dado de servidor (json_script), nunca hex no cliente; CHROME de gráfico (eixo/grade/tooltip/borda) é sempre lido de getComputedStyle em runtime — o mesmo padrão já usado pela PCA em apps/pca/templates/pca/dashboard.html"
    - "montarGraficos() idempotente: lê chrome + paleta do tema ATUAL a cada chamada, faz dispose() das instâncias ECharts existentes antes de init() — só assim setOption não herda opções da chamada anterior. Chamada na carga (DOMContentLoaded) e de novo a cada evento de troca de tema, sem reload de página"
    - "Badges de estado de domínio (Tailwind nativo, não hex) recebem só variantes dark: para contraste — nunca migram para tokens st-*/dominio.css, que é vocabulário do sistema derivado (D-92)"

key-files:
  created: []
  modified:
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_form_modal.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_confirmar_exclusao_modal.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_tabela_resultado.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py"
    - ".template-tests/test_04_03_identity.py"

key-decisions:
  - "json_script:\"paleta-graficos\" foi acrescentado ao dashboard.html já dentro da Task 1 (TDD), não só na Task 2 como a prosa do plano descrevia — o comportamento 6/6 de Task 1 exige que o HTML renderizado contenha o <script id=\"paleta-graficos\"> para o teste passar (ver Deviations)"
  - "_filtros.html não recebeu nenhuma classe nova — já estava correto no nível Base (bg-surface border border-grid, sem sombra); confirmado, não alterado"

requirements-completed: [DS-05, DS-03]

# Metrics
duration: 70min
completed: 2026-08-23
---

# Phase 07 Plan 06: O dashboard do app exemplo para de cravar cor Summary

**A paleta semântica do donut chega do servidor por `json_script` (derivada de `core.tema.familia_marca`, mesma função que alimenta o `<style>` de `base.html`), o chrome dos gráficos ECharts é lido de `getComputedStyle` em runtime, a troca de tema reconstrói os dois gráficos vivos sem recarregar a página, os 3 níveis de elevação chegam aos consumidores do app exemplo, e a árvore inteira de templates (`core/templates` + `apps`) fecha em zero hex de cor.**

## Performance

- **Duration:** ~70 min
- **Started:** 2026-08-23 (leitura do contexto e dos arquivos-fonte)
- **Completed:** 2026-08-23
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- `apps/…/exemplo/views.py`: `dashboard_view` importa `core.tema.familia_marca` e monta `paleta_graficos["rampa_status"]` com `claro`/`escuro`, cada um com 4 hex (`seq-600`, `seq-450`, `seq-300`, `brand-tint`) — o topo (`claro[0]`) é literalmente `settings.COR_PRIMARIA`; comentário em pt-BR documenta por que é dado semântico (não estilo), a fonte única com `base.html` e por que a rampa é sequencial (CVD-safe para qualquer `COR_PRIMARIA`)
- `dashboard.html`: terceiro `json_script` (`"paleta-graficos"`) ao lado dos dois existentes; bloco `<script>` reestruturado com `lerVarCss()`, `temaAtual()` e `montarGraficos()` — as 18 ocorrências da tabela do plano (17 hex em 13 linhas + a interpolação `{{ cor_primaria }}`) foram todas substituídas; `montarGraficos()` chamada na carga e de novo em `document.addEventListener("tema:alterado", …)`, com `dispose()` antes de `init()` das duas instâncias
- Elevação aplicada: 4 cards de KPI + 2 cards de gráfico de `dashboard.html` sobem a Elevado (`shadow-sm dark:bg-surface-2 dark:shadow-none`); os painéis dos 2 modais sobem a Flutuante (`dark:bg-surface-3 dark:shadow-md`, `shadow-lg` já presente); `_filtros.html`/`_tabela_resultado.html` confirmados no nível Base, sem sombra acrescentada
- Badges de status de `_tabela_resultado.html` ganham variantes `dark:` (paleta nativa Tailwind, sem migrar para `st-*`/`dominio.css`) com comentário Django apontando o arquivo correto para um sistema real declarar tokens de estado
- `.template-tests/test_04_03_identity.py`: as 3 novas asserções (`json_script:"paleta-graficos"`, ausência de `cor_primaria`, ausência de hex) substituem a asserção do contrato antigo
- Gate final `grep -rnE '#[0-9a-fA-F]{6}' core/templates apps --include='*.html'` vazio — critério 3 do ROADMAP fechado; `core/views.py` confirmado em zero hex (herdado do plano 07-04)

## Task Commits

Each task was committed atomically:

1. **Task 1 RED — teste falho para `paleta_graficos`** - `bc56c74` (test)
2. **Task 1 GREEN — `dashboard_view` serve `paleta_graficos`** - `94dd473` (feat)
3. **Task 2 — `dashboard.html` sem hex, chrome em runtime, reconstrução no `tema:alterado`** - `17fcd19` (feat)
4. **Task 3 — elevação nos consumidores do exemplo + gate de hex** - `af85b81` (feat)

**Plan metadata:** commit pendente (docs: complete plan)

## Files Created/Modified

- `apps/…/exemplo/views.py` - `paleta_graficos` no `contexto`, derivado de `core.tema.familia_marca(settings.COR_PRIMARIA)`, zero hex literal
- `apps/…/exemplo/templates/exemplo/dashboard.html` - terceiro `json_script`; script reestruturado (`lerVarCss`/`temaAtual`/`montarGraficos`); 4 KPIs + 2 cards de gráfico em nível Elevado
- `apps/…/exemplo/templates/exemplo/_form_modal.html` - painel em nível Flutuante (`dark:bg-surface-3 dark:shadow-md`)
- `apps/…/exemplo/templates/exemplo/_confirmar_exclusao_modal.html` - painel em nível Flutuante
- `apps/…/exemplo/templates/exemplo/_tabela_resultado.html` - badges de status com variantes `dark:` + comentário sobre `dominio.css`
- `apps/…/exemplo/tests/test_dashboard.py` - 6 novos testes de comportamento (11 no total)
- `.template-tests/test_04_03_identity.py` - 3 novas asserções no lugar do contrato `const corBrand`

## Decisions Made

Ver `key-decisions` no frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - blocking issue] `json_script:"paleta-graficos"` acrescentado a `dashboard.html` já na Task 1, não só na Task 2**
- **Found during:** Task 1, ao rodar a suíte RED→GREEN
- **Issue:** O `<files>` da Task 1 lista só `views.py` e `tests/test_dashboard.py`; a prosa da Task 2 diz que é ela quem "acrescenta, junto dos dois `json_script` existentes, `{{ paleta_graficos|json_script:"paleta-graficos" }}`". Mas o `<behavior>` da Task 1 exige literalmente que "o HTML renderizado contenha `<script id="paleta-graficos" type="application/json">`" e que o `json.loads` funcione — e a `<acceptance_criteria>` exige que os 11 testes saiam com código 0 ao FINAL da Task 1. Sem tocar o template, o teste 6/6 (`test_paleta_graficos_chega_ao_html_por_json_script_valido`) ficaria vermelho até a Task 2, quebrando o gate de GREEN da própria Task 1.
- **Fix:** Task 1 acrescentou só a linha `{{ paleta_graficos|json_script:"paleta-graficos" }}` ao lado dos dois `json_script` existentes — nenhuma outra mudança no template. A Task 2 seguiu normalmente com a reestruturação completa do bloco `<script>` (a linha já estava lá, sem duplicação).
- **Files modified:** `apps/…/exemplo/templates/exemplo/dashboard.html`
- **Verification:** `bash .template-tests/ensaio_django.sh testar apps.exemplo.tests.test_dashboard` — 11/11 verde ao final da Task 1.
- **Committed in:** `94dd473` (Task 1)

---

**Total deviations:** 1 (ajuste de escopo entre Task 1 e Task 2, sem mudança de arquitetura — só a ordem de qual task escreve uma linha já prevista para as duas)
**Impact on plan:** Nenhum. A linha era necessária de qualquer forma; a única diferença é que chegou uma task mais cedo do que a prosa descrevia, para satisfazer o próprio gate GREEN que o plano exige.

## Issues Encountered

**Verificação de navegador (critério "sem recarregar a página"):** o ambiente de execução não tem um navegador com interface gráfica nem uma ferramenta de automação de navegador instalada (Playwright/Puppeteer/Selenium ausentes; instalar um pacote novo está fora do escopo de auto-fix da Regra 3). A verificação foi feita por evidência equivalente, não por clique real:
1. `node -c` no bloco `<script>` extraído do `dashboard.html` renderizado — sintaxe válida.
2. Todas as 6 variáveis lidas por `lerVarCss` (`--cor-brand`, `--cor-surface`, `--cor-surface-2`, `--cor-grid`, `--cor-ink`, `--cor-ink-2`) confirmadas presentes nos DOIS blocos de `core/static/src/input.css` (`:root` e `[data-tema="escuro"]`), então nenhuma chamada de `lerVarCss` pode devolver string vazia em nenhum dos dois temas.
3. `montarGraficos()` é chamada tanto na carga quanto no listener de troca de tema, sempre com `dispose()` antes de `init()` — logo, uma reconstrução idempotente e sem estado obsoleto está garantida no código, não só suposta.
4. O contrato `paleta_graficos["rampa_status"]["claro"|"escuro"]` foi confirmado por HTTP real (via `Client` do Django dentro do banco de ensaio) mudando de `#1e40af...` para `#0f766e...` e voltando, na mesma prova negativa da Task 1.

Isso não substitui uma inspeção visual humana. Fica registrado aqui como pendência de verificação manual (não bloqueante — toda a suíte automatizada está verde) para quem revisar este plano com acesso a um navegador.

## Provas Negativas Registradas

1. **`COR_PRIMARIA` trocada muda `paleta-graficos` sem rebuild (Task 1):** no `.env` da cópia de ensaio, `COR_PRIMARIA` trocada de `#1e40af` para `#0f766e` + `bash .template-tests/ensaio_django.sh compor up -d web` (nunca `restart`) — sem `--build` — mudou os 8 valores servidos em `paleta-graficos` (`claro`: `#1e40af,#6b81ca,#aab6e1,#edf0f9` → `#0f766e,#61a59f,#a4cbc8,#ecf4f3`; `escuro` também mudou). Restaurado para `#1e40af` em seguida; valor de volta ao baseline confirmado por nova requisição.
2. **Gate de hex sobre a árvore inteira (Task 3):** `grep -rnE '#[0-9a-fA-F]{6}' core/templates apps --include='*.html'` devolveu vazio (exit 1) numa única passada, sem nenhuma linha isentada — nenhum hex sobrou em nenhum template de `core` ou `apps`, incluindo `core/templates/base.html` (as 3 cores lá são `{{ }}`, não literais, herdadas do plano 07-04/07-05).

## User Setup Required

None — nenhuma configuração de serviço externo necessária.

## Next Phase Readiness

- Critérios 2 e 3 do ROADMAP (chrome de gráfico em runtime + zero hex em template) estão fechados; `apps.exemplo` sobe de 23 para 29 testes, todos verdes.
- O gate `grep -rnE '#[0-9a-fA-F]{6}' core/templates apps --include='*.html'` está verde e é o critério de aceite mais amplo da fase — qualquer plano restante (07-07, 07-08) que reintroduza um hex literal quebra este gate imediatamente.
- Toda a `<verification>` do plano está verde: `ensaio_django.sh testar core apps.exemplo` (112/112), `python3 -m unittest discover -s .template-tests -p 'test_*.py'` (32/32), `test_copier_copy.sh` (OK), gate de hex (vazio).
- Pendência registrada em "Issues Encountered": inspeção visual real da troca de tema no navegador (não disponível neste ambiente) fica para quem revisar com acesso a display gráfico — a lógica de reconstrução está provada por código e pelos testes automatizados, não por captura de tela.

---
*Phase: 07-herdar-o-design-system-do-pca*
*Completed: 2026-08-23*
