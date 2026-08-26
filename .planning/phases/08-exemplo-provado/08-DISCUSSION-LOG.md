# Phase 8: Exemplo provado - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-26
**Phase:** 8-exemplo-provado
**Areas discussed:** Modelagem de diárias e passagens

---

## Modelagem de diárias e passagens

### Estrutura das entidades

| Option | Description | Selected |
|--------|-------------|----------|
| Modelo único: Viagem | Servidor, destino, período, motivo, valores de diárias e passagens, status — padrão do exemplo se aplica direto; capítulos curtos para a persona | ✓ |
| Viagem + lançamentos (FK) | Diaria/Passagem como filhos relacionados; ensina FK mas adiciona admin inline e complexidade | |
| Duas entidades independentes | Diária e Passagem como cadastros separados; duplica as telas ensinadas | |

**User's choice:** Modelo único: Viagem (recomendado)

### Workflow de status

| Option | Description | Selected |
|--------|-------------|----------|
| Status simples via choices | Solicitada/Aprovada/Paga/Cancelada, CharField sem regras de transição | ✓ |
| Sem status | Só dados factuais; perde a dimensão categórica didática | |
| Workflow com regras | Transições validadas; lógica de negócio foge do método do template | |

**User's choice:** Status simples via choices (recomendado)

### Servidor/beneficiário

| Option | Description | Selected |
|--------|-------------|----------|
| Campo texto simples | CharField; zero acoplamento com auth; é o que uma planilha faria | ✓ |
| FK para Usuario do core | Integra com auth, mas acopla o domínio e complica seed/testes | |
| Cadastro próprio de Servidor | Segundo modelo com FK; reabriria a complexidade de duas entidades | |

**User's choice:** Campo texto simples (recomendado)

### Auditoria

| Option | Description | Selected |
|--------|-------------|----------|
| Sim, com HistoricalRecords | Segue a convenção do template; guia ensina auditoria como parte natural do modelo | ✓ |
| Não, deixar fora | Modelo mais enxuto, mas divergiria da convenção declarada do template | |

**User's choice:** Sim, com HistoricalRecords (recomendado)

---

## Claude's Discretion

- Campos exatos, verbose names, validações e seed do fixture
- Escopo detalhado das telas e do dashboard (ancorado no critério 4 do roadmap)
- Mecânica de instalação do fixture na cópia e profundidade dos testes/smoke

As áreas "Escopo das telas e do dashboard", "Forma do fixture e material p/ Fase 9" e "Profundidade da prova" foram oferecidas e não selecionadas — ficam a critério de researcher/planner, ancoradas na pesquisa do marco e nos critérios do roadmap.

## Deferred Ideas

None
