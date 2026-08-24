---
phase: 07-herdar-o-design-system-do-pca
plan: 12
subsystem: graficos
tags: [echarts, wcag, contraste, css-variables, xss, tema-escuro, dashboard]

# Dependency graph
requires:
  - phase: 07-09
    provides: "core/tests/contraste.py — helper WCAG único do repositório (contraste, tokens_do_input_css)"
  - phase: 07-06
    provides: "chrome do gráfico lido de getComputedStyle em runtime + repintura no evento tema:alterado"
provides:
  - "chrome-do-grafico-lendo-o-token-certo — splitLine lê --cor-grid, borda do donut lê corCard"
  - "mapeamento-de-elevacao-do-script-amarrado-por-teste-ao-HTML-dos-cards"
  - "tooltip-do-echarts-escapado — esc() aplicada a toda interpolação dos dois formatters"
  - "json-parse-do-dashboard-degradando-em-vez-de-derrubar"
affects:
  - "07-13 (G-03: paleta de DADO do donut) — o cromo já está fora do caminho; a 4ª fatia é escopo de lá"
  - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Grade e borda de gráfico leem o token do PAPEL (linha, fundo do card), nunca um nível de elevação assumido"
    - "Cor de fundo lida por script é mapeada por tema num único `const`, espelhando as classes que o card declara"
    - "Formatter do ECharts é HTML: TODA interpolação passa por escape, inclusive as numéricas — regra sem exceção"
    - "Gate de fonte resolve o identificador até o token CSS antes de medir, e falha alto quando não casa nada"

key-files:
  created:
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_grafico_chrome.py"
  modified:
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html"

key-decisions:
  - "Piso de cromo em 1,25:1 (não 3:1 nem 4,5:1): grade e separação são cromo, não dado nem texto — e um gate em `> 1,00` passaria com 1,001:1"
  - "`esc()` aplicada a TODA interpolação dos formatters, inclusive numéricas — regra com exceções obriga o derivado a reclassificar campo a campo, e é aí que o escape some"
  - "`corSurface2` preservada: deixou de alimentar o splitLine mas passou a alimentar `corCard` — não é ligação órfã"
  - "Zero hex literal também na prosa do teste: valores saem sempre de tokens_do_input_css() e reaparecem nas mensagens de falha"

patterns-established:
  - "Prova de acessibilidade sem navegador em duas metades encadeadas: resolução do identificador→token no fonte, depois contraste computado contra o fundo real"
  - "Gate de fonte com RECADO_DE_FORMA: quando o regex não casa, a falha diz explicitamente para não relaxar o regex"
  - "Mensagem de falha nunca despeja o haystack: assertIsNotNone(regex.search(...)) e assertTrue(x in texto) no lugar de assertRegex/assertIn sobre arquivo inteiro"

requirements-completed: [DS-05, DS-03]

# Metrics
duration: 22min
completed: 2026-08-24
---

# Phase 07 Plano 12: Chrome dos gráficos lendo o token do papel Summary

**A grade do eixo Y deixa de ser matematicamente idêntica ao fundo do card no tema escuro (1,00:1 → 1,38:1) porque passou a ler `--cor-grid` em vez de `--cor-surface-2`, a separação entre as fatias do donut passa a acompanhar o fundo real do card por tema, e os dois formatters do ECharts deixam de concatenar HTML sem escapar.**

## Performance

- **Duração:** ~22 min
- **Iniciado:** 2026-08-24T04:04:00Z
- **Concluído:** 2026-08-24T04:26:00Z
- **Tarefas:** 3
- **Arquivos modificados:** 2 (1 criado, 1 modificado)

## Accomplishments

- **G-04 fechado com contraste medido, não inspecionado.** O `splitLine` lia `--cor-surface-2` enquanto o card **é** `dark:bg-surface-2`: a grade desenhava o mesmo tom sobre o mesmo tom. Agora lê `--cor-grid`, o token de LINHA, e o gate mede a razão contra o fundo real do card por tema.
- **O mapeamento de elevação virou explícito e amarrado ao HTML.** `const corCard = temaAtual() === "escuro" ? corSurface2 : corSurface;` espelha as classes que os dois cards declaram, e o teste falha se alguém mudar a elevação do card sem mudar o script (T-07-37).
- **WR-13 mitigado no artefato de referência.** O dashboard que todo derivado copia deixou de ensinar concatenação de HTML sem escape.
- **IN-04 mitigado.** Um `json_script` vazio não derruba mais os dois gráficos.

## Task Commits

1. **Task 1: gate de contraste do cromo (TDD RED)** — `4734c3d` (test)
2. **Task 2: grade lê o token de linha, donut lê o fundo real** — `0ac962b` (fix)
3. **Task 3: formatter escapado + `JSON.parse` com fallback** — `3f2e2d8` (fix)
4. **Rule 1: hex literal na docstring do gate (DS-05)** — `e888a6a` (fix)

## Files Created/Modified

- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_grafico_chrome.py` (criado) — 11 testes em 5 classes: resolução identificador→token no fonte, contraste computado do cromo por tema, mapeamento de elevação amarrado ao HTML, escape dos formatters, fallback de `JSON.parse`
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html` (modificado) — `corCard`, `splitLine` lendo `corGrid`, `borderColor` lendo `corCard`, função `esc()` e as duas interpolações escapadas, `|| "{}"` no terceiro `JSON.parse` e leitura da rampa degradando para lista vazia

## O gap em número: antes e depois, por tema

Medidos com `core/tests/contraste.py` sobre os valores lidos de `input.css`, contra o fundo **real** do card (`--cor-surface` no claro, `--cor-surface-2` no escuro, que é o que as classes `bg-surface … dark:bg-surface-2` declaram):

| Elemento | Tema | Lia antes | Contraste antes | Lê agora | Contraste agora |
|---|---|---|---|---|---|
| Grade do eixo Y (`splitLine`) | claro | `--cor-surface-2` | **1,09:1** | `--cor-grid` | **1,29:1** |
| Grade do eixo Y (`splitLine`) | escuro | `--cor-surface-2` | **1,00:1** — o mesmo tom do card | `--cor-grid` | **1,38:1** |
| Separação das fatias (donut) | claro | `--cor-surface` | 1,00:1 (coincidia com o card, invisível **por acaso** — que é o comportamento certo aqui) | `corCard` → `--cor-surface` | 1,00:1, agora **por construção** |
| Separação das fatias (donut) | escuro | `--cor-surface` | 1,12:1 mais **escuro** que o card — linha que não existe no claro | `corCard` → `--cor-surface-2` | 1,00:1, recorte do próprio card |

O caso do donut merece a nota: ali o alvo **não** é contraste alto, é coincidir com o fundo — a borda de 2px é um recorte que separa fatias adjacentes, não uma linha desenhada. No claro ela já coincidia; no escuro ela era uma linha escura espúria. Depois, coincide nos dois temas porque lê o card, não um nível fixo.

### A saída vermelha registrada (Task 1, antes de qualquer edição)

`Ran 11 tests` → `FAILED (failures=9)`. As duas que passavam eram os resolvedores de sítio (`splitLine` e `itemStyle.borderColor` existiam e eram únicos). As nove falhas:

```
FAIL: test_grade_do_eixo_contrasta_com_o_fundo_real_do_card (tema='claro')
  1.0905241547147786 not greater than or equal to 1.25 : [claro] grade `--cor-surface-2`
  sobre card `--cor-surface`: 1.09:1, abaixo do piso de cromo 1.25:1
FAIL: test_grade_do_eixo_contrasta_com_o_fundo_real_do_card (tema='escuro')
  1.0 not greater than or equal to 1.25 : [escuro] grade `--cor-surface-2` sobre card
  `--cor-surface-2`: 1.00:1, abaixo do piso de cromo 1.25:1
FAIL: test_grade_do_eixo_nao_e_o_mesmo_tom_do_card (tema='escuro')
  1.0 not greater than 1.0 : [escuro] a grade do eixo lê `--cor-surface-2` (#22211d) e o
  card é `--cor-surface-2` (#22211d): contraste 1.00:1 — mesmo tom, grade invisível (G-04)
FAIL: test_corcard_mapeia_a_elevacao_do_card_por_tema         (corCard não existia)
FAIL: test_borda_do_donut_usa_a_cor_do_card_mapeada_por_tema  ('corSurface' != 'corCard')
FAIL: test_funcao_de_escape_existe_no_script                  (esc não declarada)
FAIL: test_formatters_escapam_todo_nome_vindo_de_dado (${p.name})
FAIL: test_formatters_escapam_todo_nome_vindo_de_dado (${params.name})
FAIL: test_todo_json_parse_tem_fallback_para_conteudo_vazio (argumento='elPaletaData.textContent')
```

Note que os hex aparecem na **mensagem de falha**, medidos do arquivo — não no código do teste (ver Desvio 2).

### A prova de que o gate falha alto quando a forma do script muda

Exigida pelo critério de aceite da Task 1. Renomeei temporariamente a ligação `const corSurface2 = lerVarCss("--cor-surface-2");` para `corSuperficieDois`, mantendo o uso `corSurface2` no `splitLine`, e rodei só `ResolucaoDoChromeTest`:

```
FAIL: test_o_resolvedor_encontra_o_sitio_da_grade_do_eixo
AssertionError: 'corSurface2' not found in {'corBrand': '--cor-brand', 'corSurface':
'--cor-surface', 'corGrid': '--cor-grid', 'corInk': '--cor-ink', 'corInk2': '--cor-ink-2',
'corSuperficieDois': '--cor-surface-2'} : `splitLine` usa `corSurface2`, que não é nenhuma
ligação lerVarCss conhecida (['corBrand', 'corGrid', 'corInk', 'corInk2',
'corSuperficieDois', 'corSurface']) — a forma do script de dashboard.html mudou; o
resolvedor deste teste precisa acompanhar. NÃO relaxe o regex para que ele volte a passar
sem casar nada — um gate de fonte que não acha o sítio que deveria medir passa verde sobre
um defeito (foi assim que o G-04 atravessou a fase).
```

O template foi restaurado byte a byte depois da prova (`git diff` vazio antes da Task 2).

## Verificação

| Comando | Resultado |
|---|---|
| `ensaio_django.sh testar apps.exemplo.tests.test_grafico_chrome` | **OK** — 11/11 |
| `ensaio_django.sh testar apps.exemplo` | **OK** — 44/44, exit 0 |
| `ensaio_django.sh testar core apps.exemplo` | **OK** — 164/164, exit 0 |
| `python3 -m unittest discover -s .template-tests -p 'test_*.py'` | **OK** — 39/39, exit 0 |
| `node --check` no último bloco `<script>` extraído | **exit 0**, sintaxe válida (mesmo procedimento do 07-06) |
| `grep -rn -E "#[0-9a-fA-F]{3,8}\b" core/templates/ apps/` | **zero acertos** (DS-05 intacto) |
| `grep -c "corCard" dashboard.html` | 4 (≥ 3 exigidos) |
| `grep -c "color: corSurface2" dashboard.html` | 0 |
| `grep -c "borderColor: corSurface," dashboard.html` | 0 |
| `grep -c 'esc(' dashboard.html` | 4 (≥ 3 exigidos) |
| `grep -c 'JSON.parse'` vs `grep -c 'JSON\.parse(.*||'` | 3 e 3 — todo `JSON.parse` tem fallback |
| `grep -c "lerVarCss"` / `grep -c "contraste"` no teste | 5 / 7 |

### A releitura na troca de tema, conferida

`corCard` foi declarada **dentro** de `montarGraficos()`, junto das seis ligações `lerVarCss` — não no escopo do `DOMContentLoaded`. Como `montarGraficos()` é chamada na carga **e** de novo no `document.addEventListener("tema:alterado", …)` (com `dispose()` antes de `init()`), o ternário `temaAtual() === "escuro" ? …` é reavaliado a cada troca, sem recarregar a página. Se `corCard` tivesse sido posta fora da função, o conserto valeria só para o tema em que a página carregou — que é a metade silenciosa deste tipo de defeito. `montarGraficos()` continua sendo a única fonte de cor dos dois gráficos.

## Decisions Made

1. **Piso de cromo em 1,25:1, e a justificativa está na docstring do módulo.** Grade e separação são cromo: não carregam dado, delimitam. O piso de 3:1 pertence ao objeto gráfico portador de informação (escopo do 07-13) e o de 4,5:1 a texto. O piso que de fato fecha o gap é `> 1,00`, mas um gate assim passaria com 1,001:1 — igualmente invisível. 1,25:1 reprova `--cor-surface-2` no claro (1,09:1), que é a regressão exata que se quer barrar, e é folgado para os valores reais (1,29 e 1,38). O número tem dono e motivo escritos, para que a primeira falha futura não seja "resolvida" baixando-o.

2. **`esc()` em TODA interpolação dos formatters, inclusive `params.value`, `params.percent` e os `valorFormatado` de `toLocaleString`.** A alternativa — escapar só o que "vem de dado" — obriga quem adapta o dashboard para o domínio real a reclassificar cada campo, e é nessa reclassificação que o escape desaparece. Escapar um número não custa nada; a regra sem exceção é copiável sem julgamento. Registrado em comentário no próprio arquivo.

3. **`corSurface2` NÃO foi removida.** Depois da troca ela deixou de alimentar o `splitLine`, mas passou a alimentar `corCard`. Confirmado por grep antes de qualquer remoção: 2 ocorrências, ambas em uso.

4. **Nenhuma mudança na paleta de DADO nem em `views.py`.** A 4ª fatia do donut usando `brand-tint` (G-03) é escopo do 07-13, que roda depois. Este plano tocou só cromo: grade, separação e tooltip.

5. **Fallback `"{}"` e não `"[]"` para a paleta**, porque `paleta_graficos` é objeto; e o consumo virou `(PALETA.rampa_status || {})[temaAtual()] || []`, porque um objeto vazio faria `PALETA.rampa_status[temaAtual()]` lançar `TypeError` — trocar `SyntaxError` por `TypeError` não teria consertado nada. Gráfico sem cor customizada é degradação aceitável; dois gráficos ausentes não.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Usabilidade do gate] Mensagens de falha despejavam o template inteiro**

- **Encontrado durante:** Task 1, ao ler a saída da execução RED
- **Problema:** `assertRegex(self.texto, …)`, `assertIn(x, self.texto)` e `assertNotIn(x, self.texto)` imprimem o *haystack* completo na falha. Como o haystack aqui é `dashboard.html` inteiro (~12 KB), cada uma das três falhas de escape produzia um bloco de 12 KB de HTML escapado. Um gate cuja mensagem precisa ser rolada por 12 KB é um gate que ninguém lê — e um gate que ninguém lê é o mecanismo pelo qual um defeito medido volta a passar despercebido, que é exatamente a classe de problema que este plano fecha.
- **Correção:** trocado por `assertIsNotNone(REGEX.search(self.texto), msg)` e `assertTrue(x in self.texto, msg)`, que imprimem só a mensagem explicativa. O comportamento assertado é idêntico; só a diagnosticabilidade mudou. Comentário no arquivo explica o porquê, para que ninguém "simplifique" de volta.
- **Arquivos:** `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_grafico_chrome.py`
- **Verificação:** a segunda execução RED produziu mensagens de uma linha; o número de falhas não mudou.
- **Commit:** `4734c3d` (dentro do commit da Task 1)

**2. [Rule 1 - Bug introduzido pela própria Task 1] Hex literal na docstring quebrava o baseline de DS-05**

- **Encontrado durante:** verificação global, ao rodar `grep -rn -E "#[0-9a-fA-F]{3,8}\b" core/templates/ apps/`
- **Problema:** a docstring do teste explicava o G-04 citando `#22211d` duas vezes. O baseline da fase — conferido em `git grep` no commit anterior ao plano — é **zero** acerto de `#RRGGBB` em `core/templates/` e `apps/`, e é um dos critérios de verificação deste próprio plano. Minha Task 1 introduziu o primeiro. Além do gate, é a mesma classe de erro que `core/tests/contraste.py` existe para impedir: um hex copiado na prosa é uma cópia da fonte que envelhece calada.
- **Correção:** prosa reescrita por nome de token (`--cor-surface-2` sobre `--cor-surface-2`, "o MESMO tom"). Os valores continuam saindo de `tokens_do_input_css()` e reaparecem nas mensagens de falha, onde são medidos e não citados. Nota na docstring registra a regra.
- **Arquivos:** `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_grafico_chrome.py`
- **Verificação:** `grep` volta a zero acertos; `test_grafico_chrome` segue 11/11.
- **Commit:** `e888a6a`

---

**Total de desvios:** 2 auto-corrigidos (1 × Rule 2, 1 × Rule 1)
**Impacto no plano:** nenhum alargamento de escopo. O primeiro é diagnosticabilidade do gate que o próprio plano encomendou; o segundo é um defeito que eu mesmo introduzi e que o critério de verificação do plano pegou — funcionou como projetado.

## Issues Encountered

**O critério de aceite da Task 2 pedia exit 0 num comando que só podia fechar na Task 3.** O `verify` da Task 2 é `testar test_grafico_chrome test_dashboard`, mas o gate criado na Task 1 cobre as três tarefas — inclusive `esc()` e `JSON.parse`, que são escopo da Task 3. Ao fim da Task 2 restavam 4 falhas, **todas** e exclusivamente de `SegurancaDoFormatterTest` e `RobustezDoJsonParseTest`. Conferi uma a uma antes de commitar que nenhuma pertencia ao cromo, e a suíte fechou em verde ao fim da Task 3. Não é desvio: é consequência de um gate único escrito na primeira tarefa, que é o formato que o próprio plano pediu.

**Custo de execução do ensaio.** Toda edição no working tree invalida a impressão digital e o `testar` seguinte recria o banco de ensaio. As seis execuções (RED, prova de forma, pós-Task 2, pós-Task 3, `core apps.exemplo`, reconfirmação) couberam no orçamento de 600 s cada, sem precisar do fallback em background.

## User Setup Required

Nenhum — nenhuma configuração de serviço externo, nenhum pacote novo. O ECharts já está no projeto.

## Known Stubs

Nenhum. Não há valor de placeholder, dado mockado nem componente sem fonte de dados neste plano.

## Threat Flags

Nenhuma superfície nova. As mitigações do registro STRIDE do plano foram aplicadas:

| Threat ID | Disposição | Como ficou |
|---|---|---|
| T-07-34 (XSS via `formatter`) | mitigado | `esc()` declarada e aplicada a toda interpolação; gate exige a função **e** as duas chamadas |
| T-07-35 (DoS por `json_script` vazio) | mitigado | `\|\| "{}"` no `JSON.parse` + leitura da rampa degradando para `[]`; gate exige fallback em todo `JSON.parse` |
| T-07-36 (grade invisível no escuro) | mitigado | `splitLine` lê `--cor-grid`; gate de contraste ≥ 1,25:1 nos dois temas |
| T-07-37 (elevação do card mudar sem o script) | mitigado | `test_cards_de_grafico_declaram_a_elevacao_que_o_script_assume` amarra `CARD_POR_TEMA` às classes dos dois cards no HTML |

## Next Phase Readiness

**Pronto para o 07-13 (G-03).** O cromo saiu do caminho: `views.py`, `core/tema.py`, `input.css`, `tailwind.config.js` e a `rampa_status` estão intocados por este plano, exatamente como o 07-13 precisa. O `test_grafico_chrome.py` mede apenas cromo e não colide com um gate de contraste de **dado** (piso 3:1) — os dois pisos convivem porque medem categorias diferentes, e a docstring deste módulo diz isso explicitamente para que ninguém tente unificá-los.

Restam da lista de gaps: G-03 (07-13) e G-05 (07-14).

---
*Fase: 07-herdar-o-design-system-do-pca*
*Concluído: 2026-08-24*

## Self-Check: PASSED

Conferido em 2026-08-24: os 2 arquivos de código citados existem no disco, o SUMMARY existe, e os 4 commits (`4734c3d`, `0ac962b`, `3f2e2d8`, `e888a6a`) estão no histórico.
