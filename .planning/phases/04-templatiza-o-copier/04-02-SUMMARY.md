---
phase: 04-templatiza-o-copier
plan: 02
subsystem: template-copier
tags: [copier, jinja, template, configuration, documentation, security]

requires:
  - phase: 04-templatiza-o-copier
    provides: "Autorização auditável para instalar exclusivamente copier==9.17.1 em .venv-template/."
provides:
  - "Tracer Copier in-place com oito respostas validadas, StrictUndefined e respostas persistidas."
  - "Defaults de identidade e conexão renderizados em .env.example sem segredos nas respostas."
  - "READMEs distintos para o template-fonte e para o sistema derivado."
affects: [04-03, 04-04, 04-05, 04-06, 04-07, template-copier]

actuals:
  tokens: 3793 # 15.171 caracteres no diff realizado, dividido por 4 e arredondado para cima
  tasks: 2
  commits: 3

tech-stack:
  added: ["copier==9.17.1 isolado em .venv-template/"]
  patterns:
    - "Template in-place: somente arquivos que interpolam respostas recebem o sufixo .jinja."
    - "Identidade e conexão derivadas para .env.example; segredos nunca entram em perguntas ou respostas Copier."
    - "Updates conscientes: respostas versionadas, Git limpo, tags semver e resolução de conflitos inline."

key-files:
  created:
    - copier.yml
    - .copier-answers.yml.jinja
    - .env.example.jinja
    - README.md
    - README.md.jinja
  modified:
    - .gitignore
  removed:
    - .env.example

key-decisions:
  - "Copier 9.17.1 fica exclusivamente em .venv-template/, fora de requirements.txt e do Python global."
  - "As oito respostas usam validators antes da renderização; identidade/conexão são persistidas, segredos permanecem locais no .env."
  - "O README do sistema é renderizado por README.md.jinja; a configuração evita excluir seu caminho de destino junto com o README estático do template."

patterns-established:
  - "_copier_answers é renderizado pelo próprio Copier; não há escritor YAML, _tasks, migrations ou extensões Jinja."
  - "A fronteira template → derivado é validada por cópia real em diretório temporário, incluindo ausência de documentos internos e segredos."

requirements-completed: [TPL-01, TPL-02]

coverage:
  - id: D1
    description: "Copier gera um projeto Django completo com respostas persistidas e arquivos internos excluídos."
    requirement: TPL-01
    verification:
      - kind: integration
        ref: ".venv-template/bin/copier copy --defaults --data ...; checagem de manage.py, config/, core/, Dockerfile, compose.yml e .copier-answers.yml"
        status: pass
    human_judgment: false
  - id: D2
    description: "Perguntas validam identidade, slug, hostname, porta, banco, sigla e cor antes da renderização."
    requirement: TPL-02
    verification:
      - kind: integration
        ref: "Cópias inválidas para nome/sigla vazios, slug com separador, porta 1023 e cor inválida retornaram erro sem destino utilizável."
        status: pass
    human_judgment: false
  - id: D3
    description: "Defaults de ambiente usam as respostas sem persistir SECRET_KEY, senha PostgreSQL ou credenciais R2."
    requirement: TPL-02
    verification:
      - kind: integration
        ref: "Inspeção ASVS L1 da cópia Aurora: respostas sem nomes de segredo e .env.example com sentinelas não utilizáveis."
        status: pass
    human_judgment: false
  - id: D4
    description: "Template e sistema derivado recebem READMEs distintos, com atualização Git/Copier explícita e sem automação pós-cópia."
    requirement: TPL-01
    verification:
      - kind: integration
        ref: "Cópia Aurora contém README.md renderizado com a identidade e não contém o título do README interno; copier.yml não declara _tasks, _migrations ou extensões."
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-08-18
status: complete
---

# Phase 04 Plan 02: Tracer Copier e documentação dual Summary

**Copier 9.17.1 isolado gera sistemas Django parametrizados, com respostas seguras, `.env.example` renderizado e documentação operacional separada do template.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-08-18T16:14:21Z
- **Completed:** 2026-08-18T16:21:07Z
- **Tasks:** 2/2
- **Files modified:** 7

## Accomplishments

- Criado o contrato in-place do Copier com oito perguntas, defaults derivados, `jinja2.StrictUndefined`, validators de formato e exclusões de artefatos internos.
- Migrado `.env.example` para `.env.example.jinja`, preenchendo identidade, banco, hostname e porta sem transportar segredos a `.copier-answers.yml`.
- Criados READMEs distintos: o do template documenta nascimento, Git, tags e update; o renderizado documenta operação diária, apps e ícones opcionais.
- Comprovada uma cópia real de `Sistema Aurora`, incluindo geração dos arquivos Django, persistência de respostas, ausência de documentos internos e proteção dos sentinelas de segredo.

## Task Commits

1. **Task 1: Provar copier copy da pergunta ao projeto gerado** — `3d2ae53` (`feat`)
2. **Task 2: Separar documentação do template e do sistema gerado** — `c6a0dd1` (`docs`)

## Files Created/Modified

- `copier.yml` — perguntas, validators, renderização estrita e exclusões do template.
- `.copier-answers.yml.jinja` — persistência oficial de respostas e metadados de update.
- `.env.example.jinja` — defaults renderizados sem segredos.
- `.gitignore` — isolamento de `.venv-template/`.
- `README.md` — ritual do template: instalação, nascimento, segredos, Git, releases e updates.
- `README.md.jinja` — manual operacional renderizado para cada sistema derivado.
- `.env.example` — removido após a migração para o arquivo renderizado.

## Verification Evidence

- `.venv-template/bin/copier --version` retornou `copier 9.17.1`; `requirements.txt` permanece sem Copier.
- Cópia real com valores Aurora criou `manage.py`, `config/`, `core/`, `Dockerfile`, `compose.yml`, `.copier-answers.yml`, `.env.example` e README renderizado.
- Nome e sigla vazios, slug com separador, porta `1023` e cor inválida foram rejeitados antes de criar destino utilizável.
- A cópia não continha `.planning`, `IDEIA.md`, `REVIEW.md`, `CLAUDE.md`, `.venv-template` ou `copier.yml`.
- A matriz ASVS L1 passou: respostas sem nomes de segredo, sentinelas não utilizáveis no `.env.example`, validators auditáveis e nenhuma automação/extensão Jinja.

## Decisions Made

- A instalação usa `python3 -m venv` nesta máquina porque o executável `python` não existe; o ambiente e a versão permanecem exatamente os aprovados.
- O arquivo de respostas é exclusivamente `{{ _copier_answers | to_yaml }}` para manter `_src_path` e `_commit` gerenciados pelo Copier.
- O README renderizado contém a identidade respondida, enquanto a documentação interna não atravessa para a cópia.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Usar `python3` para criar o ambiente isolado**
- **Found during:** Task 1
- **Issue:** O host não possui o executável `python`; `python -m venv` falhava antes de criar o ambiente.
- **Fix:** Executado `python3 -m venv .venv-template`, seguido da instalação autorizada e pinada de `copier==9.17.1`.
- **Files modified:** `.venv-template/` (não versionado e ignorado)
- **Verification:** `.venv-template/bin/copier --version` retornou `copier 9.17.1`.
- **Committed in:** `3d2ae53` (configuração correspondente em `.gitignore`)

**2. [Rule 1 - Bug] Preservar o README renderizado diante de `_exclude` por destino**
- **Found during:** Task 2
- **Issue:** Em Copier 9.17.1, `_exclude: README.md` é comparado ao caminho de destino renderizado e eliminava também `README.md.jinja`.
- **Fix:** Removida a exclusão literal e documentada a substituição do README estático pelo `README.md.jinja`; a cópia real confirma que somente o README renderizado atravessa a fronteira.
- **Files modified:** `copier.yml`, `README.md`, `README.md.jinja`
- **Verification:** Cópia Aurora contém `README.md` com a identidade respondida e não contém o título do README do template.
- **Committed in:** `c6a0dd1`

---

**Total deviations:** 2 auto-fixed (1 bloqueio de ambiente, 1 bug de semântica do Copier).
**Impact on plan:** Ambas preservam o isolamento e a fronteira de geração exigidos; não houve expansão de escopo.

## Known Stubs

None. A palavra “placeholder” no README renderizado descreve os ícones PWA neutros já versionados, não uma interface sem fonte de dados nem um bloqueio do objetivo deste plano.

## Issues Encountered

None além dos desvios auto-corrigidos acima.

## User Setup Required

None - nenhum serviço externo foi configurado. O operador futuro preenche segredos somente no `.env` do sistema derivado.

## Next Phase Readiness

- Os planos seguintes podem partir de um `copier copy` real com respostas versionáveis e fronteira de exclusões comprovada.
- A documentação já contém o ritual A→B e o comando contratual `.template-tests/test_copier_update.sh` para a prova de update planejada no 04-07.

## Self-Check: PASSED

- Arquivos criados e migrados confirmados no repositório: `copier.yml`, `.copier-answers.yml.jinja`, `.env.example.jinja`, `README.md` e `README.md.jinja`.
- Commits de Task 1 (`3d2ae53`) e Task 2 (`c6a0dd1`) confirmados no histórico.
- A única exclusão rastreada foi `.env.example`, intencionalmente substituído por `.env.example.jinja`.

---
*Phase: 04-templatiza-o-copier*
*Completed: 2026-08-18*
