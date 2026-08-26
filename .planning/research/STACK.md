# Pesquisa de Stack — Guia de construção de sistemas (v0.3.0)

**Marco:** v0.3.0 — Guia de construção de sistemas
**Contexto:** MARCO SUBSEQUENTE — adiciona documentação didática ao template existente. Capacidades já validadas (Django 5.2, Copier, Tailwind, suíte `.template-tests/`) NÃO são re-pesquisadas.
**Pesquisado:** 2026-08-25
**Confiança:** ALTA (o marco quase não adiciona stack; a análise é sobre ferramentas de documentação)

## Adições de stack necessárias

**Nenhuma dependência de runtime nova.** O guia é Markdown puro, lido no GitHub/editor — o mesmo formato do `README.md` e dos `core/README.md`/`apps/exemplo/README.md` já existentes.

| Necessidade | Ferramenta | Decisão |
|-------------|-----------|---------|
| Formato do guia | Markdown puro (CommonMark/GFM) | Usar — já é o padrão do repositório; zero build, zero dependência |
| Gerador de site de docs (MkDocs, Sphinx, Docusaurus) | — | **Não usar** — viola a invariante de portabilidade (nenhum passo extra no nascimento); o público lê Markdown direto |
| Verificação dos trechos de código | Suíte existente: bash POSIX em `.template-tests/` + `unittest` | Estender — mesmo padrão de `test_05_nascimento.sh` e `ensaio_django.sh`: gerar cópia real, aplicar o código do guia, rodar |
| Extração de snippets do guia | Script Python simples (stdlib: `re` sobre cercas ```python etc.) | Criar em `.template-tests/` — nada de doctest/sybil/mkdocs-test: dependência nova para o que 40 linhas de stdlib resolvem |
| Diagramas | ASCII art ou Mermaid em cerca de código | ASCII preferido — renderiza em qualquer lugar, inclusive `less` no servidor |

## Por que não adicionar nada

1. **Invariante de portabilidade:** o sistema gerado não pode depender do host. Um gerador de docs criaria um passo de build para... texto.
2. **O público-alvo do guia é o menos técnico possível** — um arquivo `.md` que abre em qualquer lugar serve melhor que um site que precisa ser servido.
3. **A infra de prova já existe:** `ensaio_django.sh` sobe uma cópia Copier real com banco. Provar o código do guia é escrever mais uma suíte `test_*` que reutiliza esse harness — padrão já estabelecido em 13 suítes.

## Pontos de integração

- `.template-tests/` (excluído do `copier.yml`) recebe a suíte que prova o guia — o fixture com o código do exemplo completo vive lá, **fora** do sistema gerado (mantém o template agnóstico de domínio).
- `copier.yml`: o(s) arquivo(s) do guia entram na cópia como arquivo do núcleo (sem `.jinja` se não houver interpolação; com, se citar `{{ sistema_nome }}`).

## O que NÃO adicionar

- MkDocs/Sphinx/Docusaurus (build desnecessário)
- sybil/pytest-doctestplus (dependência para extração que a stdlib faz)
- Screenshots como arquivos binários no template (ver PITFALLS — apodrecem e pesam o repo)
