---
phase: 07-herdar-o-design-system-do-pca
plan: 03
subsystem: navegacao
tags: [django-templatetags, copier, skip-if-exists, inclusion-tag]

# Dependency graph
requires: ["07-01", "07-02"]
provides:
  - "core/templatetags/navegacao.py — inclusion tag {% item_nav %} com dicionário fechado de ícones ICONES"
  - "core/templates/core/_nav.html — arquivo do núcleo, estático, sem .jinja, byte a byte idêntico nas duas variantes"
  - "core/templates/core/_nav_dominio.html(.jinja) — ponto de extensão do derivado, protegido por _skip_if_exists"
  - ".template-tests/test_07_nav_extensao.py — prova executável dos critérios 5, 6 e 7 da Fase 7"
affects: ["07-04", "07-05", "07-06", "07-07", "07-08"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Item de menu opcional: reverse() em try/except NoReverseMatch na inclusion tag, não {% if %} de Copier no arquivo upstream"
    - "Arquivo do derivado protegido por _skip_if_exists do Copier, não script pós-update nem .gitattributes merge=ours"
    - "Impressão sha256 de caminho-relativo+conteúdo de uma subárvore inteira como prova de 'nenhum outro arquivo mudou'"

key-files:
  created:
    - core/templatetags/navegacao.py
    - core/templates/core/_item_nav.html
    - core/templates/core/_nav.html
    - core/templates/core/_nav_dominio.html.jinja
    - core/tests/test_navegacao.py
    - .template-tests/test_07_nav_extensao.py
  modified:
    - copier.yml
    - "apps/{% if incluir_app_exemplo %}exemplo{% endif %}/README.md.jinja"
    - .template-tests/test_copier_copy.sh
    - .template-tests/test_copier_update.sh
    - .template-tests/test_04_04_optional_exemplo.py
  deleted:
    - core/templates/core/_nav.html.jinja

key-decisions:
  - "TDD na Task 1: 6 testes de core/tests/test_navegacao.py escritos e confirmados falhando (TemplateSyntaxError: 'navegacao' is not a registered tag library) antes de navegacao.py/_item_nav.html existirem — RED→GREEN literal"
  - "test_copier_update.sh ganhou --no-tags no git clone (Rule 3, bug pré-existente e bloqueante): o repositório real já tem a tag v0.1.0 da release; sem --no-tags o clone efêmero herda essa tag e 'git tag v0.1.0' falha com 'tag already exists' antes de qualquer mudança desta plan"
  - "exigir_sem_exemplo() passa a provar sobrevivência do arquivo do derivado (_nav_dominio.html existe após update), não mais ausência de 'exemplo:' nele — com _skip_if_exists o arquivo é do derivado e pode legitimamente conter 'exemplo:' sem que isso seja ressurreição do app"
  - "Prova negativa do critério 6 e prova negativa do _skip_if_exists exigiram descobrir que git clone (usado pelo próprio test_copier_update.sh) só enxerga estado COMMITADO — remover _skip_if_exists do working tree sem commitar não afeta a suíte; a prova negativa real exigiu um commit temporário revertido em seguida com git reset --soft + git checkout -- (nunca git reset --hard)"

requirements-completed: [NAV-01, NAV-02, NAV-03, REL-01]

# Metrics
duration: 24min
completed: 2026-08-23
---

# Phase 07 Plan 03: Ponto de extensão da navegação Summary

**`_nav.html` vira arquivo do núcleo estático e byte a byte idêntico nas duas variantes, `_nav_dominio.html` nasce como stub do derivado protegido por `_skip_if_exists`, cada item de menu vira uma linha via a nova inclusion tag `{% item_nav %}` (rota opcional via `try/except NoReverseMatch`, ícone de dicionário fechado, rótulo sempre escapado), e os itens do app exemplo saem do arquivo upstream — com prova executável dos critérios 5, 6 e 7 em `test_07_nav_extensao.py`.**

## Performance

- **Duration:** 24 min
- **Started:** 2026-08-23T18:13:11Z
- **Completed:** 2026-08-23T18:37:02Z
- **Tasks:** 3
- **Files modified:** 12 (6 criados, 5 modificados, 1 apagado)

## Accomplishments

- `core/templatetags/navegacao.py`: `item_nav(context, rota, rotulo, icone="", prefixo="")` — `reverse()` em `try/except NoReverseMatch` devolvendo `{"url": ""}` (D-89, T-07-08); `ICONES` é dicionário fechado de `mark_safe` com `casa`/`grafico`/`lista` (D-90, T-07-06); docstring documenta explicitamente que a tag não é mecanismo de autorização (T-07-07)
- `core/templates/core/_item_nav.html`: as 12 linhas do item, tratamento visual do padrão (`bg-brand-tint text-brand-ink`, barra de 2px, ícone opcional) por construção; `{{ rotulo }}` sem `|safe` (T-07-05)
- `core/templates/core/_nav.html`: arquivo do núcleo, sem `.jinja`, sem `{% raw %}`, sem `exemplo:`; dois filhos — `{% item_nav "core:shell" ... %}` + `{% include "core/_nav_dominio.html" %}`
- `core/templates/core/_nav_dominio.html.jinja`: stub do derivado, semeado com os dois itens do exemplo quando `incluir_app_exemplo=true`, vazio (só cabeçalho) quando `false`
- `copier.yml`: `_skip_if_exists` protegendo `core/templates/core/_nav_dominio.html` e `core/static/src/dominio.css`
- `apps/exemplo/README.md.jinja`: ponto de integração 3 passa a citar `_nav_dominio.html` como arquivo do sistema
- `test_copier_copy.sh`, `test_copier_update.sh`, `test_04_04_optional_exemplo.py`: asserções de `exemplo:` migradas de `_nav.html` para `_nav_dominio.html`; nova asserção de identidade byte a byte de `_nav.html`; ensaio A→B→C ganhou o passo real do critério 7 (derivado escreve "Painel" antes do update, sobrevive a dois updates seguidos, sem marcador de conflito)
- `.template-tests/test_07_nav_extensao.py` (novo): 3 testes — identidade byte a byte de `_nav.html` ao adicionar itens no domínio (critério 5), impressão sha256 de toda a subárvore `core/` provando que remover os itens do exemplo não toca nenhum outro arquivo (critério 6, prova literal), e `_skip_if_exists` protegendo os dois arquivos do derivado

## Task Commits

Each task was committed atomically (RED→GREEN na Task 1, conforme `tdd="true"`):

1. **Task 1 RED: teste falho para item_nav** - `b31ccf6` (test)
2. **Task 1 GREEN: inclusion tag item_nav e _item_nav.html** - `e9859e3` (feat)
3. **Task 2: _nav.html estático, _nav_dominio.html protegido, exemplo migrado** - `28ceba9` (feat)
4. **Task 3: contratos de update — nav do núcleo estática, exemplo migrado** - `1cfdeff` (test)

**Plan metadata:** commit pendente (docs: complete plan)

## Files Created/Modified

- `core/templatetags/navegacao.py` (novo) - `item_nav` + `ICONES` fechado
- `core/templates/core/_item_nav.html` (novo) - as 12 linhas do item
- `core/templates/core/_nav.html` (novo) - núcleo, estático
- `core/templates/core/_nav.html.jinja` (apagado) - substituído pelo par acima
- `core/templates/core/_nav_dominio.html.jinja` (novo) - stub protegido do derivado
- `core/tests/test_navegacao.py` (novo) - 6 testes de comportamento da tag
- `copier.yml` - `_skip_if_exists` para `_nav_dominio.html` e `dominio.css`
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/README.md.jinja` - ponto 3 cita `_nav_dominio.html`
- `.template-tests/test_copier_copy.sh` - asserções de `exemplo:` migradas + gate de identidade
- `.template-tests/test_copier_update.sh` - passo do derivado escrevendo "Painel" + `--no-tags` no clone
- `.template-tests/test_04_04_optional_exemplo.py` - prova byte a byte + asserções em `_nav_dominio.html`
- `.template-tests/test_07_nav_extensao.py` (novo) - 3 testes de contrato dos critérios 5/6/7

## Decisions Made

Ver `key-decisions` no frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Bloqueio] `git clone` em `test_copier_update.sh` herdava a tag `v0.1.0` real do repositório**
- **Found during:** Task 3, ao rodar `bash .template-tests/test_copier_update.sh` pela primeira vez nesta sessão
- **Issue:** O script clona `${ROOT}` (este repositório) com `git clone -q --no-hardlinks`, que por padrão copia TODAS as tags do repositório de origem. Como este repositório já tem a tag real `v0.1.0` (release anterior — ver STATE.md, "repositório está com 37 commits desde a tag v0.1.0"), o clone efêmero também a herdava, e a linha seguinte do script (`git -C "${TEMPLATE}" tag v0.1.0`, que cria a PRÓPRIA tag do ensaio) falhava com `fatal: tag 'v0.1.0' already exists` antes mesmo de qualquer mudança desta plan ser exercitada. Bug pré-existente, não causado por este plano, mas bloqueante para verificar a Task 3.
- **Fix:** Acrescentado `--no-tags` ao `git clone`, isolando o ensaio de qualquer tag real do repositório de origem.
- **Files modified:** `.template-tests/test_copier_update.sh`
- **Verification:** `bash .template-tests/test_copier_update.sh` passou a rodar do início ao fim (antes falhava na linha 2 de execução, `EXIT:128`); confirmado com `EXIT:0` após a correção.
- **Committed in:** `1cfdeff` (Task 3)

---

**Total deviations:** 1 auto-fixed (1 bloqueio pré-existente)
**Impact on plan:** Sem o `--no-tags`, nenhuma verificação de `test_copier_update.sh` desta plan (nem das plans seguintes que dependem dele) seria executável — bloqueio genuíno, não relacionado ao escopo funcional desta plan.

## Issues Encountered

Nenhum bloqueio não resolvido. A investigação da prova negativa do `_skip_if_exists` (ver abaixo) revelou uma armadilha metodológica não documentada no `07-RESEARCH.md`: `git clone` só enxerga estado **commitado** do repositório de origem — editar `copier.yml` no working tree sem commitar não tem nenhum efeito sobre o `TEMPLATE` clonado por `test_copier_update.sh` (diferente de `copier copy`/`copier update` chamados diretamente sobre um path local, que incluem mudanças sujas automaticamente, conforme o aviso `DirtyLocalWarning` já observado nas plans 07-01/07-02). A prova negativa real exigiu um commit temporário (revertido com `git reset --soft` + `git checkout --`, nunca `git reset --hard`).

## Provas Negativas Registradas

1. **Critério 6 — remover também uma linha de `_nav.html` (Task 3):** com a suíte `test_07_nav_extensao.py` temporariamente instrumentada para apagar, além dos dois itens do exemplo em `_nav_dominio.html`, a última linha de `core/templates/core/_nav.html`, `test_remover_itens_do_exemplo_nao_toca_nenhum_arquivo_do_nucleo` **falhou** com `AssertionError: Lists differ: ['templates/core/_nav.html', 'templates/core/_nav_dominio.html'] != ['templates/core/_nav_dominio.html']` — a impressão sha256 da subárvore `core/` capturou exatamente o caminho divergente extra. A instrumentação foi revertida em seguida (arquivo restaurado a partir de backup); a suíte voltou a passar 3/3.

2. **`_skip_if_exists` ausente (Task 3):** removido temporariamente o bloco `_skip_if_exists` de `copier.yml`. Primeira tentativa de reprodução (editar o arquivo sem commitar) **não** produziu falha — descoberta de que `git clone` (usado pelo script) ignora mudanças não commitadas do repositório de origem. Reprodução correta: commit temporário de `copier.yml` sem `_skip_if_exists`, execução de `bash .template-tests/test_copier_update.sh`, que **falhou** com:
   ```
   FALHOU: marcadores inline encontrados após update:
   .../destino/core/templates/core/_nav_dominio.html:2:<<<<<<< before updating
   .../destino/core/templates/core/_nav_dominio.html:4:=======
   .../destino/core/templates/core/_nav_dominio.html:6:>>>>>>> after updating
   ```
   O commit temporário foi desfeito com `git reset --soft HEAD~1` seguido de `git checkout -- copier.yml` (nunca `git reset --hard`, nunca `git stash`); `git diff copier.yml` confirmado vazio depois. `bash .template-tests/test_copier_update.sh` voltou a passar (`EXIT:0`) na sequência.

## User Setup Required

None - nenhuma configuração de serviço externo necessária.

## Next Phase Readiness

- `{% item_nav %}`, `_item_nav.html`, `_nav.html` estático e `_nav_dominio.html` protegido estão prontos para qualquer plano seguinte que precise adicionar itens de navegação — inclusive um eventual DividaAtiva, que segundo o `07-RESEARCH.md` (Pitfall 16) vai conflitar em três arquivos no próximo `copier update`, incluindo `_nav.html`; a resolução recomendada (`git checkout --theirs` + recriar os itens em `_nav_dominio.html`) já está documentada na pesquisa, mas o roteiro de 3 parágrafos no README (mencionado no Pitfall 16) **não** faz parte do escopo desta plan — confirmar se um plano seguinte da fase (07-08, fechamento da fase) cobre isso.
- Toda a `<verification>` do plano está verde: `test_copier_copy.sh` (matriz completa), `test_copier_update.sh` (ensaio A→B→C com o passo do critério 7), `python3 -m unittest discover -s .template-tests -p 'test_*.py'` (32/32), `ensaio_django.sh testar core apps.exemplo` (83/83, dos quais 6 novos em `test_navegacao.py`).
- `copier.yml` agora protege dois arquivos do derivado (`_nav_dominio.html` desta plan, `dominio.css` da 07-02) — qualquer plano futuro que precise adicionar um terceiro arquivo protegido segue o mesmo padrão de comentário obrigatório.

---
*Phase: 07-herdar-o-design-system-do-pca*
*Completed: 2026-08-23*

## Self-Check: PASSED

All created/modified files verified present on disk (core/templatetags/navegacao.py,
core/templates/core/_item_nav.html, core/templates/core/_nav.html,
core/templates/core/_nav_dominio.html.jinja, core/tests/test_navegacao.py,
.template-tests/test_07_nav_extensao.py, copier.yml, apps/exemplo README.md.jinja,
test_copier_copy.sh, test_copier_update.sh, test_04_04_optional_exemplo.py);
core/templates/core/_nav.html.jinja confirmado ausente; todos os quatro hashes de
commit (b31ccf6, e9859e3, 28ceba9, 1cfdeff) verificados presentes em `git log`.
