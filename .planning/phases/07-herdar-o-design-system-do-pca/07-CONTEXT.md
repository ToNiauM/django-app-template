# Phase 7: Herdar o design system do PCA - Context

**Gathered:** 2026-08-23
**Status:** Ready for planning
**Source:** Decisões travadas pelo operador durante `/gsd-plan-phase 7`, ancoradas no
`07-RESEARCH.md` (pesquisa de primeira mão em `/opt/web/pca`, com Copier 9.17.1 e
Tailwind 3.4.17 executados de verdade nesta sessão).

<domain>
## Phase Boundary

O template herda **direto do PCA** (`/opt/web/pca`, que não é derivado do template — é
anterior a ele) o design system inteiro: tokens de cor em CSS, tema escuro, 3 degraus de
superfície com elevação, raio único, régua tipográfica, pilha de fonte, focus-ring único,
classes de componente com `safelist`, e paleta de gráfico servida pelo Django. E resolve o
encaixe de navegação (T-01/T-03 da auditoria de 2026-08-23) para que um derivado ponha os
próprios itens no menu **sem editar um único arquivo do `core`**.

A fase fecha com a tag `v0.2.0`, que entrega Fase 6 e Fase 7 juntas — o Copier lê a última
tag e não o HEAD, então nenhum sistema derivado recebeu a Fase 6 ainda.

**Fora desta fase:**
- Os 7 pares de token de status do PCA (`st-concluido`, `st-em-tramitacao`, `st-atrasado`…)
  — vocabulário do domínio dele. Sobe a *mecânica* do par fundo+texto e a disciplina
  CVD-safe; cada sistema declara os próprios status.
- Tema escuro no admin do Django (Q2 da pesquisa) — o admin é ferramenta de superusuário e
  o Django 5.2 já resolve por `prefers-color-scheme`. Ver `<deferred>`.
- Qualquer alteração em `/opt/web/pca`.
- Qualquer conteúdo de domínio.

</domain>

<decisions>
## Implementation Decisions

*(Numeração continua de D-78, última decisão da Fase 6.)*

### Fonte física da cor da marca

- **D-79:** A fonte física dos tokens é **`core/static/src/input.css` com hex plano**, e o
  arquivo **não passa por Jinja**. Ele carrega o valor **padrão** do template. Nada de
  `color-mix()` em variável que o JS precise ler (Pitfall 7: `getComputedStyle` não resolve
  funções de cor em custom property).
- **D-80:** O **`.env` (`COR_PRIMARIA`) sobrescreve em runtime**, não em build-time. A
  família de marca (hover, ink, tint, rampa sequencial) é derivada **em Python no boot**,
  em `core/tema.py`, espelhando o precedente já existente de `core/admin_site.py` que
  injeta `--primary`/`--header-bg`/`--link-fg` a partir do `.env`. Isso satisfaz o critério
  3 (fonte física é `input.css`) e o critério 4 (`cor_primaria` continua pergunta do
  Copier) lidos de boa-fé, mantém `input.css` fora do Jinja — logo, fora de conflito de
  `copier update` para sempre — e conserta a mentira atual do README (Pitfall 18: o README
  gerado hoje afirma que `COR_PRIMARIA` alimenta a paleta Tailwind, e não alimenta).
- **D-81:** As derivações do PCA são **reprodutíveis pela `misturar()` que o template já
  tem**, com os coeficientes verificados na pesquisa: `misturar(B,255,0.12)` → brand-hover,
  `misturar(B,0,0.18)` → brand-ink, `misturar(B,255,0.92)` → brand-tint (o template usa
  0.9 hoje — **corrigir para 0.92**), `misturar(B,255,0.34)` → `seq-450`,
  `misturar(B,255,0.62)` → `seq-300`. O par claro/escuro da marca preserva matiz e
  saturação HSL e muda só a luminosidade (22,2% → 72,7%) — regra derivável para qualquer
  `cor_primaria`, não uma tabela de valores fixos.

### Superfície Copier

- **D-82:** **Nenhuma pergunta nova no `copier.yml`** para raio, régua tipográfica ou pilha
  de fonte. Os três entram como **padrão fixo do template**, herdado do PCA: raio único de
  2px colapsando as 6 chaves, régua de 6 degraus nomeados em 11/12/13/14/16/20px com teto
  em 20px, pilha `system-ui`. São decisões de identidade da família CFC, não de sistema
  individual. Satisfaz o critério 4 (o derivado não edita `tailwind.config.js` para nada)
  sem inchar o questionário.
- **D-83:** **`tailwind.config.js.jinja` perde o sufixo `.jinja` e passa a ser verbatim.**
  Com as cores vindo de `var(--cor-*)` e o resto sendo padrão fixo (D-82), não sobra nada
  de variável no arquivo. Deixa de ser templatizado → vira arquivo que o derivado nunca
  edita e que nunca conflita em `copier update`. É o que torna o critério 7 alimentável.

### Paleta de gráfico

- **D-84:** A paleta do donut do app exemplo é a **rampa sequencial derivada da marca**
  (`seq-300` / `seq-450` / `seq-600`), não 3 matizes categóricos fixos. *(Decisão delegada
  ao modelo pelo operador.)* Razão: um template não consegue escolher 3 matizes que
  sobrevivam a **qualquer** `cor_primaria` e continuem CVD-safe; a rampa deriva sozinha, de
  modo que todo derivado ganha um donut coerente com a própria marca sem decidir nada — que
  é a tese da fase inteira ("herdar por construção, editar nada").
- **D-85:** A paleta chega do **servidor via `json_script`** e é consumida pelo ECharts.
  Nenhum hex sobrevive em template ou em JS de template (critério 3). Isso é o que faz o
  tema escuro funcionar nos gráficos (critério 2).
- **D-86:** O **dourado institucional `secundaria` (#a07400) é forma e nunca texto** — 3,99:1
  reprova AA de texto. A disciplina entra como regra explícita, não como convenção tácita.

### Encaixe da navegação

- **D-87:** **Não existe override de template neste projeto** — `TEMPLATES.DIRS` aponta para
  o mesmo diretório que o `APP_DIRS` do `core` (verificado na pesquisa). Logo o desenho é
  **"arquivo-stub protegido"**, não "override": o template entrega
  `core/templates/core/_nav_dominio.html` vazio e o marca com **`_skip_if_exists`** no
  `copier.yml`. A pesquisa provou com Copier 9.17.1 real que com `_skip_if_exists` o
  upstream reescreve `_nav.html`, o derivado mantém o próprio stub e há **zero marcadores de
  conflito**; sem ele, o stub ganha `<<<<<<< before updating`. É a peça que faz os critérios
  5, 6 e 7 funcionarem — não é decorativa.
- **D-88:** `{% include "core/_nav_dominio.html" %}` no fim da nav do `_nav.html`. O
  `_nav.html` fica **estático e intocado** pelo derivado, e um teste de contrato prova isso.
- **D-89:** Inclusion tag **`{% item_nav url rotulo icone prefixo %}`** substitui as 12
  linhas repetidas por item, carregando o tratamento visual do PCA por construção
  (`bg-brand-tint`, filete de 2px, `aria-current="page"`). A tag resolve a rota em
  **`try/except NoReverseMatch`** — o padrão documentado do Django para views opcionais. É
  isso que faz os itens do app exemplo sumirem sozinhos quando `incluir_app_exemplo=false`,
  sem o derivado editar arquivo upstream (critério 6, T-03).
- **D-90:** Um nome de ícone desconhecido renderiza o item **sem ícone** e nunca quebra a
  página.
- **D-91:** O que sobe do PCA na navegação é **só o tratamento visual** (já idêntico). O
  `_nav_visoes.html` do PCA sofre da mesma repetição de 12 linhas — a inclusion tag é
  **trabalho novo**, não herança.

### Fronteira de domínio

- **D-92:** O derivado declara os próprios status em **`dominio.css`** — arquivo próprio,
  fora do `input.css` do core. Sobe a mecânica do par fundo+texto e a disciplina CVD-safe;
  nenhum token `st-*` do PCA é copiado.

### Higiene do código gerado

- **D-93:** **"PCA" e "CFC" são palavras proibidas na árvore gerada**, auditadas por teste
  executável (`test_copier_copy.sh:48-93`, `IGNORECASE`, 15 tokens). Nenhum comentário de
  procedência (Pantone 541 C, Resolução CFC nº 1.464/2014) pode ser copiado para o código,
  e **todo identificador `pca*` do script de tema tem que ser renomeado**. A procedência
  cromática vive na documentação de planejamento, não no artefato gerado.

### Correções obrigatórias apuradas na pesquisa

- **D-94:** **`bg-ink/40` → `bg-black/40`** nos dois modais do app exemplo. Verificado por
  compilação real do Tailwind 3.4.17: `.bg-ink/40` **não gera regra nenhuma** quando
  `ink: "var(--cor-ink)"` — o véu ficaria transparente. O PCA não bateu nisso porque mediu
  zero usos antes de migrar. `bg-black/40` é o que o próprio PCA usa.
- **D-95:** As **quatro suítes de `.template-tests/` que testam a tag `v0.1.0` em vez do
  working tree** (`test_copier_copy.sh`, `test_04_03`, `test_04_04`, `test_04_06`) passam a
  usar **`--vcs-ref=HEAD`**. Verificado: sem a flag, o `copier copy` gera árvore **sem**
  `logo-entidade.svg` (Fase 6) e grava `_commit: v0.1.0`. Qualquer teste de contrato novo
  escrito nessas suítes daria resultado sem sentido.
- **D-96:** **`shadow-xs` não existe no Tailwind v3** — 4 classes mortas a corrigir.
- **D-97:** **`@import` só funciona na primeira linha do CSS** e some em silêncio depois.
- **D-98:** Adotar a régua tipográfica **encolhe `text-base` de 16px para 13px em 71
  ocorrências**, e `text-2xl` (6 usos) fura o teto de 20px. A migração é mecânica mas tem
  que ser feita de propósito, ocorrência a ocorrência — não é um find/replace cego.
- **D-99:** O `<script>` de tema tem que ser **síncrono e vir ANTES do `<link>`** do CSS
  (evita flash de tema errado). A chave de tema **não pode ser apagada no logout**.

### Claude's Discretion

- Mapeamento elemento-a-elemento dos 3 níveis de elevação nos consumidores do template
  (cards de KPI do exemplo, modais HTMX, a `<aside>`, a tabela de resultado) — o padrão
  define os níveis, o plano precisa fazer o mapeamento explicitamente para o critério 1 ser
  conferível. (Q4 da pesquisa.)
- Adotar os valores de `muted` e `grid` do PCA onde divergem do template — recomendação da
  pesquisa, aceita; os valores exatos ficam a critério do plano.
- Nome exato do módulo de tema (`core/tema.py`) e assinatura das funções de derivação.
- Nomes das 6 chaves da régua tipográfica e das 3 chaves de superfície.
- Conjunto exato de entradas no `safelist`.
- Divisão em planos/ondas e granularidade dos commits.
- Quais asserções entram em cada teste de contrato, além das exigidas pelos critérios 5 e 6.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Especificação desta fase
- `.planning/ROADMAP.md` §"Phase 7: Herdar o design system do PCA" — a spec primária:
  tabela peça-a-peça do que sobe, encaixe da navegação, o que NÃO sobe, 8 critérios de
  sucesso, nota de release.
- `.planning/phases/07-herdar-o-design-system-do-pca/07-RESEARCH.md` — valores concretos,
  20 pitfalls (12 verificados por execução real), padrões de arquitetura e esqueletos de
  código. **Leitura obrigatória antes de planejar.**

### Fonte do padrão (repo externo, somente leitura)
- `/opt/web/pca/BRIEFING-RESKIN-CFC.md` §2 — procedência cromática (Resolução CFC nº
  1.464/2014, Pantone 541 C e 132 C; não existe hex oficial, todo sRGB é derivação).
- `/opt/web/pca/` fases 01, 02, 10 e 13 `*-UI-SPEC.md` — medidas e contrastes.
- `/opt/web/pca/core/static/src/input.css`, `tailwind.config.js`,
  `core/templates/core/_nav.html` — implementação de referência.

### Contrato do template (este repo)
- `copier.yml` — perguntas existentes, `cor_primaria`, e onde entra `_skip_if_exists`.
- `.template-tests/` — 11 suítes, incluindo o ensaio A→B→C de `copier update`.
- `CLAUDE.md` — restrições do projeto.
- `.planning/STATE.md` — decisões D-01..D-78 das fases anteriores (esp. D-47/D-50: ".env
  primeiro, .jinja mínimo").

</canonical_refs>

<specifics>
## Specific Ideas

- **Decisão de rota do operador (2026-08-23):** o template herda **direto do PCA**, não do
  DividaAtiva. O DividaAtiva tem só um recorte do padrão (cor, raio, tipografia, fonte,
  focus-ring, de uma quick task de reskin) e receberá o resto pelo `copier update` desta
  versão — em vez de reimplementar à mão e conflitar consigo mesmo depois.
- **O conflito aberto que a fase fecha:** o DividaAtiva precisou apagar o link "Início" do
  `_nav.html` e colar sete blocos de doze linhas — **79 linhas trocadas dentro de arquivo
  upstream**, conflito garantido em todo `copier update`. É o pior conflito aberto da
  família, e resolvê-lo **antes** da v0.2.0 é o que torna o update dos derivados viável.
- **O DividaAtiva vai conflitar nesta atualização, e isso não viola o critério 7** (Pitfall
  16) — ele *já editou* `_nav.html`. O critério fala de arquivo que o derivado **não tenha
  tocado**.
- **Pendência de release carregada pela fase:** `git tag -l` → só `v0.1.0`; são **39**
  commits desde então (o ROADMAP diz 37 — número desatualizado). Nada em `copier.yml` nem
  em CI depende da tag (não há `.github/` neste repositório). A fase fecha com
  `git tag -a v0.2.0`.

</specifics>

<deferred>
## Deferred Ideas

- **Tema escuro no admin do Django** (Q2 da pesquisa) — `core/admin_site.py:48-49` já injeta
  `--primary`/`--header-bg`/`--link-fg` no `:root` do admin, e o Django 5.2 tem tema escuro
  nativo por `prefers-color-scheme`, independente do `data-tema` do sistema. Fora de escopo:
  o admin é ferramenta de superusuário e o Django resolve sozinho. Reabrir se o operador
  quiser que forçar "claro" no sistema também force claro no admin.
- Migrar o `_nav_visoes.html` do próprio PCA para a inclusion tag — o PCA sofre da mesma
  repetição de 12 linhas, mas alterar `/opt/web/pca` está fora desta fase.

</deferred>

---

*Phase: 07-herdar-o-design-system-do-pca*
*Context gathered: 2026-08-23 via /gsd-plan-phase (decisões travadas pelo operador)*
