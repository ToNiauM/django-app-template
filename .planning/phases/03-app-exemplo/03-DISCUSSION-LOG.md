# Phase 3: App Exemplo - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-18
**Phase:** 3-App Exemplo
**Areas discussed:** Modelo de dados do App Exemplo, Estrutura e UX do CRUD de referência, Modais HTMX de Criação/Edição, Dashboard ECharts e Agregações ORM, Asset Vendor ECharts, Isolamento e Remoção do App

---

## Modelo de dados do App Exemplo

| Option | Description | Selected |
|--------|-------------|----------|
| Modelo rico representativo `ItemExemplo` com auditoria | Campos de texto, choices (categoria/status), valor decimal, data, flags e `history = HistoricalRecords()` | ✓ |
| Modelo mínimo (apenas título e descrição) | Apenas campos textuais básicos | |

**User's choice:** Modelo rico representativo `ItemExemplo` com auditoria (modo `--auto`, padrão recomendado)
**Notes:** O modelo rico permite demonstrar filtros multi-seleção, validações de data/número e agregações financeiras no dashboard.

---

## Estrutura e UX do CRUD de referência

| Option | Description | Selected |
|--------|-------------|----------|
| Paginador server-side + Filtros HTMX + Ordenação dinâmica | Django `Paginator` com `hx-get`, debounce de busca, filtros multi-seleção e `hx-push-url="true"` | ✓ |
| Paginação client-side / Datatables JS | Tabela renderizada de uma vez com paginação no cliente | |

**User's choice:** Paginador server-side + Filtros HTMX + Ordenação dinâmica (modo `--auto`, padrão recomendado)
**Notes:** Segue a arquitetura da casa demonstrada na PCA, sem acoplamento a bibliotecas pesadas de frontend.

---

## Modais HTMX de Criação/Edição

| Option | Description | Selected |
|--------|-------------|----------|
| Modais server-rendered via HTMX + Alpine | Fragmentos HTML carregados sob demanda com validação via `ModelForm` e resposta HTTP 422 em caso de erro | ✓ |
| Páginas completas separadas (sem modais) | Telas dedicadas com full page reload | |

**User's choice:** Modais server-rendered via HTMX + Alpine (modo `--auto`, padrão recomendado)
**Notes:** Proporciona experiência fluida de SPA com a simplicidade e segurança do backend Django.

---

## Dashboard ECharts e Agregações ORM

| Option | Description | Selected |
|--------|-------------|----------|
| Agregações 100% no banco (ORM) + ECharts responsivo | `.aggregate()` e `.annotate()` no PostgreSQL com cards de KPI e gráficos de barras/pizza | ✓ |
| Cálculos em Python com iteradores | Iteração manual em listas de objetos | |

**User's choice:** Agregações 100% no banco (ORM) + ECharts responsivo (modo `--auto`, padrão recomendado)
**Notes:** Invariante de desempenho herdada da PCA para dashboards de apoio à decisão.

---

## Asset Vendor ECharts

| Option | Description | Selected |
|--------|-------------|----------|
| Local em `core/static/vendor/echarts.min.js` | Arquivo estático embutido sem dependência de internet ou CDN | ✓ |
| CDN externa | Carregamento via script tag CDN | |

**User's choice:** Local em `core/static/vendor/echarts.min.js` (modo `--auto`, padrão recomendado)
**Notes:** Mantém a portabilidade e operação offline do sistema gerado.

---

## Isolamento e Remoção do App (EX-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Desacoplamento estrito + Guia de remoção no README | Zero dependência reversa e documentação passo a passo em `apps/exemplo/README.md` | ✓ |
| App integrado sem documentação de remoção | Acoplamento direto entre core e exemplo | |

**User's choice:** Desacoplamento estrito + Guia de remoção no README (modo `--auto`, padrão recomendado)
**Notes:** Atende diretamente o requisito EX-04 de documentação viva descartável.

---

## Claude's Discretion

- Estrutura exata de templates parciais e nomes de rotas.
- Paleta visual detalhada e temas dos gráficos ECharts.
- Implementação do comando `seed_exemplo` com dados realistas.

## Deferred Ideas

None — discussion stayed within phase scope.
