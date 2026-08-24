---
phase: 07-herdar-o-design-system-do-pca
verified: 2026-08-23T23:49:20Z
status: gaps_found
score: 8/8 must-haves verificados
overrides_applied: 0
re_verification: null
gaps_source: 07-REVIEW.md (revisão de código posterior a esta verificação; os 4 itens foram reconferidos pelo orquestrador)
human_verification:
  - test: "Decidir se a Fase 7 deve permanecer marcada como `mode: mvp` no ROADMAP.md, ou se a marca deve ser removida/corrigida."
    expected: "Ou o goal da fase é reescrito no formato User Story (`As a …, I want to …, so that ….`), ou a linha `**Mode:** mvp` sai da seção da Phase 7."
    why_human: "A fase está marcada `mode: mvp`, mas o goal não é uma User Story (`gsd-sdk query user-story.validate` devolve `valid: false`, com os 3 erros de slot). O protocolo de verificação sob MVP mode manda recusar a verificação e pedir `/gsd mvp-phase 07`. Recusar aqui seria destrutivo: a fase tem 8 success criteria explícitos e testáveis, que são o contrato real e que foram todos verificados de forma independente. É uma inconsistência de metadado de planejamento, não de código — e só o operador decide qual dos dois lados corrigir."
  - test: "Decidir se o item \"Início\" do `_nav.html` do núcleo é aceitável para o DividaAtiva na migração v0.1.0 → v0.2.0."
    expected: "Ou o DividaAtiva aceita exibir o item \"Início\" (rota `core:shell`, a raiz `\"\"` que todo sistema gerado tem), ou o operador registra que ele precisará editar `_nav.html` — reabrindo, só para esse item, o conflito de upstream que a fase eliminou para todo o resto."
    why_human: "O roteiro do README (linha 488) instrui o derivado a fazer `git checkout --theirs` no `_nav.html` e recriar seus itens em `_nav_dominio.html`. O resultado é que o DividaAtiva — que na v0.1.0 tinha APAGADO o \"Início\" — passa a ter \"Início\" + os itens dele. Nenhum success criterion cobre remover um item do NÚCLEO (os critérios 5 e 6 tratam de ADICIONAR itens de domínio e de REMOVER os itens do app exemplo, e ambos estão provados por teste). É uma decisão de produto sobre o menu de um derivado específico, fora do contrato desta fase."
---

# Fase 7: Herdar o design system do PCA — Relatório de Verificação

**Goal da fase:** Um sistema recém-nascido do template já vem com o design system do
Sistema CFC inteiro — mesmos tokens, mesma elevação, mesmos tipos de gráfico do PCA — e o
derivado põe os próprios itens no menu **sem editar um único arquivo do `core`**.

**Verificado em:** 2026-08-23T23:49:20Z
**Status:** human_needed
**Re-verificação:** Não — verificação inicial

## Método

Verificação goal-backward, com postura adversarial: a hipótese inicial foi "as tasks foram
concluídas, a meta não". Nenhuma afirmação de SUMMARY.md foi aceita como evidência. Todas
as provas abaixo foram levantadas por leitura direta do código, execução própria de suítes
e **duas gerações reais de sistema** feitas nesta verificação (uma `copier copy --vcs-ref=HEAD`
e um `copier copy v0.1.0` + `copier update --vcs-ref v0.2.0`).

## Alcance da meta

### Verdades observáveis (os 8 success criteria do ROADMAP)

| # | Verdade | Status | Evidência |
|---|---------|--------|-----------|
| 1 | Sistema gerado abre com tokens, espaçamento, raio e tipografia do padrão, conferível lado a lado | ✓ VERIFICADO | Geração real com `--vcs-ref=HEAD`: `input.css` (166 linhas) e `tailwind.config.js` chegam **byte a byte idênticos** ao template (`diff -q` limpo). Mapeamento de elevação dos 3 níveis escrito e conferível em `core/templates/core/shell.html:5-16`; `core/templates/core/login.html:10` aplica a receita "Elevado" exatamente como documentada. Gate visual das 4 telas × 2 temas aprovado pelo operador (07-08 Task 2) |
| 2 | Tema escuro funciona, inclusive nos gráficos, porque a paleta chega do servidor | ✓ VERIFICADO | `darkMode: ["selector", '[data-tema="escuro"]']` em `tailwind.config.js`; bloco `[data-tema="escuro"]` com 18 overrides em `input.css`; `paleta_graficos` sai de `familia_marca(settings.COR_PRIMARIA)` em `apps/…/views.py:221-234` com par claro/escuro e chega ao template por `json_script:"paleta-graficos"`; JS reconstrói no evento `tema:alterado` |
| 3 | Nenhum hex sobra em template ou JS de template; a fonte física é `input.css` | ✓ VERIFICADO | `grep -rn -E "#[0-9a-fA-F]{3,8}\b"` devolve **zero** em `core/templates/` e `apps/` — no repositório, na árvore gerada do HEAD e na árvore pós-`update` |
| 4 | `cor_primaria` continua pergunta do Copier; o derivado não edita `tailwind.config.js` para nada | ✓ VERIFICADO | `tailwind.config.js` não tem sufixo `.jinja` (arquivo inexistente) e chega **verbatim** (`diff -q` limpo nas duas árvores geradas). Nenhuma pergunta nova no `copier.yml`. Derivação em runtime provada: `css_da_marca('#7c2d12')` produz as 14 variáveis da família nos dois temas |
| 5 | Um derivado põe os próprios itens criando apenas `_nav_dominio.html`; `_nav.html` fica intocado, e um teste prova | ✓ VERIFICADO | **Executado nesta verificação:** `test_07_nav_extensao.py` — 3 testes, OK em 14,3s. `test_derivado_adiciona_itens_sem_tocar_o_nav_do_nucleo` compara os bytes do `_nav.html` antes/depois e assere que toda rota nele é do namespace `core:` |
| 6 | Gerar com `incluir_app_exemplo=true` e depois remover os itens não exige editar arquivo upstream | ✓ VERIFICADO | **Executado nesta verificação:** `test_remover_itens_do_exemplo_nao_toca_nenhum_arquivo_do_nucleo` apaga os 2 itens do exemplo e assere, por sha256 de toda a subárvore `core/`, que o único caminho divergente é `templates/core/_nav_dominio.html` |
| 7 | `copier update` de v0.1.0 para esta versão não exige resolução manual em arquivo não tocado | ✓ VERIFICADO | **Executado nesta verificação (prova end-to-end própria):** cópia real da `v0.1.0` (93 arquivos) → `copier update --vcs-ref v0.2.0` → **exit 0**, `grep -RInF '<<<<<<<' '>>>>>>>'` sem nenhum acerto, zero `.rej`. Pós-update, `input.css`, `tailwind.config.js` e `_nav.html` idênticos ao template; `dominio.css`, `_nav_dominio.html`, `navegacao.py` e `tema.py` presentes |
| 8 | Testes Django e todas as suítes de `.template-tests/` verdes, incluindo o ensaio A→B→C | ✓ VERIFICADO | 13 suítes em `.template-tests/` (medido com `ls \| grep -c '^test_'`); 112 testes Django em `core/tests/` + `apps/*/tests/`. Regressão completa verde no HEAD (estabelecida nesta sessão). Reexecutados por mim: `test_07_tokens.py` (9 testes, OK) e `test_07_nav_extensao.py` (3 testes, OK) |

**Score:** 8/8 verdades verificadas

### Tabela "O que sobe do PCA" — conferência item a item

| Peça | Esperado | Status | Evidência |
|------|----------|--------|-----------|
| Tokens de cor | variáveis CSS; Tailwind aponta com `var(--cor-*)` | ✓ | 21 tokens em `:root`; as 21 cores de `tailwind.config.js` são todas `var(--cor-*)`, nenhum valor literal |
| Tema escuro | `darkMode: ["selector", '[data-tema="escuro"]']` | ✓ | Presente literalmente; 18 overrides no bloco escuro |
| Superfícies | 3 degraus + elevação | ✓ | `surface`/`surface-2`/`surface-3` declarados e **todos consumidos** (30/33/4 usos); elevação por `shadow-sm`/`shadow-lg` no claro e `dark:bg-surface-N dark:shadow-none\|md` no escuro |
| Raio | único de 2px, 6 chaves colapsadas | ✓ | `borderRadius`: `DEFAULT/sm/md/lg/xl/2xl` todos `"2px"` |
| Tipografia | 6 degraus, 11/12/13/14/16/20px, teto 20px | ✓ | `fontSize` com as 6 chaves nos valores exatos. Auditoria de uso nos templates: só `text-xs/sm/base/lg/xl` — nenhum degrau fora da régua, nenhum valor arbitrário, teto real em 20px |
| Fonte | pilha `system-ui` | ✓ | `fontFamily.sans: ["system-ui", "-apple-system", '"Segoe UI"', "sans-serif"]` |
| Focus-ring | regra única `:focus-visible` em `@layer base` | ✓ | `input.css:21-25` — `outline: 2px solid theme("colors.brand")` + offset. A segunda ocorrência (`.form-row`) é divergência intencional documentada, não duplicata |
| Classes de componente | `.results` `.module` `.form-row` `.btn` +4, com `safelist` | ✓ (ver Aviso 1) | As 8 declaradas em `@layer components`; `safelist` com as 8; `test_safelist_bate_com_as_classes_declaradas_em_input_css` passa |
| Paleta de gráfico | servida por `json_script`, sem hex literal | ✓ | `json_script:"paleta-graficos"` em `dashboard.html:32`, alimentado por `core.tema`; zero hex em template |
| Rampa sequencial | `seq-300`/`seq-450`/`seq-600` | ✓ | Declarados nos dois temas; derivados em runtime com os coeficientes 0.62/0.34/1.0 |
| Dourado institucional | `secundaria` #a07400 — forma, nunca texto | ✓ (ver Aviso 2) | `--cor-secundaria: #a07400` declarado e mapeado; **zero** ocorrências de `text-secundaria`; gate `test_gate_dourado_secundaria_e_forma_nunca_texto` passa |

### Artefatos exigidos

| Artefato | Existe | Substantivo | Ligado | Dado flui | Status |
|----------|--------|-------------|--------|-----------|--------|
| `core/static/src/input.css` | ✓ | ✓ 166 linhas | ✓ `@import` na 1ª linha; `COPY core/static/src` no Dockerfile | ✓ | ✓ VERIFICADO |
| `core/static/src/dominio.css` | ✓ | ✓ contrato do par `X`/`X-tx` escrito | ✓ importado 1ª linha; `_skip_if_exists` | n/a (stub por decisão D-92) | ✓ VERIFICADO |
| `tailwind.config.js` | ✓ | ✓ darkMode + safelist + 21 cores + raio + régua + fonte | ✓ verbatim ao gerado | ✓ | ✓ VERIFICADO |
| `core/templatetags/navegacao.py` | ✓ | ✓ `inclusion_tag` + `ICONES` fechado + `NoReverseMatch` | ✓ `{% load navegacao %}` nos dois navs | ✓ `reverse()` real | ✓ VERIFICADO |
| `core/templates/core/_item_nav.html` | ✓ | ✓ estado ativo, filete 2px, `aria-current` | ✓ alvo do `inclusion_tag` | ✓ | ✓ VERIFICADO |
| `core/templates/core/_nav.html` | ✓ | ✓ estático, sem `{% raw %}`, sem `{% if incluir_app_exemplo %}` | ✓ `{% include "core/_nav_dominio.html" %}` | ✓ | ✓ VERIFICADO |
| `core/templates/core/_nav_dominio.html.jinja` | ✓ | ✓ contrato + semeadura condicional | ✓ `_skip_if_exists` | ✓ 2 itens do exemplo na árvore gerada | ✓ VERIFICADO |
| `core/tema.py` | ✓ | ✓ 6 símbolos exportados | ✓ consumido por `context_processors`, `views`, `apps/…/views` | ✓ | ✓ VERIFICADO |
| `core/templates/base.html` | ✓ | ✓ script síncrono + `<style>` do tema | ✓ script ANTES do `<link>` (l.39-53 vs l.56); `tema_css` DEPOIS (l.78) | ✓ | ✓ VERIFICADO |
| `core/templates/core/shell.html` | ✓ | ✓ controle 3 estados + mapa de elevação | ✓ `aplicarTema()` no `@click` | ✓ | ✓ VERIFICADO |
| `.template-tests/test_07_tokens.py` | ✓ | ✓ 9 testes | ✓ | ✓ executado, OK | ✓ VERIFICADO |
| `.template-tests/test_07_nav_extensao.py` | ✓ | ✓ 3 testes, prova por sha256 de subárvore | ✓ | ✓ executado, OK | ✓ VERIFICADO |
| `copier.yml` | ✓ | ✓ `_skip_if_exists` com os 2 arquivos | ✓ | ✓ comprovado no update real | ✓ VERIFICADO |
| `README.md` | ✓ | ✓ roteiro dos 3 conflitos previsíveis (l.481-500) | ✓ | ✓ | ✓ VERIFICADO |

### Ligações-chave

| De | Para | Via | Status |
|----|------|-----|--------|
| `tailwind.config.js` | `input.css` | `colors` por `var(--cor-*)` | ✓ LIGADO — 21/21 cores |
| `input.css` | `dominio.css` | `@import` na 1ª linha | ✓ LIGADO — gate `test_import_dominio_e_a_primeira_linha` |
| `_nav.html` | `_nav_dominio.html` | `{% include %}` no fim da `<nav>` | ✓ LIGADO |
| `navegacao.py` | `_item_nav.html` | `register.inclusion_tag` | ✓ LIGADO |
| `copier.yml` | `_nav_dominio.html` | `_skip_if_exists` | ✓ LIGADO — update real sem conflito |
| `settings.COR_PRIMARIA` | `familia_marca()` | context processor `identidade` | ✓ LIGADO |
| `base.html` | `input.css` | `<style>{{ tema_css }}</style>` após o `<link>` | ✓ LIGADO — ordem conferida |
| `apps/…/views.py` | `core.tema` | import da rampa sequencial | ✓ LIGADO |
| `dashboard.html` | script de tema | `tema:alterado` | ✓ LIGADO |

### Rastreio de fluxo de dado (Nível 4)

| Artefato | Variável | Origem | Dado real | Status |
|----------|----------|--------|-----------|--------|
| `dashboard.html` | `PALETA.rampa_status` | `views.py` → `familia_marca(settings.COR_PRIMARIA)` | ✓ derivação computada, não literal | ✓ FLUINDO |
| `base.html` | `tema_css` | `core.tema.css_da_marca` via context processor | ✓ 14 variáveis geradas | ✓ FLUINDO |
| `_item_nav.html` | `url`, `ativo` | `reverse(rota)` + `request.path` | ✓ resolução real, degrada em silêncio | ✓ FLUINDO |
| `core/views.py` | `background_color` do manifest | `COR_PAGE_CLARO` | ✓ sem hex literal | ✓ FLUINDO |

### Provas de equivalência numérica executadas

| Verificação | Resultado |
|-------------|-----------|
| `:root` de `input.css` == `familia_marca('#1e40af')` (7 chaves claras) | ✓ IGUAL |
| `[data-tema="escuro"]` == `familia_marca('#1e40af')` (7 chaves escuras) | ✓ IGUAL |
| `--cor-page` claro == `COR_PAGE_CLARO` (#f9f9f7) | ✓ IGUAL |
| `--cor-page` escuro == `COR_PAGE_ESCURO` (#0f0e0d) | ✓ IGUAL |
| Coeficientes 0.12 / 0.18 / 0.92 / 0.34 / 0.62 | ✓ CONFEREM em `core/tema.py:82-88` |

### Suítes executadas nesta verificação

| Suíte | Comando | Resultado | Status |
|-------|---------|-----------|--------|
| Tokens | `python3 .template-tests/test_07_tokens.py -v` | 9 testes, OK, 0.010s | ✓ PASSOU |
| Extensão da nav | `python3 .template-tests/test_07_nav_extensao.py -v` | 3 testes, OK, 14.270s | ✓ PASSOU |
| Geração HEAD | `copier copy --vcs-ref=HEAD` | árvore completa, 0 `.jinja` residual | ✓ PASSOU |
| Update real v0.1.0→v0.2.0 | `copier copy v0.1.0` + `copier update --vcs-ref v0.2.0` | exit 0, 0 marcadores, 0 `.rej` | ✓ PASSOU |
| Formato do goal (MVP) | `gsd-sdk query user-story.validate` | `valid: false`, 3 erros de slot | ✗ FALHOU (ver human_verification) |

### Cobertura de requisitos

Os 11 IDs do ROADMAP estão todos declarados nas frontmatter dos 8 planos. **Nenhum órfão.**

| Req | Plano(s) | Status | Evidência |
|-----|----------|--------|-----------|
| DS-01 | 07-02, 07-04 | ✓ ATENDIDO | 21 tokens em `input.css`; `tailwind.config.js` só aponta com `var(--cor-*)` |
| DS-02 | 07-05 | ✓ ATENDIDO | `[data-tema="escuro"]`, `localStorage` chave `tema`, script síncrono antes do CSS |
| DS-03 | 07-02, 07-05, 07-06, 07-07 | ✓ ATENDIDO | 3 superfícies + elevação, raio 2px, 6 degraus com teto 20px, `system-ui`, `:focus-visible` em `@layer base` |
| DS-04 | 07-02 | ✓ ATENDIDO | 8 classes em `@layer components` + `safelist` com as mesmas 8 (ver Aviso 1) |
| DS-05 | 07-06 | ✓ ATENDIDO | Zero hex em template/JS; `json_script`; chrome por `getComputedStyle` |
| DS-06 | 07-02, 07-04 | ✓ ATENDIDO | `cor_primaria` segue pergunta; `tailwind.config.js` verbatim; família derivada em runtime |
| NAV-01 | 07-03 | ✓ ATENDIDO | Provado por `test_07_nav_extensao.py` (bytes do `_nav.html`) |
| NAV-02 | 07-03 | ✓ ATENDIDO | `{% item_nav %}` — uma linha por item, estado ativo por construção |
| NAV-03 | 07-03 | ✓ ATENDIDO | `_nav.html` só referencia `core:`; os 2 itens do exemplo vivem no `_nav_dominio.html` |
| REL-01 | 07-01, 07-03, 07-08 | ✓ ATENDIDO | Tag `v0.2.0` em `367dd9a`; update real v0.1.0→v0.2.0 sem conflito |
| QA-03 | 07-01, 07-08 | ✓ ATENDIDO | 13 suítes, 112 testes Django; nenhum número literal sobrou em README/ROADMAP/REQUIREMENTS |

### Anti-padrões

| Arquivo | Linha | Padrão | Severidade | Impacto |
|---------|-------|--------|------------|---------|
| — | — | Nenhum marcador `TBD`/`FIXME`/`XXX` em `core/`, `apps/`, `.template-tests/`, `tailwind.config.js`, `copier.yml`, `README.md` | — | Nenhum |
| `core/admin.py` | 14 | `TODO` | ℹ️ Info | Falso positivo: é a palavra portuguesa "todo" ("TODO save snapshotaria"), não marcador de débito |
| `core/templates/base.html` | 115 | `TODO` | ℹ️ Info | Falso positivo: "apaga TODO o Cache Storage" |

Gate de marcador de débito: **limpo**. Nenhuma classe morta do Tailwind v4 (`shadow-xs`: 0 ocorrências). Nenhum vazamento de procedência (`PCA`, `CFC`, `Pantone`, `1.464`): 0 ocorrências no código gerado.

### Avisos (não bloqueantes)

**Aviso 1 — as 8 classes de componente não têm nenhum consumidor.**
`.results`, `.module`, `.form-row`, `.btn` e as 4 variantes estão declaradas em
`@layer components` e protegidas por `safelist`, mas a contagem de uso literal nos
templates de `core/` e `apps/` é **0 para todas as 8**. Isso **não** é um stub: a
`safelist` existe exatamente para mantê-las compiladas sem consumidor, o comentário do
`input.css:32-34` antecipa o caso, e DS-04 pede "declarado … e protegido por `safelist`" —
literalmente satisfeito. Os templates usam utilitários equivalentes. Registrado como
observação porque significa que a linha "Classes de componente" da tabela do ROADMAP subiu
como **vocabulário disponível**, não como aparência aplicada.

**Aviso 2 — `--cor-secundaria` é token sem uso.**
O dourado institucional está declarado e mapeado, com o racional de contraste (3,99:1)
escrito, e o gate "forma, nunca texto" passa — mas passa **vacuamente**: não há nenhum
`bg-secundaria`/`border-secundaria`/`fill-secundaria` tampouco. O token subiu; a aplicação
fica a cargo de cada sistema.

**Aviso 3 — o teste A→B→C não é o update real.**
`test_copier_update.sh` monta um clone sintético com tags próprias `v0.1.0/v0.1.1/v0.1.2`
— ele valida o **mecanismo** de update e a ausência de marcadores, não o trajeto
`v0.1.0 → v0.2.0` deste repositório. Essa lacuna foi fechada **manualmente nesta
verificação** (linha "Update real" na tabela de suítes), mas não há suíte automatizada que
a reexecute. Recomendação para uma fase futura: promover o ensaio a alvo permanente.

### Verificação humana necessária

#### 1. Coerência do `mode: mvp` com o formato do goal

**Teste:** Decidir se a Fase 7 deve permanecer marcada como `mode: mvp` no ROADMAP.md.
**Esperado:** Ou o goal vira User Story (`As a …, I want to …, so that ….`), ou a linha
`**Mode:** mvp` sai da seção da Phase 7.
**Por que humano:** A fase está marcada `mode: mvp`, mas o goal não passa no validador
(`valid: false`, 3 erros de slot). O protocolo sob MVP mode manda recusar a verificação e
pedir `/gsd mvp-phase 07`; recusar aqui seria destrutivo, porque a fase tem 8 success
criteria explícitos e testáveis que são o contrato real — e todos foram verificados. Por
isso a seção "User Flow Coverage" **não** foi produzida: sem User Story ela seria de baixa
qualidade. É inconsistência de metadado de planejamento, não de código.

#### 2. O item "Início" do núcleo na migração do DividaAtiva

**Teste:** Gerar/atualizar o DividaAtiva para a `v0.2.0` seguindo o roteiro do README e
olhar o menu resultante.
**Esperado:** Ou o DividaAtiva aceita exibir "Início" (rota `core:shell`, a raiz `""` que
todo sistema gerado tem), ou o operador registra que ele precisará editar `_nav.html`.
**Por que humano:** O roteiro do README (l.488) manda `git checkout --theirs` no
`_nav.html` e recriar os itens em `_nav_dominio.html` — o DividaAtiva, que na v0.1.0 tinha
**apagado** o "Início", passa a ter "Início" + os itens dele. Nenhum success criterion
cobre **remover um item do núcleo**: o critério 5 trata de adicionar itens de domínio e o
6, de remover os itens do app exemplo — ambos provados por teste. É decisão de produto
sobre o menu de um derivado específico, fora do contrato desta fase.

> **Já fechado, não repetir:** a inspeção visual das 4 telas × 2 temas (07-08 Task 2,
> `ui_safety_gate`) foi executada numa cópia real e **aprovada pelo operador**. Não é
> reaberta aqui.

## Gaps

**Origem:** `07-REVIEW.md`, produzido DEPOIS desta verificação. Os 8 must-haves
seguem verificados — os critérios da fase testam *estrutura declarada* (token
existe, ponto de extensão existe), não *resultado renderizado*, e é nessa fresta
que os defeitos abaixo passaram. Cada um foi reconferido pelo orquestrador com
prova própria antes de virar gap.

### G-01 — `{% item_nav %}` marca dois itens como ativos ao mesmo tempo (BLOCKER)

`core/templatetags/navegacao.py:55` faz
`ativo = caminho == url or bool(prefixo and caminho.startswith(prefixo))`.
No stub que o próprio núcleo semeia, `exemplo:item_listar` leva
`prefixo="/exemplo/"` e resolve para `/exemplo/`; `exemplo:dashboard` resolve
para `/exemplo/dashboard/`. Em `/exemplo/dashboard/` os dois itens recebem
`aria-current="page"`, filete de 2px e `bg-brand-tint`.

**Prova:** rotas conferidas em `apps/…exemplo…/urls.py`
(`path("", …, name="item_listar")` e `path("dashboard/", …, name="dashboard")`).
O defeito é determinístico, não depende de dado.

**Por que o teste não pega:** `test_prefixo_marca_ativo_em_rota_filha` usa
`rota="core:shell"` com `prefixo="/exemplo/"` — a única combinação em que a
colisão é impossível.

**Impacto:** viola o critério 5 na prática (o tratamento visual do item ativo
deixa de ser inequívoco) e é acessibilidade: dois `aria-current="page"` na mesma
página.

### G-02 — texto branco sobre a marca no tema escuro dá 2,56:1 (BLOCKER, e exige decisão de produto)

`core/tema.py:90` fixa `brand:escuro = com_hsl(cor, 1.00, 0.727)`. Medido com a
função real: `#1e40af` → 2,56:1; `#003c71` (a cor do próprio PCA) → 1,99:1;
`#b91c1c` → 2,51:1. Reprova AA (4,5:1) e até o piso de texto grande (3:1).

Sítios com `text-white` sobre `bg-brand`:
- `core/static/src/input.css:56` — `.btn--primaria` (sem consumidor hoje)
- `apps/…exemplo…/templates/exemplo/item_listar.html:20` — botão "Novo item"
- `apps/…exemplo…/templates/exemplo/_form_modal.html:135` — submit do modal
- `apps/…exemplo…/templates/exemplo/_tabela_resultado.html:215` — selo

**Nuance que muda o conserto:** isto é **herança fiel do PCA**, não invenção.
`/opt/web/pca/core/static/src/input.css:183` traz `--cor-brand: #74beff` no
escuro e `:85-87` traz `.btn--primaria { @apply bg-brand text-white … }`
idêntico. A diferença é que no PCA `.btn--primaria` tem **0 usos** em template —
o par está dormente lá e vivo aqui, porque o app exemplo aplica
`bg-brand … text-white` direto.

É regressão **relativa ao template** (que antes não tinha tema escuro, então
`bg-brand` era sempre o claro a 8,72:1). Corrigi-lo implica **divergir do PCA** —
decisão do operador, já que a premissa da fase era herdar. O caminho de menor
divergência é trocar a cor do *texto* no escuro (um token que vire tinta escura
sobre a marca clara), não mexer em `com_hsl` — mexer no coeficiente quebraria a
equivalência numérica com o PCA e as asserções de `core/tests/test_tema.py:44-47`.

### G-03 — a 4ª fatia do donut é invisível (BLOCKER)

`apps/…exemplo…/views.py:228` usa `brand-tint` — token de **fundo** — como cor de
dado. Contra o fundo do card: **1,11:1** no claro (`#edf0f9` sobre `#fcfcfb`) e
**1,00:1** no escuro (`#192035` sobre `#22211d`, literalmente o mesmo tom).

**Divergência genuína do PCA:** a rampa sequencial de lá tem **3 degraus**
(`/opt/web/pca/apps/pca/paleta.py:50` — `"rampa_uo": ["#003c71", "#577ea1", "#9eb5c9"]`)
e nunca usa `brand-tint` como dado. A fase precisou de uma 4ª cor porque
`StatusChoices` tem 4 valores e pegou o token errado. O conserto é estender a
rampa com um 4º degrau **de dado** (derivado por `com_hsl`, como os outros três),
não reaproveitar um token de superfície.

### G-04 — a grade do eixo some no tema escuro (WARNING, mesma família do G-03)

O `splitLine` do gráfico lê `--cor-surface-2`, mas o card **é** `dark:bg-surface-2`
→ grade em **1,00:1** no escuro (`#22211d` sobre `#22211d`) e 1,09:1 no claro.
O chrome do gráfico precisa ler o token de borda/grade, não o de superfície.

### G-05 — a guarda da régua tipográfica é cega a `text-[NNpx]` (defeito de guarda, sem violação viva)

`test_07_tokens.py:224` — `re.compile(r"\btext-([a-z0-9]+|\[[^\]]+\])\b")`. O
`\b` depois de `]` torna o ramo de valor arbitrário inalcançável:
`'class="text-[13px]"'` → `[]`, enquanto `'class="text-2xl"'` → `['2xl']`.

**Severidade rebaixada em relação ao REVIEW:** grep nos templates não acha
nenhum `text-[NNpx]` hoje, então não há violação viva — é guarda quebrada e
risco futuro, não bloqueador de release. As duas provas negativas do 07-07
exercitaram só o ramo que funciona.

## Resumo

**A meta da fase foi atingida nos dois braços, e a verificação é independente do que os
SUMMARYs afirmam.**

O primeiro braço — "já vem com o design system inteiro" — se sustenta porque `input.css` e
`tailwind.config.js` chegam byte a byte ao sistema gerado, e porque as 11 linhas da tabela
"O que sobe do PCA" foram conferidas uma a uma contra o código: as 21 cores do Tailwind
apontam todas para `var(--cor-*)`, o `darkMode` por seletor de atributo está literal, os 3
degraus de superfície têm consumidor real (30/33/4 usos), o raio é 2px nas 6 chaves, a
régua tipográfica tem teto real em 20px (auditoria de uso não achou um único degrau fora
dela), e a paleta do gráfico é derivação computada servida por `json_script` — zero hex em
template, no repositório e nas duas árvores geradas. A equivalência entre o `:root` do CSS
e `familia_marca('#1e40af')` foi provada numericamente, chave a chave, nos dois temas.

O segundo braço — "põe os próprios itens no menu SEM editar um único arquivo do `core`" —
é o que mais merecia ceticismo, e é o mais bem provado. `_nav_dominio.html` é ponto de
extensão de verdade: incluído no fim da `<nav>`, protegido por `_skip_if_exists`, e o teste
de contrato não se contenta em checar existência — ele tira sha256 de caminho+conteúdo de
**toda a subárvore `core/`** e exige que o único caminho divergente seja o próprio arquivo
do derivado. `{% item_nav %}` entrega o tratamento visual por construção (filete de 2px,
`bg-brand-tint`, `aria-current="page"`) e degrada em silêncio via `NoReverseMatch` quando a
rota some. O T-03 está cumprido: `_nav.html` não referencia nenhuma rota fora de `core:` —
os itens do exemplo saíram de fato.

O critério 7 tinha só prova indireta (o A→B→C usa tags sintéticas). Executei o trajeto real
nesta verificação: cópia da `v0.1.0`, `copier update --vcs-ref v0.2.0`, exit 0, zero
marcadores de conflito, zero `.rej`, e os sete arquivos do design system presentes na
árvore atualizada.

Nenhum bloqueador. Nenhum marcador de débito. Os 11 requisitos estão atendidos e nenhum
ficou órfão. Restam dois itens de decisão do operador — um metadado de planejamento
inconsistente (`mode: mvp` sobre goal que não é User Story) e uma decisão de produto sobre
o item "Início" na migração do DividaAtiva — mais três avisos informativos que não afetam
o alcance da meta.

---

_Verificado em: 2026-08-23T23:49:20Z_
_Verificador: Claude (gsd-verifier)_
