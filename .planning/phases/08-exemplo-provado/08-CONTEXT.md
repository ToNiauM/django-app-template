# Phase 8: Exemplo provado - Context

**Gathered:** 2026-08-26
**Status:** Ready for planning

<domain>
## Phase Boundary

O código que o guia (Fase 9) vai ensinar existe antes do texto: o app de diárias e passagens vive como fixture em `.template-tests/fixtures/guia/`, instala numa cópia Copier real via `ensaio_django.sh` e é provado de ponta a ponta — migração aplicada, testes do app passando, smoke HTTP das telas — sem nunca vazar para o template ou para o sistema gerado (teste negativo). A suíte nova `test_08_guia*` roda junto com as 13 existentes pelo `test_command` padrão. Requisitos: PRV-01, PRV-03.

Escrever o texto do guia é da Fase 9. Distribuição (`copier copy`/`copier update`) e release são da Fase 10.

</domain>

<decisions>
## Implementation Decisions

### Modelagem de diárias e passagens
- **D-01:** Modelo único `Viagem` — sem entidades relacionadas. Campos na linha de: servidor, destino, período (datas), motivo, valor de diárias, valor de passagens, status. Todo o padrão do app exemplo (listagem paginada, filtros, modal 422, dashboard) se aplica direto sobre ele; capítulos mais curtos para a persona "sabe planilha, não sabe Django".
- **D-02:** Status simples via `choices` (ex.: Solicitada / Aprovada / Paga / Cancelada), `CharField` sem regras de transição. É o filtro principal da listagem e a dimensão categórica dos gráficos.
- **D-03:** Servidor/beneficiário como campo texto simples (`CharField`) — zero acoplamento com o auth do core; é o que uma planilha faria.
- **D-04:** `Viagem` registrada na auditoria com `HistoricalRecords()` — o fixture segue a convenção declarada do template (`core/README.md`), e o guia ensina auditoria como parte natural do modelo.

### Claude's Discretion
- Campos exatos, verbose names, validações e dados de seed do fixture — desde que respeitem D-01–D-04 e as invariantes do projeto (pt-BR, datas DD/MM/AAAA, moeda R$).
- Escopo detalhado das telas e do dashboard — ancorar no critério 4 do roadmap (modelo, admin, listagem paginada com filtros, modal 422/`HX-Trigger`, `_nav_dominio.html` com `{% item_nav %}`, dashboard ECharts com paleta da marca), espelhando os padrões do app exemplo.
- Forma de instalação do fixture na cópia e profundidade dos testes/smoke — guiar-se pela pesquisa do marco (`.planning/research/`) e pelos critérios de sucesso do roadmap.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requisitos e pesquisa do marco
- `.planning/REQUIREMENTS.md` — PRV-01 e PRV-03 são os requisitos desta fase; fora de escopo do marco (sem unidade Copier opcional, sem MkDocs)
- `.planning/research/SUMMARY.md` — abordagem "código antes do texto", fixture em `.template-tests/fixtures/`, suíte `test_08_guia*`
- `.planning/research/ARCHITECTURE.md` — arquitetura do guia/fixture e fronteiras editoriais
- `.planning/research/PITFALLS.md` — armadilhas: vazamento de domínio, apodrecimento, conflito de update

### Harness de prova existente
- `.template-tests/ensaio_django.sh` — ferramenta que gera cópia Copier real, sobe Compose e roda alvos Django dentro dela; ler o cabeçalho inteiro (orçamento de tempo normativo: timeout 600000 ms, primeira criação em background com polling)
- `.planning/config.json` — `test_command`: `python3 -m unittest discover -s .template-tests -p 'test_*.py'` (a suíte nova precisa ser descoberta por esse padrão)
- `copier.yml` — `_exclude` já cobre `.template-tests` (base do teste negativo de vazamento)

### Padrões a espelhar no fixture
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/` — app de referência completo: models, admin, views, forms, urls, templates (`item_listar.html`, `_tabela_resultado.html`, `_filtros.html`, `_form_modal.html`, `dashboard.html`), testes (`test_crud`, `test_models`, `test_dashboard`, `test_nav_ativo`, `test_isolamento`) e `seed_exemplo`
- `core/README.md` — convenção `HistoricalRecords()` para modelos de domínio (D-04)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ensaio_django.sh`: harness pronto para gerar cópia real e executar migrate/testes/smoke lá dentro — a suíte `test_08_guia*` o reutiliza, não reinventa
- App exemplo: fonte de todos os padrões que o fixture replica (tabela server-side com ordenação whitelist, filtros multi-seleção, modal HTMX 422 + `HX-Trigger`, dashboard ECharts com agregação via ORM, `json_script`, drill-down)
- `{% item_nav %}` (Fase 7): o fixture cria `_nav_dominio.html` usando a inclusion tag — exatamente o fluxo que o guia ensinará
- Paleta da marca em runtime (`core/tema.py` → `familia_marca`): o dashboard do fixture consome a paleta servida, zero hex em template/JS

### Established Patterns
- Invariantes herdadas da PCA valem para o fixture: agregações via ORM (`annotate`/`aggregate`), paginação server-side, CSRF do HTMX via `htmx:configRequest`, pt-BR/`America/Sao_Paulo`, datas DD/MM/AAAA, moeda R$
- Testes de template em `.template-tests/test_*.py` descobertos por unittest; scripts shell (`test_*.sh`) são tracers à parte
- Stack fechada — nenhuma dependência nova no marco

### Integration Points
- `.template-tests/fixtures/guia/` — novo diretório do fixture (dentro de caminho já excluído pelo `copier.yml`)
- Cópia gerada: `apps/diarias` + `INSTALLED_APPS` + include de urls + `_nav_dominio.html` — os mesmos passos que o leitor do guia fará à mão

</code_context>

<specifics>
## Specific Ideas

- O fixture é material didático antes de ser código: cada escolha de modelagem foi feita para caber na persona "sabe planilha, não sabe Django" (modelo único, status por choices, beneficiário texto) — o planner não deve "melhorar" a modelagem além do decidido.
- Domínio de diárias e passagens no contexto do CFC (setor público): destino, período, motivo, valores — vocabulário familiar a quem preenche planilha de viagem.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 8-exemplo-provado*
*Context gathered: 2026-08-26*
