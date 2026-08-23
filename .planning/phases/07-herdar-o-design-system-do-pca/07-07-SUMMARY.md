---
phase: 07-herdar-o-design-system-do-pca
plan: 07
subsystem: design-system
tags: [tailwind, typography, django-templates, contract-testing]

# Dependency graph
requires:
  - phase: 07-02
    provides: "tailwind.config.js fontSize com as 6 chaves da régua (xs/sm/base/md/lg/xl, 11-20px) — este plano é o primeiro a fazer valer a régua nos templates"
  - phase: 07-05
  - phase: 07-06
    provides: "dashboard.html no estado pós-remoção de hex (07-06) — este plano toca as mesmas linhas de texto sem reintroduzir cor literal"
provides:
  - "Zero text-2xl (e acima) e zero text-[NNpx] em core/templates + apps/**/*.html — o teto de 20px é real"
  - "test_07_tokens.py::test_templates_so_usam_as_seis_chaves_da_regua_tipografica — gate executável instalado antes da migração, varre templates por classe text-* fora das 6 chaves"
  - "As ~83 ocorrências de text-base/text-sm/text-xs revisadas ocorrência a ocorrência com decisão registrada (14 promovidas, o resto mantido por julgamento explícito)"
affects: ["07-08"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Gate de régua tipográfica lê fontSize da FONTE (tailwind.config.js) via regex tolerante a chave entre aspas, nunca do CSS compilado — mesma convenção dos gates de cor de 07-02/07-06"
    - "Título de seção (h2) que ficava do mesmo tamanho do corpo depois do encolhimento sobe para text-lg; botão adota text-base por paridade com o vocabulário .btn (text-[13px]) do input.css; o resto do sistema (nav, badge, cabeçalho de tabela, paginação, corpo) absorve o encolhimento sem mudar de classe"

key-files:
  created: []
  modified:
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/item_listar.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_form_modal.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_confirmar_exclusao_modal.html"
    - "core/templates/core/shell.html"
    - ".template-tests/test_07_tokens.py"

key-decisions:
  - "Bug pré-existente (07-02) corrigido no regex que lê as chaves de fontSize: '^\\s*([a-zA-Z0-9]+):' nunca casava chave entre aspas (\"2xl\": [...]); sem a correção a prova negativa 'acrescentar 2xl faz o item 1 falhar' passaria em falso positivo silencioso — corrigido para '^\\s*\"?([a-zA-Z0-9]+)\"?:' nos dois testes que leem fontSize"
  - "Botão adota text-base (13px), não text-sm — paridade com o vocabulário .btn (text-[13px]) do input.css; aplicado a 6 sítios (Gerenciar itens, Novo item, Cancelar/Salvar item do form modal, Cancelar/Sim-excluir do modal de exclusão, 3 botões de tema do shell)"
  - "Corpo do diálogo de confirmação de exclusão promovido a text-base — é o conteúdo principal do modal (a pergunta), não uma legenda secundária"
  - "Nome do sistema no header mobile do shell (l.52) e a sigla na aside desktop (l.67) mantidos em text-base: font-bold já compensa o encolhimento e há paridade entre as duas apresentações da marca — não promovidos a text-md"
  - "_tabela_resultado.html mantém text-sm como tamanho-base da tabela (l.7): a maioria das células já é badge/legenda em text-xs (protegido por 'não promova' explícito do plano); promover quebraria a paridade de densidade com cabeçalho e paginação"
  - "Micro-rótulos uppercase dos campos do _form_modal.html (Título/Descrição/Categoria/Status/Valor/Prazo) mantidos em text-xs: são um padrão de design deliberado (uppercase + tracking-wider + text-muted), distinto do 'rótulo de campo' body-level do critério de <interfaces>"

requirements-completed: [DS-03]

# Metrics
duration: 45min
completed: 2026-08-23
---

# Phase 07 Plan 07: A régua tipográfica de 6 degraus passa a valer nos templates Summary

**As 6 ocorrências de `text-2xl` que furavam o teto de 20px somem, um gate executável (`test_07_tokens.py`) passa a travar qualquer classe de tamanho fora das 6 chaves da régua, e as ~83 ocorrências de `text-base`/`text-sm`/`text-xs` foram revisadas ocorrência a ocorrência — 14 promovidas por julgamento explícito (2 títulos de gráfico e 2 títulos de modal a `text-lg`, 6 botões e 1 corpo de diálogo a `text-base`), o resto mantido na régua que já era o alvo.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-23
- **Completed:** 2026-08-23
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- `dashboard.html` e `item_listar.html`: os 6 `text-2xl` (h1 de página + 4 números de KPI) viraram `text-xl` — o teto de 20px é real; `font-semibold`/`tracking-tight`/`font-mono` preservados para compensar a perda de 4px dos números de KPI
- `test_07_tokens.py`: novo teste `test_templates_so_usam_as_seis_chaves_da_regua_tipografica` varre `core/templates` e `apps` por classes `text-<sufixo>`, classifica cada sufixo (tamanho conhecido do Tailwind ou valor arbitrário `[...]`) e falha citando `arquivo:linha` se algo escapar das 6 chaves da régua; instalado **antes** da Task 3, nasceu verde porque a Task 1 já tinha eliminado o que furava o teto
- Duas provas negativas confirmadas e revertidas: acrescentar `text-2xl` a `dashboard.html` derruba o novo teste citando `dashboard.html:12`; acrescentar a chave `"2xl"` ao `fontSize` derruba o item 1 (chaves da régua) — e revelou um bug real no regex herdado de 07-02 (ver Deviations)
- Migração ocorrência a ocorrência das ~83 classes `text-base`/`text-sm`/`text-xs`: 14 sítios promovidos por critério explícito (título de seção que ficava do tamanho do corpo → `text-lg`; botão → `text-base` por paridade com `.btn`; corpo do diálogo de confirmação → `text-base`), o restante mantido — incluindo as decisões de **não** promover que exigiram julgamento (nome do sistema no header mobile, sigla da aside, tamanho-base da tabela de resultado, micro-rótulos dos campos do formulário)
- Distribuição final: `text-base` 16×, `text-lg` 4×, `text-sm` 11×, `text-xl` 8×, `text-xs` 44× — 83 ocorrências, zero fora da régua

## Task Commits

Each task was committed atomically:

1. **Task 1: Inventário e eliminação do que fura o teto de 20px** - `3817483` (fix)
2. **Task 2: Gate executável da régua — instalado ANTES da migração** - `f7906cf` (test)
3. **Task 3: Revisão ocorrência a ocorrência dos degraus que encolheram** - `4a4e863` (feat)

**Plan metadata:** commit pendente (docs: complete plan)

## Files Created/Modified

- `apps/…/exemplo/templates/exemplo/dashboard.html` - 6 `text-2xl`→`text-xl` (Task 1); botão "Gerenciar itens" e os 2 `h2` de título de gráfico revisados (Task 3)
- `apps/…/exemplo/templates/exemplo/item_listar.html` - `text-2xl`→`text-xl` no h1 (Task 1); botão "Novo item" revisado (Task 3)
- `apps/…/exemplo/templates/exemplo/_form_modal.html` - h2 do título e os 2 botões de rodapé revisados (Task 3)
- `apps/…/exemplo/templates/exemplo/_confirmar_exclusao_modal.html` - h2 do título, corpo da pergunta e os 2 botões revisados (Task 3)
- `core/templates/core/shell.html` - os 3 botões de tema revisados (Task 3)
- `.template-tests/test_07_tokens.py` - novo teste de gate da régua + correção do regex de leitura de `fontSize` (Rule 1)

## Inventário (Task 1 — comando de contagem, antes da eliminação do teto)

```
$ grep -rnoE '\btext-(xs|sm|base|md|lg|xl|2xl|3xl|4xl|5xl|6xl)\b' core/templates apps --include='*.html' | sed 's/.*://' | sort | uniq -c
     10 text-base
     21 text-sm
      6 text-2xl
      2 text-xl
     44 text-xs

$ grep -rnoE 'text-\[[0-9]+px\]' core/templates apps --include='*.html' | sort | uniq -c
(vazio)
```

83 ocorrências no total (10 base + 21 sm + 44 xs + 6 2xl + 2 xl), das quais 71 nos três
degraus que encolhem (base/sm/xs) — a contagem da pesquisa original (79) já tinha mudado
com os planos 07-03/07-05/07-06, como o plano previa.

## Inventário (Task 3 — distribuição final, depois da migração completa)

```
$ grep -rnoE '\btext-(xs|sm|base|md|lg|xl)\b' core/templates apps --include='*.html' | sed 's/.*://' | sort | uniq -c
     16 text-base
      4 text-lg
     11 text-sm
      8 text-xl
     44 text-xs
```

83 ocorrências, todas dentro das 6 chaves da régua. `text-md` não foi necessário em
nenhum sítio (avaliado para `shell.html:52`, decisão foi manter `text-base`).

## Decisões por sítio (arquivo:linha classe-antes → classe-depois (motivo))

### Task 1 — eliminação do teto de 20px

- `dashboard.html:12  text-2xl → text-xl  (h1 de título de página — teto da régua)`
- `dashboard.html:39  text-2xl → text-xl  (número de KPI "Total de Itens"; font-semibold+font-mono compensam a perda de 4px)`
- `dashboard.html:46  text-2xl → text-xl  (número de KPI "Valor Acumulado"; idem)`
- `dashboard.html:53  text-2xl → text-xl  (número de KPI "Taxa de Conclusão"; idem)`
- `dashboard.html:60  text-2xl → text-xl  (número de KPI "Valor Médio"; idem)`
- `item_listar.html:12  text-2xl → text-xl  (h1 de título de página — teto da régua)`

### Task 3 — degraus que encolheram (promovidos)

- `dashboard.html:17  text-sm → text-base  (botão "Gerenciar itens" — vocabulário .btn prefere text-base)`
- `dashboard.html:71  text-base → text-lg  (h2 "Valor por Categoria" — ficava do mesmo tamanho do corpo em 13px)`
- `dashboard.html:82  text-base → text-lg  (h2 "Distribuição por Status" — idem)`
- `item_listar.html:20  text-sm → text-base  (botão "Novo item" — vocabulário .btn)`
- `_form_modal.html:15  text-base → text-lg  (h2 do título do modal — título de seção)`
- `_form_modal.html:131  text-sm → text-base  (botão "Cancelar" — vocabulário .btn)`
- `_form_modal.html:135  text-sm → text-base  (botão "Salvar item" — vocabulário .btn)`
- `_confirmar_exclusao_modal.html:15  text-base → text-lg  (h2 do título do modal — título de seção)`
- `_confirmar_exclusao_modal.html:33  text-sm → text-base  (corpo da pergunta de confirmação — conteúdo principal do diálogo, não legenda)`
- `_confirmar_exclusao_modal.html:51  text-sm → text-base  (botão "Cancelar" — vocabulário .btn)`
- `_confirmar_exclusao_modal.html:56  text-sm → text-base  (botão "Sim, excluir item" — vocabulário .btn)`
- `shell.html:100  text-sm → text-base  (botão de tema "Automático" — vocabulário .btn)`
- `shell.html:104  text-sm → text-base  (botão de tema "Claro" — idem)`
- `shell.html:108  text-sm → text-base  (botão de tema "Escuro" — idem)`

### Task 3 — decisões de não mudar que exigiram julgamento

- `shell.html:52  text-base (mantido)  (nome do sistema no header mobile — plano pediu avaliação explícita; font-bold já compensa o encolhimento e há paridade com a sigla da aside desktop l.67, também text-base bold; não promovido a text-md)`
- `shell.html:67  text-base (mantido)  (sigla do sistema na aside desktop — mesma família de decisão do item acima, não é <h1>/<h2>, é rótulo de identidade)`
- `_tabela_resultado.html:7  text-sm (mantido)  (tamanho-base de toda a tabela — a maioria das células já é badge/legenda em text-xs; promover quebraria a paridade de densidade com cabeçalho e paginação, ambos protegidos por "não promova" explícito do plano)`
- `_tabela_resultado.html:250  text-base (mantido)  (h3 do estado vazio "Nenhum item encontrado" — mensagem efêmera dentro da tabela, não título de seção persistente; contraste com a legenda em text-xs abaixo já é suficiente)`
- `_form_modal.html:48,61,75,87,102,114  text-xs (mantidos, 6 sítios)  (micro-rótulos uppercase dos campos — padrão de design deliberado: uppercase + tracking-wider + text-muted, distinto do "rótulo de campo" body-level do critério de <interfaces>)`

### Task 3 — decisões de não mudar mecânicas (badge/cabeçalho/paginação/legenda/corpo, conforme critério explícito de `<interfaces>`)

- `base.html:96  text-base (mantido)  (corpo global do sistema — é a densidade-alvo, não legado a corrigir)`
- `shell.html:69  text-sm (mantido)  (nome completo abaixo da sigla — papel de legenda)`
- `shell.html:113  text-sm (mantido)  (iniciais do avatar do usuário — elemento tipo badge)`
- `shell.html:116  text-sm (mantido)  (bloco e-mail + Sair no rodapé — metadado compacto)`
- `shell.html:148  text-xl (mantido)  (h1 já estava no teto — é o padrão de referência que dashboard/item_listar passam a seguir)`
- `shell.html:153  text-base (mantido)  (corpo da página inicial padrão)`
- `login.html:13  text-xl (mantido)  (h1 já no teto — critério de título)`
- `_item_nav.html:5  text-base (mantido)  (item de navegação — densidade pretendida, explicitamente protegido pelo plano)`
- `_breadcrumbs.html:37,41  text-xs (mantidos, 2 sítios)  (trilha de navegação — metadado)`
- `dashboard.html:13  text-sm (mantido)  (subtítulo descritivo abaixo do h1 — papel de legenda)`
- `dashboard.html:38,40,45,47,52,54,59,61  text-xs (mantidos, 8 sítios)  (rótulo/legenda dos cards de KPI)`
- `dashboard.html:72,83  text-xs (mantidos, 2 sítios)  (legenda abaixo dos títulos de gráfico)`
- `item_listar.html:13  text-sm (mantido)  (subtítulo descritivo — mesmo papel de dashboard.html:13)`
- `_tabela_resultado.html:9  text-xs (mantido)  (cabeçalho de tabela)`
- `_tabela_resultado.html:113  text-xs (mantido)  (descrição truncada da linha — legenda)`
- `_tabela_resultado.html:119  text-xs (mantido)  (badge de categoria)`
- `_tabela_resultado.html:138,142,146,150  text-xs (mantidos, 4 sítios)  (badges de status)`
- `_tabela_resultado.html:162  text-xs (mantido)  (coluna de prazo — dado secundário)`
- `_tabela_resultado.html:177,184  text-xs (mantidos, 2 sítios)  (botões Editar/Excluir dentro da linha densa da tabela)`
- `_tabela_resultado.html:196,208,215,223,234  text-xs (mantidos, 5 sítios)  (barra de paginação)`
- `_tabela_resultado.html:251  text-xs (mantido)  (legenda do estado vazio)`
- `_tabela_resultado.html:260  text-xs (mantido)  (link "Limpar filtros" do estado vazio)`
- `_filtros.html:29,39,53  text-sm (mantidos, 3 sítios)  (texto dos controles de filtro — busca e selects)`
- `_filtros.html:70  text-xs (mantido)  (botão "Limpar" — explicitamente protegido pelo plano)`
- `_form_modal.html:39  text-xs (mantido)  (erro geral do formulário — legenda de alerta)`
- `_form_modal.html:53,66,80,92,107,119  text-xs (mantidos, 6 sítios)  (mensagens de erro por campo — legenda)`
- `_confirmar_exclusao_modal.html:36  text-xs (mantido)  ("Esta ação não pode ser desfeita." — legenda)`

## Decisions Made

Ver `key-decisions` no frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Regex de leitura de `fontSize` (herdado de 07-02) não casava chave entre aspas**
- **Found during:** Task 2, ao rodar a prova negativa "acrescentar a chave `2xl` ao `fontSize` faz o item 1 falhar"
- **Issue:** `font_size_keys = set(re.findall(r"^\s*([a-zA-Z0-9]+):", font_size_block, re.MULTILINE))` (em `test_fontsize_e_borderradius_tem_as_chaves_do_contrato`, escrito pelo plano 07-02) e o mesmo padrão que eu tinha copiado para o novo teste nunca casam uma chave declarada entre aspas — obrigatório em JS para chaves que começam com dígito, como `"2xl": [...]`. Ao acrescentar `"2xl": ["24px", ...]` ao bloco `fontSize` para a prova negativa, os dois testes continuaram verdes: a chave nova era silenciosamente ignorada pela extração, não pela regra de negócio. Isso teria feito a prova negativa exigida pelo `<acceptance_criteria>` da Task 2 passar em falso positivo — o gate pareceria funcionar sem de fato barrar o furo do teto por essa via.
- **Fix:** trocado o padrão para `r'^\s*"?([a-zA-Z0-9]+)"?:'` nos dois lugares (`test_fontsize_e_borderradius_tem_as_chaves_do_contrato`, linha ~125, e o novo `test_templates_so_usam_as_seis_chaves_da_regua_tipografica`). Confirmado que a chave `2xl` entre aspas agora é capturada e os dois testes falham citando o item extra.
- **Files modified:** `.template-tests/test_07_tokens.py`
- **Verification:** com `"2xl": [...]` acrescentado ao `tailwind.config.js`, `python3 -m unittest discover -s .template-tests -p 'test_07_tokens*.py'` falhou em 2 testes citando `'2xl'` como item extra; revertido em seguida, suíte volta a 9/9 verde.
- **Committed in:** `f7906cf` (Task 2)

---

**Total deviations:** 1 (correção de bug pré-existente descoberto pela própria prova negativa que o plano exigiu — sem mudança de arquitetura)
**Impact on plan:** Nenhum negativo. O bug já existia desde 07-02 e não tinha sido pego porque nenhum plano anterior tinha tentado acrescentar uma chave numérica ao `fontSize`; a prova negativa desta task é o que revelou.

## Issues Encountered

Nenhum bloqueio. As duas provas negativas exigidas pela Task 2 (`<acceptance_criteria>`)
foram executadas, confirmadas e revertidas sem deixar diff (`git diff --stat` vazio nos
dois arquivos temporariamente alterados: `dashboard.html` e `tailwind.config.js`).

## Provas Negativas Registradas

1. **`text-2xl` acrescentado a `dashboard.html:12` derruba o gate (Task 2):** `sed -i '12s/text-xl/text-2xl/'` seguido de `python3 -m unittest discover -s .template-tests -p 'test_07_tokens*.py'` — 1 falha, mensagem cita exatamente `apps/…/dashboard.html:12 text-2xl`. Revertido com `cp` do backup; `git diff --stat` confirma zero diff.
2. **Chave `"2xl"` acrescentada ao `fontSize` derruba o item 1 do gate (Task 2):** ver "Deviations" acima — a prova revelou e corrigiu um bug real no regex, não só confirmou o comportamento esperado. Revertido com `cp` do backup; `git diff --stat` confirma zero diff.

## User Setup Required

None — nenhuma configuração de serviço externo necessária.

## Next Phase Readiness

- Critério 1 do ROADMAP ("conferível lado a lado", teto de 20px real, régua tipográfica
  valendo nos templates) está fechado: zero `text-2xl`+ e zero `text-[NNpx]` na árvore,
  gate executável instalado e comprovado por 2 provas negativas.
- `bash .template-tests/ensaio_django.sh testar core apps.exemplo` — 112/112 verde.
- `python3 -m unittest discover -s .template-tests -p 'test_*.py'` — 33/33 verde (9 em
  `test_07_tokens.py`, incluindo o novo gate).
- `docker build --target assets .` — sucesso, CSS gerado com 19225 bytes (piso de 5000
  bytes com folga).
- O plano 07-08 (fechamento da fase, inspeção humana das 4 telas em cópia real,
  `ui_safety_gate: true`) é o próximo — esta task deixa o T-07-21 do threat model (piso de
  11px legível) pronto para essa inspeção visual: nenhum corpo de texto ficou em 11px,
  só metadado/legenda/badge, conforme o critério de `<interfaces>`.

## Self-Check: PASSED

- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html` — FOUND
- `.template-tests/test_07_tokens.py` — FOUND
- `.planning/phases/07-herdar-o-design-system-do-pca/07-07-SUMMARY.md` — FOUND
- Commit `3817483` (Task 1) — FOUND
- Commit `f7906cf` (Task 2) — FOUND
- Commit `4a4e863` (Task 3) — FOUND
- Commit `fc553ce` (SUMMARY) — FOUND
