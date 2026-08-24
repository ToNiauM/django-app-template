---
phase: quick-260818-n9k
plan: 01
status: complete
subsystem: templates
tags: [django, templates, comment-leak, security, regression-tests]
requires: []
provides:
  - "Templates sem vazamento de comentários {# #} multilinha no HTML renderizado"
  - "Teste estático no gate nativo que trava a reintrodução de {# #} multilinha"
  - "Teste renderizado (projeto gerado) cobrindo /login/, / e o fragmento htmx"
affects: [core/templates, .template-tests, core/tests]
tech-stack:
  added: []
  patterns:
    - "Comentários multilinha em templates Django sempre via {% comment %}...{% endcomment %}"
key-files:
  created:
    - .template-tests/test_quick_comentarios_template.py
    - core/tests/test_templates.py
  modified:
    - core/templates/base.html
    - core/templates/core/_login_form.html
    - core/templates/core/shell.html
key-decisions:
  - "RED do TDD demonstrado via fixture em scratch (nunca comitado) em vez de git stash — stash é proibido em worktrees compartilhados"
  - "Teste estático espelha o tag_re do Django (regex {#.*?#} sem re.DOTALL): aceita comentários de uma linha, falha só nos multilinha"
metrics:
  duration: 6min
  completed: 2026-08-18
---

# Quick Task 260818-n9k: Vazamento de Comentários de Template Summary

Quatro comentários `{# #}` multilinha convertidos para `{% comment %}` (base.html, _login_form.html, shell.html) — o lexer do Django não casa `{#...#}` entre linhas e os emitia como texto literal no HTML de login e do shell; regressão travada por teste estático no gate nativo e teste renderizado no projeto gerado.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Converter os quatro comentários multilinha `{# #}` para `{% comment %}` | ae81a16 | core/templates/base.html, core/templates/core/_login_form.html, core/templates/core/shell.html |
| 2 | Testes de regressão contra vazamento de comentários (TDD) | ba86084 | .template-tests/test_quick_comentarios_template.py, core/tests/test_templates.py |

## What Was Done

**Causa raiz (confirmada):** `tag_re` em `django.template.base` casa `{#...#}` sem `re.DOTALL` — comentários inline só valem em UMA linha. Quatro blocos multilinha vazavam como texto literal:

1. `core/templates/base.html` (comentário hx-history, antes do `<body>` → topo da página)
2. `core/templates/core/_login_form.html` (fallback no-JS → tela de login e swap htmx)
3. `core/templates/core/shell.html` (hx-on::before-request do logout)
4. `core/templates/core/shell.html` (fallback no-JS do logout)

**Correção:** os quatro blocos agora usam `{% comment %}...{% endcomment %}` (mesmo padrão do comentário de centering já existente em base.html). Texto explicativo preservado palavra por palavra — referências a hx-history, D-16/D-17, CR-01 e T-02-11 seguem nos templates. Comentários de uma linha não foram tocados; nenhum arquivo `.jinja` alterado.

**Testes:**
- `.template-tests/test_quick_comentarios_template.py` — estático, sem dependência de Django: remove de cada `*.html` os `{#...#}` de uma linha (mesma semântica do lexer) e falha se restar `{#`/`#}`. Inclui guarda de sanidade contra varredura em vácuo. Roda no gate nativo (`python3 -m unittest discover -s .template-tests -p 'test_*.py'`).
- `core/tests/test_templates.py` — `django.test.TestCase` na convenção de `test_login_flow.py` (docstring pt-BR, `@override_settings`, `Usuario.objects.create_user`): `/login/` anônimo, `/` autenticado (force_login) e o fragmento htmx do POST inválido — todos com `assertNotIn("{#")`/`assertNotIn("#}")`. Executa no projeto gerado via `manage.py test core` (harness test_05_nascimento.sh).

## TDD Cycle

- **RED:** demonstrado com fixture de scratch contendo `{# #}` multilinha (nunca comitada) — a varredura detecta o vazamento, provando que o assert `problemas == {}` falharia no estado pré-correção. Comentário de uma linha comprovadamente aceito.
- **GREEN:** teste estático passa contra os templates corrigidos.
- Nota: `git stash` (sugerido no plano para o RED) não foi usado — proibido em worktrees; o plano previa a alternativa da fixture, que foi a adotada.

## Verification Results

1. `grep -rn '{#' core/templates apps --include='*.html' | grep -v '#}'` → sem saída.
2. `{% comment %}` count: base.html=2, shell.html=3, _login_form.html=1 (todos ≥ mínimo).
3. Gate nativo completo: **15 tests OK** (inclui os 2 novos).
4. Termos "hx-history", "CR-01", "T-02-11" presentes nos templates convertidos.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `varrer_templates` quebrava fora da raiz do repo**
- **Found during:** Task 2 (driver RED em scratch)
- **Issue:** `Path.relative_to(ROOT)` levantava `ValueError` ao varrer diretório de fixture fora do repo.
- **Fix:** fallback para caminho absoluto quando o arquivo não está sob ROOT.
- **Files modified:** .template-tests/test_quick_comentarios_template.py
- **Commit:** ba86084 (incluído no commit do teste)

**2. [Rule 3 - Blocking] Gate nativo sem `.venv-template` no worktree**
- **Found during:** Task 2 (verificação do gate completo)
- **Issue:** `.venv-template/` é gitignored e não existe no worktree; 10 testes Copier pré-existentes erravam com `FileNotFoundError`. Symlink para o venv do repo principal disparou `ForbiddenPathError` do Copier (symlink apontando para fora da raiz do template).
- **Fix:** cópia por hardlink (`cp -al /opt/sistema_base/.venv-template .venv-template`) — diretório real, gitignored e no `_exclude` do copier.yml; gate ficou 100% verde (15 OK). Artefato de ambiente, não comitado.
- **Files modified:** nenhum versionado

## Known Stubs

None.

## Threat Flags

None — a mudança REDUZ superfície de divulgação (T-qk-01 mitigado: racional interno de segurança deixa de aparecer no HTML servido).

## Self-Check: PASSED
