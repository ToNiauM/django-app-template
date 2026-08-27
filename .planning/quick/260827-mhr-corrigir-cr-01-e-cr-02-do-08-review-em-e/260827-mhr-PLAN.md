---
phase: quick-260827-mhr
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py"
  - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_filtros.html"
  - .template-tests/fixtures/guia/apps/diarias/views.py
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html
autonomous: true
requirements: [CR-01, CR-02]

must_haves:
  truths:
    - "Clicar duas vezes num cabeçalho de coluna inverte a ordenação (a URL montada nunca carrega `ordem` duplicado)"
    - "Digitar na busca dispara GET HTMX com debounce de 300ms; trocar qualquer select de filtro dispara GET HTMX imediato"
    - "exemplo e diarias permanecem espelhos modulo domínio nos trechos alterados"
  artifacts:
    - path: "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py"
      provides: "extrair_querystring_filtros com excluir=(\"pagina\", \"ordem\")"
      contains: "excluir=(\"pagina\", \"ordem\")"
    - path: ".template-tests/fixtures/guia/apps/diarias/views.py"
      provides: "extrair_querystring_filtros com excluir=(\"pagina\", \"ordem\")"
      contains: "excluir=(\"pagina\", \"ordem\")"
    - path: "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_filtros.html"
      provides: "gatilhos vivos no form dono do hx-get (busca + categoria + status)"
      contains: "hx-trigger=\"submit,"
    - path: ".template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html"
      provides: "gatilhos vivos no form dono do hx-get (busca + status)"
      contains: "hx-trigger=\"submit,"
  key_links:
    - from: "_filtros.html <form id=form-filtros>"
      to: "view de listagem (item_listar / viagem_listar)"
      via: "hx-get + hx-trigger com from:find nos controles"
      pattern: "hx-trigger=\"submit, input changed delay:300ms from:find"
---

<objective>
Corrigir os 2 achados críticos do 08-REVIEW.md em ESPELHO no app de referência (`apps/exemplo`) e no fixture do guia (`apps/diarias`):

- **CR-01:** `extrair_querystring_filtros` deixa `ordem` dentro da querystring de filtros; os cabeçalhos de tabela montam `?ordem={novo}&{{ querystring_filtros }}` e o Django devolve o ÚLTIMO valor (o antigo) — a alternância de ordenação vira no-op após o primeiro sort ou qualquer filtro.
- **CR-02:** `hx-trigger` "naked" (sem verbo AJAX no mesmo elemento) é no-op no htmx 1.9.12 — busca com debounce e filtro por select não disparam requisição nenhuma.

Purpose: o fixture `diarias` é o artefato canônico que todo leitor do guia vai copiar; os defeitos se propagam para cada sistema derivado. Corrigir só um lado faria guia e referência divergirem.
Output: 4 arquivos corrigidos (2 views.py + 2 _filtros.html), suíte `.template-tests` integral verde.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/08-exemplo-provado/08-REVIEW.md
@.planning/STATE.md

**ATENÇÃO a paths com Jinja:** o diretório do app exemplo chama-se literalmente `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/` (sintaxe Copier no NOME do diretório). Em bash, SEMPRE entre aspas duplas: `"apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py"`. Com as ferramentas Edit/Write, usar o path absoluto tal qual.

**Estado atual verificado (não re-verificar, já lido no planejamento):**

1. Ambos os `views.py` têm a mesma assinatura hoje:
   `def extrair_querystring_filtros(params, excluir=("pagina",)):`
   - exemplo: logo após o dict `COLUNAS_ORDENACAO_PERMITIDAS`
   - fixture: idem (linha ~37)

2. `_filtros.html` do **exemplo** tem TRÊS controles com gatilhos órfãos:
   - `<input name="q">` com `hx-trigger="input changed delay:300ms, search"`
   - `<select name="categoria">` com `hx-trigger="change"`
   - `<select name="status">` com `hx-trigger="change"` (select SIMPLES, sem `multiple`)

3. `_filtros.html` do **fixture** tem DOIS controles com gatilhos órfãos:
   - `<input name="q">` com `hx-trigger="input changed delay:300ms, search"`
   - `<select name="status">` com `hx-trigger="change"` (select simples)

4. Nenhum teste interno asserta o markup antigo nem a assinatura do helper: `apps/.../tests/test_crud.py` e o test_crud.py do fixture só passam `ordem` como parâmetro único direto na view (grep já feito por `hx-trigger|extrair_querystring|excluir=` em todos os `.py` de testes — zero ocorrências). Portanto, em princípio NENHUM teste precisa mudar; a contingência da Task 3 cobre o caso de algum teste de nível de template (`test_08_*`) reprovar.
</context>

<tasks>

<task type="auto">
  <name>Task 1: CR-01 — excluir `ordem` da querystring de filtros nos dois views.py</name>
  <files>apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py, .template-tests/fixtures/guia/apps/diarias/views.py</files>
  <action>
Nos DOIS arquivos, alterar a assinatura de `extrair_querystring_filtros` de `excluir=("pagina",)` para `excluir=("pagina", "ordem")` e acrescentar comentário pt-BR curto imediatamente acima do `def`, conforme o fix literal do CR-01:

`# ordem é reanexada explicitamente pelos templates e nunca deve viajar dentro da querystring de filtros.`

Manter a docstring e o corpo da função intactos. A edição é idêntica byte a byte nos dois arquivos (a função é igual nos dois) — o fixture é espelho didático do exemplo. Não tocar em mais nada nos views.py (WR-02/WR-03/IN-* ficam de fora por decisão do operador).
  </action>
  <verify>
    <automated>grep -c 'excluir=("pagina", "ordem")' "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py" .template-tests/fixtures/guia/apps/diarias/views.py — cada arquivo retorna exatamente 1; e grep -c 'reanexada explicitamente' nos dois retorna 1 cada</automated>
  </verify>
  <done>Ambos os `views.py` com `excluir=("pagina", "ordem")` + comentário pt-BR; nenhuma outra linha alterada nesses arquivos.</done>
</task>

<task type="auto">
  <name>Task 2: CR-02 — mover gatilhos vivos para o form dono do hx-get nos dois _filtros.html</name>
  <files>apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_filtros.html, .template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html</files>
  <action>
Em cada `_filtros.html`, adicionar `hx-trigger` ao `<form id="form-filtros">` (o elemento que já possui `hx-get`/`hx-target`/`hx-swap`/`hx-push-url` — manter TODOS esses atributos e a `class` intactos), com seletores `from:find` adaptados aos names REAIS de cada template:

**Exemplo** (3 controles: q, categoria, status — ambos selects simples):
`hx-trigger="submit, input changed delay:300ms from:find input[name='q'], change from:find select[name='categoria'], change from:find select[name='status']"`

**Fixture diarias** (2 controles: q, status — select simples):
`hx-trigger="submit, input changed delay:300ms from:find input[name='q'], change from:find select[name='status']"`

Em seguida, REMOVER os atributos `hx-trigger` órfãos dos controles:
- exemplo: linha `hx-trigger="input changed delay:300ms, search"` do input `name="q"` e as duas linhas `hx-trigger="change"` dos selects `categoria` e `status`
- fixture: linha `hx-trigger="input changed delay:300ms, search"` do input `name="q"` e a linha `hx-trigger="change"` do select `status`

Os dois templates devem ficar equivalentes modulo domínio (exemplo tem o bloco extra de categoria e names/urls próprios; fora isso, mesma estrutura de trigger). Nenhum hex novo, nenhuma classe alterada, nenhum outro atributo tocado. As aspas simples dentro dos seletores são seguras dentro do atributo HTML entre aspas duplas.
  </action>
  <verify>
    <automated>grep -c "hx-trigger" em cada _filtros.html retorna exatamente 1 (só o do form); grep -c "from:find input\[name='q'\]" retorna 1 em cada; grep -c "select\[name='categoria'\]" retorna 1 no exemplo e 0 no fixture; grep -c 'hx-trigger="change"' retorna 0 nos dois</automated>
  </verify>
  <done>Único `hx-trigger` por template, no `<form>`, com `submit` + debounce 300ms na busca + `change` nos selects; gatilhos órfãos removidos; demais atributos do form preservados.</done>
</task>

<task type="auto">
  <name>Task 3: Suíte integral .template-tests verde (com rebuild disparado pelo drift do fixture)</name>
  <files>(nenhum novo — contingência: testes que assertem o markup antigo)</files>
  <action>
Rodar a suíte integral:

`python3 -m unittest discover -s .template-tests -p 'test_*.py'`

**Instrução operacional obrigatória:** a mudança no fixture dispara drift/rebuild da cópia de ensaio no test_08 (copier + docker build + healthz), então o comando é LENTO — usar `timeout: 600000` (o máximo) na chamada Bash e, como pode passar de 10 min, preferir `run_in_background: true` e monitorar a saída até o veredito final (`OK` ou lista de falhas). NÃO interpretar timeout da ferramenta como falha da suíte — relançar em background e aguardar o processo concluir.

**Contingência (só se houver falha):** se algum teste de `.template-tests/test_08_*` ou dos apps (`apps/.../tests/`, fixture `tests/`) reprovar por assertar o markup/comportamento antigo (ex.: grep de `hx-trigger` no input, ou querystring contendo `ordem`), atualizar ESSE teste para o comportamento novo — mantendo o espelho exemplo↔diarias se o teste existir dos dois lados. Grep de planejamento indica que nenhum teste atual asserta o markup antigo, então o esperado é verde sem edição extra. Qualquer falha NÃO relacionada aos 4 arquivos alvo deve ser reportada, não "consertada" por escopo alargado.
  </action>
  <verify>
    <automated>python3 -m unittest discover -s .template-tests -p 'test_*.py' termina com OK (timeout 600000 ms; se estourar, run_in_background e aguardar)</automated>
  </verify>
  <done>Suíte integral verde; nenhum arquivo além dos 4 alvos (+ eventuais testes acompanhantes) modificado; WR-01..03 intocados.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| querystring do usuário → view de listagem | entrada não confiável (`ordem`, `q`, `status`, `categoria`) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-qmhr-01 | Tampering | `extrair_querystring_filtros` / `order_by` | mitigate | mudança só REMOVE `ordem` do echo da querystring; a whitelist `COLUNAS_ORDENACAO_PERMITIDAS` permanece a única porta para o `order_by` (intocada) |
| T-qmhr-02 | Injection/XSS | atributos `hx-trigger` nos templates | accept | valores estáticos, sem interpolação de entrada do usuário; autoescape do Django cobre os demais atributos (inalterados) |
</threat_model>

<verification>
- `grep -c 'excluir=("pagina", "ordem")'` = 1 em cada views.py alvo
- `grep -c "hx-trigger"` = 1 em cada `_filtros.html` (somente no `<form>`)
- Diff restrito aos 4 arquivos alvo (+ testes acompanhantes, se a contingência da Task 3 disparar)
- `python3 -m unittest discover -s .template-tests -p 'test_*.py'` → OK integral
</verification>

<success_criteria>
- CR-01 e CR-02 corrigidos em espelho (exemplo ↔ diarias), conforme fix literal do 08-REVIEW.md com seletores adaptados aos names reais (exemplo inclui `select[name='categoria']`)
- Nenhum toque em WR-01..03, IN-01..08 ou arquivos fora do escopo
- Nenhum hex novo em templates
- Suíte `.template-tests` integral verde
</success_criteria>

<output>
Create `.planning/quick/260827-mhr-corrigir-cr-01-e-cr-02-do-08-review-em-e/260827-mhr-SUMMARY.md` when done
</output>
