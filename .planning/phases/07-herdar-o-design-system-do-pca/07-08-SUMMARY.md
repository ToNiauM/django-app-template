---
phase: 07-herdar-o-design-system-do-pca
plan: 08
status: complete
subsystem: release-e-documentacao
tags: [readme, roadmap, requirements, release, v0.2.0, checkpoint]
dependency-graph:
  requires: ["07-01", "07-02", "07-03", "07-04", "07-05", "07-06", "07-07"]
  provides: ["roteiro-atualizacao-derivados-v0.1.0", "inventario-suites-medido", "tag-v0.2.0"]
  affects: ["README.md", ".planning/ROADMAP.md", ".planning/REQUIREMENTS.md"]
tech-stack:
  added: []
  patterns:
    - "Inventário de suítes sempre medido na hora (ls .template-tests/ | grep -c '^test_'), nunca decorado em documento"
key-files:
  created: []
  modified:
    - "README.md"
    - ".planning/ROADMAP.md"
    - ".planning/REQUIREMENTS.md"
decisions:
  - "Contagem de suítes medida no momento da task: 13 (10 herdadas + test_07_tokens.py + test_07_nav_extensao.py + test_07_cor_runtime.sh); nenhum inteiro citado em ROADMAP/REQUIREMENTS — ambos passam a dizer 'todas as suítes de .template-tests/'"
  - "Cópia retida órfã do checkpoint anterior (projeto nascimento2699983, de pé há 3h) foi derrubada em vez de reaproveitada: a senha efêmera dela morreu com a sessão que a gerou, e o contrato de 05-03-PLAN.md:151 proíbe recriar credencial por fora do tracer"
  - "Tag v0.2.0 criada anotada e NÃO publicada — git push é decisão do operador, conforme o <action> da Task 3"
  - "REQUIREMENTS.md linha 70 (QA-03) já estava marcada '- [x]' antes desta task, não '- [ ]' como o plano assumia; preservado o estado do checkbox e trocado apenas o miolo da frase ('as 11 suítes' → 'todas as suítes'), sem reindentar nem mexer no rótulo"
metrics:
  duration: "3 tasks — Task 1 em sessão anterior; Tasks 2 e 3 em 2026-08-23"
  completed: "2026-08-23"
---

# Phase 07 Plan 08: Fecho da fase — roteiro de atualização, inventário medido e tag v0.2.0 Summary

**Status: COMPLETO.** As três tasks rodaram. A Task 1 foi executada em sessão
anterior; a Task 2 (`checkpoint:human-verify`, gate="blocking") foi aprovada
pelo operador em 2026-08-23 e a Task 3 fechou com a regressão inteira verde e
a tag anotada `v0.2.0` criada.

## One-liner

README ganha o roteiro de 8 passos para derivados presos na v0.1.0, o
operador aprova a inspeção visual das 4 telas nos 2 temas, e a tag anotada
`v0.2.0` passa a entregar as Fases 6 e 7 juntas — 85 commits que nenhum
sistema derivado tinha como enxergar.

## Task 1 — Roteiro de atualização dos derivados, regressão documentada e inventário de suítes medido

Executada e commitada.

- **README.md** — nova subseção "Atualizando um sistema que nasceu na
  v0.1.0" em "Releases e atualização do núcleo", com a tabela dos três
  conflitos previsíveis (`_nav.html`, `tailwind.config.js`, `input.css`) e o
  roteiro de 8 passos citado em `<interfaces>` do plano. Seção "Regressão do
  template" atualizada: linha `ensaio_django.sh derrubar` no início e depois
  da suíte de cor, as três suítes novas da Fase 7 documentadas
  individualmente, nova subseção explicando a ferramenta
  `ensaio_django.sh` (subcomandos, banco que sobrevive entre invocações,
  `derrubar` como limpeza de host), e nota sobre `--vcs-ref=HEAD`. Seção
  "Criando a tag de release" com os exemplos trocados de `v0.1.0` para
  `v0.2.0` e frase explicando o que a release entrega (Fases 6 e 7 juntas).
- **`.planning/ROADMAP.md`** (critério 8) e **`.planning/REQUIREMENTS.md`**
  (QA-03) — "as 11 suítes de `.template-tests/`" trocado por "todas as
  suítes de `.template-tests/`" nos dois documentos. O número "11" já era
  falso antes desta fase (o HEAD tinha 10 suítes no momento da auditoria); a
  troca é limpeza de dívida, não enfraquecimento de critério — "todas as
  suítes" continua valendo para as 13 que existem hoje e para as que
  vierem depois.

**Inventário medido nesta task:** `ls .template-tests/ | grep -c '^test_'`
devolveu **13**: `test_04_03_identity.py`, `test_04_04_optional_exemplo.py`,
`test_04_05_backup.py`, `test_04_06_operations.py`,
`test_04_07_collectstatic.py`, `test_05_nascimento.sh`,
`test_06_persistencia.py`, `test_07_cor_runtime.sh`,
`test_07_nav_extensao.py`, `test_07_tokens.py`, `test_copier_copy.sh`,
`test_copier_update.sh`, `test_quick_comentarios_template.py`.
`ensaio_django.sh` foi excluído de propósito (não é suíte, nome não começa
com `test_`).

### Verificação

- `grep -c 'v0.2.0' README.md` → 6 (≥3 ✓)
- `grep -c '_nav_dominio.html' README.md` → 4 (≥2 ✓)
- `grep -c '_skip_if_exists' README.md` → 1 (≥1 ✓)
- `grep -c 'test_07_tokens.py' README.md` → 1, `test_07_nav_extensao.py` → 1,
  `test_07_cor_runtime.sh` → 3 (todos ≥1 ✓)
- `grep -c 'ensaio_django.sh' README.md` → 4 (≥2 ✓)
- `grep -rc '11 suítes' README.md .planning/ROADMAP.md .planning/REQUIREMENTS.md`
  → 0 em todos ✓
- `grep -c 'todas as suítes' .planning/ROADMAP.md` → 1, mesmo em
  `.planning/REQUIREMENTS.md` → 1 ✓
- `grep -cE '\b(11|14) suítes\b' README.md` → 0 ✓
- `grep -c -- '--vcs-ref=HEAD' README.md` → 2 (≥1 ✓)
- `grep -c 'checkout --theirs' README.md` → 4 (≥1 ✓)
- `bash .template-tests/test_copier_update.sh` → exit 0, e
  `grep -Fq 'A → B → C' README.md` continua verdadeiro (a seção não foi
  quebrada)

## Task 2 — Inspeção visual das 4 telas, nos dois temas (`checkpoint:human-verify`, gate="blocking")

**Aprovada pelo operador em 2026-08-23.** Nenhum arquivo foi alterado nesta
task, como o plano exige.

**Preparação executada antes do handoff:**

- **Cópia retida órfã derrubada.** O checkpoint de uma sessão anterior deixou
  o projeto Compose `nascimento2699983` de pé há 3 horas em
  `/tmp/tmp.H6F4XpYhzU/nascimento`. A senha efêmera daquele administrador
  vivia só na memória daquela sessão e estava perdida, o que tornava a cópia
  inútil para inspeção. Derrubada com `down --volumes --remove-orphans`,
  `dados/` removido via container root e diretório apagado.
- `bash .template-tests/ensaio_django.sh derrubar` → exit 0. `docker compose ls`
  sem nenhum projeto de ensaio ou nascimento (critério de aceite próprio da
  mitigação T-07-23b).
- Credencial efêmera nova gerada com
  `python3 -c 'import secrets; print(secrets.token_urlsafe(24))'`, tracing
  desabilitado, e o tracer invocado **uma única vez** com a senha passada pelo
  ambiente. Identidade fixa contratada pelo Plano 05-01
  (`nascimento@example.invalid`), sem `createsuperuser` manual.
- `NASCIMENTO_ADMIN_PASSWORD=… bash .template-tests/test_05_nascimento.sh --keep`
  → exit 0. **112 testes Django** verdes na cópia gerada; dados sobreviveram a
  `down --volumes` + `up -d`.
- **Checagem de vazamento (mitigação T-07-23c):** `grep -rIF "<senha>"` no
  repositório do template e na árvore gerada (exceto `dados/`) → **nada
  encontrado** nos dois. A senha não entrou em arquivo, SUMMARY, README,
  `.copier-answers.yml`, log nem comando versionado; foi apresentada ao
  operador só no retorno do checkpoint e descartada com `unset` na derrubada.
- Smoke da cópia retida: `/healthz` → 200, `/login/` → 200,
  `/exemplo/dashboard/` sem autenticação → 302.

**Roteiro conferido pelo operador:** as 4 telas (login, shell `/`, CRUD
`/exemplo/`, dashboard `/exemplo/dashboard/`) nos 2 temas, cobrindo ausência de
flash no recarregamento em escuro, legibilidade da régua encolhida (corpo 13px,
metadados 11px, títulos 20px), raio de 2px em todos os cantos, os três níveis de
elevação, anel de foco de 2px na navegação por Tab, opacidade do véu dos modais
de criação e exclusão do CRUD, repintura dos gráficos ao trocar o tema sem
recarregar, filete vertical de 2px no item de menu ativo e sobrevivência da
escolha de tema ao logout/login.

**Veredito:** "aprovado". Nenhum ponto reprovado, nenhuma correção necessária
antes da release.

**Encerramento:** cópia retida derrubada com
`docker compose -p nascimento3327374 down --volumes --remove-orphans`,
diretório `/tmp/tmp.8zIeqp6eUJ` apagado e credencial descartada com `unset`.

## Task 3 — Regressão completa verde e a tag v0.2.0

Executada na ordem da seção "Regressão do template" do README, com host limpo
antes e depois.

| # | Passo | Resultado |
|---|-------|-----------|
| 1 | `ensaio_django.sh derrubar` | exit 0; `docker compose ls` sem projeto de ensaio ✓ |
| 2 | `test_copier_copy.sh` | exit 0 — "matriz Copier copy, exclusões, neutralidade e operação passou" |
| 3 | `test_copier_update.sh` | exit 0 — "update Copier A→B→C entregou núcleo e preservou o opt-out" |
| 4 | `python3 -m unittest discover -s .template-tests -p 'test_*.py'` | exit 0 — **33 testes** em 136s |
| 5 | `test_07_cor_runtime.sh` | exit 0 — "COR_PRIMARIA comanda a família de marca inteira em runtime, sem rebuild de imagem" |
| 6 | `ensaio_django.sh derrubar` (a suíte de cor recria o banco) | exit 0; host sem resíduo ✓ |
| 7 | `test_05_nascimento.sh` (sem `--keep`) | exit 0 — **112 testes Django** na cópia gerada, dados sobreviveram a `down --volumes` |

**Contagem de testes Django do ensaio de nascimento: 112** — bem acima do piso
de 77 (54 em `core` + 23 em `apps.exemplo`) citado pelo plano. A diferença são
os testes que esta fase acrescentou (`test_navegacao`, `test_tema`,
`test_tema_escuro`, `test_dashboard`) somados aos das fases anteriores.

**Tag criada.** `git status --short` sem saída antes da criação. Tag anotada
`v0.2.0` com mensagem em pt-BR descrevendo o que a release entrega das Fases 6
e 7. **Não** foi publicada — `git push` é decisão do operador.

### Verificação da Task 3

- `git tag -l` → lista `v0.1.0` e `v0.2.0` ✓
- `git cat-file -t v0.2.0` → `tag` (anotada, não leve) ✓
- Asserção relativa da posição da tag:
  `test "$(git rev-list v0.1.0..v0.2.0 --count)" -eq "$(git rev-list v0.1.0..HEAD --count)"`
  → exit 0, com ambos valendo **85** ✓
- `git show v0.2.0 --stat` → tagger, data e a mensagem completa ✓
- **Geração de conferência com a tag** (`copier copy --defaults --vcs-ref v0.2.0`,
  sem `--vcs-ref=HEAD`) → exit 0, `.copier-answers.yml` com `_commit: v0.2.0`, e
  a árvore contém os três artefatos que a `v0.1.0` não entregava:
  - `core/static/img/logo-entidade.svg` ✓
  - `core/static/src/dominio.css` ✓
  - `core/templates/core/_nav_dominio.html` ✓
- **Prova de contraste:** `git cat-file -e v0.1.0:<caminho>` falha para os três
  caminhos — eles de fato não existiam na release anterior, então a tag é o
  que destrava as Fases 6 e 7 nos derivados.

**Número informativo registrado:** 85 commits entre `v0.1.0` e `v0.2.0`. O
`07-CONTEXT.md` dizia 39 e o planejamento mediu 42; o valor cresceu com os
commits da própria fase, e é por isso que a asserção de aceite é relativa e não
um número mágico.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - discrepância de estado] Checkbox de QA-03 já vinha `[x]`, não `[ ]`**
- **Found during:** Edição de `.planning/REQUIREMENTS.md`
- **Issue:** O plano assumia (e sua acceptance criteria testava literalmente)
  que a linha começava com `- [ ] **QA-03**:` e que o grep
  `^- \[ \] \*\*QA-03\*\*:.*todas as suítes` deveria retornar 1 após a
  edição. Na prática a linha já estava `- [x] **QA-03**:` antes desta task
  (requisito provavelmente marcado como completo por uma execução anterior
  da fase).
- **Fix:** Preservado o estado real do checkbox (`[x]`) e trocado somente o
  miolo da frase, exatamente como instruído em "não reindente, não troque
  `- [ ]` por `- [x]` e não mexa no rótulo" — a instrução pede para não
  *alterar* o estado do checkbox, então mantive o que já estava lá em vez
  de forçá-lo a `[ ]`.
- **Files modified:** `.planning/REQUIREMENTS.md`
- **Commit:** (ver hash abaixo)

Nenhum outro desvio. As demais mudanças seguiram o plano literalmente.

## Estado do host ao fim do plano

`docker compose ls -a` não lista nenhum projeto de ensaio ou nascimento, e
`git status --short` não produz saída. Nenhuma credencial de ensaio, container,
volume ou diretório temporário sobreviveu à fase (mitigações T-07-23, T-07-23b
e T-07-23c honradas).

## Self-Check: PASSED

- FOUND: README.md (modificado, contém as strings verificadas na Task 1)
- FOUND: .planning/ROADMAP.md (critério 8 sem "11 suítes")
- FOUND: .planning/REQUIREMENTS.md (QA-03 sem "11 suítes")
- FOUND: tag anotada `v0.2.0` apontando para o HEAD verificado
- Regressão completa das 7 etapas executada nesta sessão, toda com exit 0
- Checkpoint bloqueante da Task 2 aprovado pelo operador antes da tag
