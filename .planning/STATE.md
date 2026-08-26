---
gsd_state_version: 1.0
milestone: v0.3.0
milestone_name: Guia de construção de sistemas
status: planning
last_updated: "2026-08-26T00:29:36.256Z"
last_activity: 2026-08-26
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (atualizado 2026-08-24 após o marco v0.2.0)

**Core value:** Criar um sistema novo funcional (login, layout, CRUD de exemplo, dashboard de exemplo, Docker, backup) em minutos — restando ao time apenas modelar o domínio em `apps/`.
**Current focus:** Nenhum — as 7 fases do marco v0.2.0 estão fechadas. Próximo escopo em `/gsd-new-milestone`.

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-08-26 — Milestone v0.3.0 started

## Performance Metrics

**Velocity:**

- Total plans completed: 21
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 4 | - | - |
| 2 | 4 | - | - |
| 04 | 7 | - | - |
| 05 | 3 | - | - |
| 06 | 3 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 01 P01 | 6min | 1 tasks | 10 files |
| Phase 01-funda-o-django P02 | 8min | 1 tasks | 14 files |
| Phase 01-funda-o-django P03 | 15min | 1 tasks | 6 files |
| Phase 01-funda-o-django P04 | 10min | 3 tasks | 9 files |
| Phase 02 P01 | 4min | 2 tasks | 6 files |
| Phase 02 P02 | 5min | 3 tasks | 7 files |
| Phase 02 P03 | 6min | 3 tasks | 10 files |
| Phase 02 P04 | 5min | 3 tasks | 10 files |
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 05 P01 | 196min | 1 tasks | 5 files |
| Phase 06 P01 | 8min | 3 tasks | 8 files |
| Phase 06 P02 | 9min | 3 tasks | 6 files |
| Phase 06 P03 | 4min | 3 tasks | 4 files |
| Phase 07 P01 | 18min | 3 tasks | 5 files |
| Phase 07 P02 | 25min | 3 tasks | 10 files |
| Phase 07-herdar-o-design-system-do-pca P03 | 24min | 3 tasks | 12 files |
| Phase 07-herdar-o-design-system-do-pca P04 | 35min | 4 tasks | 7 files |
| Phase 07-herdar-o-design-system-do-pca P05 | 40min | 3 tasks | 4 files |
| Phase 07-herdar-o-design-system-do-pca P06 | 70min | 3 tasks | 7 files |
| Phase 07-herdar-o-design-system-do-pca P07 | 45min | 3 tasks | 6 files |
| Phase 07-herdar-o-design-system-do-pca P09 | 13min | 3 tasks | 4 files |
| Phase 07-herdar-o-design-system-do-pca P10 | 18min | 3 tasks | 5 files |
| Phase 07-herdar-o-design-system-do-pca P11 | 27min | 2 tasks | 7 files |
| Phase 07-herdar-o-design-system-do-pca P12 | 22min | 3 tasks | 2 files |
| Phase 07-herdar-o-design-system-do-pca P13 | 16min | 3 tasks | 7 files |

## Accumulated Context

### Roadmap Evolution

- Phase 6 added
- Phase 7 added (2026-08-23): Herdar o design system do PCA — o padrão visual do Sistema CFC passa a nascer com todo sistema gerado. Pedido do operador.
  - **Rota decidida**: o template herda **direto de `/opt/web/pca`**, não do DividaAtiva. Motivo: o PCA é anterior ao template (não tem `.copier-answers.yml`) e é a fonte real do padrão; o DividaAtiva tem só um recorte dele. Herdar do filho implicaria implementar o mesmo sistema duas vezes e conflitar com o próprio trabalho do filho no `copier update` seguinte.
  - **Consequência para o DividaAtiva**: a Fase 8 de lá encolhe — deixa de reimplementar o design system à mão e passa a "rodar o `copier update` desta versão e adaptar o que é do domínio da dívida".
  - **Escopo ampliado em 2026-08-23 (operador)**: entra também o **encaixe da navegação** (T-01 da auditoria) — `{% include "core/_nav_dominio.html" %}` como ponto de extensão mais uma inclusion tag `{% item_nav %}` para o item. Motivo: o `_nav.html` é o pior conflito aberto da família (79 linhas reescritas pelo DividaAtiva dentro de arquivo upstream), e resolvê-lo ANTES da v0.2.0 é o que torna o `copier update` dos derivados viável em vez de doloroso. Resolve junto o T-03 (itens do app exemplo saem do `_nav.html` base).
  - **Pendência de release que esta fase carrega**: o repositório está com 37 commits desde a tag `v0.1.0`. Como o Copier lê a última tag e não o HEAD, a Fase 6 inteira (marca, logos, bind mount) nunca chegou a nenhum sistema derivado. A fase deve fechar com uma tag `v0.2.0` que entregue Fase 6 e Fase 7 juntas.

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: Template clonável via Copier (não pacote pip, não monorepo)
- Init: Stack fechada idêntica à da PCA (Django 5.2 LTS, PostgreSQL 17, HTMX/Alpine/Tailwind, ECharts)
- Init: `Usuario` customizado desde a primeira migração (preserva viabilidade de SSO futuro)
- Init: PCA em `/opt/web/pca` não será alterada
- Init: Toda documentação e artefatos de planejamento em pt-BR
- [Phase 07-11]: G-02 consertado pela cor do TEXTO (`--cor-brand-tx`), nunca pelo token de fundo — `core/tema.py` e `core/tests/test_tema.py` ficam intocados e a equivalência numérica com o padrão de referência sobrevive byte a byte
- [Phase 07-11]: `--cor-brand-tx` do escuro é hex plano igual a `--cor-page` do escuro (nunca `var(--cor-page)`), com asserção de igualdade lida do arquivo — `getComputedStyle` não resolve função de cor dentro de custom property
- [Phase 07-11]: Varredura estrutural do par da marca vem SEMPRE em par (negativa: sem `text-white`; positiva: com `text-brand-tx`), porque a negativa sozinha fecharia apagando a classe e deixando o botão herdar `text-ink`
- [Phase 01-01]: Reproduzida literalmente a topologia de settings/middleware/axes/CSRF da PCA, generalizada e sem menção a domínio
- [Phase 01-01]: requirements.txt restrito às 9 dependências desta fase — sem django-simple-history (Fase 2) e sem openpyxl/freezegun
- [Phase 01-02]: Kernel do app core (Usuario/UsuarioManager, axes_lockout, HtmxRedirectMiddleware, context processor, healthz, base.html com CSRF/htmx) reproduzido verbatim da PCA, sem PcaAdminConfig/login/logout (esses são CORE-03/Fase 2 e Plan 01-04)
- [Phase 01-03]: compose.yml restrito a web+db (sem backup, INF-03/Fase 4); pgdata sem external:true nesta fase (Assumption A4 — clone limpo sobe sozinho)
- [Phase 01-03]: nome de projeto compose herdado do diretório (sistema_base) isola containers/rede/volume de qualquer stack pca_* no mesmo host
- [Phase 01-04]: login_view/logout_view/shell_view reproduzidos verbatim do padrão da PCA, com validação explícita de open redirect em ?next= via url_has_allowed_host_and_scheme
- [Phase 02-01]: COR_PRIMARIA validada com re.fullmatch(#RRGGBB) no boot — ImproperlyConfigured como barreira contra CSS injection via .env (T-02-01)
- [Phase 02-01]: Tokens de marca derivados por misturar() em JS puro no tailwind.config.js — um unico hex literal de identidade (D-17), sem CSS vars (sem dark mode nesta fase)
- [Phase 02-02]: Kernel da fase entrega zero template tags customizadas — D-12 veta templatetag com ORM e a trilha vem pronta da view (item 'template tags' de CORE-04 atendido deliberadamente sem tags)
- [Phase 02-02]: Botão Sair do shell como <form hx-post> com csrf_token de fallback no-JS (padrão IN-02), não botão solto
- [Phase 02-03]: Gate do admin mantido no padrão do Django (is_active and is_staff) — decisão A1 travada por teste; gate superuser é política de domínio, não do template
- [Phase 02-03]: Auditoria padrão: HistoricalRecords() nos modelos de domínio; user model é exceção via simple_history.register() em core/admin.py (dependência circular em model swappable)
- [Phase 02-04]: hx-on::before-request da limpeza de cache no <form hx-post> (elemento emissor), não no <button> — é onde o htmx dispara before-request
- [Phase 02-04]: SW hand-rolled com cache static-v1 restrito a /static/ + fallback offline; navegações nunca gravadas em cache (HTML autenticado jamais persiste no cliente)
- [Phase ?]: O collectstatic recebe somente valores fictícios não secretos no build; o .env substitui-os em runtime.
- [Phase ?]: O preflight usa o contrato focado de collectstatic; a matriz Copier integral roda separadamente por exceder 45 segundos.
- [Phase 06-01]: Bind mount ${PGDATA_DIR:-./dados/pg} substitui o named volume pgdata — down -v não destrói mais o banco (D-73/D-76)
- [Phase 06-01]: .gitignore fora do _exclude do copier.yml; .gitignore.jinja renderiza e protege .env e /dados/ no sistema gerado (D-74)
- [Phase 06-01]: copier copy --vcs-ref=HEAD na rede de testes — com a tag v0.1.0 o Copier copiava a última tag em vez do estado atual do template
- [Phase 06-02]: Logos por arquivo fixo em core/static/img/ (logo-entidade.svg, logo-subsistema.svg) via {% static %} — trocar = substituir o arquivo, sem editar código (D-65); alt sempre via sistema_sigla (D-67)
- [Phase 06-02]: Favicon reaproveita icon-192.png no base.html (D-72) — zero arquivo novo, elimina 302 de /favicon.ico; comentário XML dos SVGs sem hífen duplo (XML proíbe -- em comentário)
- [Phase ?]: [Fase 06-03] Seção única 'Customização de marca' no README gerado absorve a antiga seção de ícones PWA — 5 pontos de marca num só lugar (D-77); PNG não é aceito como logo (contrato nome+extensão SVG fixos)
- [Phase ?]: [Fase 06-03] Migração named volume → bind mount documentada como passo manual (cp -a /de/. /para/ com stack parada) — nenhum script (D-40); one-liner usa sistema_slug_pgdata interpolado no fonte Jinja
- [Phase ?]: Guarda anti-v0.1.0 usa grep -E ancorado ('_commit: v0.1.0(,|$)'), não grep -F substring — o describe correto do HEAD ('v0.1.0-48-gHASH') contém 'v0.1.0' como substring e um -F causaria falso positivo em toda execução correta — Rule 1 - bug encontrado durante Task 2/3
- [Phase 07-02]: input.css vira a fonte física dos tokens de cor (21 claros/18 overrides escuros em hex plano); tailwind.config.js chega verbatim ao sistema gerado, sem sufixo .jinja e sem interpolação
- [Phase 07-02]: dominio.css nasce como stub _skip_if_exists: o derivado declara os próprios tokens de estado (par --cor-<estado>/-tx), nunca copiados de outro sistema
- [Phase 07-02]: bg-ink/40, shadow-xs e backdrop-blur-xs corrigidos nos templates do app exemplo: nenhuma das três gera regra no Tailwind 3.4.17 depois da migração de cores para var(--cor-*) (confirmado por build real)
- [Phase 07-03]: TDD literal na Task 1 — 6 testes de item_nav escritos e confirmados falhando (TemplateSyntaxError) antes da tag existir
- [Phase 07-03]: test_copier_update.sh ganhou --no-tags no git clone (Rule 3) — repositório real já carrega a tag v0.1.0 da release, sem a flag o clone efêmero herdava essa tag e quebrava a criação da tag própria do ensaio
- [Phase 07-03]: exigir_sem_exemplo() prova sobrevivência de _nav_dominio.html após update, não mais ausência de exemplo: nele — com _skip_if_exists o arquivo é do derivado e pode legitimamente conter exemplo: sem ser ressurreição do app
- [Phase 07-04]: core/tema.py deriva a família de marca inteira (colorsys/misturar) em Python no boot, espelhando core/admin_site.py; COR_PAGE_CLARO/COR_PAGE_ESCURO amarrados a input.css por teste
- [Phase 07-04]: test_07_cor_runtime.sh captura a porta do banco de ensaio uma única vez e nunca redescobre via ensaio_django.sh porta/subir após um up -d web — garantir_banco() ali faz um único curl sem retry e detona recriação completa se o serviço ainda está subindo
- [Phase 07-05]: Controle de tema entra dentro do wrapper mt-auto existente (flex-col), não como irmão solto acima dele — evita vão visível por margin-top:auto dividido entre dois irmãos
- [Phase 07-05]: RE_PREFIXO_HERDADO montado por concatenação em vez de literal — o teste de neutralidade é copiado verbatim para todo sistema gerado e não pode conter o prefixo por extenso
- [Phase 07-06]: paleta_graficos servido por json_script, derivado de core.tema.familia_marca(COR_PRIMARIA) — rampa sequencial (seq-600/seq-450/seq-300/brand-tint), nos dois temas, mesma função que alimenta o <style> de base.html
- [Phase 07-06]: chrome de gráfico (eixo/grade/tooltip/borda) lido de getComputedStyle em runtime via lerVarCss() — montarGraficos() faz dispose()+init() e é chamada de novo no evento tema:alterado, reconstruindo os gráficos sem reload de página
- [Phase 07-06]: json_script:"paleta-graficos" acrescentado a dashboard.html já na Task 1 (TDD), não só na Task 2 — o comportamento 6/6 exigia o HTML renderizado desde a GREEN da própria Task 1
- [Phase ?]: [Phase 07-07]: Regex de leitura de fontSize (herdado de 07-02) corrigido para casar chaves entre aspas ('"2xl":') — bug pré-existente revelado pela prova negativa exigida pela Task 2, sem o qual o gate da régua tipográfica passaria em falso positivo silencioso
- [Phase ?]: [Phase 07-07]: Botão adota text-base (13px), não text-sm — paridade com o vocabulário .btn (text-[13px]) do input.css; aplicado a 6 sítios (Gerenciar itens, Novo item, Cancelar/Salvar item, Cancelar/Sim-excluir, 3 botões de tema do shell)
- [Phase ?]: [Phase 07-07]: Título de seção (h2) que ficava do mesmo tamanho do corpo em 13px promovido a text-lg (16px) — aplicado aos 2 títulos de gráfico do dashboard e aos 2 títulos de modal
- [Phase 07-09]: core/tests/contraste.py é a fonte única da fórmula WCAG e vive DENTRO do sistema gerado — .template-tests está em _exclude do copier.yml, um helper lá deixaria todo derivado sem a guarda de contraste
- [Phase 07-09]: Teto tipográfico vira propriedade da build: fontSize sai de theme.extend (que SOMA ao default, mantendo text-2xl…text-9xl gerando regra) para theme (que SUBSTITUI) — provado com Tailwind real, text-2xl passa de 1 regra para 0
- [Phase 07-09]: TEXT_CLASS_RE troca o \b final por lookahead (?![\w-]): além de ressuscitar o ramo de valor arbitrário do G-05, passa a recusar text-ink-2, que o \b antigo casava indevidamente como text-ink
- [Phase ?]: [Phase 07-10]: excecoes entra no FIM da assinatura de item_nav (posicional-compatível) e a correspondência exata nunca é anulada por ela — exato vence prefixo, e a exceção é declarada no sítio da chamada porque uma inclusion_tag não enxerga os irmãos
- [Phase ?]: [Phase 07-10]: nav_dominio (simple_tag tolerante) substitui o include literal em _nav.html — o arquivo é do derivado, apagá-lo é estado previsto e o Django não tem ignore missing; degrada para menu vazio, nunca 500 (WR-10)
- [Phase ?]: [Phase 07-10]: a topologia pai/filho da nav é exercitada na suíte do core contra um urlconf sintético do próprio módulo (override_settings ROOT_URLCONF=__name__) — a prova com o stub REAL vive em apps/exemplo/tests/test_nav_ativo.py, onde as rotas exemplo:* existem por construção
- [Phase 07-12]: Piso de contraste de CROMO fixado em 1,25:1 (não 3:1 nem 4,5:1) — grade e separação de fatia não carregam dado nem texto; um gate em > 1,00 passaria com 1,001:1, e 1,25 reprova --cor-surface-2 no claro (1,09:1), que é a regressão a barrar
- [Phase 07-12]: esc() aplicada a TODA interpolação dos formatters do ECharts, inclusive as numéricas — regra com exceções obriga o derivado a reclassificar campo a campo ao adaptar o dashboard, e é aí que o escape some
- [Phase 07-12]: corCard declarada DENTRO de montarGraficos(), não no escopo do DOMContentLoaded — é o que faz o ternário de tema ser reavaliado no evento tema:alterado; fora da função o conserto valeria só para o tema em que a página carregou
- [Phase ?]: [Phase 07-13]: A rampa sequencial estende pelo lado FORTE (seq-750 = misturar(cor,0,0.35) no claro, com_hsl(cor,1.00,0.860) no escuro) — estender na direção do branco daria ~1,4:1 contra um card quase branco e trocaria um invisível por outro
- [Phase ?]: [Phase 07-13]: core/tema.py alterado por ACRÉSCIMO PURO (20 linhas, 0 remoções) — os comentários herdados com as contagens antigas ficaram intactos e a atualização entrou como linha NOVA, porque reescrevê-los apagaria a evidência de que nenhum coeficiente do padrão foi tocado
- [Phase ?]: [Phase 07-13]: Piso de fatia de DADO em 1,5:1 (não 3:1) — o degrau seq-300 herdado vive em 1,95:1 no claro e exigir 3:1 obrigaria a redesenhar a rampa do padrão de referência para consertar um defeito que não está nela
- [Phase ?]: [Phase 07-13]: seq-750 fixado FORA do dict 'esperado' de test_tema.py — aquele dict é o conjunto de valores MEDIDOS no padrão, cuja rampa tem três degraus; o quarto é extensão deste template, não herança
- [Phase ?]: [Phase 07-13]: O brand-tint proibido pelo gate é recalculado de settings.COR_PRIMARIA, nunca lido do input.css — o token depende da marca e num derivado com outra cor a comparação passaria por engano, deixando o defeito sobreviver ao próprio teste

### Pending Todos

None yet.

### Blockers/Concerns

- Agentes GSD não instalados (`npx get-shit-done-cc@latest --global`) — pesquisa e roadmap foram gerados inline; instalar antes de `/gsd:plan-phase` para habilitar researcher/checker/verifier

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260818-2og | Auditoria integral de negócio, produto, operação e escalabilidade; sobrescrever REVIEW.md sem alterar código-fonte | 2026-08-18 | docs-only | [260818-2og-auditar-integralmente-o-sistema-base-com](./quick/260818-2og-auditar-integralmente-o-sistema-base-com/) |
| 260818-n9k | Corrigir vazamento de comentários `{# #}` de template Django exibidos como texto (login e topo da página); causa raiz + teste de regressão | 2026-08-18 | ba86084 | [260818-n9k-corrija-o-vazamento-de-coment-rios-de-te](./quick/260818-n9k-corrija-o-vazamento-de-coment-rios-de-te/) |
| 260818-qc7 | Documentar padrão nginx conf.d + certbot --nginx na seção de publicação do README | 2026-08-18 | 8a52155 | [260818-qc7-documentar-padr-o-nginx-conf-d-certbot-n](./quick/260818-qc7-documentar-padr-o-nginx-conf-d-certbot-n/) |
| 260818-qoy | Adicionar seção 'Os três ciclos de trabalho' ao README do template | 2026-08-18 | f910787 | [260818-qoy-adicionar-se-o-os-tr-s-ciclos-de-trabalh](./quick/260818-qoy-adicionar-se-o-os-tr-s-ciclos-de-trabalh/) |
| 260818-qwd | Documentar criação da tag de release + seção Resumo executável (exemplo financeiro:12010) no README | 2026-08-18 | 44ae507 | [260818-qwd-documentar-cria-o-da-tag-de-release-e-re](./quick/260818-qwd-documentar-cria-o-da-tag-de-release-e-re/) |

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Categoria | Item | Situação | Diferido em |
|-----------|------|----------|-------------|
| uat | Fase 03 — inspeção humana direta de foco no primeiro campo do modal, resize da janela e drill-down por clique no dashboard | Fechado por cobertura (testes de 422/HX-Trigger + gate visual da 07-08), por decisão do operador; os 3 comportamentos seguem sem inspeção visual direta | 2026-08-24 |
| release | Publicar a tag `v0.2.0` | **Já publicada** — confirmado por `git ls-remote --tags origin` em 2026-08-24: objeto `6c7bc99` sobre `01ced83`, idêntico ao local. O registro do plano 07-14 ("não publicada") está desatualizado | — |
| ferramenta | `gsd-sdk query audit-open` reporta os 5 quick tasks como incompletos: lê `.planning/quick/<dir>/SUMMARY.md`, mas o `/gsd-quick` grava `<dir>/<id>-SUMMARY.md` | Bug do GSD, não do projeto — os 5 têm PLAN, SUMMARY e commit | 2026-08-24 |

## Session Continuity

Last session: 2026-08-24
Stopped at: Marco v0.2.0 fechado e arquivado
Resume file: None

## Operator Next Steps

- Decidir sobre publicar os 3 commits locais de `.planning/` (`git push origin main`) — não afetam nenhum sistema gerado, já que o `copier.yml` exclui `.planning`
- A release já está no ar: a `v0.2.0` está publicada em `origin` sobre `01ced83`
- Abrir o próximo escopo com `/gsd-new-milestone`
