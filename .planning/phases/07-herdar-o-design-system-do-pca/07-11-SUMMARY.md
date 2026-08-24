---
phase: 07-herdar-o-design-system-do-pca
plan: 11
subsystem: tokens-de-cor
tags: [wcag, contraste, tokens, tema-escuro, gap-closure, g-02]
gap_closure: true
dependency-graph:
  requires: ["helper-contraste-wcag"]
  provides:
    - "token-brand-tx"
    - "gate-de-contraste-do-par-da-marca"
  affects:
    - "core/static/src/input.css"
    - "tailwind.config.js"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo"
tech-stack:
  added: []
  patterns:
    - "Todo fundo de marca tem par de texto declarado como token que inverte com o tema — nunca `text-white` cravado"
    - "Contraste de par texto/fundo é asserção computada sobre mais de uma COR_PRIMARIA, não inspeção visual"
    - "A varredura estrutural vem em par: negativa (não pode text-white) e positiva simétrica (tem que ter text-brand-tx), senão o gate fecha apagando a classe"
key-files:
  created:
    - "core/tests/test_contraste_marca.py"
  modified:
    - "core/static/src/input.css"
    - "tailwind.config.js"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/item_listar.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_form_modal.html"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/templates/exemplo/_tabela_resultado.html"
    - ".template-tests/test_07_tokens.py"
decisions:
  - "O conserto do G-02 é pela cor do TEXTO (`--cor-brand-tx`), não pelo token de fundo: `core/tema.py` fica intocado e a equivalência numérica com o padrão de referência sobrevive byte a byte"
  - "`--cor-brand-tx` do escuro é o mesmo valor de `--cor-page` do escuro, amarrado por asserção de igualdade lida do arquivo (T-07-32) — nunca `var(--cor-page)` dentro da variável, porque `getComputedStyle` não resolve função de cor em custom property"
  - "A exceção da varredura positiva é `aria-hidden=\"true\"`: fundo de marca decorativo (o filete de 2px do item de navegação ativo) não carrega texto e não tem par a declarar; `@apply` nunca é exempto, porque `.btn--primaria` compõe com `.btn`"
metrics:
  duration: 27min
  tasks: 2
  files: 7
  completed: 2026-08-24
requirements: [DS-01, DS-03, DS-06]
---

# Phase 07 Plan 11: O par texto+fundo da marca vira contrato de token Summary

`text-white` sobre `bg-brand` deixou de existir: o par de texto da marca agora é
`--cor-brand-tx`, que inverte com o tema (branco no claro, a tinta da página escura no
escuro), e um gate de contraste computado mede as doze combinações de 3 `COR_PRIMARIA` ×
2 temas × (repouso, hover) contra o piso AA de 4,5:1 — o pior caso do gap, `#003c71` no
escuro, sai de **1,99:1** para **9,69:1**.

## O que foi construído

### Task 1 — `core/tests/test_contraste_marca.py`, o gate vermelho (commit `84d7748`)

Oito métodos de teste, 18 falhas contra o código de antes. O arquivo mede com
`core/tests/contraste.py` (o helper único do 07-09) e lê os valores de token de
`tokens_do_input_css()` — do arquivo, nunca repetidos à mão. A separação em relação a
`test_tema.py` é deliberada e está escrita no docstring: aquele prova equivalência de
**fórmula** com o padrão de referência, este prova **acessibilidade do resultado
renderizado**. Os dois passam e falham independentemente, e foi por só existir o primeiro
que o G-02 atravessou a fase — `--cor-brand` do escuro estava "correto" em relação ao
padrão e ainda assim ilegível sob branco.

Quatro asserções de token (`TokenDeTextoDaMarcaTests`): declarado nos dois blocos, claro
é `#ffffff`, escuro **é** `--cor-page` do escuro (T-07-32), e escuro tem valor **próprio**
— não herança. Essa última existe porque `tokens_do_input_css()` funde os blocos: um
`brand-tx` só no `:root` apareceria no dict escuro valendo branco, e o gate de contraste
reprovaria sem dizer por quê.

Doze `subTest(cor=…, tema=…, estado=…)` com o valor medido na mensagem
(`f"{medido:.2f}:1"`), porque uma falha que só diz "False is not true" custa uma rodada
inteira de investigação.

E duas varreduras estruturais **em par**, que é o ponto mais importante do arquivo:

- **negativa** — nenhuma declaração junta `bg-brand` com `text-white`;
- **positiva simétrica** — toda declaração com `bg-brand` e conteúdo textual declara
  `text-brand-tx`.

Sem a segunda, o gate fecharia com alguém simplesmente **apagando** o `text-white`: o
botão passaria a herdar `text-ink`, que no escuro é `#eeeeee` — mesma ilegibilidade, agora
sem nenhuma classe para grepar.

A varredura opera sobre o **valor do atributo `class`** (e sobre o corpo do `@apply`), não
sobre a linha inteira — varrer a linha produziria falso positivo em qualquer marcação com
`bg-brand` num elemento e `text-white` num vizinho. `bg-brand` é casado com
`(?<![\w-])bg-brand(?![\w-])`, que recusa `bg-brand-hover`/`-tint`/`-ink` e aceita
`hover:bg-brand`.

Uma terceira varredura prova a **própria guarda**: exige que ela tenha encontrado ao menos
o `@apply` do `input.css`. Uma varredura que não acha nada passa vazia e parece verde — é
a mesma classe de defeito do G-05.

### Task 2 — o token declarado, mapeado e aplicado (commit `41a307f`)

`--cor-brand-tx: #ffffff` no `:root` e `#0f0e0d` em `[data-tema="escuro"]`, hex plano nos
dois, com comentário dizendo as três coisas que o plano pediu: por que existe (a derivação
fixa a luminosidade do escuro em 72,7%, então é **sempre** cor clara e branco por cima
reprova sempre), que o valor escuro é o `--cor-page` do escuro com teste amarrando os
dois, e qual é o limite honesto do claro. `.btn--primaria` passou a
`@apply bg-brand text-brand-tx hover:bg-brand-hover`; `tailwind.config.js` ganhou
`"brand-tx": "var(--cor-brand-tx)"` logo após `brand-tint`; os três templates do app
exemplo trocaram `text-white` por `text-brand-tx` — só isso na linha, nem tamanho, nem
raio, nem sombra.

Contagens travadas movidas em `.template-tests/test_07_tokens.py`: 21 → **22** e 18 → **19**,
com o nome do método acompanhando (`test_root_declara_22_tokens_e_escuro_declara_19_overrides`
— o nome carrega o contrato), e `brand-tx` acrescentado a `MIGRATED_TOKENS` para que o gate
de opacidade reprove `text-brand-tx/50`, que o Tailwind não gera.

## Os contrastes, antes e depois

Medidos com `core/tests/contraste.py` sobre a saída real de `tema.familia_marca(cor)`.
A coluna "antes" é `#ffffff` sobre o fundo; a "depois" é `--cor-brand-tx` do tema.

| `COR_PRIMARIA` | tema | estado | fundo | antes (`text-white`) | depois (`text-brand-tx`) |
|---|---|---|---|---|---|
| `#1e40af` | claro | repouso | `#1e40af` | 8,72:1 | **8,72:1** |
| `#1e40af` | claro | hover | `#3957b9` | 6,49:1 | **6,49:1** |
| `#1e40af` | escuro | repouso | `#889feb` | **2,56:1** ✗ | **7,54:1** |
| `#1e40af` | escuro | hover | `#b4c2f2` | **1,76:1** ✗ | **10,96:1** |
| `#003c71` | claro | repouso | `#003c71` | 11,14:1 | **11,14:1** |
| `#003c71` | claro | hover | `#1f5382` | 8,02:1 | **8,02:1** |
| `#003c71` | escuro | repouso | `#74beff` | **1,99:1** ✗ | **9,69:1** |
| `#003c71` | escuro | hover | `#a7d6ff` | **1,53:1** ✗ | **12,59:1** |
| `#b91c1c` | claro | repouso | `#b91c1c` | 6,47:1 | **6,47:1** |
| `#b91c1c` | claro | hover | `#c13737` | 5,43:1 | **5,43:1** |
| `#b91c1c` | escuro | repouso | `#ed8686` | **2,51:1** ✗ | **7,67:1** |
| `#b91c1c` | escuro | hover | `#f3b2b2` | **1,78:1** ✗ | **10,86:1** |

Os seis valores do claro não mudam — `--cor-brand-tx` do claro **é** `#ffffff`, e essa é a
propriedade que garante que o conserto não regride o tema que já estava bom. Os seis do
escuro estavam todos abaixo até do piso de texto grande (3:1). Os quatro números que o
plano publicou como orientação (7,5 / 9,7 / 11,0 / 8,7) batem com o medido dentro do
arredondamento.

O pior caso do gap é o **hover no escuro com `#003c71`**: 1,53:1, praticamente invisível —
e é a cor do próprio padrão de referência.

### A saída de falha registrada (estado defeituoso, antes da Task 2)

```
Ran 8 tests in 0.013s
FAILED (failures=18)
```

Doze delas são os `subTest` de contraste; quatro são as asserções de token
(`'brand-tx' not found in {...}` — com o dict inteiro na mensagem, que é o que torna o
diagnóstico imediato); duas são as varreduras, listando os quatro sítios com arquivo e
linha:

```
apps/exemplo/templates/exemplo/_form_modal.html:135 → … bg-brand … text-white …
apps/exemplo/templates/exemplo/_tabela_resultado.html:215 → … bg-brand … text-white
apps/exemplo/templates/exemplo/item_listar.html:20 → … bg-brand … text-white …
core/static/src/input.css:56 → bg-brand text-white hover:bg-brand-hover
```

As quatro do tema **claro** falharam por token ausente, não por contraste ruim — o claro
nunca teve o defeito. Isso é o comportamento correto do gate: sem o token não há o que
medir, e a mensagem diz exatamente isso em vez de estourar `KeyError`.

## Divergência consciente em relação ao padrão de referência

Registro pedido explicitamente pelo plano e pelo operador.

O padrão de referência traz `--cor-brand: #74beff` no escuro e
`.btn--primaria { @apply bg-brand text-white … }` — **idênticos** aos nossos. Não herdamos
errado: herdamos fielmente. A diferença é que lá `.btn--primaria` tem **zero** usos em
template — o par está **dormente** no padrão e **vivo** aqui, porque o app exemplo aplica
`bg-brand … text-white` direto em três botões.

A divergência introduzida fica **confinada ao par texto+fundo**, exatamente onde o defeito
está e em nenhum lugar além:

- `core/tema.py` — **zero linhas alteradas**. `git diff --stat core/tema.py` vazio.
- `core/tests/test_tema.py` — **zero linhas alteradas**. As asserções exatas
  (`com_hsl("#003c71", 1.0, 0.727) == "#74beff"`) seguem valendo byte a byte.
- Nenhum token de fundo mudou de valor. A família de marca inteira continua derivável do
  padrão.

O caminho alternativo — mexer no coeficiente de `com_hsl` para escurecer `brand:escuro` —
teria quebrado a equivalência numérica com o padrão e as asserções de `test_tema.py`, e
teria mudado **catorze** valores para consertar **um** par. Foi rejeitado pelo operador
antes da execução e não foi reaberto.

`brand-tx` é neutro (page/ink): **não** entra em `familia_marca()` e **não** acompanha
`COR_PRIMARIA`. É por isso que o plano não precisou tocar em `core/tema.py`.

## Limite honesto, documentado no comentário do token

No tema **claro**, `--cor-brand` é a própria `COR_PRIMARIA`, escolhida por quem gera o
sistema e sem teto de luminosidade. Uma `COR_PRIMARIA` muito clara reprovaria com branco
por cima, e **nenhum token conserta isso** — é escolha do derivado, não defeito daqui. O
gate cobre três cores de referência (o default do template, a do padrão e uma quente); a
limitação está escrita no comentário de `--cor-brand-tx` no `:root`, onde quem for mexer a
lê.

## Fora de escopo, deliberadamente

Dois `text-white` continuam no repositório e **não** são o defeito deste gap — usam a
paleta default do Tailwind, não `bg-brand`:

| Arquivo | Linha | Par |
|---|---|---|
| `apps/…exemplo…/templates/exemplo/_confirmar_exclusao_modal.html` | 56 | `bg-red-600 text-white` |
| `core/templates/core/_login_form.html` | 32 | `bg-blue-700 text-white` |

Ambos são hex fixo de build-time (não invertem com o tema), então o contraste deles não
depende de `COR_PRIMARIA` e não tem o problema estrutural do G-02. A varredura os ignora
por construção — ela só olha declarações que contêm `bg-brand`. Ficam registrados como
observação, não foram "consertados de passagem".

Um terceiro sítio usa `bg-brand` e **não** entra no contrato:
`core/templates/core/_item_nav.html:6`, o filete de 2px do item de navegação ativo. É
`aria-hidden="true"` e não contém texto — é a exceção única e explícita da varredura
positiva.

## Verificação

| Comando | Resultado |
|---|---|
| `bash .template-tests/ensaio_django.sh testar core.tests.test_contraste_marca` | **exit 0** — 8 testes, OK (antes: 18 falhas) |
| `bash .template-tests/ensaio_django.sh testar core apps.exemplo` | **exit 0** — 153 testes, OK |
| `python3 -m unittest discover -s .template-tests -p 'test_*.py'` | **exit 0** — 39 testes, OK (144,6 s) |
| `docker build --target assets .` | **exit 0** — `tailwind.css` com **19267 bytes** (piso 5000) |
| `git diff --stat core/tema.py core/tests/test_tema.py` | **vazio** |

Conferências pontuais dos critérios de aceite:

| Critério | Esperado | Medido |
|---|---|---|
| `grep -c -- "--cor-brand-tx" core/static/src/input.css` | 2 | **2** |
| `grep -c "brand-tx" tailwind.config.js` | 1 | **1** |
| `grep -rn "bg-brand" core apps … \| grep -c "text-white"` | 0 | **0** |
| `grep -rc "text-brand-tx"` nos 3 templates | 1 cada | **1, 1, 1** |
| hex cravado em `core/templates`/`apps` (`*.html`) | nenhum | **nenhum** (critério 3 da fase não regrediu) |

No CSS compilado: `.text-brand-tx{color:var(--cor-brand-tx)}`, com `--cor-brand-tx:#fff`
e `--cor-brand-tx:#0f0e0d` presentes — o Tailwind gerou a classe, o token não foi podado
pelo purge e o par chega ao navegador.

## Decisões

1. **Conserto pela cor do texto, não pelo token de fundo.** Trava do operador, herdada do
   próprio diagnóstico do G-02. Confina a divergência ao par defeituoso e preserva
   `core/tema.py` inteiro.
2. **`--cor-brand-tx` do escuro é hex plano igual a `--cor-page`, não `var(--cor-page)`.**
   `input.css` é a fonte física e o `HEX_TOKEN_RE` do gate exige `#rrggbb`;
   `getComputedStyle` não resolve função de cor dentro de custom property. A igualdade é
   garantida por asserção, não por indireção de CSS.
3. **Varredura em par (negativa + positiva).** A negativa sozinha seria fechável apagando
   a classe; a positiva sozinha não pegaria um `text-white` acrescentado junto. Juntas,
   fecham as duas portas.
4. **`aria-hidden="true"` como única exceção da positiva, e nenhuma exceção para `@apply`.**
   O atributo já significa "não carrega texto" — usá-lo como discriminante é preciso e
   auto-documentado. `@apply` não é exempto porque `.btn--primaria` compõe com `.btn`, que
   traz `text-[13px] font-semibold`.

## Deviations from Plan

Nenhuma — o plano foi executado exatamente como escrito. As duas tasks, os quatro sítios,
as duas contagens travadas e a entrada em `MIGRATED_TOKENS` saíram conforme especificado,
e os contrastes medidos batem com os que o plano publicou como orientação.

## Threat Flags

Nenhuma superfície de segurança nova. `--cor-brand-tx` é constante de estilo: não depende
de `COR_PRIMARIA`, não depende de nenhuma entrada de request e não atravessa fronteira de
confiança (T-07-33, disposição `accept`, confirmada). T-07-31 e T-07-32 estão mitigadas
pelos testes descritos acima.

## Self-Check: PASSED

- `core/tests/test_contraste_marca.py` — FOUND
- `core/static/src/input.css` — FOUND
- `tailwind.config.js` — FOUND
- `.template-tests/test_07_tokens.py` — FOUND
- os 3 templates do app exemplo — FOUND
- commit `84d7748` — FOUND
- commit `41a307f` — FOUND
