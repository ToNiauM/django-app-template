---
phase: 07-herdar-o-design-system-do-pca
plan: 10
subsystem: navegacao
tags: [nav, aria-current, acessibilidade, gap-closure, item-ativo, copier]
gap_closure: true
dependency-graph:
  requires: []
  provides:
    - "item-ativo-unico"
    - "item-nav-tolerante-a-contexto-sem-request"
    - "inclusao-tolerante-do-nav-dominio"
  affects:
    - "core/templatetags/navegacao.py"
    - "core/templates/core/_nav.html"
    - "core/templates/core/_nav_dominio.html.jinja"
tech-stack:
  added: []
  patterns:
    - "Correspondência exata de rota vence correspondência por prefixo; a exceção é declarada no sítio da chamada, não inferida — uma inclusion_tag não enxerga os irmãos e qualquer inferência dependeria da ordem do arquivo do derivado"
    - "Include de arquivo que pertence ao derivado passa por simple_tag tolerante — o Django não tem `ignore missing` (isso é Jinja2)"
    - "Teste de fechamento de gap prova o ARTEFATO renderizado (core/_nav.html + o stub semeado, com request real), não a tag isolada"
key-files:
  created:
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_nav_ativo.py"
  modified:
    - "core/templatetags/navegacao.py"
    - "core/templates/core/_nav.html"
    - "core/templates/core/_nav_dominio.html.jinja"
    - "core/tests/test_navegacao.py"
    - ".template-tests/test_07_nav_extensao.py"
decisions:
  - "`excecoes` entra no FIM da assinatura de item_nav (posicional-compatível): nenhuma chamada existente no template do derivado precisa mudar no copier update"
  - "A correspondência exata nunca é anulada por `excecoes` — é o que impede que uma exceção mal escrita apague o estado ativo do item dono da rota"
  - "A topologia pai/filho do núcleo é exercitada contra um urlconf sintético declarado no próprio módulo de teste (`@override_settings(ROOT_URLCONF=__name__)`), não contra as rotas do app exemplo: a suíte do core roda nas duas variantes de geração"
  - "`{% nav_dominio %}` substitui `{% include %}` literal: o arquivo é do derivado e apagá-lo é estado previsto — menu vazio, nunca 500"
metrics:
  duration: 18min
  tasks: 3
  files: 5
  completed: 2026-08-24
requirements: [NAV-01, NAV-02, NAV-03, QA-03]
---

# Phase 07 Plan 10: Um item ativo por página Summary

O menu do sistema de referência para de acender dois itens ao mesmo tempo: `item_nav`
ganha desempate explícito (`excecoes`), o stub que o núcleo semeia declara a exceção, e há
um teste que renderiza `core/_nav.html` inteiro com request real e exige exatamente um
`aria-current="page"`.

## O que foi construído

### Task 1 — a prova executável do defeito (RED)

Dois arquivos de teste, escritos e rodados ANTES de qualquer conserto.

**`apps/…exemplo…/tests/test_nav_ativo.py`** (novo) — prova o G-01 com o stub REAL.
`render_to_string("core/_nav.html", request=RequestFactory().get(caminho))` renderiza o
menu inteiro: item do núcleo (`core:shell`) + `{% nav_dominio %}` + os dois itens do
exemplo. `request=` é o que faz o context processor de request rodar e o `{% item_nav %}`
enxergar `request.path`.

Não basta contar: a contagem sozinha passaria por acidente se o item errado acendesse.
`TAG_ANCORA = re.compile(r"<a\b[^>]*>")` casa cada `<a …>` com atributos, e a asserção
verifica que a ÚNICA tag com `aria-current="page"` é a que carrega o `href` do
`reverse()` esperado.

Três caminhos, e os três juntos são o que impede o conserto de virar "desligar o prefixo":

| Caminho | Item que deve acender | Por quê |
|---|---|---|
| `/exemplo/dashboard/` | Dashboard | correspondência exata |
| `/exemplo/` | Itens (CRUD) | correspondência exata |
| `/exemplo/42/editar/` | Itens (CRUD) | rota-filha sem item próprio — o `prefixo` |

O quarto teste (`test_o_stub_semeado_declara_os_dois_itens_do_exemplo`) é guarda do próprio
teste: sem ele, os três acima passariam por ausência de item, não por desempate.

**`core/tests/test_navegacao.py`** — a topologia, sem depender do app exemplo. O módulo
declara o próprio `urlpatterns` (`/x/`, `/x/y/`, `/x/z/`, `/x/<pk>/editar/` num namespace
`sintetico`) e a classe nova aplica `@override_settings(ROOT_URLCONF=__name__)`. É a forma
mínima em que a colisão pode acontecer, e roda nas duas variantes de geração.

O teste antigo `test_prefixo_marca_ativo_em_rota_filha` usava `rota="core:shell"` com
`prefixo="/exemplo/"` — a única combinação do universo em que a colisão é impossível,
porque a URL exata do item (`/`) nunca está sob o prefixo declarado (IN-07). Ele saiu de
`ItemNavTests` e voltou na classe nova com o item DONO do prefixo tendo URL sob o prefixo,
como no stub real. Os 5 testes restantes de `ItemNavTests` (escape do rótulo, ícone
desconhecido, `NoReverseMatch`, ativo/inativo por caminho) ficaram intactos — nenhuma
asserção existente foi removida ou relaxada.

### As saídas de falha, contra o código de hoje

`bash .template-tests/ensaio_django.sh testar core.tests.test_navegacao apps.exemplo.tests.test_nav_ativo`:

```
FAIL: test_em_dashboard_apenas_o_item_dashboard_fica_ativo
  (apps.exemplo.tests.test_nav_ativo.ItemAtivoUnicoNoMenuSemeadoTests)
O defeito do G-01, na forma exata em que ele aparece.
----------------------------------------------------------------------
AssertionError: 2 != 1 : em /exemplo/dashboard/ o menu marcou 2 itens como
atuais; aria-current indica UMA localização

Ran 21 tests in 0.030s
FAILED (failures=1, errors=17)
EXIT=1
```

**A contagem é 2.** O defeito é determinístico e apareceu na primeira execução, com o stub
que o próprio núcleo semeia — não numa combinação construída para o teste.

Os 17 erros são os outros três grupos, cada um por um motivo distinto e verificável:

| Grupo | Erro contra o código antigo |
|---|---|
| `excecoes` (7 testes) | `IndexError: pop from empty list` em `library.py:456 parse_bits` — a tag recebia 5 argumentos e a assinatura tinha 4 |
| contexto sem `request` (2 testes) | `KeyError: 'request'` em `navegacao.py:54` |
| `nav_dominio` (3 testes) | `AttributeError: … does not have the attribute 'get_template'` — a tag não existia |
| `ItemNavTests` (5 testes) | mesmo `IndexError` do `parse_bits`: o helper `_renderizar` compartilhado passou a mandar `excecoes` |

Commit: `62d7c25`.

### Task 2 — o conserto (GREEN)

**A. `item_nav`.** A regra final, com `excecoes=""` no fim da assinatura:

```python
request = context.get("request")
caminho = request.path if request is not None else ""

sob_prefixo = bool(prefixo) and caminho.startswith(prefixo)
excluido    = any(caminho.startswith(p) for p in excecoes.split() if p)
ativo       = caminho == url or (sob_prefixo and not excluido)
```

Três coisas de uma vez. O `or` de fora garante que a **correspondência exata nunca é
anulada** por `excecoes` — um item continua ativo na própria URL, aconteça o que
acontecer, e é isso que impede que uma exceção mal escrita apague o estado do item dono da
rota. O parâmetro entra no FIM, posicional-compatível: nenhuma chamada existente no
`_nav_dominio.html` de um derivado precisa mudar no `copier update`. E `context.get()`
fecha o WR-02.

A docstring diz **por que** a exceção é declarada e não inferida: uma `inclusion_tag`
renderiza um item por vez, sem estado compartilhado e sem enxergar os irmãos; qualquer
desempate automático dependeria da ORDEM em que os itens aparecem no arquivo — frágil
exatamente no arquivo que pertence ao derivado. Declarada, a exceção é lida junto com o
item que ela governa.

O parágrafo do T-07-07 (a tag NÃO é mecanismo de autorização) continua no cabeçalho do
módulo, palavra por palavra.

**B. `nav_dominio`.** `simple_tag(takes_context=True)` que devolve `""` em
`TemplateDoesNotExist`. `context.flatten()` é o que faz `request` e o resto do contexto
chegarem aos `{% item_nav %}` de dentro do arquivo incluído — dois testes provam isso
(repasse de variável e markup não-escapado).

**C. `_nav.html`.** `{% include "core/_nav_dominio.html" %}` → `{% nav_dominio %}`, e o
`{% comment %}` do topo ganhou a linha que declara a tolerância como decisão.

**D. O stub semeado.** `core/templates/core/_nav_dominio.html.jinja`, dentro do
`{% raw %}` e do `{% if incluir_app_exemplo %}`:

```
{% item_nav "exemplo:item_listar" "Itens (CRUD)" "lista" "/exemplo/" "/exemplo/dashboard/" %}
```

E o bloco de contrato do topo (também dentro do `{% raw %}`) passou a ensinar `excecoes`:
a linha de forma agora é `{% item_nav "app:rota" "Rótulo" "icone" "prefixo-opcional"
"excecoes-opcionais" %}`, com o parágrafo que explica que sem ela dois itens acendem
juntos. **É onde o conserto se propaga** — todo mantenedor de derivado que for criar um
item lê esse texto.

`_item_nav.html` não foi tocado: o tratamento visual está correto, o defeito era de
decisão de estado, não de marcação.

Commit: `5fccd41`.

### Task 3 — a asserção que não podia falhar

O bloco removido de `.template-tests/test_07_nav_extensao.py` (l. 83-98), na íntegra:

```python
with tempfile.TemporaryDirectory() as tmp:
    destino = render(Path(tmp) / "sis", incluir_app_exemplo=False)
    nav = destino / "core/templates/core/_nav.html"
    antes = nav.read_bytes()

    dominio = destino / "core/templates/core/_nav_dominio.html"
    dominio.write_text(
        '{% load navegacao %}\n{% item_nav "core:shell" "Painel" "casa" %}\n',
        encoding="utf-8",
    )

    self.assertEqual(
        antes,
        nav.read_bytes(),
        "_nav.html foi modificado ao adicionar itens no derivado",
    )
```

Lê os bytes de `_nav.html`, escreve em **outro** arquivo, e assere que `_nav.html` não
mudou. Nenhum código toca `_nav.html` entre as duas leituras — a asserção não podia falhar
nem se o ponto de extensão inteiro fosse removido (WR-07).

O substituto gera as **duas** variantes (`incluir_app_exemplo` true e false, ambas com
`--vcs-ref=HEAD`) e compara `core/templates/core/_nav.html` byte a byte **entre elas** — o
padrão de `test_04_04_optional_exemplo.py:96-101`. Devolver um `{% if incluir_app_exemplo %}`
para dentro do `_nav.html` quebra esta; a antiga não quebraria. Foram acrescentadas ao
mesmo teste duas guardas de WR-10: `{% nav_dominio %}` presente e nenhum `{% include`
literal.

Teste novo `test_stub_semeado_declara_a_excecao_que_evita_dois_itens_ativos`: na árvore
gerada com `incluir_app_exemplo=true`, a linha do `exemplo:item_listar` tem que carregar
`"/exemplo/"` **e** `"/exemplo/dashboard/"`, e o texto do stub tem que conter `excecoes`.
É o gate que impede um `copier update` futuro de reintroduzir a colisão pela porta do stub.

Intactas as duas provas que já valiam: rotas de `_nav.html` só no namespace `core:` e o
sha256 da subárvore `core/` inteira (`test_remover_itens_do_exemplo_nao_toca_nenhum_arquivo_do_nucleo`),
que é a prova executável do critério 5 da fase e continua verde.

A suíte **não** mantinha contagem de itens nem de linhas do `_nav.html` — nada a atualizar
nesse ponto. O que mudou é a contagem de testes do arquivo: **3 → 4**, medida.

Commit: `bb4efae`.

## Prova negativa do gate novo

Um gate que passa antes e depois não guarda nada. A exceção foi removida do stub à mão e o
teste rodado:

```
$ sed -i 's| "/exemplo/" "/exemplo/dashboard/"| "/exemplo/"|' core/templates/core/_nav_dominio.html.jinja
$ python3 -m unittest test_07_nav_extensao.ExtensaoDeNavegacaoTests.test_stub_semeado_declara_a_excecao_que_evita_dois_itens_ativos

AssertionError: '"/exemplo/dashboard/"' not found in
'{% item_nav "exemplo:item_listar" "Itens (CRUD)" "lista" "/exemplo/" %}' :
o item do prefixo não excetua /exemplo/dashboard/: dois itens acendem juntos no dashboard

Ran 1 test in 9.589s
FAILED (failures=1)
```

Stub restaurado em seguida; `grep -c '/exemplo/dashboard/'` de volta a 1.

## Verificação

| Comando | Resultado |
|---|---|
| `bash .template-tests/ensaio_django.sh testar core apps.exemplo` | **OK — 145 testes**, exit 0 |
| `python3 .template-tests/test_07_nav_extensao.py -v` | OK — 4 testes, 31,4 s, exit 0 |
| `python3 -m unittest discover -s .template-tests -p 'test_*.py'` | OK — 39 testes, 134,9 s, exit 0 |
| `git ls-files \| grep _nav` | 6 arquivos; nenhum par `.jinja` órfão |

145 = 130 (estado ao fim do 07-09) + 15 novos (11 em `core.tests.test_navegacao`, 4 em
`apps.exemplo.tests.test_nav_ativo`). 39 = 38 + 1 (o gate do stub).

`git ls-files | grep _nav` confirma que os únicos arquivos de nav são `_nav.html`,
`_item_nav.html` e `_nav_dominio.html.jinja` (mais os três de teste). **`_nav.html` não tem
par `.jinja`** — `git ls-files | grep -c '_nav.html.jinja'` retorna 0, então não houve par
templatizado a sincronizar, que é o erro clássico deste repositório.

Critérios mecânicos do plano:

| Critério | Exigido | Medido |
|---|---|---|
| `grep -c "aria-current" …/test_nav_ativo.py` | ≥ 3 | 5 |
| `grep -c "override_settings" core/tests/test_navegacao.py` | ≥ 1 | 3 |
| `core:shell` dentro do teste de prefixo | ausente | ausente (urlconf sintético) |
| `grep -c "excecoes" core/templatetags/navegacao.py` | ≥ 3 | 5 |
| `grep -c "context\[.request.\]" core/templatetags/navegacao.py` | 0 | 0 |
| `grep -c "include" core/templates/core/_nav.html` | 0 | 0 |
| `grep -c '/exemplo/dashboard/' …/_nav_dominio.html.jinja` | 1 | 1 |
| `git ls-files \| grep -c '_nav.html.jinja'` | 0 | 0 |
| `grep -c "incluir_app_exemplo" .template-tests/test_07_nav_extensao.py` | ≥ 2 | 9 |
| `grep -c "exemplo/dashboard" .template-tests/test_07_nav_extensao.py` | ≥ 1 | 3 |
| `grep -c "nav_dominio" core/templates/core/_nav.html` | 1 | **2** — ver desvio 1 |

## Decisões

**`excecoes` no fim da assinatura, e não um parâmetro nomeado novo no meio.** A tag é
chamada posicionalmente no arquivo do derivado (`{% item_nav "app:rota" "Rótulo" "icone"
"/prefixo/" %}`). Qualquer posição que não seja a última quebraria toda chamada existente
no próximo `copier update` — e o arquivo é justamente o que o núcleo nunca reescreve, então
a quebra seria silenciosa até alguém abrir a página.

**Exato vence, sempre.** `ativo = caminho == url or (sob_prefixo and not excluido)`. O
`excluido` só pode desligar o ramo do prefixo. Uma exceção copiada errado degrada para "o
item do prefixo não acende numa rota-filha", nunca para "o item some da própria URL".

**Urlconf sintético em vez das rotas do exemplo, na suíte do núcleo.** As rotas `exemplo:*`
só existem com `incluir_app_exemplo=true`. Amarrar a prova topológica a elas deixaria a
suíte do `core` dependente da variante de geração. O `urlpatterns` de módulo com
`@override_settings(ROOT_URLCONF=__name__)` reproduz a forma exata do defeito (item dono do
prefixo com URL sob o prefixo + irmão com URL exata sob ele) e roda nas duas variantes. A
prova com o stub REAL vive no app exemplo, onde as rotas existem por construção.

**`mark_safe` em `nav_dominio` não é atalho (T-07-27).** O conteúdo é um template
renderizado pelo próprio motor do Django, com autoescape já aplicado dentro do render — não
é string vinda de request. `test_rotulo_com_script_sai_escapado` segue verde e não foi
tocado; um teste novo (`test_markup_do_arquivo_incluido_nao_sai_escapado`) fixa o
comportamento pretendido do lado oposto.

## Deviations from Plan

**1. [Rule 3 - Bloqueio] `grep -c "nav_dominio" core/templates/core/_nav.html` retorna 2, não 1**

- **Found during:** Task 2
- **Issue:** o critério literal é impossível de satisfazer sem quebrar outro gate já verde.
  Com o `{% include %}` removido, a única fonte da string `core/_nav_dominio.html` dentro
  de `_nav.html` passa a ser o comentário do topo — e
  `.template-tests/test_04_04_optional_exemplo.py:106` faz
  `self.assertIn("core/_nav_dominio.html", nav_texto)`. Zerar a menção no comentário
  reprovaria esse teste e, pior, apagaria a única frase que diz ao mantenedor de derivado
  ONDE pôr os itens dele. O arquivo já tinha 2 linhas com `nav_dominio` antes deste plano
  (comentário + include), então o critério nunca foi alcançável em 1.
- **Fix:** a intenção do critério — **uma única invocação da tag** — foi cumprida
  literalmente: `grep -c '{% nav_dominio %}'` retorna **1**. As menções em prosa foram
  reduzidas ao mínimo: o caminho aparece uma vez (linha 7, a que o `test_04_04` exige) e a
  frase "a extensão vem da tag abaixo" deixou de repetir o nome. Total: 2 linhas, o mínimo
  alcançável.
- **Files modified:** `core/templates/core/_nav.html`
- **Commit:** `5fccd41`

Nenhum outro desvio. Nenhuma asserção existente foi removida ou relaxada; nenhum pacote
novo foi instalado.

## Known Stubs

Nenhum. As três entregas são executáveis e exercitadas por teste. O único "stub" do plano é
`core/templates/core/_nav_dominio.html`, que é stub **por design** (`_skip_if_exists`: o
arquivo pertence ao derivado) e cujo conteúdo semeado agora é auditado por gate.

## Threat Flags

Nenhuma superfície nova fora do `<threat_model>` do plano. `nav_dominio` está coberta por
T-07-27 (mitigate — autoescape do próprio motor, provado por teste) e T-07-30 (mitigate —
`""` em `TemplateDoesNotExist`, teste dedicado). `excecoes` está coberta por T-07-29
(accept — `str.split()` sobre string de menu). O parágrafo do T-07-28 sobreviveu à
reescrita da docstring, como o registro exigia.

## O que este plano NÃO fez

Deliberado, para não invadir os planos seguintes da onda:

- **G-02** (texto branco sobre a marca no escuro, 2,56:1) — nenhuma cor tocada
- **G-03/G-04** (4ª fatia do donut e grade do eixo) — intocados
- Nenhuma contagem de token mudou; `core/tema.py` e `input.css` não foram abertos

## Autoteste

Arquivos declarados como criados:

- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_nav_ativo.py` — FOUND

Commits declarados:

- `62d7c25` — FOUND
- `5fccd41` — FOUND
- `bb4efae` — FOUND

## Self-Check: PASSED
