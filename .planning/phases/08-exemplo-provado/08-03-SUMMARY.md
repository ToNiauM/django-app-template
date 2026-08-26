---
phase: 08-exemplo-provado
plan: 03
subsystem: testing
tags: [prv-03, copier, unittest, teste-negativo, vazamento, sha256]
requires:
  - "08-01: fixture apps/diarias commitado (camada de dados e views)"
  - "08-02: fixture apps/diarias commitado (camada visual e testes)"
provides:
  - "Teste negativo de vazamento de domínio (PRV-03): apps/diarias nunca chega ao template renderizado nem à cópia gerada, nas duas variantes de incluir_app_exemplo"
  - "Prova de que git ls-files não lista o domínio fora de .template-tests/fixtures/"
affects:
  - "09 (escrita do guia): as asserções são estruturais e sobrevivem à citação legítima de 'diarias' em docs/guia/"
tech-stack:
  added: []
  patterns:
    - "Render leve Copier em tempdir com --vcs-ref=HEAD (padrão test_04_04/test_07_nav)"
    - "Interseção de sha256 de conteúdo puro (sem caminho) entre fixture e cópia"
key-files:
  created:
    - .template-tests/test_08_guia_vazamento.py
  modified: []
key-decisions:
  - "Hash de conteúdo puro (sem caminho relativo) na interseção fixture×cópia — impressao_subarvore() embute o caminho e nunca colidiria entre árvores distintas"
  - "Arquivos de 0 bytes do fixture (__init__.py de pacote) excluídos do conjunto de hashes — colidem com qualquer __init__.py vazio legítimo da cópia e dariam vermelho falso permanente, sem carregar nenhum byte de domínio"
  - "Guarda simétrica no teste de git ls-files: o fixture PRECISA estar rastreado (>=10 arquivos) — se sumir do git, o render com --vcs-ref=HEAD passaria em vácuo"
metrics:
  duration: 8min
  completed: 2026-08-26
---

# Phase 08 Plan 03: Teste negativo de vazamento do guia Summary

**Teste negativo estrutural (PRV-03) verde nas duas variantes: cópia recém-nascida sem apps/diarias, zero byte do fixture na cópia, e git ls-files limpo fora do fixture — por render leve Copier em tempdir, sem Docker.**

## O que foi construído

`.template-tests/test_08_guia_vazamento.py` (221 linhas, unittest stdlib, padrão dos módulos vizinhos) com três grupos de prova:

1. **Cópia recém-nascida sem o domínio (2 variantes).** `render()` copiado do padrão de `test_04_04_optional_exemplo.py` com `--vcs-ref=HEAD` obrigatório (a tag v0.2.0 publicada seria renderizada sem a flag). Com `incluir_app_exemplo=True`: `apps/diarias` ausente E `apps/` contém EXATAMENTE `["__init__.py", "exemplo"]`. Com `False`: EXATAMENTE `["__init__.py"]`.
2. **Nenhum byte do fixture na cópia.** `hashes_de_conteudo()` calcula sha256 só dos bytes (sem caminho — deliberadamente diferente de `impressao_subarvore()`), ignora `__pycache__`/`.pyc`, e a interseção fixture×cópia é assertada vazia. Guarda anti falso verde: o conjunto do fixture precisa ter >= 10 hashes não-vazios.
3. **Template limpo.** `git ls-files` (subprocess, cwd=ROOT) não lista nenhum caminho `apps/diarias*` nem `*/diarias/*` fora de `.template-tests/fixtures/`, mais guarda simétrica de que o fixture está rastreado.

Proibições respeitadas (Pitfall 8): zero grep textual de "diarias" em conteúdo da cópia; zero import/invocação do harness do banco de ensaio — o módulo usa renders leves próprios em `TemporaryDirectory()`.

## Verificação

- `python3 -m unittest discover -s .template-tests -p 'test_08_guia_vazamento.py' -v` → OK, 3 testes em ~17s
- Discover com padrão amplo `test_08_guia*.py` coleta só os 3 testes do módulo novo — nada de `fixtures/`
- Coleta pelo `test_command` padrão (`test_*.py`): 42 testes no total, os 3 novos presentes, zero vindos de `fixtures/` (confirmado por ausência de `__init__.py` nos níveis `fixtures/`, `guia/` e `apps/` do fixture)
- Nenhuma asserção foi enfraquecida: lista exata de `apps/` e interseção de hashes permanecem no código

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug latente] Arquivos vazios excluídos do conjunto de hashes do fixture**
- **Found during:** Task 1
- **Issue:** o fixture tem 5 `__init__.py` de 0 bytes; o sha256 do conteúdo vazio colide com qualquer `__init__.py` vazio legítimo da cópia (`apps/__init__.py`, `migrations/__init__.py`…) — a interseção literal do plano daria vermelho falso permanente sem detectar vazamento algum
- **Fix:** parâmetro `ignorar_vazios=True` aplicado só ao lado do fixture, com o racional documentado no docstring (arquivo vazio não carrega byte de domínio); guarda de >= 10 hashes preservada
- **Files modified:** .template-tests/test_08_guia_vazamento.py
- **Commit:** 98c51b4

**2. [Rule 1 - Conflito de critério] Docstring reescrito para não conter a string `ensaio_django`**
- **Found during:** Task 1 (verificação de aceitação)
- **Issue:** o plano pede docstring explicando por que o banco compartilhado fica de fora E exige que `grep -F 'ensaio_django'` não encontre nada — citar o script pelo nome violava o grep
- **Fix:** a prosa descreve o harness sem a string literal ("o harness shell de ensaio Django"); o critério literal passa e a explicação permanece
- **Files modified:** .template-tests/test_08_guia_vazamento.py
- **Commit:** 98c51b4

## Observações

- Task 2 não produziu diff: a suíte nasceu verde na primeira execução, e a prova de descoberta segura não exigiu remoção de `__init__.py` (o fixture já estava correto desde a onda 1). Por isso o plano tem um único commit de código.
- Pattern 4 preservado: este módulo nunca toca o banco de ensaio compartilhado — o fixture instalado lá (plano 08-04) é estado legítimo.

## Known Stubs

Nenhum — o artefato é uma suíte de teste completa, sem placeholders.

## Threat Flags

Nenhuma superfície nova fora do threat model do plano: T-08-P3-01/02/03 mitigados pela própria suíte (asserções estruturais, guarda de fixture não-vazio, prova nas duas variantes).

## Self-Check: PASSED

- .template-tests/test_08_guia_vazamento.py existe
- Commit 98c51b4 existe no historico
