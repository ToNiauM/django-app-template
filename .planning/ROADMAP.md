# Roadmap: Sistema Base — Template CFC

## Overview

Do zero a um template Copier que gera sistemas Django completos para o CFC. Primeiro nasce a fundação: um projeto Django rodando em Docker com autenticação, usuário customizado e settings seguros por ambiente. Depois vem o shell visual (layout, admin, PWA, auditoria), então o app exemplo que serve de documentação viva (CRUD de referência + dashboard ECharts). Com o sistema-modelo pronto, ele é templatizado via Copier (variáveis, `copier copy`/`copier update`, ops de produção), o fluxo completo de nascimento é verificado ponta a ponta e documentado no README, e por fim o padrão visual do Sistema CFC é herdado do PCA junto com o ponto de extensão da navegação.

## Milestones

- ✅ **v0.2.0 — Design system herdado do PCA** — Fases 1–7 (fechado em 2026-08-24)

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

### 📋 Próximo marco (a definir)

Nenhuma fase planejada. Use `/gsd-new-milestone` para abrir o próximo escopo.

Encaminhamentos conhecidos, registrados em `PROJECT.md` → Requisitos → Ativos:

- Publicar a tag `v0.2.0` (`git push origin v0.2.0`) — decisão do operador
- Rodar o `copier update` desta versão no DividaAtiva
- Construir o Orçamento — primeiro uso real do template, em projeto próprio

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
