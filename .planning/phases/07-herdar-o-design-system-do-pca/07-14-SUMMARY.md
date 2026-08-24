---
phase: 07-herdar-o-design-system-do-pca
plan: 14
subsystem: release-e-verificacao
status: complete
completed: 2026-08-24
tasks_total: 3
tasks_done: 3
gap_closure: true
wave: 4
requirements: [REL-01, QA-03, DS-02, DS-03, DS-05, NAV-02]
files_modified:
  - README.md
  - .planning/ROADMAP.md
  - .planning/STATE.md
---

# 07-14 — Fecho da rodada de gap closure

## One-liner

O operador aprovou os quatro consertos numa cópia real, a regressão das 7
etapas passou verde em 394 s somados, e a `v0.2.0` — que apontava para
`367dd9a`, o commit que **contém** os quatro bloqueadores — foi apagada e
recriada sobre `01ced83`, sem sair da máquina.

## Task 1 — Inspeção visual dos quatro pontos consertados (`checkpoint:human-verify`, gate="blocking")

**Aprovada pelo operador em 2026-08-24.** Nenhum arquivo alterado, como o
plano exige.

### Preparação executada antes do handoff

- **Cópia órfã derrubada.** O projeto Compose `nascimento753123` estava de pé
  desde 01:39 em `/tmp/tmp.63S4rYMWlz/nascimento` — exatamente o cenário que
  o plano manda eliminar: a senha efêmera daquele administrador vivia só na
  memória da sessão que a gerou, o que tornava a cópia inútil para inspeção.
  `down --volumes --remove-orphans` → exit 0, diretório apagado.
- `bash .template-tests/ensaio_django.sh derrubar` → exit 0.
  `docker compose ls -a` sem nenhum projeto de ensaio ou nascimento
  (critério de aceite da mitigação T-07-23b).
- Credencial efêmera gerada **pelo executor** com
  `python3 -c 'import secrets; print(secrets.token_urlsafe(24))'`, tracing
  desabilitado (`set +x`, `unset HISTFILE`), e passada ao tracer **uma única
  vez, só pelo ambiente**. Identidade fixa contratada pelo plano 05-01
  (`nascimento@example.invalid`), sem `createsuperuser` manual.
- `NASCIMENTO_ADMIN_PASSWORD=… bash .template-tests/test_05_nascimento.sh --keep`
  → exit 0. **169 testes Django** verdes na cópia gerada (medido; eram 112 no
  07-08 — os cinco planos de fechamento acrescentaram 57). Dados sobreviveram
  a `down --volumes` + `up -d`.
- **Checagem de vazamento (T-07-23):** `grep -rIF "<senha>"` no repositório do
  template e na árvore gerada (com `--exclude-dir=dados`) → **vazio nos
  dois**. A senha não entrou em arquivo, SUMMARY, README,
  `.copier-answers.yml`, log nem comando versionado. O script de preparação
  ficou fora do repositório (scratchpad de sessão) e não continha a senha,
  apenas a geração dela; foi apagado ao fim.
- **Smoke:** `/healthz` → 200, `/login/` → 200, `/exemplo/dashboard/` sem
  autenticação → 302.
- Entrega ao operador: URL, usuário e senha **só no retorno do checkpoint**.

### Veredito

O operador respondeu **"aprovado"**, acrescentando "está muito bom o
template".

**Registro honesto do formato do veredito:** a aprovação veio **global**, não
item a item por tema. O `<resume-signal>` do plano contrata literalmente
`Responda "aprovado" ou descreva o que reprovou, indicando o ponto (1 a 4) e
o tema` — ou seja, "aprovado" sem qualificação é o sinal contratado de que os
quatro pontos passaram nos dois temas, e é assim que fica registrado. Não
houve declaração separada por ponto, e este SUMMARY não a inventa.

Os quatro pontos submetidos:

| # | Ponto | Origem do conserto |
|---|-------|--------------------|
| 1 | Um único item de menu aceso em `/exemplo/dashboard/` e em `/exemplo/` | 07-10 (G-01) |
| 2 | As 4 fatias do donut visíveis e distinguíveis, nos 2 temas, repintando na troca | 07-13 (G-03) |
| 3 | Grade do eixo Y discreta mas visível no tema escuro | 07-12 (G-04) |
| 4 | Texto legível nos botões primários no escuro, inclusive no hover | 07-11 (G-02) |

### Limpeza pós-veredito

`down --volumes --remove-orphans` → exit 0; `dados/` removido via container
`postgres:17` root (o initdb grava como uid 999 e o usuário do host não
consegue apagar); diretório temporário apagado; `docker compose ls -a` sem
resíduo.

## Task 2 — Regressão completa das 7 etapas e o registro do que mudou

### As 7 etapas, na ordem do README

Cada etapa com timeout próprio de 600 s, nunca encadeadas.

| # | Etapa | Exit | Duração |
|---|-------|------|---------|
| 1 | `ensaio_django.sh derrubar` | 0 | 0 s |
| 2 | `test_copier_copy.sh` | 0 | 28 s |
| 3 | `test_copier_update.sh` | 0 | 60 s |
| 4 | `unittest discover -s .template-tests` | 0 | 153 s |
| 5 | `test_07_cor_runtime.sh` | 0 | 46 s |
| 6 | `ensaio_django.sh derrubar` | 0 | 3 s |
| 7 | `test_05_nascimento.sh` | 0 | 104 s |

Total somado: **394 s**.

### Contagens medidas nesta task

| O quê | Valor | Como foi medido |
|---|---|---|
| Suítes em `.template-tests/` | **13** | `ls .template-tests/ \| grep -c '^test_'` |
| Testes da etapa 4 | **39** | `Ran 39 tests in 152.545s` no bloco da etapa 4 do log |
| Testes Django na cópia gerada (etapa 7) | **169** | `Ran 169 tests in 37.059s` no bloco da etapa 7 |
| Tokens `--cor-*` no `:root` | **23** | regex ancorado em declaração, não `grep` bruto |
| Tokens sobrescritos no bloco escuro | **20** | idem; o escuro é subconjunto estrito do claro |
| Commits `v0.1.0..HEAD` | **113** | `git rev-list --count` |

**Armadilha de medição registrada:** o log traz três linhas `Ran N tests`. A
do meio (`Ran 1 test`) é o preflight de `collectstatic` **dentro** de
`test_05_nascimento.sh`, não uma suíte. Amarrar cada contagem ao bloco
`===== ETAPA N =====` do log foi o que evitou publicar "1 teste" como
resultado da etapa 4. Um `sed -n 2p` ingênuo teria feito exatamente isso.

Os contadores de token também mudaram desde o `07-VERIFICATION.md`, que
registrava 21/18: `--cor-brand-tx` (07-11) e `--cor-seq-750` (07-13) entraram
depois. 21+2 = 23 e 18+2 = 20 — consistente.

### `README.md`

O operador pediu, no meio da execução, que o README fosse atualizado "com
todas as informações possíveis". Isso **amplia** o escopo que a Task 2
previa (um parágrafo sobre a tag). Ampliação registrada como desvio
autorizado pelo operador. O arquivo passou de 610 para 984 linhas, com
quatro seções novas:

1. **Estrutura do repositório do template** — as três regras que explicam
   qualquer arquivo da árvore (`.jinja` renderiza; sem sufixo é verbatim;
   `_exclude` não sai daqui), mapa de diretórios e os dois caminhos que
   `_skip_if_exists` transfere para o derivado.
2. **O design system herdado** — fonte física das cores, `COR_PRIMARIA` em
   runtime pelas 8 chaves de `_CHAVES_MARCA`, tema escuro, elevação/raio/
   régua/fonte/anel de foco, classes de componente e `safelist`, paleta de
   gráfico por `json_script`, `dominio.css` e a guarda de contraste herdada.
3. **Ponto de extensão da navegação** — as três peças, tabela dos cinco
   argumentos de `{% item_nav %}` e por que `excecoes` é declarada no sítio
   da chamada.
4. **Tag publicada não se move** — a regra pedida pelo plano.

Mais: tabela dos 8 validators do Copier no passo 4 do nascimento; inventário
da regressão completado (`test_06_persistencia.py` e
`test_quick_comentarios_template.py` faltavam); orçamento de timeout por
etapa; e a instrução de conferir `docker compose ls -a` antes de cada rodada.

**Erro de fato pego antes de virar documentação:** o rascunho afirmava que
`--cor-brand-tx` era derivado da marca por `core/tema.py`. É falso —
`_CHAVES_MARCA` tem 8 entradas e nenhuma é `brand-tx`. São dois hex planos no
`input.css` (`#ffffff` no claro, `#0f0e0d` no escuro, este idêntico ao
`--cor-page` do escuro). O README documenta a exceção e o porquê dela: o
texto sobre a marca só tem duas respostas possíveis, e derivá-lo
introduziria variável onde a decisão é binária.

**Falso positivo no critério de aceite, registrado:** o critério
`grep -ci "tag publicada" README.md >= 1` **já passava antes desta task** —
a linha 718 contém "a última tag publicada", frase sobre o comportamento do
Copier, não a regra. O critério passaria em falso positivo sem nenhuma
escrita. A conferência foi feita **por conteúdo**: a subseção
`### Tag publicada não se move` foi escrita e lida. Hoje o `grep` devolve 3.

### `.planning/ROADMAP.md`

Os seis planos de fechamento (07-09 a 07-14) aparecem exatamente 1× cada.
Linha `**Plans:**` atualizada para a contagem real de arquivos
`07-*-PLAN.md` no diretório da fase.

**Divergência interna do plano, resolvida pelo critério de aceite:** o
`<action>` da Task 2 pede `**Plans:** 6/6 concluídos`, mas o critério de
aceite da mesma task exige que a linha bata com a contagem real de
`07-*-PLAN.md` — que é **14**, não 6. Seguido o critério de aceite, que é o
contrato verificável. O "6/6" refere-se à subseção de fechamento de gaps,
que já lista os seis planos com suas ondas.

Os 8 success criteria não foram reescritos: continuam sendo o contrato da
fase e continuam atendidos.

## Task 3 — `v0.2.0` recriada sobre o commit corrigido, sem publicar

### Pré-condições, todas conferidas antes de tocar na tag

| # | Pré-condição | Resultado |
|---|---|---|
| 1 | `git status --short` sem saída | vazio |
| 2 | Regressão das 7 etapas verde nesta sessão | sim (Task 2) |
| 3 | `git rev-parse v0.2.0^{commit}` = `367dd9a` | confirmado |
| 4 | `git ls-remote --tags origin \| grep v0.2.0` vazio | vazio — nunca publicada |

A pré-condição 4 foi verificada **antecipadamente**, ainda durante o
checkpoint da Task 1, antes de gastar os 394 s da regressão: se a tag já
estivesse publicada, o plano pararia e a resposta correta passaria a ser uma
`v0.2.1`, decisão do operador. Falhar cedo custa menos.

Conferido também que `367dd9a` é **ancestral do HEAD**
(`git merge-base --is-ancestor`), o que torna a operação reversível: apagar
a tag não torna nenhum commit inalcançável, e restaurar o estado anterior é
um `git tag -a v0.2.0 367dd9a`.

### A tag

`git tag -d v0.2.0` (era `a29c337`, o objeto de tag anotada que apontava para
o commit `367dd9a`) e `git tag -a v0.2.0` sobre o HEAD verificado. Mensagem
em pt-BR descrevendo o que a release entrega (Fases 6 e 7) mais um parágrafo
sobre o fechamento dos quatro bloqueadores.

### Asserções relativas — nenhum número mágico

| Asserção | Resultado |
|---|---|
| `git cat-file -t v0.2.0` = `tag` | `tag` (anotada) |
| `git rev-list v0.2.0..HEAD --count` = 0 | 0 |
| `git rev-list v0.1.0..v0.2.0 --count` = `git rev-list v0.1.0..HEAD --count` | 113 = 113 |
| `git rev-parse v0.2.0^{commit}` ≠ `367dd9a` | `01ced83` |

### Geração de conferência

`copier copy --defaults --vcs-ref v0.2.0` numa pasta temporária.

**Desvio necessário, registrado:** o comando exato do `<action>` **falha** —
`ValueError: Question "sistema_nome" is required`. A pergunta `sistema_nome`
não tem `default:` no `copier.yml`, então `--defaults` sozinho não consegue
responder. É defeito do texto do plano, não do template: o
`test_05_nascimento.sh` sempre passou `--data` para todas as respostas.
Acrescentado o mínimo — `--data 'sistema_nome=Conferencia'` — e o resto
resolvido pelos defaults derivados. Exit 0.

`.copier-answers.yml` grava `_commit: v0.2.0` (o arquivo é YAML *flow style*,
numa linha só — um `grep -E "^_commit:"` ancorado devolve vazio e daria falso
negativo; conferido lendo o arquivo).

Presentes na árvore de conferência: `core/static/src/dominio.css`,
`core/templates/core/_nav_dominio.html`, `core/static/img/logo-entidade.svg`.

Provas de que os quatro consertos chegaram à árvore da tag:

| Sinal | Esperado | Medido |
|---|---|---|
| `grep -c -- "--cor-brand-tx" core/static/src/input.css` | 2 | 2 |
| `grep -c "seq-750" tailwind.config.js` | 1 | 1 |
| `text-white` acompanhado de `bg-brand` em `apps/` | 0 | 0 |
| `grep -c "excecoes" core/templatetags/navegacao.py` | ≥ 1 | 5 |
| `cor-grid` consumido pelo dashboard | ≥ 1 | 1 |
| hex solto em template | 0 | 0 |

O único `text-white` restante em `apps/` está sobre `bg-red-600`, no botão de
confirmação de exclusão — branco sobre vermelho é o par correto, e não é o
par da marca que o G-02 consertou.

Pasta de conferência apagada. `git status --short` vazio antes e depois.

### Nada foi publicado

`git push` não foi executado, em nenhuma forma.
`git ls-remote --tags origin | grep v0.2.0` continua vazio. Publicar é
decisão do operador.

## Estado final

- `git status --short` — vazio
- `docker compose ls -a` — sem projeto de ensaio ou nascimento
- `v0.2.0` → `01ced83`, anotada, no HEAD, local
- Fase 07 com 14 planos executados e 14 SUMMARYs

## Desvios do plano

1. **Escopo do README ampliado pelo operador** durante a execução ("com todas
   as informações possíveis"). Quatro seções novas em vez de um parágrafo.
2. **`--defaults` sozinho não gera** — `sistema_nome` não tem default;
   acrescentado `--data 'sistema_nome=Conferencia'`.
3. **`**Plans:**` seguiu o critério de aceite (14), não o `<action>` (6)** —
   os dois se contradizem dentro da mesma task.
4. **Veredito do operador veio global**, não item a item; registrado como tal.
5. **Ordem da escrita da tag no README** — a regra durável ("tag publicada
   não se move") foi escrita na Task 2, como o plano pede. O registro
   factual de que a `v0.2.0` desta vez foi recriada não foi escrito no
   README: ele é histórico de uma release específica e vive neste SUMMARY e
   na mensagem da própria tag anotada, que é onde alguém investigando aquela
   tag vai olhar. Escrevê-lo no README exigiria afirmar, antes da Task 3
   rodar, algo que ainda não era verdade.
