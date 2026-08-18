---
phase: 04-templatiza-o-copier
plan: 01
subsystem: supply-chain
tags: [copier, pypi, provenance, supply-chain, checkpoint]

requires:
  - phase: 03-app-exemplo
    provides: "Sistema-base pronto para ser convertido em template Copier"
provides:
  - "Autorização específica e auditável para instalar somente copier==9.17.1 no Plano 04-02"
  - "Evidência de que nenhum binário Copier ou dependência da aplicação existia antes da instalação"
affects: [04-02, 04-03, 04-04, 04-05, 04-06, 04-07, template-copier]

actuals:
  tokens: 1724 # 6.896 caracteres no único arquivo alterado, dividido por 4
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Ferramentas externas passam por gate de procedência, versão pinada e isolamento antes de instalação."

key-files:
  created:
    - ".planning/phases/04-templatiza-o-copier/04-01-SUMMARY.md"
  modified: []

key-decisions:
  - "Autorizar exclusivamente copier==9.17.1 após cruzar PyPI oficial, documentação oficial e atestação de proveniência."
  - "Instalação futura limitada a .venv-template/; sem instalação global e sem inclusão em requirements.txt."

patterns-established:
  - "Checkpoint de cadeia de suprimentos: conferir registro, projeto oficial, versão exata, binário ausente e isolamento antes de executar ferramenta externa."

requirements-completed: [] # Este plano é um gate; TPL-01 e TPL-03 só serão concluídos pelos planos de implementação.

coverage:
  - id: D1
    description: "Autorização de procedência para copier==9.17.1 vinculada ao projeto oficial Copier."
    verification:
      - kind: other
        ref: "https://pypi.org/project/copier/9.17.1/ e https://copier.readthedocs.io/"
        status: pass
      - kind: other
        ref: "Sinal explícito: $gsd-execute-phase 4 --auto, tratado como aprovado copier==9.17.1"
        status: pass
    human_judgment: false
  - id: D2
    description: "Ambiente permanece sem instalação ou execução prévia do Copier."
    verification:
      - kind: other
        ref: "test ! -x .venv-template/bin/copier && ! command -v copier"
        status: pass
      - kind: other
        ref: "! rg -n '(^|[<=>~[:space:]])copier([<=>~[:space:]]|$)' requirements.txt"
        status: pass
    human_judgment: false

duration: "< 1 min"
completed: 2026-08-18
status: complete
---

# Phase 04 Plan 01: Proveniência do Copier Summary

**Gate de cadeia de suprimentos concluído para `copier==9.17.1`, com registro PyPI, documentação oficial e autorização explícita antes de qualquer instalação.**

## Performance

- **Duration:** < 1 min
- **Started:** 2026-08-18T16:10:09Z
- **Completed:** 2026-08-18T16:10:09Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Confirmada a distribuição oficial `copier` na versão exata `9.17.1` em `https://pypi.org/project/copier/9.17.1/`.
- Confirmado que o registro PyPI vincula a release ao projeto `copier-org/copier`, aos maintainers `sisp` e `yajo`, e à atestação Trusted Publishing/Sigstore da tag `v9.17.1`.
- Confirmado em `https://copier.readthedocs.io/` que o projeto oficial é o CLI/biblioteca de geração de templates e referencia `copier-org/copier`.
- Registrado o sinal de autorização específico e as evidências de que o Copier continua ausente do PATH, de `.venv-template/` e de `requirements.txt`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Confirmar procedência de copier==9.17.1 antes de instalar ou executar** - commit registrado no self-check abaixo (docs)

## Files Created/Modified

- `.planning/phases/04-templatiza-o-copier/04-01-SUMMARY.md` - Evidência de procedência, autorização e checagens ASVS L1 para liberar o Plano 04-02.

## Provenance and Authorization

### Fontes oficiais verificadas

- **PyPI:** `https://pypi.org/project/copier/9.17.1/` apresenta o pacote `copier` 9.17.1, os arquivos sdist/wheel e o requisito Python >= 3.10.
- **Vínculo de projeto:** a mesma release referencia `copier-org/copier`; a página lista os maintainers `sisp` e `yajo`.
- **Atestação:** PyPI informa Trusted Publishing e atestação para o workflow `release.yml` de `copier-org/copier`, com origem na tag `v9.17.1` e entradas Sigstore.
- **Documentação:** `https://copier.readthedocs.io/` identifica Copier como "a library and CLI app for rendering project templates", referencia `copier-org/copier` e documenta o comando `copier copy`.

### Sinal de autorização

O usuário invocou explicitamente `$gsd-execute-phase 4 --auto`. Conforme a instrução recebida para este checkpoint bloqueante, essa invocação é registrada como o sinal humano inequívoco **`aprovado copier==9.17.1`**, somente após a verificação independente das duas fontes oficiais acima.

Esta autorização é estritamente limitada à futura instalação de **`copier==9.17.1`** em **`.venv-template/`** pelo Plano 04-02. Ela não autoriza instalação global, versão diferente, pacote homônimo, alteração de `requirements.txt` nem execução do Copier neste plano.

## Verification Evidence

| Controle | Comando/evidência | Resultado |
|---|---|---|
| Binário isolado ausente | `test ! -x .venv-template/bin/copier` | PASS |
| Copier ausente do PATH | `! command -v copier` | PASS |
| Ferramenta fora das dependências da aplicação | `! rg -n '(^|[<=>~[:space:]])copier([<=>~[:space:]]|$)' requirements.txt` | PASS |
| Gate ASVS L1 combinado | `test ! -x .venv-template/bin/copier && ! command -v copier` | PASS |
| Procedência do pacote | PyPI 9.17.1 + documentação oficial cruzadas | PASS |

Nenhum pacote foi instalado, nenhum ambiente virtual foi criado e nenhum comando `copier` foi executado durante este plano.

## Decisions Made

- A aprovação é específica para o nome, versão, registro e projeto oficial: `copier==9.17.1` do projeto Copier, e não uma autorização genérica de ferramenta de template.
- O Plano 04-02 deve instalar exclusivamente a versão pinada em `.venv-template/`, preservando a separação entre ferramenta de desenvolvimento e dependências Django.
- `TPL-01` e `TPL-03` permanecem pendentes nesta etapa: este plano registra somente a autorização necessária para seus planos de implementação.

## Deviations from Plan

None - plan executed exactly as written, com o sinal de autorização explicitamente fornecido na invocação do executor conforme instrução do usuário.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- O Plano 04-02 pode criar `.venv-template/` e instalar somente `copier==9.17.1`.
- Antes dessa etapa, os únicos binários permitidos continuam ausentes; qualquer divergência de nome, versão ou origem exige novo checkpoint bloqueante.

## Self-Check: PASSED

- Arquivo criado: `.planning/phases/04-templatiza-o-copier/04-01-SUMMARY.md`.
- Commit de Task 1 encontrado no histórico: `0d5ee5e`.
- O commit não contém exclusões de arquivos rastreados.

---
*Phase: 04-templatiza-o-copier*
*Completed: 2026-08-18*
