---
phase: 07-herdar-o-design-system-do-pca
reviewed: 2026-08-23T00:00:00Z
depth: standard
files_reviewed: 38
files_reviewed_list:
  - .template-tests/ensaio_django.sh
  - .template-tests/test_04_03_identity.py
  - .template-tests/test_04_04_optional_exemplo.py
  - .template-tests/test_04_06_operations.py
  - .template-tests/test_07_cor_runtime.sh
  - .template-tests/test_07_nav_extensao.py
  - .template-tests/test_07_tokens.py
  - .template-tests/test_copier_copy.sh
  - .template-tests/test_copier_update.sh
  - Dockerfile
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/README.md.jinja
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_confirmar_exclusao_modal.html
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_form_modal.html
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_tabela_resultado.html
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/item_listar.html
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py
  - apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py
  - copier.yml
  - core/context_processors.py
  - core/static/src/dominio.css
  - core/static/src/input.css
  - core/tema.py
  - core/templates/base.html
  - core/templates/core/_item_nav.html
  - core/templates/core/_nav.html
  - core/templates/core/_nav.html.jinja
  - core/templates/core/_nav_dominio.html.jinja
  - core/templates/core/login.html
  - core/templates/core/shell.html
  - core/templatetags/navegacao.py
  - core/tests/test_navegacao.py
  - core/tests/test_tema.py
  - core/tests/test_tema_escuro.py
  - core/views.py
  - tailwind.config.js
  - tailwind.config.js.jinja
  - README.md
findings:
  critical: 4
  warning: 15
  info: 10
  total: 29
status: issues_found
---

# Fase 7: Relatório de Revisão de Código

**Revisado:** 2026-08-23
**Profundidade:** standard
**Arquivos revisados:** 38
**Status:** issues_found

## Resumo

A fase entrega bastante: os tokens saíram do build-time para o runtime, o
ponto de extensão da navegação é real e o gate "zero hex em template" é
verificável. Mas a revisão adversarial encontrou **quatro defeitos
bloqueantes** que passaram por todos os gates da fase, todos na mesma
categoria: **as provas executáveis provam menos do que os SUMMARYs afirmam.**

1. A inclusion tag `{% item_nav %}` marca **dois itens como ativos ao mesmo
   tempo** na configuração que o próprio template semeia — e os 6 testes de
   `test_navegacao.py` escolheram exatamente a combinação de argumentos que
   não expõe a colisão.
2. A migração de `brand` para variável de tema criou um par
   `bg-brand`/`text-white` com **2,56:1 de contraste no tema escuro** (1,76:1
   no hover), em 4 sítios, para **qualquer** `COR_PRIMARIA` — porque
   `com_hsl(cor, 1.0, 0.727)` sempre produz uma cor clara.
3. A 4ª fatia do donut é `brand-tint` (o token de *fundo tênue*): **1,11:1 no
   claro e 1,00:1 no escuro** contra o card — a fatia é literalmente
   invisível, contradizendo o racional de D-84 ("todo derivado ganha um donut
   coerente… CVD-safe").
4. O gate da régua tipográfica **nunca detecta `text-[NNpx]`**: o ramo de
   valor arbitrário do regex é código morto (`\b` depois de `]`). O 07-07
   afirma "zero `text-[NNpx]` na árvore, gate executável instalado e
   comprovado por 2 provas negativas" — as duas provas exercitaram só o outro
   ramo.

O checkpoint humano bloqueante do 07-08 declarou verificados "raio de 2px em
todos os cantos" e "repintura dos gráficos ao trocar o tema" — o primeiro é
falso na fonte (`.form-row` usa `rounded-[6px]`, `.btn` usa `rounded-none`) e
o segundo repinta com uma grade invisível no escuro (WR-04).

## Critical Issues

### CR-01: `{% item_nav %}` marca dois itens ativos simultaneamente

**Arquivo:** `core/templatetags/navegacao.py:55` (semeadura em `core/templates/core/_nav_dominio.html.jinja:14-15`)

**Issue:**

```python
ativo = caminho == url or bool(prefixo and caminho.startswith(prefixo))
```

O stub semeado pelo template declara os dois itens do app exemplo assim:

```
{% item_nav "exemplo:dashboard"    "Dashboard"     "grafico" %}
{% item_nav "exemplo:item_listar"  "Itens (CRUD)"  "lista"    "/exemplo/" %}
```

E `apps/exemplo/urls.py` resolve `exemplo:item_listar` → `/exemplo/` e
`exemplo:dashboard` → `/exemplo/dashboard/`.

Em `/exemplo/dashboard/`:
- **Dashboard** → `caminho == url` → `ativo = True`
- **Itens (CRUD)** → `"/exemplo/dashboard/".startswith("/exemplo/")` → `ativo = True`

Resultado: **dois `<a aria-current="page">` na mesma `<nav>`**, dois filetes de
2px e dois fundos `bg-brand-tint` acesos. É comportamento incorreto no
artefato de referência que todo sistema derivado recebe e copia, e viola o
propósito declarado de `aria-current="page"` (indicar *a* localização atual).

A cobertura não pega porque `core/tests/test_navegacao.py:46-53`
(`test_prefixo_marca_ativo_em_rota_filha`) testa `prefixo="/exemplo/"` com a
rota **`core:shell`** (url `/`) — uma combinação que não existe no produto e
que é justamente a única em que a colisão não pode acontecer.

**Fix:** a tag precisa saber que uma correspondência exata vence uma
correspondência por prefixo. Solução mínima, sem estado compartilhado:

```python
@register.inclusion_tag("core/_item_nav.html", takes_context=True)
def item_nav(context, rota, rotulo, icone="", prefixo="", excecoes=""):
    """`excecoes`: prefixos separados por espaço que NÃO ativam este item
    mesmo estando sob `prefixo` (rotas-irmãs com item próprio no menu)."""
    try:
        url = reverse(rota)
    except NoReverseMatch:
        return {"url": ""}

    caminho = context.get("request").path if context.get("request") else ""
    sob_prefixo = bool(prefixo) and caminho.startswith(prefixo)
    excluido = any(caminho.startswith(p) for p in excecoes.split() if p)
    ativo = caminho == url or (sob_prefixo and not excluido)
    ...
```

e no stub semeado:

```
{% item_nav "exemplo:dashboard"   "Dashboard"    "grafico" %}
{% item_nav "exemplo:item_listar" "Itens (CRUD)" "lista" "/exemplo/" "/exemplo/dashboard/" %}
```

Acrescente um teste que renderize os **dois** itens em `/exemplo/dashboard/` e
asserte `html.count('aria-current="page"') == 1`.

---

### CR-02: `text-white` sobre `bg-brand` reprova AA no tema escuro (2,56:1) para qualquer `COR_PRIMARIA`

**Arquivos:**
- `core/static/src/input.css:56` — `.btn--primaria { @apply bg-brand text-white hover:bg-brand-hover; }`
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_form_modal.html:135` — "Salvar item"
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/item_listar.html:20` — "Novo item"
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_tabela_resultado.html:215` — página ativa da paginação (`text-xs`, 11px)

**Issue:** antes desta fase `bg-brand` era um hex fixo de build-time
(`#1e40af`) e `text-white` sobre ele dava **8,72:1**. A fase migrou `brand`
para `var(--cor-brand)` **com override escuro** derivado por
`com_hsl(cor, 1.00, 0.727)` (`core/tema.py:90`) — luminosidade HSL fixada em
72,7%, ou seja, **sempre uma cor clara**, para qualquer `COR_PRIMARIA`. Com o
default `#1e40af` o escuro é `#889feb`:

| par | contraste | AA texto (4,5:1) |
|---|---|---|
| `#ffffff` sobre `#889feb` (`bg-brand`, escuro) | **2,56:1** | reprova |
| `#ffffff` sobre `#b4c2f2` (`bg-brand-hover`, escuro) | **1,76:1** | reprova |

Não é um valor infeliz da paleta default — é estrutural: a derivação garante
uma cor de marca clara no escuro, então branco por cima **sempre** reprova. O
`dominio.css` que a própria fase escreveu declara "Piso de contraste, nos DOIS
temas: 4,5:1 para texto".

Nenhum teste desta fase mede contraste; o checkpoint humano do 07-08 conferiu
"legibilidade da régua encolhida" mas não o par texto/fundo dos botões.

**Fix:** introduzir o par de texto da marca como token, no mesmo padrão
fundo+texto que `dominio.css` já contratualiza:

```css
/* core/static/src/input.css */
:root                    { --cor-brand-tx: #ffffff; }
[data-tema="escuro"]     { --cor-brand-tx: #0f0e0d; }  /* = --cor-page escuro */
```

```js
// tailwind.config.js
"brand-tx": "var(--cor-brand-tx)",
```

e trocar `text-white` por `text-brand-tx` nos 4 sítios acima (incluindo
`.btn--primaria`). Com `#0f0e0d` sobre `#889feb` o contraste vai a **7,54:1**.
Acrescente o par ao `familia_marca()`/`css_da_marca()` se quiser que ele
acompanhe `COR_PRIMARIA`, ou mantenha-o neutro (é sempre page/ink).

---

### CR-03: a 4ª fatia do donut é invisível (1,11:1 no claro, 1,00:1 no escuro)

**Arquivo:** `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py:228` e `:234`

**Issue:** `StatusChoices` tem 4 valores, mas a rampa sequencial derivada tem
3 degraus (`seq-600`/`seq-450`/`seq-300`, D-84). A implementação completou o
4º slot com `brand-tint` — o token que `core/static/src/input.css:84` define
como "fundo tênue do item ativo", isto é, um **fundo**, não uma cor de dado.

| fatia | fundo do card | contraste |
|---|---|---|
| `brand-tint` claro `#edf0f9` | `bg-surface` `#fcfcfb` | **1,11:1** |
| `brand-tint:escuro` `#192035` | `dark:bg-surface-2` `#22211d` | **1,00:1** |

A 4ª categoria de status não tem fatia visível em nenhum dos dois temas — e a
borda das fatias é desenhada em `corSurface` (`dashboard.html:220`), o que
elimina até o contorno. O donut mente sobre a distribuição dos dados.

`test_dashboard.py:152-160` só verifica que são 4 strings no formato
`#RRGGBB`; nenhuma asserção de distinguibilidade.

**Fix:** estender a rampa com um 4º degrau real em vez de reaproveitar o
tint. Em `core/tema.py`:

```python
"seq-150": misturar(cor, 255, 0.80),          # 4º degrau da rampa
"seq-150:escuro": com_hsl(cor, 0.45, 0.300),
```

e em `views.py` trocar `familia_clara["brand-tint"]` / `["brand-tint:escuro"]`
por `["seq-150"]` / `["seq-150:escuro"]`. Acrescente um teste que calcule o
contraste de cada fatia contra `--cor-surface` (claro) e `--cor-surface-2`
(escuro) e exija ≥ 3:1 — é o piso de elemento gráfico que o próprio
`dominio.css` contratualiza.

---

### CR-04: o gate da régua tipográfica nunca detecta `text-[NNpx]` (ramo morto no regex)

**Arquivo:** `.template-tests/test_07_tokens.py:224` (e o ramo morto em `:232`)

**Issue:**

```python
TEXT_CLASS_RE = re.compile(r"\btext-([a-z0-9]+|\[[^\]]+\])\b")
```

O `\b` final exige uma fronteira de palavra depois do `]`. Como `]` é
não-palavra, a fronteira só existe se o **próximo** caractere for de palavra —
o que nunca acontece num atributo de classe (o próximo caractere é espaço ou
aspa). Verificado:

```
'class="text-[13px] font-bold"'  -> []
'class="font-bold text-[13px]"'  -> []
"class='text-[20px]'"            -> []
'class="text-2xl"'               -> ['2xl']     # só o outro ramo funciona
'class="text-[13px]x"'           -> ['[13px]']  # só com um caractere de palavra colado
```

Consequência: `e_valor_arbitrario = sufixo.startswith("[")` na linha 232 é
**código inalcançável**, e qualquer template pode escrever `text-[24px]` que o
gate passa em silêncio. O 07-07-SUMMARY declara "zero `text-2xl`+ e zero
`text-[NNpx]` na árvore, gate executável instalado e comprovado por 2 provas
negativas" — as duas provas negativas registradas (`text-2xl` no template e
`"2xl"` no `fontSize`) exercitam apenas o ramo `[a-z0-9]+`. O ramo que
justifica metade do gate nunca foi executado.

**Fix:**

```python
TEXT_CLASS_RE = re.compile(r"\btext-(\[[^\]]*\]|[a-z0-9]+)(?![\w-])")
```

(alternativa mais específica primeiro, e lookahead negativo em vez de `\b`).
Adicione uma prova negativa que insira `text-[24px]` num template e confirme
que o teste falha citando `arquivo:linha`.

## Warnings

### WR-01: script de tema quebra por completo quando `localStorage` está indisponível

**Arquivos:** `core/templates/base.html:43,51,53` e `core/templates/core/shell.html:40`

**Issue:** `aplicarTema()` chama `localStorage.setItem("tema", guardada)`
**antes** de escrever `data-tema` (linha 46). Em contexto onde o storage é
bloqueado (política corporativa, iframe com storage partitioning, modo privado
em navegadores antigos) o `setItem` lança `SecurityError` e:

1. `data-tema` nunca é gravado — o tema fica indefinido;
2. a exceção propaga para fora do `<script>` inline **síncrono**, abortando o
   bloco inteiro — o listener de `matchMedia` (linhas 52-54) nunca é registrado;
3. `shell.html:40` (`x-data="{ ..., tema: localStorage.getItem('tema') || 'auto' }"`)
   lança na inicialização do Alpine → `sidebarAberta` nunca existe, `x-cloak`
   nunca é removido e a **gaveta mobile e a `<aside>` ficam permanentemente
   invisíveis abaixo de 768px**, levando navegação, identidade e logout junto.

O `limparCachePwa()` logo abaixo tem `try/catch` justamente por esse motivo; o
script de tema não tem.

**Fix:** isolar todo acesso a storage e nunca deixá-lo bloquear a escrita do
atributo:

```js
function lerTema() { try { return localStorage.getItem("tema"); } catch (e) { return null; } }
function gravarTema(v) { try { localStorage.setItem("tema", v); } catch (e) {} }

window.aplicarTema = function (preferencia) {
  var guardada = ["auto","claro","escuro"].indexOf(preferencia) >= 0 ? preferencia : "auto";
  var escuro = guardada === "escuro" ||
    (guardada === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.setAttribute("data-tema", escuro ? "escuro" : "claro");
  gravarTema(guardada);                       // depois do atributo, nunca antes
  ...
};
window.aplicarTema(lerTema() || "auto");
```

e em `shell.html` usar `tema: (window.lerTema && lerTema()) || 'auto'`.

---

### WR-02: `item_nav` acessa `context["request"]` sem guarda

**Arquivo:** `core/templatetags/navegacao.py:54`

**Issue:** `caminho = context["request"].path` levanta `KeyError` em qualquer
render que não passe pelo `django.template.context_processors.request` —
`render_to_string()` sem `request=`, templates de e-mail, geração de PDF,
comandos de management. O `try/except` só protege o `reverse()`. O arquivo é
explicitamente um ponto de extensão para sistemas derivados, que vão usar
`{% item_nav %}` em contextos que este repositório não prevê.

**Fix:**

```python
request = context.get("request")
caminho = request.path if request is not None else ""
```

(com `caminho = ""` o item renderiza inativo em vez de derrubar o render).

---

### WR-03: regressão de contraste em `--cor-muted` (4,37:1 → 3,41:1)

**Arquivo:** `core/static/src/input.css:106`

**Issue:** o valor claro de `muted` passou de `#77756f` (versão anterior, em
`tailwind.config.js.jinja`) para `#898781`:

| par | antes | depois |
|---|---|---|
| `text-muted` sobre `--cor-page` `#f9f9f7` | 4,37:1 | **3,41:1** |
| `text-muted` sobre `--cor-surface-2` `#f3f2ef` | — | **3,21:1** |

São 21 ocorrências de `text-muted` em `core/templates` + `apps`, quase todas
em `text-xs` (11px) e `text-sm` (12px) — inclusive o link **"Sair"** do rodapé
da aside (`shell.html:135`) e o subtítulo do sistema (`shell.html:69`). Texto
pequeno em 3,2–3,4:1 reprova AA e fica no limite do AA Large. A régua de 07-07
encolheu os degraus **e** a paleta clareou o token no mesmo ciclo, e nenhum
gate mede contraste.

**Fix:** voltar `--cor-muted` para um valor ≥ 4,5:1 sobre `--cor-surface-2`
(o pior fundo claro), por exemplo `#6f6d67` (≈ 4,9:1 sobre `#f3f2ef`), ou
restringir `text-muted` a papéis não-textuais. Acrescente um teste de
contraste que leia `input.css` e verifique os pares texto/fundo declarados.

---

### WR-04: o chrome dos gráficos lê `--cor-surface` mas o card é `dark:bg-surface-2`

**Arquivo:** `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html:170` e `:220`

**Issue:** a Task 3 do 07-06 subiu os dois cards de gráfico para o nível
Elevado (`dark:bg-surface-2`), mas o script continua lendo o chrome do nível
Base:

- `splitLine: { lineStyle: { color: corSurface2 } }` (linha 170) — no escuro
  `--cor-surface-2` é `#22211d`, **exatamente a cor do card**: contraste
  **1,00:1**, grade do eixo Y invisível.
- `itemStyle: { borderColor: corSurface }` do donut (linha 220) — no escuro
  `--cor-surface` é `#181614`, mais escuro que o card `#22211d`: as separações
  entre fatias viram linhas escuras que não existem no tema claro.

O SUMMARY 07-06 registra que a verificação foi por "evidência equivalente"
(as 6 variáveis existem nos dois blocos, `node -c` no script), o que confirma
que a leitura funciona — mas não que o valor lido é o **certo** para o
elemento em que o gráfico está montado.

**Fix:** ler o fundo real do container em vez de assumir o nível Base:

```js
function corDoFundoDoCard(el) {
  return getComputedStyle(el.closest("[class*='bg-surface']") || el).backgroundColor;
}
// ou, mais simples e coerente com o mapeamento de elevação de shell.html:
const corCard = temaAtual() === "escuro" ? corSurface2 : corSurface;
// splitLine usa --cor-grid (que já é o token de linha), não uma superfície:
splitLine: { lineStyle: { color: corGrid } },
itemStyle: { borderColor: corCard, borderWidth: 2 },
```

---

### WR-05: `dominio.css` documenta um contrato que quebra o build do Tailwind

**Arquivo:** `core/static/src/dominio.css:18`

**Issue:** o stub instrui o sistema derivado a escrever

```css
.status-dot[data-estado="x"] { background: theme("colors.st-x"); }
```

Mas `colors` vive em `tailwind.config.js`, que abre com
`// ARQUIVO DO NÚCLEO — não edite` (linha 3) e tem um mapa fechado de 21
chaves — nenhuma `st-*`. `theme("colors.st-x")` com caminho inexistente faz o
Tailwind **abortar o build** (`'st-x' does not exist in your theme config`),
e o estágio `assets` do `Dockerfile` sai com erro. Ou seja: seguir o contrato
escrito, literalmente, derruba a imagem — e a única saída é editar o arquivo
que o núcleo proíbe editar.

**Fix:** trocar o exemplo por `var()`, que é o que a arquitetura da fase
realmente suporta e não depende do config:

```css
.status-dot[data-estado="x"] { background: var(--cor-st-x); }
```

e documentar explicitamente que tokens de domínio são consumidos por `var()`,
não por `theme()`/classes utilitárias, porque `tailwind.config.js` é do núcleo.

---

### WR-06: o "raio único de 2px" não vale para campos de formulário nem para `.btn`

**Arquivo:** `core/static/src/input.css:46` e `:52`

**Issue:** D-82 fixa "raio único de 2px colapsando as 6 chaves", e a Task 2 do
07-08 (`checkpoint:human-verify`, gate bloqueante) registra como conferido
"raio de 2px em todos os cantos". Na fonte:

- `.form-row { @apply ... rounded-[6px] ... }` → **6px**, valor arbitrário que
  contorna o token;
- `.btn { @apply rounded-none ... }` → **0px**.

`test_07_tokens.py:139-140` valida que todas as chaves de `borderRadius` valem
`"2px"`, mas não varre o CSS por `rounded-[...]`/`rounded-none` — então o gate
passa e a afirmação do checkpoint fica sem lastro na fonte.

**Fix:** ou alinhar as duas classes ao token (`rounded-sm` nas duas), ou
registrar as exceções explicitamente no comentário do `@layer components` e
acrescentar ao gate uma asserção que só permita `rounded-[...]` na lista de
exceções declaradas.

---

### WR-07: `test_derivado_adiciona_itens_sem_tocar_o_nav_do_nucleo` é tautológico

**Arquivo:** `.template-tests/test_07_nav_extensao.py:80-98`

**Issue:** o teste lê os bytes de `_nav.html`, escreve em **outro arquivo**
(`_nav_dominio.html`) e depois asserta que `_nav.html` não mudou. Nenhum
código toca `_nav.html` entre as duas leituras — a asserção **não pode
falhar** em nenhuma circunstância, nem se o ponto de extensão inteiro for
removido. É apresentada no SUMMARY 07-03 como "prova executável do critério
5". A parte que de fato prova algo é a verificação de que `_nav.html` só
referencia rotas `core:` (linhas 99-107); a comparação byte a byte é ruído
que dá falsa segurança.

**Fix:** substituir por uma asserção que possa falhar: renderizar as duas
variantes (`incluir_app_exemplo` true/false) e comparar `_nav.html` byte a
byte entre elas (o que `test_04_04_optional_exemplo.py:96-101` já faz
corretamente), ou remover a comparação vazia e manter só a checagem de rotas.

---

### WR-08: `ocorrencias_fora_do_contrato` é código morto que aparenta uma segunda verificação

**Arquivo:** `.template-tests/test_07_tokens.py:182-199`

**Issue:** o teste monta duas listas. A segunda percorre
`(bg|border|fill|text)-secundaria` e só acumula quando
`match.group(1).startswith("text-")` — ou seja, o filtro anula três das quatro
alternativas, tornando `ocorrencias_fora_do_contrato` **logicamente idêntica**
a `ocorrencias_texto`. O nome da variável ("fora do contrato") sugere que
usos além de `text-` também são auditados; nenhum é.

**Fix:** ou remover a segunda lista, ou implementar o que o nome promete —
por exemplo, exigir que todo uso de `secundaria` esteja num prefixo da lista
permitida (`bg`/`border`/`fill`) e falhar em qualquer outro (`ring-`,
`decoration-`, `divide-`, `caret-`, `placeholder-`).

---

### WR-09: ordem de redireção invertida engole o diagnóstico da restauração

**Arquivo:** `.template-tests/test_07_cor_runtime.sh:79`

**Issue:**

```sh
bash "${ENSAIO}" compor up -d web >&2 2>/dev/null || :
```

As redireções são aplicadas da esquerda para a direita: `>&2` faz o fd 1
apontar para onde o fd 2 aponta **naquele instante** (o terminal); só depois
`2>/dev/null` redireciona o fd 2. Resultado: o **stdout** do comando continua
vazando para o stderr do chamador, e o **stderr** (as mensagens de erro reais
do Compose) é descartado. Exatamente o inverso da intenção, e inconsistente
com as linhas 116 e 134, que usam só `>&2`.

Como isto está dentro do `restaurar()` do `trap`, o efeito prático é: se a
restauração do banco de ensaio falhar, o motivo desaparece e o banco fica com
`COR_PRIMARIA=#0f766e` para os gates seguintes, sem nenhum rastro.

**Fix:** `bash "${ENSAIO}" compor up -d web >/dev/null 2>&1 || :` (silenciar
os dois) ou `bash "${ENSAIO}" compor up -d web >&2 || :` (preservar
diagnóstico, coerente com os outros dois sítios).

---

### WR-10: apagar `_nav_dominio.html` derruba todas as páginas autenticadas com 500

**Arquivos:** `core/templates/core/_nav.html:18`, `core/templates/core/_nav_dominio.html.jinja:2`

**Issue:** `_nav.html` faz `{% include "core/_nav_dominio.html" %}` sem guarda.
O `{% include %}` do Django com string literal levanta `TemplateDoesNotExist`
quando o arquivo some — não existe `ignore missing` (isso é Jinja2). O próprio
stub anuncia em letras maiúsculas "ESTE ARQUIVO É DO SEU SISTEMA", o que
convida um mantenedor de derivado a apagá-lo quando não quiser itens de menu.
O resultado é **500 em toda página que estenda `shell.html`**, não um menu
vazio. Nenhum teste cobre a ausência do arquivo.

**Fix:** o Django não tem `ignore missing` (isso é Jinja2), então a inclusão
tolerante precisa vir de uma `simple_tag` no mesmo `navegacao.py`:

```python
@register.simple_tag(takes_context=True)
def nav_dominio(context):
    try:
        tpl = get_template("core/_nav_dominio.html")
    except TemplateDoesNotExist:
        return ""
    return mark_safe(tpl.render(context.flatten()))
```

Alternativa mínima: manter o `{% include %}` e adicionar ao stub um comentário
"não apague este arquivo — esvazie-o", **mais** um teste que renderize `/` com
o arquivo removido e exija comportamento definido.

---

### WR-11: segredos efêmeros gravados em `/tmp` com permissão padrão

**Arquivo:** `.template-tests/ensaio_django.sh:222,249-276`

**Issue:** `criar_banco()` gera `SECRET_KEY` e `POSTGRES_PASSWORD` com
`secrets.token_urlsafe(50)` e os escreve em
`${TMPDIR:-/tmp}/ensaio-django-<uid>-<hash>/copia/.env`. O `mkdir -p` da linha
222 usa a umask padrão (diretório 0755) e o `cp` da linha 249 preserva o modo
do `.env.example` (tipicamente 0644). Num host multiusuário, qualquer usuário
local lê a `SECRET_KEY` do Django e a senha do PostgreSQL de um serviço que
está publicado em `127.0.0.1:<porta>` e que **sobrevive entre invocações por
design** (o banco de ensaio não é derrubado por `trap`). O 07-08 registra que
uma cópia órfã ficou de pé por 3 horas.

**Fix:**

```sh
mkdir -p "${STATE_DIR}"
chmod 700 "${STATE_DIR}"
...
cp "${DESTINO}/.env.example" "${DESTINO}/.env"
chmod 600 "${DESTINO}/.env"
```

---

### WR-12: `familia_marca()` devolve o mesmo dict mutável a todos os chamadores

**Arquivo:** `core/tema.py:74-97`

**Issue:** `@lru_cache` devolve **o objeto cacheado**, não uma cópia. Todo
chamador — `css_da_marca()` a cada request e `dashboard_view()` a cada
requisição do dashboard — recebe a mesma instância de `dict`. Uma mutação
acidental por qualquer consumidor (incluindo código futuro de sistema
derivado, que é o público-alvo deste módulo) envenena o cache para o processo
inteiro, e o efeito só aparece em produção depois do primeiro request.

Inconsistência relacionada: `familia_marca()` é cacheada mas `css_da_marca()`
não é, embora o context processor a chame em **todo** request com o mesmo
argumento imutável (`settings.COR_PRIMARIA`).

**Fix:**

```python
@lru_cache(maxsize=8)
def _familia_marca_cache(cor: str) -> dict[str, str]: ...

def familia_marca(cor: str) -> dict[str, str]:
    return dict(_familia_marca_cache(cor))        # cópia defensiva

@lru_cache(maxsize=8)
def css_da_marca(cor: str) -> str:                # string é imutável, cache seguro
    ...
```

---

### WR-13: tooltip do ECharts monta HTML por concatenação sem escapar

**Arquivo:** `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/dashboard.html:158` e `:210`

**Issue:**

```js
return `<strong>${p.name}</strong><br/>Total: R$ ${valorFormatado}...`;
```

O retorno do `formatter` do ECharts é inserido como **HTML**. `p.name` vem de
`rawCat.map(d => d.categoria)` e `params.name` de `d.rotulo`, ambos montados
em `views.py:249` e `:257` como
`dict(Choices.choices).get(item["x"], item["x"])` — com **fallback para o valor
cru do banco**. `choices` no Django é validação de formulário, não constraint
de banco: um `queryset.update()`, uma migração de dados ou uma carga por SQL
gravam qualquer string, que então chega ao `innerHTML` do tooltip sem escape.

O padrão foi carregado do estado anterior do arquivo (não é novo desta fase),
mas o bloco inteiro foi reescrito por 07-06 e este dashboard é o artefato de
referência que todo sistema derivado copia e adapta para dados de domínio de
verdade — onde `name` **será** entrada de usuário.

**Fix:** escapar antes de concatenar:

```js
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => (
  { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
return `<strong>${esc(p.name)}</strong><br/>Total: R$ ${valorFormatado}...`;
```

---

### WR-14: o teto de 20px existe só no teste, não na configuração

**Arquivo:** `tailwind.config.js:56-63`

**Issue:** `fontSize` está dentro de `theme.extend`, que **acrescenta** ao
tema default em vez de substituí-lo. `text-2xl` … `text-9xl` continuam
existindo e gerando regra; a única barreira é
`test_07_tokens.py::test_templates_so_usam_as_seis_chaves_da_regua_tipografica`
— que, por CR-04, tem metade do escopo morta. Mesma observação para
`borderRadius`: `rounded-3xl` (1,5rem) e `rounded-full` sobrevivem do default.

**Fix:** mover `fontSize` de `theme.extend` para `theme` (substituição), o que
faz o Tailwind **não gerar** nada fora das 6 chaves e transforma o teto em
propriedade da build, não do teste:

```js
theme: {
  fontSize: { xs: [...], sm: [...], base: [...], md: [...], lg: [...], xl: [...] },
  extend: { colors: {...}, borderRadius: {...}, fontFamily: {...} },
}
```

Se a substituição total for indesejada, ao menos corrija CR-04 antes de
confiar no gate.

---

### WR-15: `exigir_ferramentas()` não checa `git`, e uma falha do `git` produz digest válido

**Arquivo:** `.template-tests/ensaio_django.sh:80-84,169-172`

**Issue:** a checagem de pré-requisitos cobre `docker`, `curl` e `python3`,
mas `impressao_atual()` depende de `git ls-files`. Sem `git`, o script morre
com `set -e` numa mensagem do shell, não com a mensagem clara `FALHOU:
ferramenta ausente`.

Pior: como a impressão digital é um **pipe**
(`git … | sort -z | python3 …`), o código de saída do pipe é o do `python3`.
Se o `git` falhar (repositório corrompido, `dubious ownership`), o `python3`
recebe stdin vazio e imprime o sha1 da string vazia — um digest perfeitamente
válido, porém sempre diferente do gravado. Efeito: **recriação completa do
banco de ensaio em toda invocação**, sem nenhum erro visível, com o custo de
`copier copy` + `docker build` a cada gate.

**Fix:** acrescentar `git` à lista de `exigir_ferramentas` e usar
`set -o pipefail` (ou capturar a lista de caminhos numa variável antes de
alimentar o `python3`) para que a falha do `git` seja um erro, não um digest.

## Info

### IN-01: cinco tokens de cor sem nenhum consumidor
`baseline`, `danger-tint`, `warn-bg`, `warn-tx` e `secundaria` são declarados
em `core/static/src/input.css:108-115`, mapeados em `tailwind.config.js:34-39`
e usados por **zero** templates e zero classes de componente. `destructive` é
usado apenas pela classe morta `.btn--destrutiva`. Como
`test_07_tokens.py:82-83` crava as contagens em 21/18, a limpeza exige editar
o teste. Sugestão: manter e documentar como vocabulário reservado, ou remover
os cinco e ajustar as constantes.

### IN-02: as 8 classes de `@layer components` são CSS morto
`.results`, `.module`, `.form-row`, `.btn` e as 4 `.btn--*` não aparecem em
nenhum template de `core/templates` nem de `apps`. Os nomes são do Django
admin (`results`/`module`/`form-row`), mas
`core/templates/admin/base_site.html` só injeta `<style>{{ admin_tema_css }}</style>`
— **o admin não carrega `dist/tailwind.css`**, então as regras nunca se
aplicam. `test_safelist_bate_com_as_classes_declaradas_em_input_css` compara a
safelist com o próprio `input.css` (circular) e não prova consumo.

### IN-03: `fontSize.md` declarado e nunca usado
`tailwind.config.js:60`. O próprio 07-07-SUMMARY registra "`text-md` não foi
necessário em nenhum sítio". Degrau da régua sem consumidor.

### IN-04: `JSON.parse` sem fallback só no terceiro `json_script`
`dashboard.html:112` usa `JSON.parse(elPaletaData.textContent)` enquanto as
linhas 104-105 usam `|| "[]"`. Inconsistente; um `<script>` vazio lança
`SyntaxError` e derruba os dois gráficos.

### IN-05: `_corpo_limpar_cache_pwa` depende de indentação exata
`core/tests/test_tema_escuro.py:42` usa `html.index("\n    }", inicio)` — 4
espaços literais. Reindentar `base.html` faz o teste levantar `ValueError` em
vez de falhar com mensagem. Um `re.search(r"function limparCachePwa.*?\n {4}\}", html, re.S)`
com `assertIsNotNone` degrada melhor.

### IN-06: asserções quase vazias em `test_tema_escuro.py`
`assertIn("dark:", corpo)` (linha 250) e `assertIn("Flutuante", html)`
(linha 238, procura uma palavra dentro de um `{% comment %}`) passam
trivialmente e não protegem o comportamento que os nomes dos testes prometem.

### IN-07: `test_prefixo_marca_ativo_em_rota_filha` testa uma combinação inexistente
`core/tests/test_navegacao.py:46-53` usa `rota="core:shell"` com
`prefixo="/exemplo/"` — nenhum sítio do produto faz isso, e é a única
combinação em que a colisão do CR-01 não aparece. Reescrever com o par real
(`exemplo:dashboard` + `exemplo:item_listar`) é o que faz o teste virar prova.

### IN-08: item de navegação ativo no escuro fica em 4,2:1
`brand-ink:escuro` `#5d7ce3` sobre `brand-tint:escuro` `#192035` = **4,20:1**,
com o rótulo em `text-base` (13px) — logo abaixo do piso de 4,5:1. Marginal,
mas na mesma família do CR-02. `--cor-destructive` também não tem override
escuro (`input.css:137-138`, decisão registrada) e fica em **3,35:1** sobre
`--cor-surface-2`.

### IN-09: TOCTOU na alocação de porta do banco de ensaio
`.template-tests/ensaio_django.sh:212-219` faz `bind(("127.0.0.1", 0))`, fecha
o socket e só depois usa a porta no `compose up`. Entre os dois momentos outro
processo pode tomá-la. Baixa probabilidade, mas o modo de falha (`up` falha,
`diagnosticar` roda) é ruidoso o bastante para não bloquear.

### IN-10: `_canais()` aceita hex malformado em silêncio
`core/tema.py:47-50`: `int("abc", 16)` → `2748` → `(0, 10, 188)`. Um `#abc` não
levanta erro, produz uma cor errada. Hoje o único caminho é
`settings.COR_PRIMARIA`, validado com `re.fullmatch(r"#[0-9a-fA-F]{6}")` no
boot, mas `misturar`/`com_hsl`/`familia_marca`/`css_da_marca` são API pública
de um módulo pensado para derivados. Um `if not re.fullmatch(r"#[0-9a-fA-F]{6}", hex_): raise ValueError(...)`
em `_canais` fecha a porta com uma linha.

---

_Reviewed: 2026-08-23_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
