---
phase: 07-herdar-o-design-system-do-pca
plan: 09
subsystem: guardas-executaveis
tags: [wcag, contraste, gate, tailwind, regua-tipografica, gap-closure]
gap_closure: true
dependency-graph:
  requires: []
  provides:
    - "helper-contraste-wcag"
    - "gate-regua-detecta-valor-arbitrario"
    - "teto-tipografico-na-build"
  affects:
    - "core/tests/contraste.py"
    - ".template-tests/test_07_tokens.py"
    - "tailwind.config.js"
tech-stack:
  added: []
  patterns:
    - "Fórmula WCAG 2.x implementada UMA vez em core/tests/contraste.py e importada por todas as suítes (Django por import normal, .template-tests por importlib), nunca reescrita por suíte"
    - "Toda guarda por regex ganha teste da própria guarda: as strings que ela precisa detectar viram asserção, e a prova é a falha contra o código antigo"
    - "Teto de vocabulário vira propriedade da build (theme.fontSize substitui) e não promessa de gate (theme.extend.fontSize soma)"
key-files:
  created:
    - "core/tests/contraste.py"
    - "core/tests/test_contraste.py"
  modified:
    - ".template-tests/test_07_tokens.py"
    - "tailwind.config.js"
decisions:
  - "core/tests/contraste.py é a fonte única da fórmula WCAG e vive DENTRO do sistema gerado (.template-tests está em _exclude do copier.yml — um helper lá deixaria todo derivado sem a guarda)"
  - "TEXT_CLASS_RE usa lookahead negativo (?![\\w-]) no lugar do \\b final: além de ressuscitar o ramo de valor arbitrário, passa a recusar text-ink-2, que o \\b antigo casava como text-ink"
  - "O comentário de cabeçalho do tailwind.config.js fala em 'régua de tamanhos de fonte' sem escrever o nome da chave — o teste da substituição assere ocorrência única da string no arquivo"
metrics:
  duration: 13min
  tasks: 3
  files: 4
  completed: 2026-08-24
requirements: [DS-03, DS-04, QA-03]
---

# Phase 07 Plan 09: Guardas executáveis que passam a guardar Summary

As três guardas que aparentavam guardar passam a guardar — o gate da régua enxerga
`text-[NNpx]`, o gate do dourado audita todo prefixo e o teto de 20px virou propriedade
da build — e nasce `core/tests/contraste.py`, a implementação única da fórmula WCAG 2.x
que os planos 07-11, 07-12 e 07-13 vão usar para provar contraste em vez de afirmá-lo.

## O que foi construído

### Task 1 — `core/tests/contraste.py`, a fonte única da fórmula WCAG (TDD)

Três funções, sem Django e sem `core.tema`, o que é justamente o que permite carregá-las
por caminho de fora de um projeto Django configurado:

- `luminancia_relativa(hex_)` — canal/255, linearização WCAG 2.x, soma ponderada 0.2126/0.7152/0.0722
- `contraste(hex_a, hex_b)` — `(Lclara + 0.05) / (Lescura + 0.05)`, simétrico por construção
- `tokens_do_input_css(caminho=None)` — devolve `(claro, escuro)` lendo `input.css`

O ponto do terceiro é a **fusão**: `escuro = {**claro, **overrides}`. O bloco
`[data-tema="escuro"]` só declara os tokens com valor próprio, e quem não está lá herda o
claro (`input.css:93-96`). Sem a fusão, medir `--cor-destructive`, `--cor-secundaria` ou
`--cor-baseline` no escuro daria `KeyError` em vez do valor que a página realmente pinta —
e é exatamente esse conjunto que os planos de wave 3 precisam medir.

`_canais_hex()` valida com `re.fullmatch(r"#[0-9a-fA-F]{6}")` e levanta `ValueError`
citando a entrada (T-07-24). Fecha, do lado do teste, a mesma porta que o IN-10 aponta em
`core/tema.py`: um `#abc` não pode virar cor errada em silêncio dentro de uma asserção de
acessibilidade.

O módulo se chama `contraste.py` de propósito — o discovery do Django é `test*.py`, então
ele não é coletado como suíte; quem o prova é `test_contraste.py` (18 testes).

#### Os seis contrastes, medidos pela implementação contra o publicado no 07-REVIEW

| Par | Medido (todas as casas) | Publicado | Origem |
|---|---|---|---|
| `#ffffff` sobre `#000000` | `21.0` | 21,00 | âncora matemática |
| `#000000` sobre `#000000` | `1.0` | 1,00 | âncora matemática |
| `#ffffff` sobre `#889feb` | `2.559185875781983` | 2,56 | CR-02 — o **defeito** do G-02 |
| `#0f0e0d` sobre `#889feb` | `7.535535461640155` | 7,54 | CR-02 — o **conserto** do G-02 |
| `#ffffff` sobre `#1e40af` | `8.722410784954462` | 8,72 | CR-02 — o valor de antes da fase |
| `#192035` sobre `#22211d` | `1.0030421922481398` | 1,00 | CR-03 — a 4ª fatia invisível do G-03 |

As duas âncoras batem com igualdade estrita (tolerância 1e-9); os quatro pares medidos à
mão batem dentro de ±0,05, que é a precisão que a revisão publicou. Cada asserção cita a
origem (`CR-02`/`CR-03`) em comentário — a rastreabilidade existe para que "ajustar" um
número esperado no futuro seja visivelmente contradizer uma medição registrada.

### Task 2 — o ramo morto do G-05 e a lista morta do WR-08

**Parte A.** `TAMANHOS_TAILWIND_CONHECIDOS`, `TEXT_CLASS_RE` e a varredura subiram para o
nível do módulo como `varrer_classes_de_texto(paths, chaves_da_regua)`. Isso não é
cosmética: enquanto o regex era variável local do método, um teste da guarda só poderia
declarar a própria cópia dele e não provaria nada sobre o gate. Agora os dois testes
consomem os mesmos objetos.

O regex:

```
antes:  r"\btext-([a-z0-9]+|\[[^\]]+\])\b"
depois: r"\btext-(\[[^\]]*\]|[a-z0-9]+)(?![\w-])"
```

Duas correções. A alternativa de colchete vem primeiro (o `re` para na primeira que
serve, e `[a-z0-9]+` nunca deixava a segunda ser tentada); e o `\b` final virou lookahead
negativo, porque `]` já é não-palavra e o `\b` depois dele exigia uma transição que nunca
acontecia. Efeito colateral **desejado**: `text-ink-2` deixa de casar — é cor, não
tamanho, e o `\b` antigo a casava como `text-ink`.

**Parte B.** `ocorrencias_fora_do_contrato` era logicamente idêntica a `ocorrencias_texto`:
o filtro por prefixo `text-` anulava três das quatro alternativas do regex. Agora
`r"\b([a-z-]+)-secundaria\b"` captura qualquer prefixo e reprova tudo fora de
`{bg, border, fill}` — `ring-`, `decoration-`, `divide-`, `caret-`, `placeholder-`,
`outline-`, `accent-` e `shadow-secundaria` passam a reprovar junto com `text-`.

**Parte C.** `test_o_helper_de_contraste_e_carregavel_desta_suite` carrega
`core/tests/contraste.py` por `spec_from_file_location` e assere `contraste("#ffffff",
"#000000") == 21.0`. É pequeno de propósito: não mede design nenhum, prova que a ponte
entre as duas famílias de suíte existe. Se o arquivo for movido ou renomeado, quem
descobre é este gate, em wave 1, e não um plano de wave 3 que já o assume de pé.

### Task 3 — o teto de 20px sai do teste e entra na build

`fontSize` saiu de `theme.extend` e virou irmã de `extend`, declarada antes dela. Dentro
do `extend` a régua **acrescenta** ao default e `text-2xl`…`text-9xl` continuam gerando
regra, com o gate como única barreira; em `theme` o Tailwind **substitui** o mapa.
`colors`, `borderRadius` e `fontFamily` continuam em `extend` porque precisam somar
(`text-white`, `bg-red-600`, `rounded-full` seguem em uso).

`test_fontsize_substitui_o_default_em_vez_de_estender` ancora as duas propriedades
(ordem e ocorrência única) por asserção de texto — o arquivo chega verbatim ao derivado e
nunca passa por parser JS neste repositório.

## Provas de que os testes novos pegam o defeito

Um teste que passa antes e depois não fecha gap nenhum. Os dois testes estruturais foram
rodados contra o código antigo, restaurado à mão.

### `test_o_gate_da_regua_enxerga_valor_arbitrario` com o regex antigo

```
FAIL: … (entrada='class="text-[13px] font-bold"')
AssertionError: Lists differ: [] != ['[13px]']
FAIL: … (entrada='class="font-bold text-[13px]"')
AssertionError: Lists differ: [] != ['[13px]']
FAIL: … (entrada="class='text-[20px]'")
AssertionError: Lists differ: [] != ['[20px]']
FAIL: … (entrada='class="text-ink-2"')
AssertionError: Lists differ: ['ink'] != []
Ran 1 test in 0.002s
FAILED (failures=4)
```

Três dos quatro são o ramo morto do G-05 devolvendo lista vazia; o quarto é o `text-ink-2`
que o `\b` casava indevidamente.

### `test_fontsize_substitui_o_default_em_vez_de_estender` com `fontSize` de volta no `extend`

```
FAIL: test_fontsize_substitui_o_default_em_vez_de_estender
AssertionError: 1398 not less than 1382 : a régua está DENTRO de theme.extend: o Tailwind
vai somá-la ao default e text-2xl…text-9xl voltam a gerar regra
Ran 1 test in 0.001s
FAILED (failures=1)
```

### A prova de build, que é a que interessa

Um template com `class="text-2xl text-9xl text-xl"` foi injetado dentro da imagem do
estágio `assets` e o Tailwind 3.4.17 rodou de verdade, com os dois configs:

| Classe no template | Regras geradas — config ANTIGO | Regras geradas — config ATUAL |
|---|---|---|
| `.text-2xl` | 1 (`font-size: 1.5rem` = 24px) | **0** |
| `.text-9xl` | 1 | **0** |
| `.text-xl` | 1 (`font-size: 20px`) | 1 (`font-size: 20px`) |

Um `text-2xl` esquecido num template deixa de existir no CSS. O gate virou a segunda
linha de defesa em vez da única.

## Diff do bloco `fontSize` — os seis pares intactos

```
   theme: {
+    fontSize: {
+      xs: ["11px", { lineHeight: "1.4" }],
+      sm: ["12px", { lineHeight: "1.4" }],
+      base: ["13px", { lineHeight: "1.5" }],
+      md: ["14px", { lineHeight: "1.5" }],
+      lg: ["16px", { lineHeight: "1.4" }],
+      xl: ["20px", { lineHeight: "1.3" }],
+    },
     extend: {
       …
-      fontSize: {
-        xs: ["11px", { lineHeight: "1.4" }],
-        sm: ["12px", { lineHeight: "1.4" }],
-        base: ["13px", { lineHeight: "1.5" }],
-        md: ["14px", { lineHeight: "1.5" }],
-        lg: ["16px", { lineHeight: "1.4" }],
-        xl: ["20px", { lineHeight: "1.3" }],
-      },
       fontFamily: {
```

Chaves e valores em pixels idênticos; só a indentação mudou, por causa do nível.

## Verificação

| Comando | Resultado |
|---|---|
| `bash .template-tests/ensaio_django.sh testar core.tests.test_contraste` | OK — 18 testes, exit 0 |
| `python3 -m unittest discover -s .template-tests -p 'test_07_tokens*.py'` | OK — 14 testes, exit 0 |
| `python3 -m unittest discover -s .template-tests -p 'test_*.py'` | OK — 38 testes, 115 s, exit 0 |
| `docker build --target assets .` | exit 0 |
| `bash .template-tests/ensaio_django.sh testar core apps.exemplo` | OK — **130 testes** (112 + os 18 novos), exit 0 |

Critérios mecânicos do plano:

| Critério | Valor |
|---|---|
| `def (luminancia_relativa\|contraste\|tokens_do_input_css)` em `contraste.py` | 3 |
| `grep -c assertAlmostEqual core/tests/test_contraste.py` | 6 (mínimo exigido: 4) |
| imports de `django`/`core.tema` em `contraste.py` | nenhum |
| `grep -c "^TEXT_CLASS_RE" .template-tests/test_07_tokens.py` | 1 |
| `grep -c "def test_o_gate_da_regua_"` | 2 |
| `grep -c 'startswith("text-")'` | 0 |
| `grep -c spec_from_file_location` | 1 |
| `s.index('fontSize:') < s.index('extend:')` | `True` |
| `grep -c fontSize tailwind.config.js` | 1 |

## Decisões

**O helper vive em `core/tests/`, não em `.template-tests/`.** `.template-tests/` está em
`_exclude` do `copier.yml` — nada dali chega ao derivado. Um helper lá deixaria todo
sistema gerado sem a guarda de contraste, que é precisamente o que precisa viajar com o
template. As suítes de `.template-tests/` alcançam o arquivo por `importlib`, então uma
implementação serve às duas famílias.

**O lookahead faz mais do que ressuscitar o ramo morto.** A troca de `\b` por `(?![\w-])`
também corrige um falso positivo latente: `text-ink-2` casava como `text-ink` no regex
antigo. Não havia violação viva porque `ink` não está em `TAMANHOS_TAILWIND_CONHECIDOS`,
mas a classificação estava errada e agora está certa.

**O comentário de cabeçalho do `tailwind.config.js` não escreve o nome da chave.** O teste
da Task 3 assere ocorrência única da string no arquivo — é essa unicidade que impede a
chave de voltar a coexistir com o default. O comentário fala em "régua de tamanhos de
fonte" e a docstring do teste explica por quê, para que ninguém "conserte" o comentário e
quebre a asserção sem entender o motivo.

## Deviations from Plan

Uma, cosmética e sem efeito sobre comportamento.

**1. [Rule 3 - Bloqueio] Prosa de docstring reescrita para satisfazer critério de aceite literal**
- **Found during:** Task 2
- **Issue:** o critério `grep -c 'startswith("text-")'` deve retornar 0. Depois de remover
  o código morto do WR-08, a string ainda aparecia em **duas docstrings**, que explicavam
  o defeito citando-o textualmente. O critério é um grep de linha e teria retornado 2.
- **Fix:** as duas docstrings passaram a descrever o filtro antigo em prosa ("descartava
  por prefixo tudo o que não fosse `text-`", "olhar só o prefixo `text-`), preservando a
  explicação sem a string literal.
- **Files modified:** `.template-tests/test_07_tokens.py`
- **Commit:** c6c56c5

Nenhuma asserção existente foi relaxada. As contagens de token (21/18) não foram tocadas —
quem as move são os planos 07-11 e 07-13.

## Known Stubs

Nenhum. As três entregas são executáveis e exercitadas por teste; nenhum valor
hardcodado, nenhum ponto de extensão vazio.

## O que este plano NÃO fez

Deliberado, para não invadir os planos seguintes da onda:

- **G-01** (`{% item_nav %}` marcando dois itens ativos) — intocado
- **G-02** (texto branco sobre a marca no escuro, 2,56:1) — o helper agora **mede** o
  defeito e o conserto, mas nenhuma cor foi alterada
- **G-03/G-04** (4ª fatia do donut e grade do eixo) — idem
- Nenhuma contagem de token mudou

## Autoteste

Arquivos declarados como criados:

- `core/tests/contraste.py` — FOUND
- `core/tests/test_contraste.py` — FOUND

Commits declarados:

- `9afad53` — FOUND
- `c80da52` — FOUND
- `c6c56c5` — FOUND
- `808e542` — FOUND

## Self-Check: PASSED
