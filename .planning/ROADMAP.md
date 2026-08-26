# Roadmap: Sistema Base — Template CFC

## Overview

Do zero a um template Copier que gera sistemas Django completos para o CFC. Primeiro nasce a fundação: um projeto Django rodando em Docker com autenticação, usuário customizado e settings seguros por ambiente. Depois vem o shell visual (layout, admin, PWA, auditoria), então o app exemplo que serve de documentação viva (CRUD de referência + dashboard ECharts). Com o sistema-modelo pronto, ele é templatizado via Copier (variáveis, `copier copy`/`copier update`, ops de produção), o fluxo completo de nascimento é verificado ponta a ponta e documentado no README, e por fim o padrão visual do Sistema CFC é herdado do PCA junto com o ponto de extensão da navegação.

## Milestones

- ✅ **v0.2.0 — Design system herdado do PCA** — Fases 1–7 (fechado em 2026-08-24)
- 🚧 **v0.3.0 — Guia de construção de sistemas** — Fases 8–10 (em andamento)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>✅ v0.2.0 — Design system herdado do PCA (Fases 1–7) — FECHADO em 2026-08-24</summary>

- [x] **Phase 1: Fundação Django** (4/4 planos) — Projeto Django em Docker com auth, usuário customizado e settings seguros por ambiente — concluída 2026-08-18
- [x] **Phase 2: Shell Visual e Kernel** (4/4 planos) — Layout base, admin customizado, PWA e auditoria no app `core` — concluída 2026-08-18
- [x] **Phase 3: App Exemplo** (3/3 planos) — CRUD de referência e dashboard ECharts como documentação viva — concluída 2026-08-18
- [x] **Phase 4: Templatização Copier** (7/7 planos) — Sistema-modelo vira template parametrizado com `copier copy`/`copier update` e ops de produção — concluída 2026-08-18
- [x] **Phase 5: Verificação e Documentação** (3/3 planos) — Fluxo de nascimento validado ponta a ponta e README completo — concluída 2026-08-18
- [x] **Phase 6: Customização Visual e Persistência de Dados** (3/3 planos) — Pontos de customização de marca no `core` e dados do banco persistidos no host, sobrevivendo a `docker compose down -v` — concluída 2026-08-19
- [x] **Phase 7: Herdar o design system do PCA** (14/14 planos) — O padrão visual do Sistema CFC sai do PCA e passa a nascer com todo sistema gerado, e a navegação ganha o ponto de extensão que obrigava cada derivado a reescrever o `_nav.html` — concluída 2026-08-24

Detalhes completos das fases: `.planning/milestones/v0.2.0-ROADMAP.md`
Requisitos do marco: `.planning/milestones/v0.2.0-REQUIREMENTS.md`
Resumo do marco: `.planning/MILESTONES.md`

</details>

### 🚧 v0.3.0 — Guia de construção de sistemas (Fases 8–10)

- [ ] **Phase 8: Exemplo provado** — O app de diárias e passagens existe como fixture, funciona dentro de uma cópia Copier real e as guardas de prova estão armadas
- [ ] **Phase 9: Escrita do guia** — Os capítulos do guia existem em `docs/guia/`, em linguagem simples, com todo código extraído do fixture provado
- [ ] **Phase 10: Distribuição e release** — O guia chega a todo sistema gerado, o `copier update` sai limpo e a tag `v0.3.0` está publicada

#### Phase 8: Exemplo provado

**Goal:** O código que o guia vai ensinar existe antes do texto: o app de diárias e passagens vive como fixture em `.template-tests/fixtures/guia/`, instala numa cópia Copier real e é provado de ponta a ponta — sem nunca vazar para o template ou para o sistema gerado.

**Requirements:** PRV-01, PRV-03

**Depends on:** —

**Success criteria:**

1. A suíte nova (`test_08_guia*`) gera uma cópia Copier real via `ensaio_django.sh`, instala o fixture como `apps/diarias` e sai verde: migração aplicada, testes do app passando, smoke HTTP das telas respondendo
2. Teste negativo verde: a cópia gerada recém-nascida NÃO contém `apps/diarias` nem qualquer arquivo do fixture (o domínio não vaza)
3. A suíte roda junto com as 13 existentes pelo test_command padrão do projeto
4. O fixture cobre tudo que o guia vai ensinar: modelo, admin, listagem paginada com filtros, modal 422/`HX-Trigger`, `_nav_dominio.html` com `{% item_nav %}` e dashboard ECharts com a paleta da marca

**Plans:** 2/4 plans executed

Plans:
**Wave 1**

- [x] 08-01-PLAN.md — Backend do fixture apps/diarias (modelo Viagem, admin, forms, views, urls, migração, seed)
- [x] 08-02-PLAN.md — Templates (listagem/modais/dashboard ECharts) e testes internos do fixture

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 08-03-PLAN.md — Teste negativo de vazamento (test_08_guia_vazamento.py, PRV-03)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 08-04-PLAN.md — Prova de ponta a ponta na cópia real (test_08_guia_prova.py) + suíte integral

#### Phase 9: Escrita do guia

**Goal:** Quem gerou um sistema pelo template abre `docs/guia/` e constrói o próprio sistema seguindo capítulos em linguagem simples — cada um terminando com um resultado visível na tela — com dois exemplos resumidos provando que o método transfere.

**Requirements:** GUIA-01, GUIA-02, GUIA-03, GUIA-04, GUIA-05, GUIA-06, GUIA-07, GUIA-08, GUIA-09, EX-01, EX-02, LNG-01, LNG-02, LNG-03, PRV-02

**Depends on:** Phase 8

**Success criteria:**

1. Seguindo os capítulos na ordem, o leitor sai do sistema recém-gerado e chega ao app de diárias completo: registros no admin, listagem paginada com filtros, criar/editar em modal, item no menu com estado ativo e painel com gráfico na paleta da marca
2. Todo capítulo termina com "recarregue e veja" e traz a seção "deu errado?" com os erros reais colhidos na construção do fixture
3. O capítulo de abertura entrega pré-requisitos, glossário e a regra de dono (`docs/guia/` é do núcleo); orçamento e controle de materiais existem como capítulo resumido no formato fixo; o mapa de receitas e o capítulo final existem
4. O teste de equivalência sai verde: toda cerca de código do guia é byte-idêntica ao arquivo correspondente do fixture
5. A revisão editorial com a persona "sabe planilha, não sabe Django" foi feita e aprovada — todo termo técnico traduzido na primeira ocorrência

**Plans:** TBD

#### Phase 10: Distribuição e release

**Goal:** O guia deixa de ser conteúdo do repositório-modelo e passa a chegar a todo sistema gerado — e aos derivados existentes por um `copier update` limpo — com a tag `v0.3.0` publicada.

**Requirements:** DST-01, DST-02, DST-03, REL-02

**Depends on:** Phase 9

**Success criteria:**

1. `copier copy` novo produz um sistema com `docs/guia/` completo dentro
2. Ensaio de `copier update` v0.2.0 → v0.3.0 sai com exit 0, zero marcador de conflito e zero `.rej`, com a árvore `docs/` coberta pela verificação
3. `README.md` e `README.md.jinja` linkam o guia numa seção curta, sem duplicar conteúdo dele
4. Tag `v0.3.0` anotada e publicada em `origin`, criada somente após verificar → revisar → consertar (ordem da lição 2 da retrospectiva)

**Plans:** TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Fundação Django | v0.2.0 | 4/4 | Complete | 2026-08-18 |
| 2. Shell Visual e Kernel | v0.2.0 | 4/4 | Complete | 2026-08-18 |
| 3. App Exemplo | v0.2.0 | 3/3 | Complete | 2026-08-18 |
| 4. Templatização Copier | v0.2.0 | 7/7 | Complete | 2026-08-18 |
| 5. Verificação e Documentação | v0.2.0 | 3/3 | Complete | 2026-08-18 |
| 6. Customização Visual e Persistência de Dados | v0.2.0 | 3/3 | Complete | 2026-08-19 |
| 7. Herdar o design system do PCA | v0.2.0 | 14/14 | Complete | 2026-08-24 |
| 8. Exemplo provado | v0.3.0 | 2/4 | In Progress|  |
| 9. Escrita do guia | v0.3.0 | 0/? | Not started | — |
| 10. Distribuição e release | v0.3.0 | 0/? | Not started | — |
