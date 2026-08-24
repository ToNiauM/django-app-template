---
phase: 07-herdar-o-design-system-do-pca
plan: 13
subsystem: paleta-de-grafico
tags: [wcag, contraste, rampa-sequencial, css-variables, tema-escuro, donut, echarts]

# Dependency graph
requires:
  - phase: 07-09
    provides: "core/tests/contraste.py — helper WCAG único do repositório (contraste, tokens_do_input_css)"
  - phase: 07-11
    provides: "--cor-brand-tx e as contagens de token em 22/19, que este plano move para 23/20"
provides:
  - "rampa-sequencial-de-4-degraus — seq-750 estende a rampa pelo lado FORTE, nos dois temas"
  - "gate-de-visibilidade-das-fatias — três partes: nenhum token de superfície, piso de 1,5:1, ordem decrescente medida"
  - "seq-750 em _CHAVES_MARCA — o degrau novo acompanha COR_PRIMARIA em runtime"
affects:
  - "07-14 (fechamento da fase) — as contagens travadas passam a 16/16/23/20"
  - "qualquer derivado que gere o sistema com outra COR_PRIMARIA: a quarta fatia agora é derivada, não cravada"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Token de superfície nunca é cor de dado; a rampa sequencial estende-se por derivação, no lado de MAIOR contraste com o card"
    - "Asserção de rampa é relativa (pertinência da marca + monotonicidade em contraste), nunca um índice mágico"
    - "Extensão local do padrão de referência é fixada FORA do dict de valores herdados — o dict continua dizendo só o que o padrão publica"
    - "Comentário de teste não cita a forma literal que o próprio gate proíbe"

key-files:
  created: []
  modified:
    - "core/tema.py"
    - "core/static/src/input.css"
    - "tailwind.config.js"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py"
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py"
    - "core/tests/test_tema.py"
    - ".template-tests/test_07_tokens.py"

key-decisions:
  - "A rampa estende pelo lado FORTE (misturar(cor, 0, 0.35) no claro, com_hsl(cor, 1.00, 0.860) no escuro): estender na direção do branco daria ~1,4:1 contra um card quase branco e trocaria um invisível por outro"
  - "`core/tema.py` alterado por ACRÉSCIMO PURO — 20 linhas adicionadas, 0 removidas; até os comentários herdados com as contagens antigas ficaram intactos, e a atualização de contagem entrou como linha NOVA"
  - "`seq-750` fixado à parte do dict `esperado` de test_tema.py: aquele dict é o conjunto de valores MEDIDOS no padrão de referência, cuja rampa tem três degraus — o quarto é extensão deste template, não herança"
  - "Piso de fatia em 1,5:1 (não 3:1): os três degraus herdados reproduzem byte a byte a rampa do padrão e o mais fraco vive em ~1,9:1 no claro; exigir 3:1 obrigaria a mexer nos coeficientes herdados para consertar um defeito que não está neles"
  - "O `brand-tint` proibido no gate é recalculado de settings.COR_PRIMARIA, nunca lido do input.css — o token depende da marca e a comparação passaria por engano num sistema gerado com outra cor"

patterns-established:
  - "Ordenação de rampa asserida por contraste contra o fundo do card: a mesma frase vale nos dois temas (no claro a rampa escurece, no escuro clareia) sem inversão de sinal"
  - "Gate de paleta mede o valor que sai do CONTEXTO da view — o mesmo que o json_script entrega ao ECharts — e não uma reconstrução paralela"

requirements-completed: [DS-01, DS-05, DS-06]

# Metrics
duration: 16min
completed: 2026-08-24
---

# Phase 07 Plano 13: A quarta fatia do donut vira cor de dado Summary

**A quarta fatia do donut deixa de ser `--cor-brand-tint` — um token de FUNDO a 1,11:1 no claro e 1,00:1 no escuro contra o card — e passa a ser `seq-750`, quarto degrau derivado da mesma marca, a 12,75:1 e 10,31:1; a rampa é agora monotônica em contraste nos dois temas e um gate de três partes impede que qualquer token de superfície volte a entrar como dado.**

## Performance

| Métrica | Valor |
|---|---|
| Duração | 16 min (01:21 → 01:37) |
| Tarefas | 3 de 3 |
| Commits | 3 (+1 de docs) |
| Arquivos tocados | 7 |
| Testes Django | 169 OK |
| Testes de template | 39 OK |

## O gap, em número

O donut representa quatro valores de `StatusChoices`. A quarta cor da rampa era
`brand-tint`, cujo papel declarado em `core/tema.py` é "fundo tênue do item ativo".
Contraste medido contra o fundo real do card (`--cor-surface` no claro,
`--cor-surface-2` no escuro, que é o que os cards declaram: `bg-surface … dark:bg-surface-2`):

**Estado defeituoso — os 8 contrastes, com `COR_PRIMARIA = #1e40af`:**

| degrau | claro (card `#fcfcfb`) | escuro (card `#22211d`) |
|---|---|---|
| `seq-600` | `#1e40af` — **8,50:1** | `#889feb` — **6,30:1** |
| `seq-450` | `#6b81ca` — **3,64:1** | `#5873c9` — **3,61:1** |
| `seq-300` | `#aab6e1` — **1,95:1** | `#435697` — **2,31:1** |
| `brand-tint` (4ª) | `#edf0f9` — **1,11:1** | `#192035` — **1,00:1** |

No escuro, `1,00:1` é o mesmo tom do card: a fatia não existia. Os dois números do
tema escuro saíram da execução real do teste vermelho (`1.0030421922481398` e
`1.1097717802827736` no traceback), não de estimativa.

**Estado corrigido — os mesmos 8 contrastes:**

| degrau | claro (card `#fcfcfb`) | escuro (card `#22211d`) |
|---|---|---|
| `seq-750` (4º, novo) | `#142a72` — **12,75:1** | `#c2cef5` — **10,31:1** |
| `seq-600` | `#1e40af` — **8,50:1** | `#889feb` — **6,30:1** |
| `seq-450` | `#6b81ca` — **3,64:1** | `#5873c9` — **3,61:1** |
| `seq-300` | `#aab6e1` — **1,95:1** | `#435697` — **2,31:1** |

Estritamente decrescente nos dois temas. Os três degraus herdados não se moveram um
único byte — a coluna é idêntica à da tabela anterior, o que é a prova de que a
equivalência com a `rampa_uo` do padrão de referência (`#003c71 / #577ea1 / #9eb5c9`)
sobreviveu.

## Por que o lado forte, e não o claro

A revisão sugeriu `misturar(cor, 255, 0.80)` — um quarto tom ainda mais claro. Contra
um card em `#fcfcfb` isso dá ≈ 1,4:1: trocaria um invisível por outro. A rampa herdada
já tem seu degrau mais fraco em 1,95:1 no claro; o espaço livre está do lado forte, e é
por lá que ela foi estendida:

```python
"seq-750": misturar(cor, 0, 0.35),          # claro: o mais ESCURO
"seq-750:escuro": com_hsl(cor, 1.00, 0.860),  # escuro: o mais CLARO
```

No claro o degrau novo é mais escuro que a marca; no escuro, mais claro que ela. Nos
dois casos é o de **maior** contraste contra o card do respectivo tema — que é a
propriedade que o gate exige, não os números em si. Conferido com três marcas de
referência antes de escrever a primeira linha:

| `COR_PRIMARIA` | `seq-750` claro | contraste | `seq-750` escuro | contraste |
|---|---|---|---|---|
| `#1e40af` (default) | `#142a72` | 12,75:1 | `#c2cef5` | 10,31:1 |
| `#003c71` (padrão de referência) | `#002749` | 14,75:1 | `#b8deff` | 11,46:1 |
| `#b91c1c` | `#781212` | 10,80:1 | `#f6c1c1` | 10,22:1 |

Monotônico nas três, nos dois temas.

## Acréscimo puro em `core/tema.py`

```
$ git diff --numstat HEAD~3 HEAD -- core/tema.py
20      0       core/tema.py
```

Zero remoções. Isso incluiu uma decisão deliberadamente feia: os comentários herdados
que dizem "as 7 variáveis" e "as 14 variáveis" **ficaram como estavam**, e a atualização
de contagem entrou como bloco de comentário NOVO logo acima de `_CHAVES_MARCA`,
explicando que os números antigos são de antes do acréscimo e que ficaram intactos de
propósito. Reescrever a docstring teria produzido uma remoção no diff e apagado
justamente a evidência que o critério de aceite pede — de que nenhum coeficiente do
padrão de referência foi tocado. As asserções de equivalência de `test_tema.py:37-47`
seguem literalmente as mesmas:

```
$ git diff core/tests/test_tema.py | grep '^-' | grep -v '^---'
-        self.assertEqual(len(familia), 14)
-        self.assertEqual(len(linhas_decl), 14)
```

As duas únicas remoções no arquivo inteiro são contagens — nenhum `misturar(...)` nem
`com_hsl(...)` saiu.

## `seq-750` acompanha a marca em runtime

A chave entrou em `_CHAVES_MARCA` (7 → 8), que é o que faz `css_da_marca()` emitir
`--cor-seq-750` nos dois blocos de override. Sem isso, o degrau novo ficaria cravado no
default do `input.css` e um sistema gerado com outra `COR_PRIMARIA` teria três fatias
coerentes e uma azul. Confirmado com a própria função:

```
$ python3 -c "... familia_marca('#1e40af') vs tokens_do_input_css() ..."
derivado claro  #142a72 | input.css claro  #142a72 | igual: True
derivado escuro #c2cef5 | input.css escuro #c2cef5 | igual: True
css_da_marca linhas --cor-: 16
```

## O gate, e por que ele tem três partes

`PaletaDeDadoDoDonutTests`, em `apps/…exemplo…/tests/test_dashboard.py`, mede a rampa
que sai do **contexto da view** — o mesmo valor que o `json_script` entrega ao ECharts.

1. **Nenhuma fatia é token de superfície** (`page`, `surface`, `surface-2`, `surface-3`,
   `brand-tint`). É a parte que `brand-tint` não tem como satisfazer, e é o núcleo do
   conserto.
2. **Piso absoluto de 1,5:1** contra o fundo do card, nos dois temas.
3. **Ordem por contraste decrescente**, mais a asserção separada de que a primeira fatia
   é a de maior contraste — relativa, auto-calibrada, e nunca exige mexer em coeficiente
   herdado.

Nenhuma delas sozinha fecharia o gap. O piso 2 é deliberadamente baixo (1,5:1, não os
3:1 do WCAG para objeto gráfico portador de informação) e o motivo está escrito no
docstring da classe: o degrau `seq-300` herdado vive em 1,95:1 no claro, e exigir 3:1
obrigaria a redesenhar a rampa do padrão para consertar um defeito que não está nela.
1,5:1 pega o 1,11/1,00 do defeito com folga larga.

**O ponto sutil que ficou registrado em comentário:** `tokens_do_input_css()` lê o
default do template (`#1e40af`), mas a rampa do contexto vem da `COR_PRIMARIA` efetiva.
Os tokens de superfície são neutros e a comparação é válida em qualquer ambiente; já
`brand-tint` depende da marca, então o valor proibido é sempre recalculado de
`familia_marca(settings.COR_PRIMARIA)`. Sem esse cuidado, num derivado com marca
customizada o gate passaria por engano e o defeito sobreviveria ao próprio teste.

## O índice mágico que não foi consertado com outro índice mágico

`test_paleta_graficos_topo_da_rampa_clara_e_a_propria_marca` assertava que o degrau de
índice zero era a `COR_PRIMARIA`. Com `seq-750` na frente, isso quebra. Trocar o `0`
por `1` só moveria o índice mágico de lugar. Foi substituído por
`test_paleta_graficos_a_marca_e_um_degrau_da_propria_rampa_clara`, que assere
**pertinência** — a rampa é derivada da marca e a contém, propriedade que sobrevive a
reordenação — enquanto a ORDEM passou a ser asserida à parte, por contraste medido.

## Contagens travadas, medidas nesta execução

| Arquivo | Asserção | De | Para |
|---|---|---|---|
| `core/tests/test_tema.py` | `len(familia)` | 14 | **16** |
| `core/tests/test_tema.py` | linhas `--cor-` em `css_da_marca` | 14 | **16** |
| `core/tests/test_tema.py` | chaves conferidas contra `input.css` | 7 | **8** |
| `.template-tests/test_07_tokens.py` | `len(root_tokens)` | 22 | **23** |
| `.template-tests/test_07_tokens.py` | `len(escuro_tokens)` | 19 | **20** |
| `.template-tests/test_07_tokens.py` | `MIGRATED_TOKENS` | 22 nomes | + `seq-750` |

A lista dos que herdam do claro no escuro continua com três nomes (`baseline`,
`destructive`, `secundaria`) — `seq-750` tem valor próprio no escuro, como manda a
regra.

**Decisão registrada (a Task 3 deixava em aberto):** os dois valores de `seq-750` para
`#003c71` (`#002749` e `#b8deff`) **foram** fixados em `test_tema.py`, mas **fora** do
dict `esperado`, com comentário explicando por quê. Aquele dict é o conjunto de valores
*medidos no padrão de referência*, e a `rampa_uo` de lá tem três degraus: pôr `seq-750`
ali diria que o padrão publica um valor que ele não publica. Fixado logo abaixo, tem o
mesmo efeito prático — mexer nos coeficientes reprova.

## Verificação

| Comando | Resultado |
|---|---|
| `ensaio_django.sh testar apps.exemplo.tests.test_dashboard` (ANTES) | **FAILED (failures=4)** — RED confirmado |
| `ensaio_django.sh testar apps.exemplo.tests.test_dashboard` (DEPOIS) | 16 testes, OK |
| `ensaio_django.sh testar core apps.exemplo` | 169 testes, OK |
| `python3 -m unittest discover -s .template-tests -p 'test_*.py'` | 39 testes, OK |
| `docker build --target assets .` | exit 0 |
| `git diff --numstat core/tema.py` | `20  0` — 0 remoções |
| `git diff … \| grep -c '^-.*com_hsl("#003c71"'` | 0 |
| `grep -c -- "--cor-seq-750" core/static/src/input.css` | 2 |
| `grep -c "seq-750" tailwind.config.js` | 1 |
| `grep -c "brand-tint" apps/…/views.py` | 0 |

## Deviations from Plan

### Ajustes automáticos (Regra 1 / Regra 3)

**1. [Regra 3 - Bloqueio] Dois greps de critério de aceite reprovavam por causa da própria prosa explicativa**

- **Encontrado em:** Tasks 1 e 2
- **Problema:** o critério pedia `grep -c 'rampa["claro"][0] == ' ...` igual a 0 e
  `grep -c "brand-tint" apps/…/views.py` igual a 0. A primeira versão do docstring do
  teste substituto citava a asserção antiga *literalmente* para explicar por que ela
  saiu, e o comentário de racional de `views.py` nomeava o token removido para
  documentar o defeito. Os dois greps são cegos a contexto: uma citação em comentário
  reprovava exatamente o código que eliminou o problema.
- **Correção:** a explicação ficou (é ela que impede alguém de "restaurar" o índice
  mágico numa falha futura), mas descrita em prosa — "o degrau de índice ZERO", "o token
  de FUNDO tênue da família de marca" — com uma frase dizendo explicitamente que a forma
  literal foi omitida de propósito porque o gate a procura no fonte.
- **Arquivos:** `apps/…exemplo…/tests/test_dashboard.py`, `apps/…exemplo…/views.py`
- **Commits:** `4181fd2`, `d307a8c`

### Divergências entre a previsão do plano e a medição

**1. A falha esperada era dupla; foi simples de causa, dupla de sintoma**

O plano previa que o teste vermelho reprovasse por duas razões independentes — token de
superfície E rampa não-monotônica. Medido: as 4 falhas foram todas do quarto degrau
(partes 1 e 2 do gate). A parte 3 **passava** no estado defeituoso, porque `brand-tint`
por acaso já era a cor de menor contraste dos quatro e ocupava a última posição — a
rampa era "monotônica" descendo até a invisibilidade. Isso não enfraquece o gate: é
justamente a razão de as três partes existirem juntas, já que a monotonicidade sozinha
não detecta o G-03. Registrado aqui porque contradiz uma frase do plano.

**2. O valor de `seq-750:escuro` para `#1e40af` não é o estimado no plano**

O plano estimava ≈ `#cad3ec` (≈ 10,8:1) e mandava conferir em vez de confiar. Medido:
`#c2cef5`, **10,31:1**. A propriedade exigida (ser o de maior contraste do tema) vale
com folga; o número do plano era estimativa e o registrado aqui é medição.

## Known Stubs

Nenhum. Os quatro degraus são derivados em runtime da `COR_PRIMARIA` efetiva, sem valor
cravado em nenhum ponto da cadeia view → `json_script` → ECharts.

## Threat Flags

Nenhuma superfície nova. A única entrada continua sendo `COR_PRIMARIA`, validada como
`#RRGGBB` no boot de `config/settings/base.py`; `familia_marca()` não recebe dado de
request. `T-07-39` (acréscimo quebrar coeficiente herdado) e `T-07-40` (`seq-750` fora
de `_CHAVES_MARCA`) estão mitigados por asserção, não por convenção.

## Self-Check: PASSED

- `core/tema.py`, `core/static/src/input.css`, `tailwind.config.js`,
  `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/views.py`,
  `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py`,
  `core/tests/test_tema.py`, `.template-tests/test_07_tokens.py` — todos presentes
- Commits `4181fd2`, `d307a8c`, `a7b1529` — todos encontrados em `git log`
- Árvore de trabalho limpa; nenhum arquivo apagado nos três commits
