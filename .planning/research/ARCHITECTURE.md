# Pesquisa de Arquitetura — Guia de construção de sistemas (v0.3.0)

**Marco:** v0.3.0 — Guia de construção de sistemas
**Contexto:** arquitetura existente mapeada em PROJECT.md; aqui só a integração do guia.
**Pesquisado:** 2026-08-25
**Confiança:** ALTA (fatos verificados no `copier.yml` e na árvore do repositório)

## Fatos do repositório que condicionam o desenho

- `copier.yml` usa `_exclude` por caminho de **destino**; `.template-tests/` e `.planning/` nunca chegam ao sistema gerado.
- `_skip_if_exists` marca arquivos que são **do derivado** (`_nav_dominio.html`, `dominio.css`) — o `copier update` nunca os reescreve.
- `README.md.jinja` renderiza e substitui o `README.md` do template na cópia — precedente direto para um `docs/guia/*.md.jinja` se houver interpolação.
- O `README.md` tem **984 linhas** — confirma a decisão de guia em arquivo(s) próprio(s).
- Não existe `docs/` hoje; o diretório nasce neste marco.
- Harness de prova: `ensaio_django.sh` gera cópia Copier real com banco e roda suítes dentro dela; 13 suítes `test_*` em `.template-tests/`.

## Componentes novos

| Componente | Onde | Dono | Chega ao gerado? |
|------------|------|------|------------------|
| Guia (capítulos) | `docs/guia/*.md` (ou `.md.jinja` onde citar `{{ sistema_nome }}`) | **Núcleo** (upstream) | Sim — e o `copier update` o atualiza |
| Link para o guia | Seção curta no `README.md` e no `README.md.jinja` | Núcleo | Sim |
| Fixture do exemplo completo (código de diárias e passagens) | `.template-tests/fixtures/guia/` (nome a definir no plano) | Template apenas | **Não** (`_exclude`) |
| Suíte de prova do guia | `.template-tests/test_08_guia*.{sh,py}` | Template apenas | Não |

## Decisão estrutural central: o guia é arquivo do núcleo, NÃO `_skip_if_exists`

O `_skip_if_exists` existe para arquivos que o derivado **edita** (nav, css de domínio). O guia é o oposto: conteúdo de referência que o derivado **lê** e que deve receber correções pelo `copier update`. Colocá-lo em `_skip_if_exists` congelaria cada derivado na versão do guia do dia do `copier copy`.

Consequência (mesma disciplina do `core/`): o derivado não deve editar `docs/guia/` — regra dita na introdução do próprio guia. Se o derivado editar, o `copier update` sobrescreve? Não: o Copier faz merge de 3 vias e **gera conflito** — exatamente o cenário que a Fase 7 eliminou para a nav. O guia precisa dizer isso com todas as letras ("este diretório pertence ao núcleo; anote suas notas fora dele").

## Estrutura proposta do guia

```
docs/
└── guia/
    ├── 00-comece-aqui.md        # o que é, para quem é, pré-requisitos, como ler, glossário
    ├── 01-seu-primeiro-app.md   # apps/diarias nasce: modelo, migração, admin
    ├── 02-a-primeira-tela.md    # listagem paginada copiando o padrão do exemplo
    ├── 03-criar-e-editar.md     # formulário modal HTMX (422 + HX-Trigger)
    ├── 04-menu-e-navegacao.md   # _nav_dominio.html + {% item_nav %}
    ├── 05-o-painel.md           # dashboard ECharts com a paleta da marca
    ├── 06-outros-sistemas.md    # orçamento e materiais resumidos: só o que muda
    └── 07-daqui-em-diante.md    # remover o app exemplo, receitas, aprenda mais
```

(Granularidade final é decisão de plano; a pesquisa fixa apenas: multi-arquivo, numerado, progressão tutorial com resultado visível por capítulo.)

## Fluxo do código provado

```
.template-tests/fixtures/guia/   (arquivos do app diárias, fonte da verdade)
        │
        ├─► extração/inclusão nos capítulos do guia  ──► docs/guia/*.md
        │        (teste compara: trecho do guia ≡ arquivo do fixture)
        │
        └─► suíte test_08: ensaio_django.sh gera cópia,
            instala o fixture como apps/diarias na cópia,
            roda migrate + testes do app + smoke das telas
```

Duas provas distintas e complementares:
1. **O código funciona** — fixture instalado numa cópia gerada real: migra, sobe, responde.
2. **O guia não mente** — cada cerca de código do guia é byte-idêntica ao arquivo correspondente do fixture (mesmo espírito da guarda sha256 da Fase 7: guarda executável, não convenção).

## Ordem de construção sugerida

1. Fixture do exemplo completo funcionando numa cópia gerada (o código antes do texto — o guia descreve o que já foi provado).
2. Suíte de prova (instalação do fixture + equivalência guia↔fixture).
3. Capítulos do exemplo completo (01–05), escritos extraindo do fixture.
4. Capítulo 00 (linguagem, glossário) e 06–07 (resumidos + encerramento).
5. Integração: `copier.yml`/README/README.jinja + prova de chegada na cópia e de `copier update` limpo.
6. Tag `v0.3.0` publicada (lição 1 da retrospectiva: sem tag, nenhum derivado recebe o guia).

## O que NÃO muda

- Nenhum arquivo de `core/`, `config/`, `apps/exemplo/` — o guia referencia, não altera.
- Nenhuma variável nova no `copier.yml` (salvo confirmação em plano de que o guia precisa interpolar algo além das existentes).
