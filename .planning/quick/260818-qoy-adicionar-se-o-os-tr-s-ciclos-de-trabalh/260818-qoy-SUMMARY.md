---
phase: quick-260818-qoy
plan: 01
subsystem: docs
tags: [readme, documentacao, copier, template]
requires: []
provides:
  - "Seção '## Os três ciclos de trabalho' no README.md do template-fonte"
affects: []
tech-stack:
  added: []
  patterns: []
key-files:
  created: []
  modified:
    - README.md
decisions:
  - "Ciclos apresentados como lista com negrito + tabela de leitura rápida + regra-resumo em blockquote, sem duplicar nenhum bloco de comandos"
metrics:
  duration: "~2 min"
  completed: "2026-08-18"
---

# Quick Task 260818-qoy: Seção "Os três ciclos de trabalho" no README — Summary

**One-liner:** README do template-fonte ganhou seção de orientação logo após a
introdução, explicando quando usar cada ciclo (evoluir o template / nascer um
sistema / operar um sistema) com âncoras para as seções canônicas e a
regra-resumo `.sh` = antes de tag; `copier copy` = nascimento; `copier update`
= atualizar sistema existente.

## O que foi feito

### Task 1: Inserir seção "Os três ciclos de trabalho" no README.md

- **Commit:** f910787 (35 inserções, apenas README.md)
- Nova seção `## Os três ciclos de trabalho` posicionada entre o parágrafo
  introdutório e `## Ferramenta isolada e versão aprovada`.
- Frase de abertura orienta a identificar o ciclo antes de digitar qualquer
  comando, evitando rodar script de release dentro de um sistema ou comando de
  runtime na raiz do template.
- Três ciclos descritos em lista com negrito:
  - **Evoluir o template** — raro; regressão de `.template-tests/` antes da
    tag semver; scripts `.sh` rodam uma vez por release, nunca por sistema.
  - **Nascer um sistema** — uma vez por sistema; `copier copy` da tag estável
    + `.env` + Compose + migrate + createsuperuser; nenhum script do template
    é executado no nascimento.
  - **Operar um sistema** — dia a dia; `docker compose logs/exec/restart` e
    `manage.py test`, guiado pelo README renderizado; `.template-tests/` nem
    existem no sistema gerado.
- Tabela de leitura rápida com colunas ciclo | quando | comandos-chave |
  seção de referência, comandos apenas como menções inline.
- Regra-resumo em blockquote destacado fechando a seção.
- Quatro âncoras conferidas letra a letra contra os headings existentes:
  `#regressão-do-template`, `#releases-e-atualização-do-núcleo`,
  `#nascimento-local-de-um-sistema`, `#publicação-com-proxy-tls-e-dns`.

## Verificação

Verificação automatizada do plano executada com sucesso:

- Heading `## Os três ciclos de trabalho` aparece exatamente 1 vez.
- As quatro âncoras estão presentes dentro da nova seção.
- Zero blocos de código cercados (```) dentro da nova seção.
- `git diff --name-only` mostrou somente README.md antes do commit.

## Desvios do plano

Nenhum — plano executado exatamente como escrito.

## Known Stubs

Nenhum — mudança doc-only, puramente aditiva.

## Threat Flags

Nenhum — nenhuma superfície de segurança nova.

## Self-Check: PASSED

- README.md modificado e commitado (f910787): FOUND
- Commit f910787 presente no histórico: FOUND
