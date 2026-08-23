# Fase 7: Herdar o design system do PCA — Pesquisa

**Pesquisado em:** 2026-08-23
**Domínio:** Design tokens em variáveis CSS + Tailwind v3, tema escuro por atributo, paleta de gráfico servida pelo servidor, ponto de extensão de navegação em Django Templates, contrato de `copier update`
**Confiança geral:** ALTA (quase tudo verificado lendo os arquivos reais e executando Tailwind 3.4.17 e Copier 9.17.1 nesta sessão)

> Não existe `07-CONTEXT.md`. As restrições abaixo vêm do ROADMAP (§Phase 7), do
> `CLAUDE.md` e do estado real dos dois repositórios. Onde um valor precisa ser
> **escolhido** (sem precedente no PCA), a seção diz isso explicitamente e
> recomenda um — cabe ao planejador travar.

---

## Sumário

O PCA (`/opt/web/pca`) já fez, em três fases (10, 13 e 14), exatamente a migração que
esta fase precisa importar: os tokens de cor saíram do `tailwind.config.js` e viraram
**variáveis CSS em `core/static/src/input.css`**; o config passou a apontar para elas
com `var(--cor-*)`; `:root` carrega o tema claro e `[data-tema="escuro"]` sobrescreve;
um script síncrono no `<head>`, **antes do `<link>` do CSS**, grava o atributo lendo
`localStorage`; os gráficos ECharts leem a cor de chrome em runtime com
`getComputedStyle`, e só o dado semântico (rampa e séries) continua chegando por
`json_script`. O template está no estado anterior a tudo isso: um único hex de marca
derivado em build-time por `misturar()` no `tailwind.config.js.jinja`, sem tema escuro,
sem raio/tipografia/fonte declarados, sem focus-ring, sem classes de componente, e com
**14 hex literais soltos no JavaScript** do dashboard do app exemplo.

A boa notícia mensurada: as derivações do PCA **são reprodutíveis pela `misturar()` que
o template já tem**. Verificado nesta sessão com o próprio código: a partir de `#003c71`,
`misturar(B,255,0.12)` dá exatamente `#1f5382` (o `brand-hover` do PCA) e
`misturar(B,0,0.18)` dá exatamente `#00315d` (o `brand-ink`). O `brand-tint` do PCA
(`#ebeff4`) sai de `misturar(B,255,0.92)` — o template usa hoje `0.9`, que daria
`#e6ecf1`. A rampa sequencial também é pura mistura sRGB: `seq-450` = 34% branco,
`seq-300` = 62% branco. No tema escuro a regra muda de natureza: o par claro/escuro da
marca preserva **matiz e saturação** e move só a luminosidade HSL (208,1° / 100% em
ambos; L 22,2% → 72,7%). Ou seja: existe uma regra determinística, testável e
parametrizável por `cor_primaria` para toda a família de marca, nos dois temas.

A parte de navegação é trabalho **novo** — o PCA **não tem** inclusion tag de item; ele
sofre da mesma repetição de doze linhas (`core/templates/core/_nav_visoes.html`, 4
itens × ~12 linhas). O que o PCA fornece aqui é só o *tratamento visual* do item ativo
(`bg-brand-tint text-brand-ink`, filete `w-[2px] bg-brand`, `aria-current="page"`), que
já é idêntico ao do template. O mecanismo de extensão (`_nav_dominio.html` +
`{% item_nav %}`) precisa ser projetado do zero — e a peça que o torna livre de
conflito no `copier update` foi **provada empiricamente nesta sessão**: `_skip_if_exists`.

**Recomendação primária:** migrar os tokens para `input.css` seguindo o PCA
literalmente (mesmos nomes `--cor-*`, mesma cascata `:root` / `[data-tema="escuro"]`,
mesmo `darkMode: ["selector", '[data-tema="escuro"]']`), mantendo **hex plano** em toda
variável (nada de `color-mix()` nos tokens que o JS lê); derivar a família de marca a
partir de `COR_PRIMARIA` em **Python no boot** (`core/tema.py`), espelhando o precedente
já existente de `admin_tema_css` em `core/admin_site.py:40-50`; e resolver a navegação
com `_nav.html` estático (100% upstream) + `_nav_dominio.html` protegido por
`_skip_if_exists` (100% do derivado) + inclusion tag `{% item_nav %}` em
`core/templatetags/navegacao.py`.

---

## Mapa de Responsabilidade Arquitetural

| Capacidade | Camada primária | Camada secundária | Racional |
|---|---|---|---|
| Valores físicos dos tokens (neutros, status, rampa) | Asset estático (`core/static/src/input.css`) | — | Critério 3 exige fonte física única; um `SimpleTestCase` lê o arquivo sem banco e sem build (padrão `test_paleta_contraste.py` do PCA) |
| Geração das classes utilitárias (`bg-page`, `text-ink`, `dark:`) | Build de assets (Tailwind CLI no estágio `assets` do Dockerfile) | — | JIT precisa varrer templates em build-time; `var()` resolve em runtime |
| Família de marca derivada de `COR_PRIMARIA` | Backend Django (novo `core/tema.py` + context processor) | Asset estático (fallback em `:root`) | `.env` é a fonte de runtime por D-47/D-50; derivação em Python é testável sem browser e sem build |
| Escolha do tema (auto/claro/escuro) | Cliente (script síncrono + `localStorage`) | — | Cookie + render server-side é rejeitado: o service worker cacheia `/static/`, e o PCA rejeitou o cookie explicitamente (10-UI-SPEC §8) |
| Cor de *chrome* do gráfico (eixo, grid, tooltip) | Cliente (`getComputedStyle` da raiz) | — | Precisa reagir à troca de tema sem reload (D-142) |
| Cor *semântica* do gráfico (rampa, séries) | Backend Django (`json_script`) | — | É dado, não estilo; e evita hex no JS (critério 3) |
| Itens de navegação do domínio | Template do derivado (`_nav_dominio.html`) | — | Critério 5: `_nav.html` fica intocado |
| Tratamento visual do item de navegação | Backend Django (`inclusion_tag` + `_item_nav.html`) | — | Uma fonte só para as 12 linhas; o derivado escreve uma linha |
| Itens de navegação do app exemplo | Template do derivado (semeado no `copy`) | — | Critério 6: remover não pode exigir editar upstream |
| Perguntas de parametrização | `copier.yml` | Padrão do template (sem pergunta) | Critério 4: o derivado nunca edita `tailwind.config.js` |

---

## Requisitos da Fase (propostos — não existem IDs mapeados)

O ROADMAP registra **Requirements: TBD (definir no planejamento)** e a
`REQUIREMENTS.md` não tem nenhuma família para design system. Propostos abaixo, na
convenção existente (prefixo + número sequencial de dois dígitos), para o planejador
inserir em `.planning/REQUIREMENTS.md` e na tabela de Rastreabilidade:

| ID proposto | Descrição | Critério do ROADMAP que cobre |
|---|---|---|
| **DS-01** | Sistema gerado nasce com os tokens de cor em variáveis CSS em `core/static/src/input.css`, e `tailwind.config.js` só aponta para elas via `var(--cor-*)` | 1, 3 |
| **DS-02** | Sistema gerado tem tema escuro funcional por `[data-tema="escuro"]`, com escolha persistida e sem flash de tema | 2 |
| **DS-03** | Régua física declarada: 3 degraus de superfície + elevação por sombra, raio único de 2px, 6 degraus tipográficos com teto de 20px, pilha `system-ui`, `:focus-visible` único em `@layer base` | 1 |
| **DS-04** | Vocabulário de componente `.results` `.module` `.form-row` `.btn` (+4 variantes) declarado em `@layer components` e protegido por `safelist` | 1 |
| **DS-05** | Nenhum hex de cor em template ou em JS de template; a paleta do gráfico chega do servidor e o chrome é lido das variáveis CSS em runtime | 2, 3 |
| **DS-06** | `cor_primaria` continua sendo pergunta do Copier e é a única entrada da família de marca nos dois temas; o derivado nunca edita `tailwind.config.js` | 4 |
| **NAV-01** | `core/templates/core/_nav.html` fica intocado por qualquer derivado; itens de domínio entram apenas por `core/templates/core/_nav_dominio.html`, provado por teste de contrato | 5 |
| **NAV-02** | Item de navegação vira `{% item_nav %}` — uma linha por item, com o tratamento de estado ativo do padrão por construção | 5 |
| **NAV-03** | Itens do app exemplo saem do `_nav.html` base; gerar com `incluir_app_exemplo=true` e depois remover os itens não exige editar arquivo upstream | 6 |
| **REL-01** | `copier update` de um sistema na v0.1.0 para esta versão não exige resolução manual em arquivo que o derivado não tenha tocado; a fase fecha com a tag `v0.2.0` | 7 |
| **QA-03** | Os 77 testes Django (`core` + `apps.exemplo`) e as 11 suítes de `.template-tests/` seguem verdes, incluindo o ensaio A→B→C | 8 |

---

## Restrições do Projeto (do `CLAUDE.md`)

- **Fluxo GSD obrigatório**: nada de edição direta fora de um comando GSD.
- Stack/convenções/arquitetura ainda "não documentadas" no `CLAUDE.md` — o contrato real
  está em `core/README.md` (5 convenções não-óbvias do kernel) e nos comentários dos
  arquivos. **Não há `.claude/skills/` nem `.agents/skills/` neste repositório**
  (`.claude/` contém apenas `RESUME.md` e `worktrees/`).
- `.planning/config.json`: `nyquist_validation: false` → a seção *Validation
  Architecture* está deliberadamente omitida deste documento. `language: pt-BR`,
  `granularity: coarse`, `ui_phase: true`, `ui_safety_gate: true`.
- `build_command`: `python3 -m py_compile .template-tests/*.py`
- `test_command`: `python3 -m unittest discover -s .template-tests -p 'test_*.py'`

**Invariante de projeto que morde esta fase** (`REQUIREMENTS.md` §Fora de Escopo +
TPL-04): *"Código gerado não contém nenhuma menção a 'PCA' ou a qualquer domínio de
negócio"*. Ver Pitfall 11 — isto é executável e vai reprovar comentários de procedência.

---

## O que sobe do PCA — valores concretos

### 1. Camada de token — o conjunto exato de variáveis CSS

Fonte: `/opt/web/pca/core/static/src/input.css`, linhas **119-205**. O bloco fica
**fora** de `@layer components` de propósito (o JIT poda regra em layer cujo seletor não
aparece no conteúdo varrido). `:root` e `[data-tema="escuro"]` têm a **mesma
especificidade** — a ordem de declaração decide, e quem não tem override no bloco escuro
herda o claro.

#### 1.1 Superfícies, texto e estrutura

| Token | Template hoje (`tailwind.config.js.jinja:33-46`) | PCA claro (`input.css:121-130`) | PCA escuro (`input.css:173-181`) | Situação |
|---|---|---|---|---|
| `page` | `#f9f9f7` | `#f9f9f7` | `#0f0e0d` | idêntico no claro |
| `surface` | `#fcfcfb` | `#fcfcfb` | `#181614` | idêntico no claro |
| `surface-2` | `#f3f2ef` | `#f3f2ef` | `#22211d` | idêntico no claro |
| `surface-3` | **não existe** | `#fcfcfb` (= `surface`) | `#2e2c28` | **novo** |
| `ink` | `#0b0b0b` | `#0b0b0b` | `#eeeeee` | idêntico no claro |
| `ink-2` | `#52514e` | `#52514e` | `#b9b8b5` | idêntico no claro |
| `muted` | `#77756f` | `#898781` | `#95938e` | **DIVERGEM** |
| `grid` | `#e4e2dd` | `#e1e0d9` | `#3a3833` | **DIVERGEM** |
| `baseline` | **não existe** | `#c3c2b7` | (herda) | **novo** |

> Onde os dois lados discordam (`muted`, `grid`), o PCA é a fonte declarada do padrão
> (ROADMAP §Phase 7, "Fonte do padrão"). **Recomendação: adotar os valores do PCA.**
> `muted` fica mais claro (menos contraste, mas o PCA mede `muted` só em texto
> secundário) e `grid` fica ligeiramente mais quente. `baseline` só tem consumidor se a
> fase trouxer gráficos com linha-base; **recomendação: declarar mesmo assim**, é 1 linha
> e evita que o derivado invente um nome.

#### 1.2 Família de marca — a única parte parametrizada

| Token | PCA claro | PCA escuro | Regra de derivação (VERIFICADA nesta sessão) |
|---|---|---|---|
| `brand` | `#003c71` | `#74beff` | claro = `COR_PRIMARIA`; escuro = mesmo H e S, **L = 72,7%** |
| `brand-hover` | `#1f5382` | `#a7d6ff` | claro = 12% branco; escuro = L do brand escuro **+10 pontos** (82,7%) |
| `brand-ink` | `#00315d` | `#41a6ff` | claro = 18% preto; escuro = L do brand escuro **−10 pontos** (62,7%) |
| `brand-tint` | `#ebeff4` | `#14263a` | claro = **92% branco**; escuro = valor medido à mão, sem regra simples |
| `secundaria` | `#a07400` | (herda) | fixo — dourado institucional |

Prova numérica executada com a própria `misturar()` do `tailwind.config.js.jinja`:

```
misturar("#003c71", 255, 0.12) -> #1f5382   (PCA brand-hover)  ✔ exato
misturar("#003c71",   0, 0.18) -> #00315d   (PCA brand-ink)    ✔ exato
misturar("#003c71", 255, 0.90) -> #e6ecf1   (template hoje)    ✘
misturar("#003c71", 255, 0.92) -> #ebeff4   (PCA brand-tint)   ✔ exato
```

HSL medido (mesma sessão): `#003c71` = H 208,1° S 100,0% L 22,2%;
`#74beff` = H 208,1° S 100,0% L 72,7%; `#a7d6ff` = H 208,0° S 100,0% L 82,7%;
`#41a6ff` = H 208,1° S 100,0% L 62,7%. Matiz e saturação **idênticos** — a única variável
é L. Isto é o que torna a família de marca escura derivável de um `cor_primaria`
arbitrário.

**`brand-tint` escuro (`#14263a`) não segue regra**: H 211,6° S 48,7% L 15,3% — o matiz
escorrega 3,5° e a saturação cai pela metade. É valor medido pelo PCA para o item de nav
ativo no escuro. **Decisão necessária (sem precedente derivável):** o template precisa de
uma regra. **Recomendação:** `brand-tint` escuro = mesmo H, S reduzido para ~50% do
original, L = 15%. Aplicado a `#003c71` (S 100%) dá H 208,1 S 50 L 15 = `#132d40` —
próximo, não idêntico, ao `#14263a` do PCA. Alternativa mais simples e defensável:
`misturar(brand_escuro, 0, 0.82)` sobre `#74beff` → cor no matiz certo. O planejador
trava uma; o teste de contraste (abaixo) valida qualquer escolha.

#### 1.3 Rampa sequencial e semânticos não-status

| Token | PCA claro | PCA escuro | Regra (VERIFICADA) |
|---|---|---|---|
| `seq-600` | `#003c71` | `#74beff` | **== `brand`** nos dois temas (âncora do 02-UI-SPEC §139) |
| `seq-450` | `#577ea1` | `#4196e0` | claro = **34% branco**; escuro = H igual, **S 72%, L 56,7%** |
| `seq-300` | `#9eb5c9` | `#3171a9` | claro = **62% branco**; escuro = H igual, **S 55%, L 42,7%** |
| `destructive` | `#d03b3b` | (herda) | fixo |
| `danger-tint` | `#fbe9e9` | `#2e1616` | fixo |
| `warn-bg` | `#fdf3e0` | `#2b2011` | fixo |
| `warn-tx` | `#7a5000` | `#c98400` | fixo |

Verificação: `misturar("#003c71",255,0.34) -> #577ea1` ✔ exato;
`misturar("#003c71",255,0.62) -> #9eb5c9` ✔ exato.

#### 1.4 Contrastes reproduzidos (WCAG 2.1, calculados nesta sessão)

| Par | Medido | Publicado pelo PCA | Bate |
|---|---|---|---|
| `#003c71` sobre `#f9f9f7` | **10,57:1** | 10,57:1 (BRIEFING §2.3) | ✔ |
| `#a07400` sobre `#f9f9f7` | **3,99:1** | 3,99:1 (BRIEFING §3.2) | ✔ |
| `#0b0b0b` sobre `#ebeff4` | **17,04:1** | 17,04:1 (BRIEFING §2.4d) | ✔ |
| `#9eb5c9` sobre `#fcfcfb` | **2,06:1** | 2,06:1 (BRIEFING §2.4g) | ✔ |
| `#74beff` sobre `#181614` | **9,07:1** | — | — |
| `#eeeeee` sobre `#181614` | **15,55:1** | — | — |
| `#1e40af` (default atual do template) sobre `#f9f9f7` | **8,27:1** | — | passa AA folgado |

Consequência prática: **o `cor_primaria` default do template (`#1e40af`) já passa AA
com folga**; a fase não precisa trocar o default para o azul do CFC (e não deveria —
ver Pitfall 11).

#### 1.5 O que NÃO sobe — onde exatamente cai a linha

Os **7 pares de status** do PCA (`--cor-st-concluido` / `-tx`, `st-nao-iniciado`,
`st-aguardando-dfd`, `st-em-tramitacao`, `st-vigente`, `st-cancelado`, `st-atrasado`)
são vocabulário do domínio dele — `input.css:139-153` e `196-204`. **Nenhum desses nomes
entra no template.**

O que sobe é a **mecânica**, e ela tem três peças identificáveis no código do PCA:

1. **O par fundo + texto.** Todo status tem `--cor-X` (o matiz, usado em preenchimento e
   dot) e `--cor-X-tx` (o par de texto). No claro os dois podem coincidir; no escuro só
   a variante `-tx` ganha par clareado, porque o matiz puro reprova contraste sobre
   `surface-3` (`input.css:163-170` documenta isso; `st-vigente` puro dá 1,88:1).
2. **A ponte `data-*` → cor, fora de qualquer `@layer`.** `input.css:226-258` e
   `291-302`. O Tailwind JIT não gera classe a partir de valor resolvido em runtime, e
   dentro de `@layer` ele podaria a regra. CSS solto no arquivo de entrada passa intacto.
   `theme("colors.X")` continua funcionando e compila para `var(--cor-X)` (verificado).
3. **A disciplina CVD-safe.** O PCA mediu CIEDE2000 da marca contra os 7 matizes
   (BRIEFING §3.1) e trava com teste automatizado
   (`apps/pca/tests/test_paleta_contraste.py`).

**Onde a linha cai no código do template:** o `input.css` do template declara os tokens
neutros/marca/rampa e **um comentário-contrato** explicando o par `X`/`X-tx`, a
obrigação de manter a ponte `data-*` fora de `@layer`, e o piso de contraste. Os
*valores* de status de cada sistema vão para um arquivo separado que o derivado possui
(ver §Padrão 2 abaixo). Nenhum nome `st-*` aparece no template.

### 2. Tema escuro — mecanismo completo

Config (`/opt/web/pca/tailwind.config.js:7`):

```js
darkMode: ["selector", '[data-tema="escuro"]'],
```

Script de tema (`/opt/web/pca/core/templates/base.html:7-27`) — **síncrono, no `<head>`,
ANTES do `<link>` do CSS**:

```js
window.pcaAplicarTema = function (pref) {
  var guardado = pref === "auto" || pref === "claro" || pref === "escuro" ? pref : "auto";
  localStorage.setItem("pca-tema", guardado);
  var escuro = guardado === "escuro" ||
    (guardado === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.setAttribute("data-tema", escuro ? "escuro" : "claro");
  var meta = document.getElementById("pca-theme-cor");
  if (meta) meta.setAttribute("content", escuro ? "#0f0e0d" : "#003c71");
  document.dispatchEvent(new CustomEvent("pca:tema-alterado"));
};
window.pcaAplicarTema(localStorage.getItem("pca-tema") || "auto");
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
  if ((localStorage.getItem("pca-tema") || "auto") === "auto") window.pcaAplicarTema("auto");
});
```

Controle de 3 estados no rodapé da aside (`/opt/web/pca/core/templates/core/shell.html:123-136`),
`role="group" aria-label="Tema"`, três `<button>` com `:aria-pressed` do Alpine e
`:class="tema === 'X' ? 'bg-brand-tint text-brand-ink' : ''"`. O `x-data` do shell do PCA
carrega `tema: localStorage.getItem('pca-tema') || 'auto'` (`shell.html:48`).

Persistência: **`localStorage`, nunca cookie**. Razão registrada em 10-UI-SPEC §8: o
service worker cacheia HTML e uma página vinda do cache voltaria com o tema da última
gravação. O template tem SW próprio (`core/views.py:198-263`) que **não** cacheia HTML —
mas a decisão continua correta e é a mais simples.

`<meta name="theme-color">` acompanha o tema pelo mesmo script (`#003c71` claro /
`#0f0e0d` escuro no PCA). O `theme_color` do **manifest** NÃO muda (D-161) — no template
é `core/views.py:172` e está travado por `core/tests/test_pwa.py:40`.

**Adaptação obrigatória no template:** o prefixo `pca` some. Recomendação de nomes
neutros: chave de `localStorage` `"tema"`, função global `aplicarTema`, evento
`"tema:alterado"`, id do meta `"meta-theme-cor"`. Ponto de inserção: `core/templates/base.html`,
**entre a linha 5 (`<meta name=viewport>`) e a linha 8 (`<link rel=stylesheet>`)**.

### 3. Superfícies, elevação, raio, tipografia, fonte, focus-ring

**Elevação — 3 níveis** (10-UI-SPEC §3, linhas 114-133):

| Nível | Consumidores | Claro | Escuro |
|---|---|---|---|
| Base | barra de filtros, cabeçalho de tabela, `<aside>` | `bg-surface` + `border border-grid`, **sem sombra** | igual |
| Elevado | cards de dashboard, detalhe | `bg-surface` + `border border-grid` + `shadow-sm` | `dark:bg-surface-2` + border, **sombra removida** |
| Flutuante | modais, dropdown | `bg-surface` + `shadow-lg` | `dark:bg-surface-3` + sombra residual |

Invariante vinculante (D-105/D-152): *no escuro, elevação é luminosidade, não sombra*.
Exemplo real do PCA (`core/templates/core/shell.html:186`):
`class="… bg-surface border border-grid shadow-lg … dark:bg-surface-3 dark:shadow-md"`.

**Raio** (`/opt/web/pca/tailwind.config.js:113-120`) — 6 chaves colapsadas em 2px:

```js
borderRadius: { DEFAULT: "2px", sm: "2px", md: "2px", lg: "2px", xl: "2px", "2xl": "2px" }
```

`none` **não** é declarada (herda 0px do core do Tailwind — é o que preserva
`rounded-none`); `full` **não** é declarada (vocabulário de pílula).

*Impacto real no template, medido:* `rounded-sm` aparece **38×** e já vale 0,125rem = 2px
no Tailwind v3 → **nada muda**. `rounded` (DEFAULT) aparece **4×** e vai de 4px para 2px.
`rounded-full` aparece **2×** e não é tocado. Impacto visual: mínimo.

**Tipografia** (`/opt/web/pca/tailwind.config.js:126-133`) — 6 degraus, teto em 20px:

```js
fontSize: {
  xs:   ["11px", { lineHeight: "1.4" }],
  sm:   ["12px", { lineHeight: "1.4" }],
  base: ["13px", { lineHeight: "1.5" }],
  md:   ["14px", { lineHeight: "1.5" }],   // chave NOVA — não existe no Tailwind
  lg:   ["16px", { lineHeight: "1.4" }],
  xl:   ["20px", { lineHeight: "1.3" }],
}
```

*Impacto real no template, medido:* `text-xs` 44×, `text-sm` 18×, `text-base` 9×,
`text-2xl` **6×**, `text-xl` 2×. Adotar a régua **encolhe o sistema inteiro**:
`base` 16px→13px, `sm` 14px→12px, `xs` 12px→11px. E `text-2xl` **não é declarada** —
continua 24px nativo, **furando o teto de 20px** em 6 lugares
(`apps/…/exemplo/templates/exemplo/dashboard.html:12,38,45,52,59` e mais 1). Precisam
virar `text-xl`. Isto é uma mudança visual grande — o `ui_safety_gate: true` do
`config.json` sugere checkpoint humano de inspeção.

**Fonte** (`/opt/web/pca/tailwind.config.js:134-136`):

```js
fontFamily: { sans: ["system-ui", "-apple-system", '"Segoe UI"', "sans-serif"] }
```

`core/templates/base.html:27` do template já aplica `font-sans` no `<body>`; hoje resolve
para a pilha default do Tailwind. Declarar a pilha é 3 linhas, sem risco.

**Espaçamento**: o PCA **não declara** bloco `spacing` (13-UI-SPEC §1.3) — a escala
nativa cobre 4/8/12/16/24/32px. **Não replicar nada aqui.**

**Focus-ring** (`/opt/web/pca/core/static/src/input.css:16-21`) — regra única:

```css
@layer base {
  :focus-visible {
    outline: 2px solid theme("colors.brand");
    outline-offset: 2px;
  }
}
```

Já existe **verbatim** no `/opt/web/dividaativa/core/static/src/input.css:8-13` — o
derivado o implementou à mão numa quick task, o que confirma o valor e antecipa o
conflito de update (Pitfall 16).

### 4. Classes de componente e `safelist`

Fonte (`/opt/web/pca/core/static/src/input.css:38-103`) — este é o estado **atual e
vivo**, que já incorporou a Fase 14 e **diverge** do que o `13-UI-SPEC.md §1.5` publicou
como "as-built". Use o arquivo, não o spec:

```css
@layer components {
  .results  { @apply bg-surface border border-grid rounded overflow-x-auto; }
  .module   { @apply bg-surface border border-grid rounded p-4; }
  .form-row { @apply mt-0.5 w-full rounded-[6px] border border-grid bg-page px-2 py-1 text-base
                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset
                     focus-visible:ring-brand focus-visible:border-brand; }
  .btn      { @apply rounded-none px-3 py-1 text-[13px] font-semibold; }
  .btn--primaria   { @apply bg-brand text-white hover:bg-brand-hover; }
  .btn--secundaria { @apply border border-brand text-brand hover:bg-brand-tint; }
  .btn--neutro     { @apply border border-grid text-ink-2 hover:bg-surface-2; }
  .btn--destrutiva { @apply border border-destructive text-destructive; }
}
```

> **Divergência documentada entre as duas fontes do PCA.** `13-UI-SPEC.md §1.5` publica
> `.form-row` com `rounded-none`, `border-muted` e `text-[13px]`; o `input.css` real usa
> `rounded-[6px]`, `border-grid`, `text-base` e acrescenta
> `focus-visible:border-brand`. O `input.css` é posterior (Fase 14 / Plano 14-13, WR-06)
> e é a verdade. O comentário no próprio arquivo (linhas 57-65) explica: `.form-row`
> **diverge deliberadamente** do anel único do `@layer base`, só para este componente,
> por WCAG 2.2 SC 2.4.11.

`safelist` (`/opt/web/pca/tailwind.config.js:24`):

```js
safelist: ["results", "module", "form-row", "btn"],
```

**Motivo verificado empiricamente nesta sessão:** o JIT poda regra de `@layer` cujo
seletor não aparece no conteúdo varrido. As 4 variações `.btn--*` **não estão no
safelist do PCA** — elas só sobrevivem quando um template as usa literalmente. Se o
template do Sistema Base declarar as variações sem nenhum consumidor, elas somem em
silêncio. **Recomendação: `safelist: ["results","module","form-row","btn","btn--primaria","btn--secundaria","btn--neutro","btn--destrutiva"]`** — 4 strings a mais, zero
risco, e torna o contrato auditável (é o que o próprio comentário do PCA diz que queria).

### 5. Paleta de gráfico — como o PCA serve e como o ECharts consome

**Servidor** (`/opt/web/pca/apps/pca/paleta.py:45-56`) — só dado semântico:

```python
PALETA_GRAFICOS = {
    "rampa_uo": ["#003c71", "#577ea1", "#9eb5c9"],
    "serie_planejado": "#9eb5c9",
    "serie_contratado": "#003c71",
    "serie_concluido": "#008300",
}
```

**Template** (`/opt/web/pca/apps/pca/templates/pca/dashboard.html:18`), **fora** do alvo
dos swaps HTMX de propósito (`views.py:851-853`):

```django
{{ paleta_graficos|json_script:"paleta-graficos" }}
```

**Cliente** (`dashboard.html:44-58`) — chrome lido em runtime, nunca do servidor:

```js
var PALETA = JSON.parse(document.getElementById("paleta-graficos").textContent);

function lerVarCss(nome) {
  return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
}
function aplicarChromeNaPaleta() {
  PALETA.chrome_borda   = lerVarCss("--cor-surface");
  PALETA.tooltip_fundo  = lerVarCss("--cor-surface");
  PALETA.chrome_grid    = lerVarCss("--cor-grid");
  PALETA.tooltip_borda  = lerVarCss("--cor-grid");
  PALETA.chrome_eixo    = lerVarCss("--cor-ink-2");
  PALETA.tooltip_texto  = lerVarCss("--cor-ink");
}
aplicarChromeNaPaleta();
```

**Reaplicação na troca de tema, sem reload** (`dashboard.html:353-356`):

```js
document.addEventListener("pca:tema-alterado", function () {
  aplicarChromeNaPaleta();
  montarGraficos(document);   // reconstrói as instâncias ECharts vivas
});
```

#### O que exatamente muda no app exemplo do template

`apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html`
tem **14 hex literais em JavaScript**, nas linhas:

| Linha | Literal | Papel | Vira |
|---|---|---|---|
| 107 | `"#0284c7","#0d9488","#f59e0b","#6366f1","#8b5cf6"` (5) | paleta do donut | vem do servidor |
| 118 | `#fcfcfb` | `tooltip.backgroundColor` (barras) | `lerVarCss("--cor-surface")` |
| 119 | `#e4e2dd` | `tooltip.borderColor` | `lerVarCss("--cor-grid")` |
| 121 | `#0b0b0b` | `tooltip.textStyle.color` | `lerVarCss("--cor-ink")` |
| 133 | `#e4e2dd` | `xAxis.axisLine` | `lerVarCss("--cor-grid")` |
| 134 | `#52514e` | `xAxis.axisLabel` | `lerVarCss("--cor-ink-2")` |
| 138 | `#f3f2ef` | `yAxis.splitLine` | `lerVarCss("--cor-surface-2")` |
| 140 | `#52514e` | `yAxis.axisLabel` | `lerVarCss("--cor-ink-2")` |
| 173 | `#fcfcfb` | `tooltip.backgroundColor` (donut) | `lerVarCss("--cor-surface")` |
| 174 | `#e4e2dd` | `tooltip.borderColor` | `lerVarCss("--cor-grid")` |
| 176 | `#0b0b0b` | `tooltip.textStyle.color` | `lerVarCss("--cor-ink")` |
| 182 | `#52514e` | `legend.textStyle` | `lerVarCss("--cor-ink-2")` |
| 189 | `#fcfcfb` | `series.itemStyle.borderColor` | `lerVarCss("--cor-surface")` |

Além disso, **linha 106**: `const corBrand = "{{ cor_primaria }}";` — não é hex literal,
mas é a marca vindo por interpolação de template. Vira `lerVarCss("--cor-brand")` (que
respeita o tema escuro; `{{ cor_primaria }}` não respeitaria).

E **linha 153**: `itemStyle: { color: corBrand, borderRadius: [2, 2, 0, 0] }` — o
`borderRadius` de 2px do ECharts já coincide com o raio institucional; manter.

O donut precisa de uma paleta categórica. **Decisão necessária (sem precedente direto no
PCA — a rosca dele usa cor de status por item, e status é domínio):** o app exemplo tem 3
valores de `StatusChoices`. **Recomendação:** servir a rampa sequencial derivada da marca
(`["#seq-600","#seq-450","#seq-300"]`) via `json_script`, calculada no `views.py` a
partir do mesmo `core/tema.py` — assim a paleta do donut respeita `cor_primaria`, não
inventa 5 hex arbitrários, e o modo escuro funciona por reconstrução do gráfico. Custo:
o donut fica monocromático. Alternativa: manter categórico com 3 matizes CVD-safe fixos
(verdes/azul/cinza), o que reintroduz hex fixos — mas em **Python**, não em JS, o que já
satisfaz o critério 3 ("nenhum hex sobra em template ou em JS de template").

### 6. Encaixe da navegação

#### Estado atual dos dois lados

- **Template:** `core/templates/core/_nav.html.jinja` — 66 linhas, das quais **3 itens
  de ~11 linhas cada** repetindo a mesma string de classes. Usa `{% raw %}` /
  `{% endraw %}` **três vezes** (linhas 1/34, 36/62, 64/66) para proteger a sintaxe
  Django do Jinja do Copier, com `{% if incluir_app_exemplo %}` (Jinja) no meio.
  Incluído por `core/templates/core/shell.html:73`.
- **PCA:** `core/templates/core/_nav_visoes.html` — 67 linhas, **4 itens de ~12 linhas**,
  mesma duplicação, **sem** inclusion tag. **O PCA não tem o que herdar aqui.**
- **DividaAtiva** (`/opt/web/dividaativa/core/templates/core/_nav.html`): apagou "Início"
  e colou os itens do domínio dentro do arquivo upstream — confirmado lendo o arquivo.

O tratamento visual do item ativo é **idêntico** nos dois repositórios, e é o contrato a
preservar:

```
ativo:   aria-current="page"  +  bg-brand-tint text-brand-ink
         +  <span class="absolute inset-y-0 left-0 w-[2px] bg-brand" aria-hidden="true">
inativo: text-ink-2 hover:bg-surface-2
comum:   relative flex items-center gap-3 rounded-sm px-3 py-2 text-base font-semibold
         @click="sidebarAberta = false"   (depende do x-data do shell.html)
ícone:   <svg width=18 height=18 class="w-[18px] h-[18px] flex-none" viewBox="0 0 24 24"
              fill=none stroke=currentColor stroke-width=2 aria-hidden=true>
```

#### Resolução de template no derivado — o dado que decide o desenho

`config/settings/base.py.jinja:107-122`:

```python
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "core" / "templates"],
    "APP_DIRS": True,
    ...
}]
```

**Implicação crítica:** `DIRS` aponta para **o mesmo diretório** que o `APP_DIRS` do app
`core` já expõe. Não existe "diretório do projeto" separado onde o derivado possa colocar
uma versão sua que vença a do template — os dois caminhos resolvem para o mesmo arquivo
físico. Logo **não há mecanismo de "override" de template neste projeto**: o derivado
*possui* a árvore inteira. O que precisa existir é um **arquivo de propriedade do
derivado por contrato**, e a garantia de que o `copier update` nunca o toca.

Isso muda o desenho de "override" para "arquivo-stub protegido". A proteção existe e foi
**provada nesta sessão** (ver §Padrão 3): `_skip_if_exists`.

#### `inclusion_tag` — mecânica neste repositório

`core/templatetags/` **já existe** (`__init__.py` + `formatos.py`), `core` está em
`INSTALLED_APPS` como `core.apps.CoreConfig` (`base.py.jinja:25`), e
`django.template.context_processors.request` está ativo (`base.py.jinja:114`) — que é o
que dá `request.path` para o estado ativo. O app exemplo **não tem** `templatetags/`;
`{% load static formatos %}` nos templates dele resolve para o `core`.

[CITED: docs.djangoproject.com/en/5.2/howto/custom-template-tags/] `takes_context=True`
exige que o primeiro parâmetro se chame literalmente `context`; módulos de tag só são
descobertos em `<app>/templatetags/` de app instalado; **`{% load %}` é obrigatório em
cada template** que usa a tag.

[CITED: docs.djangoproject.com/en/5.2/ref/templates/builtins/] `{% url 'nome' as var %}`
**não levanta `NoReverseMatch`** quando a rota não existe — a documentação apresenta isso
literalmente como o padrão "para linkar views opcionais". É este comportamento que
permite que os itens do app exemplo desapareçam sozinhos quando o app é removido.

### 7. Superfície Copier

`copier.yml` atual: 8 perguntas (`sistema_nome`, `sistema_slug`, `sistema_hostname`,
`sistema_porta`, `sistema_banco`, `sistema_sigla`, `cor_primaria`, `incluir_app_exemplo`),
`_templates_suffix: .jinja`, `_envops.undefined: StrictUndefined`, `_exclude` com 30
entradas, e **nenhum `_skip_if_exists`**.

`cor_primaria` hoje: `type: str`, default `#1e40af`, validator `^#[0-9a-fA-F]{6}$`.
Consumida por Jinja **uma única vez**, em `tailwind.config.js.jinja:6`
(`const COR_PRIMARIA = "{{ cor_primaria }}";`) e por `.env.example.jinja:32`
(`COR_PRIMARIA={{ cor_primaria }}`).

**Decisão recomendada sobre novas perguntas:** *nenhuma*. Raio, régua tipográfica e
fonte são **padrão do template**, não pergunta. Motivos:

1. O ROADMAP as chama de "decisões" do padrão CFC — variar por sistema quebraria a
   coerência da família, que é o valor central da fase.
2. Cada pergunta nova é uma resposta a mais que todo derivado tem que gerenciar em
   `copier update`, para zero benefício provado.
3. O critério 4 exige apenas que *o derivado não precise editar `tailwind.config.js`* —
   e isso se resolve fazendo o `tailwind.config.js` **deixar de ter Jinja** (ver Padrão
   1), não criando perguntas.

**Consequência de projeto que vale ouro:** se `cor_primaria` sair do
`tailwind.config.js`, o arquivo deixa de precisar do sufixo `.jinja` e passa a ser
copiado verbatim. Arquivo verbatim que o derivado nunca edita = **zero conflito** em todo
`copier update`, para sempre.

### 8. Release

- `git tag -l` → **`v0.1.0`** apenas. `git rev-list v0.1.0..HEAD --count` → **39** (o
  ROADMAP diz 37; a Fase 7 já acrescentou 2 commits de documentação).
- README.md:388-392 documenta que **o Copier lê a última tag (PEP 440), nunca o HEAD**.
- Procedimento documentado (README.md:374-387): árvore limpa + regressão verde →
  `git tag -a v0.2.0 -m "..."`.
- **Nada em `copier.yml` nem em CI depende da tag** — não há workflow de CI neste
  repositório (`.github/` não existe). A tag é lida exclusivamente pelo Copier em tempo
  de `copy`/`update`.
- `.copier-answers.yml` do DividaAtiva confirma `_commit: v0.1.0` — ele está preso na
  tag antiga, como o ROADMAP descreve.

### 9. Superfície de verificação

**Testes Django — o número 77 confere:**

| Suíte | Métodos `def test_` |
|---|---|
| `core/tests/test_admin.py` | 6 |
| `core/tests/test_auditoria.py` | 4 |
| `core/tests/test_identidade.py` | 3 |
| `core/tests/test_logos.py` | 5 |
| `core/tests/test_shell.py` | 6 |
| `core/tests/test_auth.py` | 3 |
| `core/tests/test_login_flow.py` | 14 |
| `core/tests/test_pwa.py` | 10 |
| `core/tests/test_templates.py` | 3 |
| **subtotal `core`** | **54** |
| `apps/exemplo/tests/test_crud.py` | 11 |
| `apps/exemplo/tests/test_isolamento.py` | 2 |
| `apps/exemplo/tests/test_dashboard.py` | 5 |
| `apps/exemplo/tests/test_models.py` | 5 |
| **subtotal exemplo** | **23** |
| **TOTAL** | **77** ✔ |

Comando real (`.template-tests/test_05_nascimento.sh:197`), **dentro do container**:

```bash
docker compose exec -T web python manage.py test core apps.exemplo --noinput
```

**As 11 suítes de `.template-tests/` — a conta também confere:** 8 classes `unittest` em
7 arquivos `.py` + 3 scripts `.sh`.

| Arquivo | Classes | Usa `--vcs-ref=HEAD`? |
|---|---|---|
| `test_04_03_identity.py` | 1 | **NÃO** ⚠ |
| `test_04_04_optional_exemplo.py` | 1 | **NÃO** ⚠ |
| `test_04_05_backup.py` | 1 | sim (l. 25) |
| `test_04_06_operations.py` | 1 | **NÃO** ⚠ |
| `test_04_07_collectstatic.py` | 1 | não invoca copier |
| `test_06_persistencia.py` | 2 | sim (l. 33) |
| `test_quick_comentarios_template.py` | 1 | não invoca copier |
| `test_copier_copy.sh` | — | **NÃO** ⚠ |
| `test_copier_update.sh` | — | tags temporárias próprias |
| `test_05_nascimento.sh` | — | sim (l. 132) |

Ver Pitfall 17 — isto é um bug ativo que sabota qualquer teste de contrato novo.

**Ensaio A→B→C** (`.template-tests/test_copier_update.sh`): clona o template para
`$TMP/template`, cria a tag `v0.1.0` local, faz `copier copy --vcs-ref v0.1.0`, commita
o destino (estado A); acrescenta uma linha em `core/README.md` do clone, tageia `v0.1.1`,
roda `copier update --data incluir_app_exemplo=false --vcs-ref v0.1.1` (estado B);
repete para `v0.1.2` (estado C). Em cada passo chama `exigir_sem_exemplo` e
`assert_no_conflict_markers`. **É a base pronta para o critério 7** — só precisa de um
passo novo que simule o derivado editando `_nav_dominio.html` antes do update.

`exigir_sem_exemplo` (linhas 43-51) contém `grep -Fq 'exemplo:' "${DESTINO}/core/templates/core/_nav.html"` — **vai quebrar** quando os itens saírem do `_nav.html`.

---

## Stack Padrão

**Esta fase não introduz nenhuma dependência nova.** Toda a mecânica usa o que já está
instalado e travado.

### Núcleo (já presente)

| Ferramenta | Versão em uso | Onde | Papel na fase |
|---|---|---|---|
| Tailwind CSS | **3.4.17** | `Dockerfile:15` (`npx --yes tailwindcss@3.4.17`) | `darkMode` seletor, `var(--cor-*)`, `safelist`, `@layer` |
| Django | 5.2 | `requirements.txt` | `inclusion_tag`, `json_script`, context processor |
| ECharts | vendorizado | `core/static/vendor/echarts.min.js` | gráficos do app exemplo |
| Alpine.js | vendorizado | `core/static/vendor/alpine.min.js` | controle de tema de 3 estados |
| Copier | **9.17.1** | `.venv-template/bin/copier` | `_skip_if_exists`, `copier update` |
| WhiteNoise | `CompressedManifestStaticFilesStorage` | `base.py.jinja:175` | hash no nome do CSS |

### Auditoria de Legitimidade de Pacote

**Não aplicável — a fase não instala nada.** Nenhum `npm install`, `pip install` ou
`cargo add` é necessário. `tailwindcss@3.4.17` já é invocado por `npx --yes` com versão
travada no `Dockerfile:15` e não muda nesta fase; `copier==9.17.1` já passou pelo gate
humano de procedência da Fase 4 (Plano 04-01).

| Pacote | Registro | Disposição |
|---|---|---|
| *(nenhum novo)* | — | — |

**Pacotes removidos por veredito `[SLOP]`:** nenhum.
**Pacotes marcados `[SUS]`:** nenhum.

### Alternativas consideradas e descartadas

| Em vez de | Poderia usar | Trade-off | Veredito |
|---|---|---|---|
| Hex plano nas variáveis | `color-mix(in srgb, …)` para derivar a marca em CSS | Reproduz `misturar()` **exatamente** (é a mesma mistura sRGB) e elimina toda matemática de cor do build. **Mas** `getComputedStyle().getPropertyValue()` devolveria a string `color-mix(...)` ao ECharts, e o regex `--cor-(\w+):\s*(#[0-9a-fA-F]{6})` dos testes de contraste não veria a cor | **Descartar para tokens lidos por JS ou por teste.** Aceitável só para tokens puramente visuais |
| Hex plano | `@property { syntax: "<color>" }` registrando as variáveis | Resolve o problema acima (o valor computado passa a ser cor resolvida) mas é Baseline "newly available" (Firefox só em 128/jul-2024) | Descartar — ganho nulo sobre hex plano |
| Derivação em Python | Derivação em Jinja no `input.css.jinja` | Tira o Python do caminho, mas transforma `input.css` em arquivo `.jinja` — e é justamente o arquivo que o derivado mais vai querer editar (tokens de status próprios) → conflito garantido em todo update | Descartar |
| Derivação em Python | Manter `misturar()` no `tailwind.config.js.jinja` | Não consegue expressar o par escuro (que é HSL, não mistura sRGB) e mantém Jinja num arquivo que o derivado talvez precise tocar | Descartar |
| `{% item_nav %}` como `inclusion_tag` | `simple_tag` devolvendo `mark_safe(...)` | Junta markup e Python no mesmo arquivo; perde o template auditável | Descartar |

---

## Padrões de Arquitetura

### Diagrama do sistema

```
┌─ COPY-TIME (copier copy, uma vez por sistema) ──────────────────────────┐
│                                                                         │
│  copier.yml: cor_primaria ──┬──► .env.example.jinja  (COR_PRIMARIA=…)   │
│                             └──► _nav_dominio.html.jinja  (semeia os     │
│                                  itens do exemplo se incluir=true)      │
│                                  [_skip_if_exists → update nunca toca]  │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
┌─ BUILD-TIME (docker build, estágio `assets`) ──────────────────────────┐
│                                                                         │
│  core/static/src/input.css  ──┐                                         │
│    :root { --cor-page … }     │   tailwind.config.js                    │
│    [data-tema=escuro] { … }   ├──► colors: { page: "var(--cor-page)" }  │
│    @layer base { :focus-… }   │    darkMode: ["selector",'[data-tema…]']│
│    @layer components {…}      │    safelist / borderRadius / fontSize   │
│  core/static/src/dominio.css ─┘         │                               │
│    (stub do derivado, @import 1ª linha) │                               │
│                                          ▼                              │
│                     tailwindcss CLI 3.4.17 ──► dist/tailwind.css        │
│                     (JIT varre core/templates/** e apps/**)             │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
┌─ RUNTIME — servidor (cada request) ────────────────────────────────────┐
│                                                                         │
│  .env COR_PRIMARIA ──► settings.COR_PRIMARIA (validado #RRGGBB no boot) │
│         │                                                               │
│         ├──► core/tema.py: deriva brand/hover/ink/tint  (claro+escuro)  │
│         │       └──► context_processors.identidade → tema_css           │
│         │              └──► base.html: <style> :root{--cor-brand:…}     │
│         │                            [data-tema=escuro]{--cor-brand:…}  │
│         ├──► core/admin_site.py: admin_tema_css (já existe)             │
│         ├──► core/views.py:172  manifest theme_color (NÃO muda c/ tema) │
│         └──► exemplo/views.py: paleta_graficos (rampa derivada)         │
│                     └──► dashboard.html: {{ …|json_script:"paleta" }}   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
┌─ RUNTIME — cliente ────────────────────────────────────────────────────┐
│                                                                         │
│  <head> script SÍNCRONO (antes do <link>)                               │
│     localStorage["tema"] ──► html[data-tema="claro"|"escuro"]           │
│     ──► atualiza <meta name=theme-color>                                │
│     ──► dispara CustomEvent("tema:alterado")                            │
│                       │                                                 │
│  botões Alpine (rodapé da aside) ──► aplicarTema('auto'|'claro'|'escuro')│
│                       │                                                 │
│                       ▼                                                 │
│  dashboard.js:  document.addEventListener("tema:alterado", …)           │
│      lerVarCss("--cor-surface"|"--cor-grid"|"--cor-ink"|"--cor-ink-2")  │
│      + JSON.parse(#paleta-graficos)  ──► echarts.setOption(…)           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Estrutura de arquivos recomendada

```
core/
├── static/src/
│   ├── input.css              # ★ REESCRITO — fonte física dos tokens (upstream)
│   └── dominio.css            # ★ NOVO stub — tokens do derivado (_skip_if_exists)
├── templates/core/
│   ├── _nav.html              # ★ VIRA .html (sem .jinja) — 100% upstream, estático
│   ├── _nav_dominio.html.jinja# ★ NOVO stub — 100% do derivado (_skip_if_exists)
│   └── _item_nav.html         # ★ NOVO — as 12 linhas, uma vez só
├── templatetags/
│   ├── formatos.py            # existente
│   └── navegacao.py           # ★ NOVO — {% item_nav %} + dicionário de ícones
├── tema.py                    # ★ NOVO — derivação da família de marca
├── context_processors.py      # + tema_css
└── templates/base.html        # + script de tema, + <style> tema_css, meta dinâmico

apps/{% if incluir_app_exemplo %}exemplo{% endif %}/
├── templates/exemplo/dashboard.html   # ★ 14 hex removidos, chrome por getComputedStyle
└── views.py                            # + paleta_graficos no contexto

tailwind.config.js             # ★ DEIXA de ser .jinja — verbatim, zero conflito
copier.yml                     # + _skip_if_exists
```

### Padrão 1 — Tokens em CSS, `cor_primaria` derivada em Python

**O quê:** `input.css` declara todos os tokens com **hex plano**, incluindo um valor de
*fallback* para a família de marca. O servidor sobrescreve só a família de marca a partir
do `.env`, num `<style>` colocado **depois** do `<link>` do CSS (para vencer por ordem de
declaração — `:root` e `[data-tema="escuro"]` têm a mesma especificidade).

**Quando usar:** é a rota recomendada. Satisfaz o critério 3 (a fonte física dos valores
é `input.css` — inclusive os de marca, na forma de default), o critério 4
(`tailwind.config.js` perde o Jinja e nunca precisa ser editado) e corrige um bug de
documentação (ver Pitfall 18).

```python
# core/tema.py  — NOVO
"""Derivação da família de marca a partir de COR_PRIMARIA.

Espelha o precedente de `core/admin_site.py:each_context` (D-14): o valor é
seguro para interpolação em CSS porque `config/settings/base.py` valida
COR_PRIMARIA contra `#[0-9a-fA-F]{6}` no boot e levanta ImproperlyConfigured.
"""
import colorsys


def _canais(hex_: str) -> tuple[int, int, int]:
    n = int(hex_[1:], 16)
    return (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF


def _hex(r: int, g: int, b: int) -> str:
    return "#%02x%02x%02x" % (round(r), round(g), round(b))


def misturar(hex_: str, alvo: int, fator: float) -> str:
    """Mistura sRGB idêntica à `misturar()` do tailwind.config.js (D-17)."""
    return _hex(*(c + (alvo - c) * fator for c in _canais(hex_)))


def com_luminancia(hex_: str, luz: float) -> str:
    """Preserva matiz e saturação HSL; troca só a luminosidade (0..1)."""
    r, g, b = (c / 255 for c in _canais(hex_))
    matiz, _, sat = colorsys.rgb_to_hls(r, g, b)
    return _hex(*(c * 255 for c in colorsys.hls_to_rgb(matiz, luz, sat)))


def familia_marca(cor: str) -> dict[str, str]:
    escuro = com_luminancia(cor, 0.727)
    return {
        # claro — fatores medidos contra o padrão de referência
        "brand": cor,
        "brand-hover": misturar(cor, 255, 0.12),
        "brand-ink": misturar(cor, 0, 0.18),
        "brand-tint": misturar(cor, 255, 0.92),
        "seq-600": cor,
        "seq-450": misturar(cor, 255, 0.34),
        "seq-300": misturar(cor, 255, 0.62),
        # escuro — matiz e saturação preservados, só a luminosidade muda
        "brand:escuro": escuro,
        "brand-hover:escuro": com_luminancia(cor, 0.827),
        "brand-ink:escuro": com_luminancia(cor, 0.627),
        "brand-tint:escuro": com_luminancia(cor, 0.153),
        "seq-600:escuro": escuro,
        "seq-450:escuro": com_luminancia(cor, 0.567),
        "seq-300:escuro": com_luminancia(cor, 0.427),
    }
```

**Teste de aceitação pronto** (`SimpleTestCase`, sem banco, sem build):
`familia_marca("#003c71")` **tem que devolver** `brand-hover == "#1f5382"`,
`brand-ink == "#00315d"`, `brand-tint == "#ebeff4"`, `seq-450 == "#577ea1"`,
`seq-300 == "#9eb5c9"` e `brand:escuro == "#74beff"` — todos verificados nesta sessão
contra o `input.css` real do padrão.

### Padrão 2 — `dominio.css`: o derivado declara os próprios status

**O quê:** `input.css` abre com `@import "./dominio.css";` e o template envia um
`dominio.css` stub, com comentário-contrato explicando o par `X`/`X-tx` e a ponte
`data-*` fora de `@layer`.

**VERIFICADO empiricamente nesta sessão** (Tailwind 3.4.17): o `@import` é resolvido pelo
`postcss-import` embutido no CLI e o conteúdo é inlinado — **mas apenas se for a primeira
declaração do arquivo**. Colocado depois de `@tailwind base`, foi **descartado em
silêncio**. Arquivo ausente → o build **falha com erro** (bom: falha ruidosa).

```css
/* core/static/src/input.css — PRIMEIRA linha, obrigatoriamente */
@import "./dominio.css";
@tailwind base;
@tailwind components;
@tailwind utilities;
```

```css
/* core/static/src/dominio.css — stub enviado uma vez; o sistema é dono deste arquivo.
   Contrato dos tokens de estado (não os copie de outro sistema — eles são
   vocabulário de domínio):

   1. Cada estado tem um PAR:  --cor-<estado>      (o matiz: preenchimento, dot)
                               --cor-<estado>-tx   (o par de TEXTO)
      No tema claro os dois podem coincidir. No escuro, só a variante `-tx` ganha
      par clareado — o matiz puro reprova contraste sobre a superfície escura.
   2. A ponte de dado para cor fica FORA de @layer:
        .status-dot[data-estado="x"] { background: theme("colors.st-x"); }
      Dentro de @layer o Tailwind podaria a regra (o valor de `data-*` só existe
      em runtime; o JIT não o vê no build).
   3. Piso de contraste: 4,5:1 para texto, 3:1 para elemento gráfico, nos DOIS temas.
      Valide os matizes para daltonismo antes de fixá-los.
*/
```

### Padrão 3 — Ponto de extensão de navegação livre de conflito

**PROVA EMPÍRICA executada nesta sessão** com o próprio Copier 9.17.1 do repositório
(template descartável, `v1` → `v2`, derivado reescreve o stub, upstream reescreve o
`_nav.html`):

| Cenário | `_nav.html` upstream mudou? | Derivado editou o stub? | `_skip_if_exists` | Resultado |
|---|---|---|---|---|
| A | sim | sim | **sim** | upstream aplicado, stub do derivado **intacto**, **zero marcadores** |
| B | sim | sim | **não**, e a resposta virou `false` (stub renderizaria vazio) | **`<<<<<<< before updating`** dentro do stub |

Ou seja: `_skip_if_exists` é **obrigatório**, não opcional. Sem ele, o critério 5 e o
critério 7 falham no primeiro update em que a resposta `incluir_app_exemplo` mude.

```yaml
# copier.yml — adição mínima
_skip_if_exists:
  - core/templates/core/_nav_dominio.html
  - core/static/src/dominio.css
```

```django
{# core/templates/core/_nav.html — 100% upstream, sem Jinja, sem .jinja #}
{% load navegacao %}
{% comment %}
  Ponto de extensão da navegação.

  ESTE ARQUIVO É DO NÚCLEO. Não edite: toda edição aqui vira conflito no
  próximo `copier update`. Os itens do seu domínio vão em
  `core/templates/core/_nav_dominio.html`, que é seu e que o update nunca toca.
{% endcomment %}
<nav aria-label="Navegação principal" class="flex flex-col gap-1">
  {% item_nav "core:shell" "Início" "casa" %}
  {% include "core/_nav_dominio.html" %}
</nav>
```

```django
{# core/templates/core/_nav_dominio.html — SEU arquivo. O núcleo nunca o reescreve.
   Uma linha por item:  {% item_nav "app:rota" "Rótulo" "icone" "prefixo-opcional" %}
   `prefixo` marca o item ativo também nas rotas-filhas (ex.: "/clientes/").
   Se a rota não existir, o item simplesmente não aparece — sem erro. #}
{% load navegacao %}
{% item_nav "exemplo:dashboard" "Dashboard" "grafico" %}
{% item_nav "exemplo:item_listar" "Itens (CRUD)" "lista" "/exemplo/" %}
```

```python
# core/templatetags/navegacao.py
from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

register = template.Library()

# Ícones por nome — o markup interno do <svg> 24×24, stroke currentColor.
# Um nome desconhecido renderiza o item sem ícone (nunca quebra a página).
ICONES = {
    "casa": mark_safe('<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>'),
    "grafico": mark_safe('<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>'),
    "lista": mark_safe('<rect width="18" height="18" x="3" y="3" rx="2"/><path d="m9 12 2 2 4-4"/>'),
}


@register.inclusion_tag("core/_item_nav.html", takes_context=True)
def item_nav(context, rota, rotulo, icone="", prefixo=""):
    """Um item da navegação principal, com o estado ativo por construção.

    `rota` é o NOME da rota (`app:nome`), não a URL. Se ela não puder ser
    revertida — porque o app foi removido pelo `copier update` — o item some em
    silêncio, sem NoReverseMatch. É o mesmo contrato documentado do
    `{% url 'x' as var %}` do Django, aplicado do lado Python.
    """
    try:
        url = reverse(rota)
    except NoReverseMatch:
        return {"url": ""}
    caminho = context["request"].path
    ativo = caminho == url or (prefixo and caminho.startswith(prefixo))
    return {"url": url, "rotulo": rotulo, "icone": ICONES.get(icone, ""), "ativo": ativo}
```

```django
{# core/templates/core/_item_nav.html — as 12 linhas, uma vez só #}
{% if url %}
<a href="{{ url }}"
   @click="sidebarAberta = false"
   {% if ativo %}aria-current="page"{% endif %}
   class="relative flex items-center gap-3 rounded-sm px-3 py-2 text-base font-semibold {% if ativo %}bg-brand-tint text-brand-ink{% else %}text-ink-2 hover:bg-surface-2{% endif %}">
  {% if ativo %}<span class="absolute inset-y-0 left-0 w-[2px] bg-brand" aria-hidden="true"></span>{% endif %}
  {% if icone %}<svg width="18" height="18" class="w-[18px] h-[18px] flex-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">{{ icone }}</svg>{% endif %}
  <span>{{ rotulo }}</span>
</a>
{% endif %}
```

### Antipadrões a evitar

- **Construir string de classe em JS e injetar no DOM.** O JIT varre o conteúdo em
  build-time; classe concatenada em runtime nunca existe no CSS. Armadilha registrada
  literalmente em `/opt/web/pca/core/static/src/input.css:76-79`.
- **Declarar regra de `data-*` dentro de `@layer components`.** O Tailwind poda o que
  não encontra nos templates. O PCA deixa essas regras soltas e documenta o motivo em 5
  blocos diferentes.
- **Cookie + atributo renderizado pelo servidor para o tema.** Rejeitado no 10-UI-SPEC §8.
- **Modificador de opacidade sobre token que virou `var()`** — ver Pitfall 1, a classe
  simplesmente deixa de existir.
- **Registry dinâmico de menu.** O contrato do `_nav.html` (linha 5-7 do atual) diz
  explicitamente: "Não existe registry dinâmico de menu por decisão". Manter.
- **Copiar os 7 pares de status do PCA.** Domínio dele; e os nomes `st-em-tramitacao`,
  `st-aguardando-dfd` são vocabulário de processo administrativo.

---

## Não Reinvente

| Problema | Não construa | Use | Por quê |
|---|---|---|---|
| Item de menu opcional que some com o app | `{% if %}` de Copier dentro do `_nav.html` | `reverse()` em `try/except NoReverseMatch` na inclusion tag | É o padrão documentado do Django para "views opcionais"; e tira o Jinja do arquivo upstream |
| Arquivo do derivado que o update não pode tocar | script pós-update, `.gitattributes merge=ours` | **`_skip_if_exists` do Copier** | Provado nesta sessão; 2 linhas de YAML |
| Mistura de cor sRGB | fórmula nova | a `misturar()` que já existe (portada para Python) | Reproduz o padrão **exatamente** — verificado em 5 valores |
| Par claro/escuro da marca | mistura com branco | HSL com matiz e saturação preservados (`colorsys` da stdlib) | É o que o padrão de referência faz; mistura com branco dessatura e muda o matiz |
| Cálculo de contraste WCAG para o teste | biblioteca nova | as ~20 linhas de `/opt/web/pca/apps/pca/tests/test_paleta_contraste.py:23-43` | `SimpleTestCase`, zero dependência, lê o `input.css` fonte |
| Cor de chrome do gráfico no tema escuro | dois dicionários no servidor | `getComputedStyle(document.documentElement).getPropertyValue("--cor-…")` | Um caminho só, reage à troca de tema sem reload |
| Serializar dado para JS | `{{ x|safe }}` ou `JSON.dumps` em view | `{{ x|json_script:"id" }}` (já usado em `dashboard.html:30-31`) | Escapa `<`, `>`, `&` — imune a XSS |
| Anel de foco | 31 declarações `focus-visible:ring-*` espalhadas | uma regra `:focus-visible` em `@layer base` | O padrão de referência já fez a consolidação |

**Insight central:** quase tudo aqui já existe, escrito e testado, a 40 caracteres de
caminho de distância. O trabalho da fase é **transportar com fidelidade e neutralizar o
domínio**, não projetar.

---

## Inventário de Estado em Runtime

Esta é uma fase de refatoração com renomeação implícita (`pca*` → neutro) e migração de
mecanismo. Categorias verificadas explicitamente:

| Categoria | O que foi encontrado | Ação necessária |
|---|---|---|
| **Dados armazenados** | **Nada.** Nenhum token de cor, nome de tema ou item de menu vive em banco. O `Usuario` e o `ItemExemplo` não têm campo de preferência visual. Verificado por leitura de `core/models.py` e das migrações 0001-0003. | nenhuma |
| **Estado no cliente (equivalente a config de serviço vivo)** | `localStorage` ganha a chave nova de tema. **Nenhum sistema derivado tem essa chave hoje** (o tema escuro não existe) — não há migração de dado, só código. **`localStorage["htmx-history-cache"]`** é apagado no logout por `limparCachePwa()` (`base.html:54-64`); a chave de tema **NÃO pode** entrar nessa limpeza (preferência visual não é dado de sessão). | edição de código; garantir que a chave de tema sobreviva ao logout |
| **Cache do Service Worker** | `CACHE_NAME = "static-v1"` (`core/views.py:215`), estratégia *cache-first* para `/static/`. **Não é problema:** `STORAGES.staticfiles` usa `whitenoise.storage.CompressedManifestStaticFilesStorage` (`base.py.jinja:175`) → o `tailwind.css` recompilado ganha **hash novo no nome**, logo URL nova, logo *cache miss*. Nenhum bump de `CACHE_NAME` é necessário. | nenhuma (confirmado por leitura do settings) |
| **Registro no SO** | **Nada.** O template não registra tarefa agendada, unit systemd nem processo pm2. `ops/` tem apenas scripts de backup invocados por Compose. | nenhuma |
| **Segredos e variáveis de ambiente** | `COR_PRIMARIA` **continua com o mesmo nome** e o mesmo validador `#RRGGBB` (`base.py.jinja:152-161`) — nenhum `.env` de derivado quebra. Se a rota recomendada for adotada, `COR_PRIMARIA` passa a ter efeito **real** sobre a paleta em runtime, o que hoje não acontece (ver Pitfall 18). | nenhuma renomeação; validar o comportamento novo |
| **Artefatos de build / pacotes instalados** | `core/static/dist/tailwind.css` está no `_exclude` do `copier.yml` — **não existe** na árvore gerada; é produzido no estágio `assets` do Dockerfile a cada `docker compose up -d --build`. Um sistema já rodando **precisa de rebuild** para ver a mudança (já documentado no README gerado, nota 1 da seção "Customização de marca"). | documentar o rebuild obrigatório no update |
| **Configuração viva fora do Git** | O único caso é o `.env` de cada sistema derivado (não versionado, protegido pelo `.gitignore.jinja`). Nenhuma variável nova é exigida por esta fase. | nenhuma |

---

## Armadilhas Comuns

### Pitfall 1 — `bg-ink/40` desaparece **por completo** sob `var()` [VERIFICADO]

**O que dá errado:** o app exemplo usa `bg-ink/40` em **2 lugares** —
`apps/…/exemplo/templates/exemplo/_confirmar_exclusao_modal.html:5` e
`…/_form_modal.html:5` (o véu do modal). Quando `ink` passa a ser `"var(--cor-ink)"`, o
Tailwind **não gera regra nenhuma** para `bg-ink/40`. Não é fallback silencioso — a
classe some do CSS e o véu fica **transparente**.

**Prova executada nesta sessão** (Tailwind 3.4.17, `ink: "var(--cor-ink)"`):

```
.bg-ink        { background-color: var(--cor-ink); }     ← gerada
.bg-ink\/40    → NENHUMA REGRA NO ARQUIVO DE SAÍDA
.bg-inkc\/40   { background-color: rgb(var(--cor-ink-c) / 0.4); }  ← só com <alpha-value>
```

**Por que acontece:** o Tailwind só aplica o modificador de opacidade quando consegue
parsear o valor como cor. Uma string `var(...)` sem `<alpha-value>` não é parseável e o
plugin descarta a variante inteira.

**O padrão de referência não bateu nisso:** o 10-UI-SPEC §4.1 registra a verificação
"zero ocorrências de token de cor com modificador de opacidade" antes de autorizar a
migração — o único `/opacidade` do PCA é `bg-black/40`, sobre a cor **nativa** `black`.

**Como evitar:** trocar `bg-ink/40` por **`bg-black/40`** nos dois arquivos (é
exatamente o que `/opt/web/pca/core/templates/core/shell.html:47` usa). A alternativa —
declarar as variáveis como triplas de canal e usar `rgb(var(--cor-ink) / <alpha-value>)`
— funciona (verificado) mas quebra o regex dos testes de contraste e polui as 40+
variáveis por causa de 2 usos.

**Sinal de alerta:** `grep -rnoE "(bg|text|border|ring)-(page|surface|surface-2|ink|ink-2|muted|grid|brand[a-z-]*)/[0-9]+" core/templates apps` deve voltar **vazio** antes do merge.

### Pitfall 2 — `shadow-xs` não existe no Tailwind v3 [VERIFICADO]

`shadow-xs` aparece **4×** nos templates do app exemplo (ex.:
`exemplo/dashboard.html:17`) e **não gera nenhuma regra** no Tailwind 3.4.17 — foi
confirmado no CSS de saída desta sessão (`shadow-sm` gerou, `shadow-xs` não). A chave só
existe no Tailwind v4. São 4 classes mortas hoje. Ao introduzir a escala de elevação de
3 níveis, trocar por `shadow-sm` (nível *Elevado*) ou remover (nível *Base*).

### Pitfall 3 — `@import` só funciona na primeira linha, e some em silêncio [VERIFICADO]

Testado nesta sessão: `@import "./dominio.css";` **depois** de `@tailwind base` foi
descartado sem erro, sem aviso visível, e o conteúdo do arquivo importado sumiu do
output. Na primeira linha, funcionou. Arquivo inexistente → build falha com exit code 2
(`postcss-import/lib/resolve-id.js`). **Consequência para o Dockerfile:** a linha 5
(`COPY core/static/src/input.css …`) precisa passar a copiar o diretório inteiro
(`COPY core/static/src ./core/static/src`), senão o build quebra ruidosamente.

### Pitfall 4 — `dark:` compila para `:where(...)`, não para `[data-tema="escuro"]` [VERIFICADO]

Com `darkMode: ["selector", '[data-tema="escuro"]']`, o Tailwind 3.4.17 emite:

```css
.dark\:bg-brand:where([data-tema="escuro"], [data-tema="escuro"] *) { … }
```

Um teste de contrato que procure `[data-tema=escuro]` **sem aspas** no artefato compilado
falha; um que procure a string exata `[data-tema="escuro"]` funciona. O PCA tem um
comentário inteiro sobre isso em `test_reskin_institucional.py:29-42` e outro em `:781`
— e lá o *bloco de variável* compila **sem** aspas (`[data-tema=escuro]{--cor-page:…}`)
enquanto a *variante* compila **com**. Duas formas, no mesmo arquivo. **Regra prática:
teste sobre a FONTE (`input.css`), não sobre o artefato compilado, sempre que der.**

### Pitfall 5 — `{% raw %}` do Jinja colidindo com sintaxe Django

`core/templates/core/_nav.html.jinja` usa `{% raw %}`/`{% endraw %}` **três vezes**
(linhas 1/34, 36/62, 64/66) porque Django e Jinja compartilham `{% %}` e `{{ }}`.
Qualquer edição no arquivo tem que respeitar a intercalação, e um `{% endraw %}` perdido
faz o Copier tentar interpretar `{% if request.path == url %}` como Jinja e explodir com
`StrictUndefined`. **A rota recomendada elimina o problema pela raiz:** com os itens do
exemplo fora do arquivo, o `_nav.html` não tem mais nenhum `{% if incluir_app_exemplo %}`
e pode perder o sufixo `.jinja` — nenhum `{% raw %}`, nenhuma colisão. O mesmo vale para
`tailwind.config.js.jinja` → `tailwind.config.js`.

### Pitfall 6 — `{% load %}` não atravessa `{% include %}`

`_nav_dominio.html` é renderizado como template próprio; o `{% load navegacao %}` do
`_nav.html` **não** vale lá dentro. Cada um dos dois arquivos precisa do seu `{% load %}`.
Esquecer produz `Invalid block tag: 'item_nav'` — erro barulhento, mas só na primeira
execução do derivado.

### Pitfall 7 — `getComputedStyle` de custom property não resolve funções

[CITED: developer.mozilla.org/en-US/docs/Web/CSS/--*] Uma custom property **não
registrada** computa para o *token stream* com `var()` substituído — não para uma cor
resolvida. Se `--cor-brand-tint` valesse `color-mix(in srgb, #fff 92%, var(--cor-brand))`,
`lerVarCss("--cor-brand-tint")` devolveria a string `color-mix(...)` e o ECharts pintaria
nada. **Regra:** todo token que o JS lê ou que um teste parseia por regex fica **hex
plano**. Se algum dia for preciso ler um token derivado, o padrão seguro é ler uma
*propriedade* resolvida (`getComputedStyle(elementoSonda).color`), não a variável.

### Pitfall 8 — Adotar a régua tipográfica encolhe o sistema inteiro

`text-base` cai de 16px para **13px**, `text-sm` de 14px para **12px**, `text-xs` de 12px
para **11px**. São 71 ocorrências nos templates. E `text-2xl` (**6×**, todas no dashboard
do exemplo) **não é declarada** pela régua — continua 24px, furando o teto de 20px. Trocar
por `text-xl`. `config.json` tem `ui_phase: true` e `ui_safety_gate: true`: **plane um
checkpoint humano de inspeção visual** (login, shell, CRUD, dashboard) depois desta
mudança, do jeito que o README já descreve para `test_05_nascimento.sh --keep`.

### Pitfall 9 — Purge das classes de componente

`.results` e `.module` **não aparecem em nenhum template do Sistema Base hoje**. Sem
`safelist`, o Tailwind as poda e elas somem em silêncio. As 4 variações `.btn--*`
**também** — e essas o padrão de referência **esqueceu** de listar. Ver a recomendação de
`safelist` com 8 entradas na §4.

### Pitfall 10 — O `<script>` de tema tem que ser síncrono e vir ANTES do `<link>`

`core/templates/base.html` carrega o CSS na **linha 8**. O script de tema entra **antes**
dela. Se vier depois (ou com `defer`, como os `<script>` das linhas 14-15), a primeira
pintura acontece no tema claro e o usuário vê um flash branco antes do escuro. É custo de
um script bloqueante curto, explicitamente aceito pelo padrão de referência (10-UI-SPEC §8).

### Pitfall 11 — "PCA" e "CFC" são palavras **proibidas** no código gerado [VERIFICADO]

`.template-tests/test_copier_copy.sh:48-93` roda `auditar_neutralidade()` sobre a árvore
renderizada inteira (nomes de caminho **e** conteúdo de arquivo), com
`re.IGNORECASE` e fronteira `(?<!\w)…(?!\w)`, contra a lista:

```
sistema_base, Sistema Base, PCA, CFC, orcamento, financeiro, dividaativa,
orcamento.cfc.org.br, cfc.org.br, toniaum/pca, github.com/ToNiauM/pca,
pca_rehearsal_, pca_pgdata, _retention_test, dominio-da-vps
```

**Consequência direta:** nenhum comentário de procedência pode ser copiado. Ficam
proibidos no `input.css`/`tailwind.config.js`/templates gerados: "Manual de Identidade
Visual do Sistema CFC/CRCs", "Resolução CFC nº 1.464/2014", "Pantone 541 C do CFC", e
qualquer referência a "PCA". As funções JS `pcaAplicarTema`, `pcaCsrfCookie`,
`pcaLimparCachePwa`, o evento `pca:tema-alterado`, a chave `pca-tema` e o id
`pca-theme-cor` **todos** têm que ser renomeados. Onde a procedência **pode** viver: em
`.planning/` (excluído), `CLAUDE.md`/`IDEIA.md`/`REVIEW.md` (excluídos), ou no `README.md`
do próprio template — **nunca** no `README.md.jinja`, que renderiza para dentro do sistema.

> Note também: `#003c71` como *default* de `cor_primaria` passaria a auditoria (é um hex,
> não a palavra) — mas embutiria a identidade de uma entidade específica num template
> declaradamente agnóstico. **Recomendação: manter `#1e40af`** (que já mede 8,27:1).

### Pitfall 12 — `_skip_if_exists` é obrigatório, não decorativo [VERIFICADO]

Já detalhado no Padrão 3. Sem ele: `<<<<<<< before updating` dentro do
`_nav_dominio.html` no primeiro `copier update` que mude `incluir_app_exemplo`.
`assert_no_conflict_markers` do ensaio A→B→C pegaria — mas só se o ensaio simular a
edição do derivado, o que hoje ele não faz.

### Pitfall 13 — Quatro testes de `.template-tests/` verificam o `_nav.html` por string

Vão quebrar quando os itens saírem do arquivo:

| Arquivo | Linha | Asserção |
|---|---|---|
| `test_copier_copy.sh` | 182 | `grep -Fq 'exemplo:' …/_nav.html` (variante `true`) |
| `test_copier_copy.sh` | 190 | `! grep -Fq 'exemplo:' …/_nav.html` (variante `false`) |
| `test_copier_update.sh` | 49 | `! grep -Fq 'exemplo:' …/_nav.html` dentro de `exigir_sem_exemplo` |
| `test_04_04_optional_exemplo.py` | 90-105 | 8 asserções sobre o conteúdo de `_nav.html` nas duas variantes |

Também: `apps/…/exemplo/README.md.jinja:14` documenta "`core/templates/core/_nav.html`
fornece os links Dashboard e Itens (CRUD)" — o texto muda para `_nav_dominio.html`, e
`test_04_04` afirma o conteúdo desse README.

### Pitfall 14 — O `<meta name="theme-color">` e o manifest são coisas diferentes

`base.html:13` (`<meta name="theme-color" content="{{ cor_primaria }}">`) passa a
acompanhar o tema pelo script. O `theme_color` do **manifest** (`core/views.py:172`) **não
muda** — é gravado na instalação do PWA. `core/tests/test_pwa.py:40` trava isso
(`assertEqual(corpo["theme_color"], settings.COR_PRIMARIA)`) e **deve continuar
passando**. São dois valores independentes.

### Pitfall 15 — A chave de tema não pode ser apagada no logout

`limparCachePwa()` (`base.html:54-64`) faz `caches.delete` de **tudo** e
`localStorage.removeItem("htmx-history-cache")`. A chave de tema é preferência visual,
não dado de sessão — não pode entrar nessa limpeza, ou o usuário perde o tema escuro a
cada logout. É uma linha de cuidado, mas é fácil de errar por "simetria".

### Pitfall 16 — O DividaAtiva **vai** conflitar, e isso não viola o critério 7

O critério 7 diz "sem exigir resolução manual **em arquivo que o derivado não tenha
tocado**". O DividaAtiva tocou três arquivos que esta fase reescreve inteiros:

| Arquivo | O que o derivado fez | Conflito no update |
|---|---|---|
| `core/templates/core/_nav.html` | apagou "Início", colou os itens do domínio | **certo** |
| `tailwind.config.js` | trocou `COR_PRIMARIA` para `#003c71`, acrescentou `borderRadius`/`fontSize`/`fontFamily` | **certo** |
| `core/static/src/input.css` | acrescentou o `@layer base { :focus-visible }` (verbatim do padrão) | **certo** — e no topo do arquivo, exatamente onde o upstream também mexe |

Os três conflitos são **resolvíveis por "ficar com a versão do template"**, porque o que
o derivado escreveu à mão é exatamente o que o upstream passa a entregar. **Recomendação:
a fase entrega, junto com a tag, um roteiro de resolução** (3 parágrafos no README, seção
"Releases e atualização do núcleo"): (a) `git checkout --theirs` nos três arquivos,
(b) recriar os itens de menu em `_nav_dominio.html` usando `{% item_nav %}`,
(c) mover eventuais tokens próprios para `dominio.css`.

### Pitfall 17 — **Quatro suítes de `.template-tests/` testam a tag v0.1.0, não o HEAD** [VERIFICADO]

O Copier, com um path local que é repositório git, copia da **última tag**, não do
working tree. Prova executada nesta sessão: um `copier copy` sem `--vcs-ref` gerou uma
árvore **sem** `core/static/img/logo-entidade.svg` (artefato da Fase 6, posterior a
`v0.1.0`) e gravou `_commit: v0.1.0`.

Suítes afetadas: **`test_copier_copy.sh`** (função `render`, l. 36-45),
**`test_04_03_identity.py`** (l. 39), **`test_04_04_optional_exemplo.py`** (l. 20-44),
**`test_04_06_operations.py`** (l. 20). As três que já corrigiram
(`test_04_05_backup.py:25`, `test_06_persistencia.py:33`, `test_05_nascimento.sh:132`)
passam `--vcs-ref=HEAD` com comentário explicando exatamente isto.

**Impacto sobre esta fase:** qualquer teste de contrato novo escrito nessas 4 suítes
**passaria ou falharia contra a v0.1.0**, dando resultado sem sentido. Corrigir as 4 é
pré-requisito de qualquer verificação de critério 5, 6 ou 7. É trabalho pequeno
(uma flag por invocação) e alto risco se esquecido.

### Pitfall 18 — O README gerado **mente** hoje sobre a cor primária

`README.md.jinja:93-94`: *"**Cor primária:** `COR_PRIMARIA` no `.env` (formato
`#RRGGBB`); a paleta Tailwind deriva dela no build."* — **falso**. `tailwind.config.js`
recebe o valor por **Jinja em tempo de `copier copy`** (`tailwind.config.js.jinja:6`),
não do `.env` em tempo de build. Trocar `COR_PRIMARIA` no `.env` hoje muda apenas o
`<meta theme-color>`, o admin e o manifest — a paleta continua a mesma. A rota recomendada
(Padrão 1) **torna a frase verdadeira**; se outra rota for escolhida, a frase precisa ser
corrigida.

### Pitfall 19 — Trocar `misturar()` de lugar afeta derivados existentes

`misturar()` vive em `tailwind.config.js` (não `.jinja`) no DividaAtiva, com o
`COR_PRIMARIA` hardcoded. Remover a função do template não quebra nada em quem já nasceu
— o arquivo dele é local — mas o conflito de update (Pitfall 16) traz o arquivo novo, e a
cor `#003c71` que ele fixou à mão precisa ser transportada para o `.env`
(`COR_PRIMARIA=#003c71`), não para o config. Documentar no roteiro de resolução.

### Pitfall 20 — `.form-row` diverge do anel de foco único **de propósito**

Não "consertar": o `:focus-visible` de `@layer base` usa `outline`, e o `.form-row`
usa `ring-2 ring-inset` + `border-brand`, deliberadamente, por WCAG 2.2 SC 2.4.11
(`input.css:57-65` do padrão). Um teste que exija "um único tratamento de foco no
projeto" reprovaria uma decisão correta.

---

## Exemplos de Código

### Bloco de tokens — esqueleto do novo `input.css`

```css
/* core/static/src/input.css — FONTE FÍSICA dos valores (DS-01/DS-05).
   `tailwind.config.js` só aponta para estas variáveis via var(--cor-*);
   os utilitários bg-page/text-ink resolvem em RUNTIME, nos dois temas. */
@import "./dominio.css";      /* PRIMEIRA linha, obrigatoriamente (Pitfall 3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :focus-visible { outline: 2px solid theme("colors.brand"); outline-offset: 2px; }
}

@layer components {
  .results  { @apply bg-surface border border-grid rounded overflow-x-auto; }
  .module   { @apply bg-surface border border-grid rounded p-4; }
  .form-row { @apply mt-0.5 w-full rounded-[6px] border border-grid bg-page px-2 py-1 text-base
                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset
                     focus-visible:ring-brand focus-visible:border-brand; }
  .btn      { @apply rounded-none px-3 py-1 text-[13px] font-semibold; }
  .btn--primaria   { @apply bg-brand text-white hover:bg-brand-hover; }
  .btn--secundaria { @apply border border-brand text-brand hover:bg-brand-tint; }
  .btn--neutro     { @apply border border-grid text-ink-2 hover:bg-surface-2; }
  .btn--destrutiva { @apply border border-destructive text-destructive; }
}

/* FORA de @layer: CSS solto sobrevive ao purge do JIT (o Tailwind poda regra
   de layer cujo seletor não encontra nos templates varridos). */
:root {
  --cor-page: #f9f9f7;  --cor-surface: #fcfcfb;
  --cor-surface-2: #f3f2ef;  --cor-surface-3: #fcfcfb;
  --cor-ink: #0b0b0b;  --cor-ink-2: #52514e;
  --cor-muted: #898781;  --cor-grid: #e1e0d9;  --cor-baseline: #c3c2b7;
  --cor-destructive: #d03b3b;  --cor-danger-tint: #fbe9e9;
  --cor-warn-bg: #fdf3e0;  --cor-warn-tx: #7a5000;
  /* Família de marca — DEFAULT do template. `COR_PRIMARIA` do .env sobrescreve
     em runtime pelo <style> de base.html (core/tema.py). */
  --cor-brand: #1e40af;      --cor-brand-hover: #3957b9;
  --cor-brand-ink: #193490;  --cor-brand-tint: #edf0f9;
  --cor-seq-600: #1e40af;    --cor-seq-450: #6379c6;  --cor-seq-300: #a5b1e0;
}

[data-tema="escuro"] {
  --cor-page: #0f0e0d;  --cor-surface: #181614;
  --cor-surface-2: #22211d;  --cor-surface-3: #2e2c28;
  --cor-ink: #eeeeee;  --cor-ink-2: #b9b8b5;
  --cor-muted: #95938e;  --cor-grid: #3a3833;
  --cor-danger-tint: #2e1616;  --cor-warn-bg: #2b2011;  --cor-warn-tx: #c98400;
  /* marca escura: mesmo matiz e saturação, luminosidade elevada (core/tema.py) */
  --cor-brand: #8ba4ec;      --cor-brand-hover: #bcc9f4;
  --cor-brand-ink: #6b8ae5;  --cor-brand-tint: #1c2540;
  --cor-seq-600: #8ba4ec;    --cor-seq-450: #5878cf;  --cor-seq-300: #3f5aa1;
}

[x-cloak] no @media (max-width: 767px) { ... }   /* manter a regra atual, escopada */
```

> Os hex de marca acima são os derivados de `#1e40af` (o default vigente) pelas mesmas
> regras — o planejador deve gerá-los com `core/tema.py` e não à mão, para que
> `input.css` e `tema.py` nunca divirjam. Um teste de contrato deve provar essa igualdade.

### `tailwind.config.js` — sem Jinja, verbatim

```js
/** @type {import('tailwindcss').Config} */
// ARQUIVO DO NÚCLEO — não edite. Os VALORES vivem em core/static/src/input.css;
// este arquivo só aponta para eles. Cores próprias do seu domínio vão em
// core/static/src/dominio.css.
module.exports = {
  darkMode: ["selector", '[data-tema="escuro"]'],
  content: ["./core/templates/**/*.html", "./apps/**/*.html"],
  safelist: ["results", "module", "form-row", "btn",
             "btn--primaria", "btn--secundaria", "btn--neutro", "btn--destrutiva"],
  theme: {
    extend: {
      colors: {
        page: "var(--cor-page)", surface: "var(--cor-surface)",
        "surface-2": "var(--cor-surface-2)", "surface-3": "var(--cor-surface-3)",
        ink: "var(--cor-ink)", "ink-2": "var(--cor-ink-2)",
        muted: "var(--cor-muted)", grid: "var(--cor-grid)",
        baseline: "var(--cor-baseline)",
        brand: "var(--cor-brand)", "brand-hover": "var(--cor-brand-hover)",
        "brand-ink": "var(--cor-brand-ink)", "brand-tint": "var(--cor-brand-tint)",
        destructive: "var(--cor-destructive)", "danger-tint": "var(--cor-danger-tint)",
        "warn-bg": "var(--cor-warn-bg)", "warn-tx": "var(--cor-warn-tx)",
        "seq-600": "var(--cor-seq-600)", "seq-450": "var(--cor-seq-450)",
        "seq-300": "var(--cor-seq-300)",
      },
      borderRadius: { DEFAULT: "2px", sm: "2px", md: "2px", lg: "2px", xl: "2px", "2xl": "2px" },
      fontSize: {
        xs: ["11px", { lineHeight: "1.4" }],  sm: ["12px", { lineHeight: "1.4" }],
        base: ["13px", { lineHeight: "1.5" }], md: ["14px", { lineHeight: "1.5" }],
        lg: ["16px", { lineHeight: "1.4" }],  xl: ["20px", { lineHeight: "1.3" }],
      },
      fontFamily: { sans: ["system-ui", "-apple-system", '"Segoe UI"', "sans-serif"] },
    },
  },
  plugins: [],
};
```

### Gráfico sem hex — o novo bloco do `exemplo/dashboard.html`

```django
{% block conteudo_pagina %}
{{ dados_categoria|json_script:"dados-categoria" }}
{{ dados_status|json_script:"dados-status" }}
{{ paleta_graficos|json_script:"paleta-graficos" }}   {# rampa derivada da marca #}
...
{% endblock %}
```

```js
var PALETA = JSON.parse(document.getElementById("paleta-graficos").textContent);

function lerVarCss(nome) {
  return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
}
function aplicarChrome() {
  PALETA.fundo  = lerVarCss("--cor-surface");
  PALETA.borda  = lerVarCss("--cor-grid");
  PALETA.texto  = lerVarCss("--cor-ink");
  PALETA.eixo   = lerVarCss("--cor-ink-2");
  PALETA.split  = lerVarCss("--cor-surface-2");
  PALETA.marca  = lerVarCss("--cor-brand");
}
aplicarChrome();
montarGraficos();

// Troca de tema reaplica o chrome nas instâncias vivas, sem recarregar a página.
document.addEventListener("tema:alterado", function () {
  aplicarChrome();
  montarGraficos();   // echarts.dispose() + init() antes de setOption
});
```

### Teste de contrato do critério 5 (esqueleto)

```python
# .template-tests/test_07_nav_extensao.py
def test_derivado_adiciona_itens_sem_tocar_o_nav_do_nucleo(self):
    """Critério 5: o único arquivo que o derivado cria/edita é _nav_dominio.html."""
    with tempfile.TemporaryDirectory() as tmp:
        destino = render(Path(tmp) / "sis", incluir_app_exemplo=False)  # --vcs-ref=HEAD!
        nav = destino / "core/templates/core/_nav.html"
        antes = nav.read_bytes()

        dominio = destino / "core/templates/core/_nav_dominio.html"
        dominio.write_text(
            '{% load navegacao %}\n{% item_nav "core:shell" "Painel" "casa" %}\n',
            encoding="utf-8",
        )
        # byte a byte: o arquivo do núcleo não pode ter sido tocado
        self.assertEqual(antes, nav.read_bytes())
```

E o passo novo do ensaio A→B→C (critério 7), dentro de
`.template-tests/test_copier_update.sh`, entre o estado A e o B:

```sh
# O derivado põe os próprios itens ANTES do update — é o cenário real.
printf '{%% load navegacao %%}\n{%% item_nav "core:shell" "Painel" "casa" %%}\n' \
    > "${DESTINO}/core/templates/core/_nav_dominio.html"
preparar_commit_destino
git -C "$DESTINO" commit -qm 'test: derivado declara o próprio menu'
# ... update ...
grep -Fq 'Painel' "${DESTINO}/core/templates/core/_nav_dominio.html" || \
    falhar 'update apagou os itens do derivado'
assert_no_conflict_markers "$DESTINO"
```

---

## Estado da Arte

| Abordagem antiga (template hoje) | Abordagem atual (padrão de referência) | Quando mudou | Impacto |
|---|---|---|---|
| Hex derivado em build-time por `misturar()` no config | Variáveis CSS em `input.css`; config aponta com `var(--cor-*)` | PCA Fase 10 (D-142) | Habilita tema escuro sem duplicar a paleta |
| Sem tema escuro | `darkMode: ["selector", '[data-tema="escuro"]']` + script síncrono + `localStorage` | PCA Fase 10 (D-143/144/145) | 3 estados (auto/claro/escuro), sem flash |
| 2 degraus de superfície | 3 degraus + elevação por sombra no claro / por luminosidade no escuro | PCA Fase 10 (D-151/152) | Modais e dropdowns legíveis nos dois temas |
| Raio não declarado | 6 chaves colapsadas em 2px | PCA Fase 13 (D-315) | Acabamento de aplicação instalada |
| Tipografia não declarada | 6 degraus nomeados, teto em 20px | PCA Fase 13 (D-318/319) | Densidade de painel administrativo |
| `focus-visible:ring-*` espalhado | 1 regra em `@layer base` | PCA Fase 13 (D-324) | Substituiu 31 declarações |
| Cor de chrome do gráfico no servidor | `getComputedStyle` em runtime; servidor só manda dado semântico | PCA Fase 10 (D-142) | Gráfico segue o tema sem reload |
| Hex de gráfico solto no JS | `json_script` + variáveis CSS | PCA Fase 10 | Elimina hex do JS |
| `text-[32px]` para KPI | `text-xl` (20px) — teto da régua | quick-260812-gjo | Régua única |

**Descontinuado / a remover do template:**

- `misturar()` no `tailwind.config.js.jinja` — vira `core/tema.py` (mesma matemática).
- `shadow-xs` (4×) — classe que não existe no Tailwind v3.
- `bg-ink/40` (2×) — vira `bg-black/40`.
- `text-2xl` (6×) — vira `text-xl`.
- 14 hex literais no JS de `exemplo/dashboard.html`.
- `{% raw %}` em `_nav.html.jinja` e o Jinja de `tailwind.config.js.jinja`.

---

## Registro de Suposições

| # | Afirmação `[ASSUMED]` | Seção | Risco se estiver errada |
|---|---|---|---|
| A1 | Nenhuma pergunta nova entra no `copier.yml` (raio/tipografia/fonte são padrão do template) | §7 Superfície Copier | Se o operador quiser variar por sistema, a rota muda: cada valor vira pergunta e `tailwind.config.js` volta a ser `.jinja` — perdendo a propriedade "verbatim, zero conflito" |
| A2 | `brand-tint` escuro derivado por `com_luminancia(cor, 0.153)` | §1.2 | O único token da família de marca sem regra derivável do padrão. Se ficar feio, é ajuste de um número — mas o contraste de texto sobre ele precisa ser validado por teste |
| A3 | O donut do app exemplo passa a usar a rampa sequencial derivada, em vez de 5 matizes categóricos | §5 | Perde diferenciação categórica visual; alternativa (3 matizes CVD-safe em Python) está descrita |
| A4 | O default de `cor_primaria` continua `#1e40af` | Pitfall 11 | Se o operador quiser `#003c71` como default, é 1 linha em `copier.yml` — mas embute identidade de entidade num template agnóstico |
| A5 | `muted` e `grid` adotam os valores do padrão (`#898781` / `#e1e0d9`), abandonando os do template | §1.1 | Mudança visual sutil e global; se o operador preferir manter, a fase perde "conferível lado a lado" (critério 1) |
| A6 | A `safelist` ganha as 4 variações `.btn--*` além das 4 classes do padrão | §4 | Sem elas, as variações somem em silêncio quando nenhum template as usa literalmente |
| A7 | A tag `v0.2.0` entrega Fase 6 + Fase 7 juntas, como o ROADMAP determina | §8 | Nenhum — está escrito no ROADMAP e no STATE |
| A8 | O roteiro de resolução de conflito do DividaAtiva entra no README do template, não numa fase separada | Pitfall 16 | Se ficar de fora, o primeiro update real do derivado vira suporte manual |

---

## Questões em Aberto (RESOLVIDAS)

> As quatro questões foram fechadas no `/gsd:discuss-phase` de 2026-08-23 e estão travadas
> em `07-CONTEXT.md`. A seção fica como registro do raciocínio; **nenhum item aqui está
> pendente**. A resolução de cada um está marcada em linha.

1. **A fonte física da marca é `input.css` ou `.env`?** — **RESOLVIDA por D-79 + D-80:**
   `input.css` carrega o hex **default**, em texto plano, fora do Jinja; o `.env`
   (`COR_PRIMARIA`) sobrescreve **em runtime**, com a família derivada em Python no boot
   (`core/tema.py`). É exatamente a recomendação abaixo. Implementada pelos planos 07-02
   (default) e 07-04 (override + prova executável em `test_07_cor_runtime.sh`).
   - O que se sabe: o critério 3 diz "a fonte física dos valores é
     `core/static/src/input.css`". O critério 4 diz que `cor_primaria` continua sendo
     pergunta do Copier. O `.env` já carrega `COR_PRIMARIA` e é o contrato de runtime
     (D-47/D-50), e `core/admin_site.py` já injeta CSS a partir dele.
   - O que não está claro: se `input.css` deve conter o hex **efetivo** do sistema (o que
     obrigaria a renderizá-lo por Jinja e a criar conflito eterno de update) ou o hex
     **default** do template, sobrescrito em runtime pelo `.env`.
   - Recomendação: **default em `input.css`, override em runtime pelo `.env`** (Padrão
     1). Satisfaz os dois critérios lidos com boa-fé, mantém `input.css` fora do Jinja e
     conserta a mentira do README (Pitfall 18). **Trava isso no `/gsd:discuss-phase`.**

2. **O tema escuro entra também no admin do Django?** — **RESOLVIDA: fora de escopo,** registrada na seção `<deferred>` de `07-CONTEXT.md` como ideia adiada. Reabrir só se o operador quiser que forçar "claro" no sistema também force claro no admin.
   - O que se sabe: `core/admin_site.py:48-49` injeta `--primary`/`--header-bg`/`--link-fg`
     no `:root` do admin. O Django 5.2 tem tema escuro nativo por
     `prefers-color-scheme`, independente do `data-tema` do sistema.
   - O que não está claro: se o operador espera que forçar "claro" no sistema também force
     claro no admin.
   - Recomendação: **fora de escopo nesta fase**. O admin é ferramenta de superusuário e o
     Django já resolve sozinho. Registrar como ideia adiada.

3. **A rampa do donut precisa ser categórica?** — **RESOLVIDA por D-84 (decisão delegada ao modelo pelo operador):** não. É a rampa **sequencial** derivada da marca, servida pelo Django via `json_script` (D-85). Implementada pelo plano 07-06, com quatro cores — `StatusChoices` tem quatro valores, não três (`apps/…/exemplo/models.py:18-22`).
   - Ver A3. Depende de o app exemplo querer ensinar "cor por categoria" ou "cor por
     intensidade". Decisão de produto, não técnica.

4. **Elevação: quais elementos do template recebem qual nível?** — **RESOLVIDA:** delegada ao planejamento pela seção `Claude's Discretion` de `07-CONTEXT.md`, e o mapeamento elemento a elemento está escrito nas tabelas de `<interfaces>` dos planos 07-05 (consumidores do `core`) e 07-06 (consumidores do app exemplo), além de ficar registrado num `{% comment %}` do próprio `shell.html` para o critério 1 ser conferível.
   - O padrão define os 3 níveis e lista os consumidores **do PCA**. O template tem
     consumidores diferentes (cards de KPI do exemplo, modais HTMX do exemplo, a `<aside>`,
     a tabela de resultado). O mapeamento é mecânico mas precisa ser feito explicitamente
     no plano, elemento a elemento, para o critério 1 ser conferível.

---

## Disponibilidade do Ambiente

| Dependência | Requerida por | Disponível | Versão | Fallback |
|---|---|---|---|---|
| `node` / `npx` | Build do Tailwind (também para verificação local do CSS gerado) | ✓ | node v22.22.2 / npm 10.9.7 | build acontece no Docker de qualquer forma |
| `tailwindcss@3.4.17` via `npx --yes` | `Dockerfile:15` | ✓ (baixado e executado nesta sessão) | 3.4.17 | — |
| `docker` | `test_05_nascimento.sh`, suíte Django, `docker compose up` | ✓ (`docker info` OK) | — | — |
| `copier` | `.template-tests/*` | ✓ | **9.17.1** em `.venv-template/bin/copier` | — |
| `python3` (host) | `.template-tests/*.py` | ✓ | 3.14.4 | — |
| `django` (host) | — | ✗ | — | **não é necessário**: a suíte Django roda dentro do container (`compose exec -T web python manage.py test`) |
| `/opt/web/pca` (repositório fonte) | leitura do padrão | ✓ | — | — |
| `/opt/web/dividaativa` (derivado) | validação do roteiro de conflito | ✓ (`_commit: v0.1.0`) | — | — |
| Navegador headless | inspeção visual | ✗ | — | `test_05_nascimento.sh --keep` + inspeção manual do operador (é o padrão já documentado no README) |

**Faltando sem fallback:** nenhuma.
**Faltando com fallback:** Django no host (roda no container); navegador headless
(checkpoint humano — coerente com `ui_safety_gate: true`).

---

## Domínio de Segurança

### Categorias ASVS aplicáveis

| Categoria ASVS | Aplica | Controle padrão |
|---|---|---|
| V2 Autenticação | não | fase não toca auth |
| V3 Sessão | não | fase não toca sessão |
| V4 Controle de acesso | não | fase não toca permissão |
| **V5 Validação de entrada / Saída** | **sim** | `COR_PRIMARIA` já é validada com `re.fullmatch(r"#[0-9a-fA-F]{6}")` em `config/settings/base.py.jinja:158-161`, levantando `ImproperlyConfigured` no boot — **é essa validação que autoriza o `\|safe` do `<style>`**. Todo dado de gráfico continua indo por `\|json_script` (escapa `<`, `>`, `&`), nunca por `\|safe`. |
| V6 Criptografia | não | — |
| V14 Configuração | **sim** | nenhum segredo novo; `.env.example.jinja` não ganha variável |

### Ameaças conhecidas para esta stack

| Padrão | STRIDE | Mitigação padrão |
|---|---|---|
| **Injeção de CSS via `COR_PRIMARIA`** (o `<style>` novo em `base.html` interpola valor de `.env`) | Tampering | Validação `#RRGGBB` no boot — **precedente T-02-01/T-02-06, já existente e testado por `core/tests/test_identidade.py:15`**. O `core/tema.py` **nunca** pode ser chamado com valor não validado |
| XSS via dados de gráfico serializados | Tampering | `\|json_script` (já em uso, `dashboard.html:30-31`); **nunca** trocar por `\|safe` ou por interpolação direta em JS |
| SVG de ícone injetável | Tampering | `ICONES` é dicionário **fechado** de `mark_safe` em código Python; nome desconhecido rende ícone vazio. Nunca aceitar markup SVG como argumento da tag |
| Conteúdo de sessão persistido no cliente | Information disclosure | `hx-history="false"` no `<body>` e `limparCachePwa()` no logout continuam intactos; a chave de tema é preferência, não dado de sessão (Pitfall 15) |
| Cache do PWA servindo CSS obsoleto | Denial of service (visual) | Não se aplica: `CompressedManifestStaticFilesStorage` dá hash novo ao arquivo, gerando URL nova (verificado em `base.py.jinja:175`) |

---

## Fontes

### Primárias (confiança ALTA — arquivos lidos e comandos executados nesta sessão)

- `/opt/web/pca/core/static/src/input.css` (338 linhas) — tokens, `@layer base`,
  `@layer components`, pontes `data-*`
- `/opt/web/pca/tailwind.config.js` (140 linhas) — `darkMode`, `safelist`, `colors`,
  `borderRadius`, `fontSize`, `fontFamily`
- `/opt/web/pca/core/templates/base.html:1-33` — script de tema síncrono
- `/opt/web/pca/core/templates/core/shell.html:110-140,186` — controle de tema, elevação
- `/opt/web/pca/core/templates/core/_nav_visoes.html` (67 linhas) — item de nav, estado ativo
- `/opt/web/pca/apps/pca/paleta.py` (56 linhas) — `PALETA_GRAFICOS`
- `/opt/web/pca/apps/pca/templates/pca/dashboard.html:18,44-58,353-356` — `json_script`,
  `getComputedStyle`, reaplicação na troca de tema
- `/opt/web/pca/apps/pca/views.py:849-853` — `json_script` fora do alvo do HTMX
- `/opt/web/pca/BRIEFING-RESKIN-CFC.md` §2 (linhas 33-118) — procedência cromática
- `/opt/web/pca/.planning/phases/10-.../10-UI-SPEC.md` §3, §4.1-4.2, §8
- `/opt/web/pca/.planning/phases/13-.../13-UI-SPEC.md` §1.1-1.5
- `/opt/web/pca/apps/pca/tests/test_paleta_contraste.py` (231 linhas) — teste de contraste portável
- `/opt/web/pca/apps/pca/tests/test_reskin_institucional.py` (1045 linhas) — contratos de CSS/markup
- `/opt/sistema_base/` — `tailwind.config.js.jinja`, `copier.yml`, `Dockerfile`,
  `core/static/src/input.css`, `core/templates/base.html`, `core/templates/core/shell.html`,
  `core/templates/core/_nav.html.jinja`, `core/admin_site.py`, `core/context_processors.py`,
  `core/views.py`, `config/settings/base.py.jinja`, `README.md`, `README.md.jinja`,
  `apps/…/exemplo/templates/exemplo/dashboard.html`, `apps/…/exemplo/views.py`,
  `.template-tests/*` (10 arquivos), `core/tests/*` (10 arquivos)
- `/opt/web/dividaativa/` — `.copier-answers.yml`, `tailwind.config.js`,
  `core/static/src/input.css`, `core/templates/core/_nav.html`

### Comandos executados (evidência de primeira mão)

| Verificação | Comando | Resultado |
|---|---|---|
| Modificador de opacidade sob `var()` | `npx tailwindcss@3.4.17` com `ink: "var(--cor-ink)"` | `.bg-ink/40` **não gerada**; `rgb(var(--x) / <alpha-value>)` gerada |
| `shadow-xs` no v3 | idem | **não gerada** |
| `dark:` com seletor por atributo | idem | `:where([data-tema="escuro"], [data-tema="escuro"] *)` |
| `theme("colors.brand")` sob `var()` | idem | compila para `var(--cor-brand)` |
| `@import` posicional | idem, `@import` antes vs. depois de `@tailwind` | antes: inlinado; depois: **descartado em silêncio**; ausente: erro exit 2 |
| Derivações de cor | `node -e` com a `misturar()` real | `#1f5382`, `#00315d`, `#ebeff4` (f=0.92), `#577ea1` (0.34), `#9eb5c9` (0.62) — todos exatos |
| Contrastes WCAG | `node -e` | 10,57 / 3,99 / 17,04 / 2,06 — batem com o publicado |
| HSL do par claro/escuro | `node -e` | H 208,1° e S 100% idênticos; L 22,2 → 72,7 |
| `_skip_if_exists` em `copier update` | Copier 9.17.1 real, template descartável v1→v2 | **com**: sem conflito, stub preservado; **sem**: `<<<<<<<` no arquivo |
| Copier lê a última tag | `copier copy` sem `--vcs-ref` no próprio repositório | gerou `_commit: v0.1.0`, **sem** `logo-entidade.svg` da Fase 6 |
| Contagem de testes | `grep -c "    def test_"` | 54 (`core`) + 23 (`exemplo`) = **77** ✔ |

### Secundárias (confiança MÉDIA-ALTA — documentação oficial)

- [CITED: docs.djangoproject.com/en/5.2/howto/custom-template-tags/] —
  `inclusion_tag`, `takes_context=True`, descoberta em `<app>/templatetags/`,
  obrigatoriedade do `{% load %}` por template
- [CITED: docs.djangoproject.com/en/5.2/ref/templates/builtins/] — `{% url … as var %}`
  não levanta `NoReverseMatch` ("in practice you'll use this to link to views that are
  optional")
- [CITED: copier.readthedocs.io/en/stable/updating/] — merge de três vias; arquivo
  alterado só pelo destino **não conflita**; `skip_if_exists` tem a presença garantida
  mesmo em update; `--conflict inline|rej`
- [CITED: developer.mozilla.org/en-US/docs/Web/CSS/--*] — custom property não registrada
  computa para o token stream com `var()` substituído, não para valor resolvido

### Terciárias (confiança BAIXA — não usadas para decisão)

- Busca web sobre resolução de custom properties registradas com `@property` — a
  resolução do CSSWG aponta para "used value", mas nenhum resultado foi conclusivo o
  bastante para basear decisão. A recomendação (hex plano) **não depende** desse ponto.

---

## Metadados

**Confiança por área:**

| Área | Nível | Motivo |
|---|---|---|
| Valores dos tokens e derivações | **ALTA** | lidos do `input.css` real e reproduzidos numericamente com 5 acertos exatos |
| Mecanismo de tema escuro | **ALTA** | lido do `base.html`/`shell.html` reais, com o spec que o governa |
| Comportamento do Tailwind (purge, `var()`, `dark:`, `@import`) | **ALTA** | executado nesta sessão com a versão exata do `Dockerfile` |
| Contrato de `copier update` e `_skip_if_exists` | **ALTA** | executado nesta sessão com o Copier 9.17.1 do próprio repositório |
| Superfície de testes e o bug do `--vcs-ref` | **ALTA** | contagem e reprodução do sintoma |
| Encaixe da navegação | **MÉDIA** | o mecanismo de extensão é projeto novo (o padrão de referência não tem inclusion tag); o *tratamento visual* é ALTA |
| Paleta do donut do app exemplo | **MÉDIA** | sem precedente direto; duas rotas descritas, uma recomendada |
| `brand-tint` escuro derivado | **MÉDIA** | único token da família sem regra derivável; recomendação com base em H/S/L medidos |

**Data da pesquisa:** 2026-08-23
**Válida até:** 2026-09-22 (30 dias — nada aqui é ecossistema em movimento rápido; o
risco de obsolescência é o `/opt/web/pca` evoluir, não a stack)
