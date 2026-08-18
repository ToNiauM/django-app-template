# Phase 3: App Exemplo - Context

**Gathered:** 2026-08-18
**Status:** Ready for planning

<domain>
## Phase Boundary

O app `apps/exemplo/` demonstra o padrão de desenvolvimento de referência da casa: um CRUD completo com tabela paginada server-side, ordenação por cabeçalho, filtros multi-seleção e modais de criação/edição via HTMX/Alpine, mais um dashboard analítico com gráficos ECharts e cards de KPI com agregações calculadas 100% no banco via ORM (`annotate`/`aggregate`). O modelo de dados exercita auditoria com `django-simple-history` (`HistoricalRecords`). O app é 100% autocontido e removível sem quebrar o sistema base.

Requisitos cobertos: EX-01, EX-02, EX-03, EX-04.

Fora desta fase: parametrização Copier das variáveis do template (Fase 4 — `copier.yml` e jinja) e scripts de backup/vhost (Fase 4 — `ops/`).

</domain>

<decisions>
## Implementation Decisions

*(Modo `--auto`: decisões selecionadas automaticamente com a opção recomendada, espelhando os padrões da PCA e as convenções estabelecidas nas Fases 1 e 2.)*

### Modelo de Dados e Auditoria (EX-01, EX-04)
- **D-24:** Modelo representativo `ItemExemplo` em `apps/exemplo/models.py` contendo uma variedade rica de tipos de dados para demonstrar filtros, validações e agregações:
  - `titulo` (`CharField(max_length=200)`): identificador textual principal
  - `descricao` (`TextField(blank=True)`): texto descritivo longo
  - `categoria` (`CharField(max_length=30, choices=CategoriaChoices)`): opções como Operacional, Estratégico, Administrativo, Financeiro (para filtros multi-seleção e agregação por categoria)
  - `status` (`CharField(max_length=20, choices=StatusChoices, default=StatusChoices.RASCUNHO)`): opções como Rascunho, Em Andamento, Concluído, Cancelado (com cores/badges semânticos)
  - `valor` (`DecimalField(max_digits=12, decimal_places=2, default=0.00)`): valor monetário para agregações de soma/média no dashboard
  - `prazo` (`DateField(null=True, blank=True)`): data limite para demonstrar filtros temporais e ordenação por data
  - `ativo` (`BooleanField(default=True)`): flag lógica
  - `criado_em` / `atualizado_em` (`DateTimeField(auto_now_add=True)` / `DateTimeField(auto_now=True)`)
  - `criado_por` (`ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)`): rastreabilidade do autor
  - `history = HistoricalRecords()`: exercita a convenção de auditoria D-23 estabelecida na Fase 2

### CRUD, Tabela Paginada Server-Side e Filtros (EX-01)
- **D-25:** Listagem paginada server-side usando `django.core.paginator.Paginator` com tamanho de página padrão (ex.: 10 a 15 itens) e preservação dos parâmetros de filtro/ordenação nos links de página.
- **D-26:** Filtros e ordenação server-side:
  - Busca textual geral via `Q(titulo__icontains=q) | Q(descricao__icontains=q)`
  - Filtros multi-seleção para `categoria` e `status` usando `request.GET.getlist()`
  - Ordenação dinâmica por colunas clicáveis com whitelist estrita de campos permitidos (`titulo`, `categoria`, `status`, `valor`, `prazo`, `criado_em`) e alternância asc/desc
- **D-27:** Interatividade HTMX na listagem:
  - Formulário de filtros com `hx-get` apontando para a view de listagem, `hx-trigger="change, input changed delay:300ms from:input[type='text']"`, `hx-target="#tabela-container"`, `hx-swap="innerHTML"` e `hx-push-url="true"` para permitir histórico e navegação no navegador.

### Modais de Criação, Edição e Exclusão via HTMX (EX-02)
- **D-28:** Formulário baseado em `ModelForm` (`ItemExemploForm`) com validação do Django:
  - Abertura de modal: botão "Novo Item" ou "Editar" dispara `hx-get` na rota correspondente, retornando o HTML do modal (`_form_modal.html`) inserido em container gerenciado pelo Alpine.js.
  - Submissão: `hx-post` envia o form; se válido, fecha o modal, dispara trigger de atualização da listagem (ou recarrega fragmento) e exibe toast/mensagem de sucesso; se inválido, retorna HTTP 422 com erros de formulário renderizados no corpo do modal sem fechar.
- **D-29:** Exclusão com diálogo de confirmação seguro via HTMX (`hx-delete` ou `hx-post` com CSRF token), com remoção visual imediata ou atualização da tabela.

### Dashboard Analítico e Agregações ORM (EX-03)
- **D-30:** Agregações 100% no banco de dados via ORM do Django, nunca processadas em memória Python:
  - KPIs de topo (Cards): `.aggregate(total_itens=Count('id'), valor_total=Sum('valor'), valor_medio=Avg('valor'), concluidos=Count('id', filter=Q(status='CONCLUIDO')))`
  - Gráficos analíticos:
    - Gráfico 1 (Barras/Colunas): Valor financeiro por categoria `.values('categoria').annotate(total=Sum('valor'), qtd=Count('id')).order_by('-total')`
    - Gráfico 2 (Rosca/Pizza): Distribuição de itens por status `.values('status').annotate(qtd=Count('id')).order_by('status')`
    - Gráfico 3 (Evolução/Linhas): Contagem ou valores por mês/período `.annotate(mes=TruncMonth('criado_em')).values('mes').annotate(total=Sum('valor'))`
- **D-31:** Visualização ECharts:
  - Dados serializados de forma segura para JSON via `json_script` ou dataset serializado em contexto.
  - Inicialização das instâncias ECharts com tema alinhado aos tokens visuais de marca do sistema (`COR_PRIMARIA`).
  - Redimensionamento automático com `window.addEventListener('resize', ...)` e suporte a ciclos de vida do Alpine.js.

### Assets Vendor (ECharts)
- **D-32:** Biblioteca Apache ECharts incluída como arquivo estático vendor local em `core/static/vendor/echarts.min.js` (copiado da PCA), eliminando qualquer dependência de CDN externa em runtime.

### Isolamento e Protocolo de Remoção (EX-04)
- **D-33:** Zero dependência reversa: nenhum módulo do `core`, `config` ou infraestrutura referencia diretamente models ou views do `apps/exemplo`.
- **D-34:** As únicas integrações do exemplo são os 3 pontos de acoplamento padrão:
  1. `config/settings/base.py` (`INSTALLED_APPS += ['apps.exemplo']`)
  2. `config/urls.py` (`path('exemplo/', include('apps.exemplo.urls', namespace='exemplo'))`)
  3. `core/templates/core/_nav.html` (links de navegação para CRUD e Dashboard)
- **D-35:** Documentação clara no `apps/exemplo/README.md` com o passo a passo de exclusão do app de exemplo ao iniciar a modelagem de domínio real em um sistema novo gerado.
- **D-36:** Comando de seed de dados (`python manage.py seed_exemplo` ou similar) para popular o banco de desenvolvimento com registros realistas para teste e visualização imediata do CRUD e dashboard.

### Claude's Discretion
- Nomes exatos das views, rotas e arquivos de template parciais em `apps/exemplo/`.
- Configuração visual e paleta de cores detalhada dos gráficos ECharts (mantendo harmonia com a cor primária).
- Quantidade exata e categorias dos dados gerados pelo comando de seed.
- Microinterações de UI nos componentes de filtro e paginação.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fonte de extração (somente leitura — NUNCA modificar)
- `/opt/web/pca/apps/pca/views.py` — padrão de queries, paginação, filtros, agregações ORM e respostas HTMX
- `/opt/web/pca/apps/pca/models.py` — padrão de campos, choices e `HistoricalRecords`
- `/opt/web/pca/apps/pca/templates/pca/tabela.html`, `_tabela_resultado.html`, `_tabela_linha.html`, `_filtros.html`, `_filtro_multiselect.html` — estrutura de tabela e filtros HTMX
- `/opt/web/pca/apps/pca/templates/pca/dashboard.html`, `_dashboard_blocos.html` — integração ECharts, cards de KPIs e scripts de renderização
- `/opt/web/pca/core/static/vendor/echarts.min.js` — script vendor do ECharts a ser adicionado em `core/static/vendor/`

### Documentos do projeto
- `.planning/PROJECT.md` — escopo, invariantes e restrições
- `.planning/REQUIREMENTS.md` — requisitos EX-01 a EX-04
- `.planning/phases/02-shell-visual-e-kernel/02-CONTEXT.md` — decisões do shell, breadcrumbs e auditoria
- `core/templates/core/shell.html` — layout base com blocos de página
- `core/templates/core/_breadcrumbs.html` — contrato de breadcrumbs (`trilha`)
- `core/templates/core/_nav.html` — ponto de extensão da navegação
- `core/README.md` — convenções de auditoria do sistema

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/templates/core/shell.html`: shell completo com aside fixa, gaveta Alpine, e blocos `cabecalho_pagina`, `titulo_pagina`, `conteudo_pagina`.
- `core/templates/core/_breadcrumbs.html`: recebe a lista `trilha` montada na view (`[{"rotulo": "Exemplo", "url": "/exemplo/"}, {"rotulo": "CRUD"}]`).
- `core/templates/core/_nav.html`: arquivo documentado explicitamente como ponto de extensão para adicionar os links do CRUD e Dashboard.
- `core/static/vendor/alpine.min.js` e `htmx.min.js`: já instalados e ativos no `base.html`.
- `tailwind.config.js`: classes utilitárias e paleta de marca já configuradas.

### Established Patterns
- Agregações com `.aggregate()` e `.annotate()` executadas exclusivamente no PostgreSQL/ORM, sem loops em Python.
- CSRF HTMX transparente via listener `htmx:configRequest` lendo cookie `csrftoken`.
- Auditoria com `history = HistoricalRecords()` em modelos de domínio.
- Comentários explicativos em pt-BR detalhando o propósito do código.

### Integration Points
- `apps/exemplo/urls.py` incluído em `config/urls.py` com namespace `exemplo`.
- `apps.exemplo` registrado em `config/settings/base.py`.
- Links do CRUD e Dashboard registrados em `core/templates/core/_nav.html`.
- `core/static/vendor/echarts.min.js` disponibilizado para inclusão nos templates de dashboard.

</code_context>

<specifics>
## Specific Ideas

- O app `apps/exemplo` serve como um "tutorial executável" de alta qualidade: quem gera um sistema novo pode estudar como fazer um CRUD com modais HTMX e um dashboard ECharts responsivo, reproduzir o padrão em seus apps de negócio reais e depois deletar `apps/exemplo` com segurança.
- O comando de seed (`seed_exemplo`) facilita a avaliação visual imediata sem necessidade de cadastrar dezenas de itens manualmente.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope (modo auto, sem novas capacidades sugeridas).

</deferred>

---

*Phase: 3-App Exemplo*
*Context gathered: 2026-08-18*
