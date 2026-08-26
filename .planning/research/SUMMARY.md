# Resumo da Pesquisa — Marco v0.3.0

**Projeto:** Sistema Base — Template CFC
**Marco:** v0.3.0 — Guia de construção de sistemas
**Pesquisado:** 2026-08-25 (inline, sem subagentes — mesmo modo da v0.2.0)
**Confiança:** ALTA — o marco quase não tem incógnita técnica; a pesquisa fixa forma didática, integração Copier e guardas contra apodrecimento

## Sumário executivo

O marco adiciona um **tutorial** (no sentido Diátaxis: aprender fazendo) ao template: do sistema recém-gerado a um app de domínio completo — diárias e passagens conduzido passo a passo, orçamento e controle de materiais resumidos. O modelo de ritmo é o tutorial oficial do Django: todo capítulo termina com resultado visível na tela. O guia ensina o *método do template* (modelar em `apps/`, copiar o padrão do `exemplo`, plugar na nav via `{% item_nav %}`, descartar o exemplo ao final) — nunca Django genérico, que fica em links.

A abordagem recomendada inverte a ordem intuitiva: **o código vem antes do texto**. O app de diárias nasce como fixture em `.template-tests/fixtures/`, é instalado numa cópia Copier real pelo harness existente (`ensaio_django.sh`) e provado com migração, testes e smoke. Só então os capítulos são escritos extraindo trechos do fixture, com um teste que exige igualdade byte a byte entre a cerca de código do guia e o arquivo correspondente — a lição central da v0.2.0 ("guarda executável em vez de convenção escrita") aplicada a documentação.

Os dois maiores riscos não são técnicos: (1) **jargão** — o requisito "menos técnico possível" exige glossário, regra de tradução na primeira ocorrência e uma revisão editorial com persona explícita como gate de *resultado*, não de estrutura; (2) **apodrecimento** — sem a prova executável, cada refactor futuro do template é uma chance de o guia mentir. E vale a lição nº 1 da retrospectiva: o guia só chega aos derivados quando a tag `v0.3.0` for publicada — a publicação é critério de fase, não afterthought.

## Achados-chave

### Stack

**Nenhuma dependência nova.** Markdown puro (sem MkDocs/Sphinx — violaria a portabilidade); extração de snippets com stdlib; prova reutilizando o harness `.template-tests/` existente. Diagramas em ASCII.

### Features

**Table stakes:** exemplo completo do zero à tela com menu; resultado visível por capítulo; pré-requisitos explícitos; glossário; troubleshooting por capítulo; como criar app em `apps/`; uso do `{% item_nav %}`; quando remover o `exemplo` (link, não duplicação).
**Diferenciais:** 2 exemplos resumidos mostrando só o que muda; capítulo de dashboard com a paleta da marca; mapa de receitas; código provado por teste.
**Anti-features:** ensinar Django do zero; repetir operação do README; screenshots; entregar o app de diárias como unidade Copier opcional.

### Arquitetura

- `docs/guia/*.md` como **arquivo do núcleo** (não `_skip_if_exists` — o derivado lê e recebe correções pelo `copier update`; congelar seria o erro inverso da nav).
- Código do exemplo em `.template-tests/fixtures/guia/` — nunca em `apps/` do template (Fora de Escopo protegido por teste negativo: a cópia gerada não contém `apps/diarias`).
- Suíte nova `test_08_guia*`: instala o fixture numa cópia gerada, prova que funciona; segundo teste prova que o guia cita o fixture byte a byte.
- README (984 linhas) ganha só uma seção curta de link; fronteira editorial: README = nascer e operar, guia = construir o domínio.

### Armadilhas principais

1. Código do guia quebrando em silêncio → fixture + igualdade byte a byte (guarda executável).
2. Domínio vazando para o template → fixture no `_exclude` + teste negativo.
3. Guia virando conflito de `copier update` → dono declarado (núcleo) + ensaio de update cobrindo `docs/`.
4. Jargão → glossário + revisão editorial com persona como gate.
5. Duplicação do README → fronteira editorial + links.
6. Tag para trás (repetir a Fase 6) → publicação da `v0.3.0` como critério de fase.

## Implicações para o roadmap

Ordem de construção com dependências reais (3 fases é o tamanho natural):

1. **Fixture provado + suíte de prova** — o app de diárias funcionando numa cópia gerada, guardas negativas e de equivalência prontas (vazias de guia ainda).
2. **Escrita do guia** — capítulos do exemplo completo extraindo do fixture; depois capítulo 0 (linguagem/glossário), resumidos e encerramento; revisão editorial de acessibilidade como gate.
3. **Integração e release** — chegada via `copier copy`, `copier update` limpo cobrindo `docs/`, links no README/README.jinja, tag `v0.3.0` publicada (verificar → revisar → consertar → taguear).
