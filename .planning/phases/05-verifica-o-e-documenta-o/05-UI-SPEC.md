---
phase: 5
slug: verifica-o-e-documenta-o
status: draft
shadcn_initialized: false
preset: none
created: 2026-08-18
---

# Phase 5 — Verificação e Documentação: UI Design Contract

> Contrato visual e de interação para a prova de nascimento do template. A Fase 5 não cria uma nova interface: ela preserva e verifica as telas já entregues pelo `core` e pelo `apps/exemplo` na cópia gerada com `incluir_app_exemplo=true`.

---

## Escopo visual da fase

- Não adicionar telas, componentes, bibliotecas de UI, fontes, ícones ou tokens para satisfazer QA-01, QA-02 ou DOC-01.
- O README é um runbook Markdown; não é uma nova superfície web. Deve orientar a abertura das telas existentes, sem duplicar ou inventar fluxos de produto.
- O ensaio automatizado prova renderização/comportamento e o alcance HTTP. A inspeção manual breve no navegador é a evidência complementar de que login, shell, CRUD e dashboard estão navegáveis na cópia efêmera; ela não introduz automação de navegador nesta fase. [Fonte: `05-RESEARCH.md`, alternativa adotada.]
- O executor não pode alterar a aparência das telas existentes apenas para fazer o ensaio passar. Uma regressão visual encontrada durante a inspeção deve ser registrada e tratada em escopo próprio, salvo se for causada diretamente pelo artefato desta fase.
- Hierarquia primária a preservar: no login, campos de credencial e CTA `Entrar` vêm antes de texto auxiliar; no CRUD, título/lista e CTA `Novo item` são o foco acima dos filtros e metadados; no dashboard, KPIs aparecem antes dos gráficos.

## Design System

| Propriedade | Valor |
|-------------|-------|
| Tool | none — templates Django renderizados no servidor |
| Preset | não aplicável |
| Biblioteca de componentes | nenhuma; partials Django e classes Tailwind existentes |
| Biblioteca de ícones | SVGs inline locais, `stroke="currentColor"`, espessura 2 |
| Fonte | `font-sans` do Tailwind (pilha system-ui); `font-mono` apenas para métricas/valores |
| Interação | HTML semântico + HTMX + Alpine já locais; navegação principal é full-page load |

**Fonte e preservação:** `tailwind.config.js.jinja`, `core/templates/base.html`, `core/templates/core/shell.html` e `03-UI-SPEC.md`. Não há `components.json`, e o projeto é Django, não React/Next/Vite; portanto o gate de inicialização do shadcn não se aplica.

---

## Spacing Scale

Valores declarados — todos múltiplos de 4 — a preservar na cópia gerada:

| Token | Valor | Uso nesta verificação |
|-------|-------|-----------------------|
| xs | 4px | lacunas de ícone e metadados (`gap-1`, `mt-1`) |
| sm | 8px | controles compactos e paginação (`p-2`, `gap-2`) |
| md | 16px | filtros, células, cards e espaçamento padrão (`p-4`, `gap-4`) |
| lg | 24px | cabeçalhos e conteúdo de modal/card (`p-6`, `gap-6`) |
| xl | 32px | vazio de coleção e respiro de blocos (`p-8`) |
| 2xl | 48px | separação maior reservada para páginas (`p-12`) |
| 3xl | 64px | separação de página reservada (`p-16`) |

**Exceções existentes a preservar:** alvo de toque móvel de 44px (`h-11 w-11`); cabeçalho móvel de 56px (`h-14`); aside desktop fixa de 232px; indicador ativo de navegação de 2px. Nenhuma exceção nova nesta fase.

---

## Typography

Usar somente os quatro tamanhos e os dois pesos já contratados para as telas verificadas. Não criar novo uso tipográfico no README para substituir essa hierarquia.

| Papel | Tamanho | Peso | Line height | Uso |
|-------|---------|------|-------------|-----|
| Micro/caption | 12px | 400 ou 600 | 1.33 | breadcrumbs, metadados, cabeçalhos de tabela, mensagens auxiliares |
| Label/controle | 14px | 400 ou 600 | 1.43 | filtros, campos, botões e células de tabela |
| Corpo | 16px | 400 ou 600 | 1.50 | texto de interface, navegação e conteúdo de modal |
| Título/destaque | 24px | 600 | 1.20 | títulos das telas de exemplo e métricas KPI |

Pesos permitidos: regular 400 e semibold 600. A classe legada `text-xl` no cabeçalho padrão do shell permanece inalterada por compatibilidade e está fora desta escala tipográfica ativa; não a adotar em novos artefatos da Fase 5.

---

## Color

| Papel | Valor | Uso |
|-------|-------|-----|
| Dominante (60%) | `page` `#f9f9f7` | fundo de página, canvas e aside |
| Secundária (30%) | `surface` `#fcfcfb` | cards, tabela, formulários, modal e cabeçalho móvel |
| Secundária elevada | `surface-2` `#f3f2ef` | hover, cabeçalhos de tabela, rodapés e fundo de estado neutro |
| Accent (10%) | `brand` — `cor_primaria` Copier, default `#1e40af` | somente os elementos listados abaixo |
| Destrutiva | vermelho `#b91c1c` (`red-700`) | confirmar exclusão, validação de formulário e erro de autenticação |

Accent reservado exclusivamente para: CTA primária `Novo item`; item/página ativa; foco de controles de filtro; página ativa na paginação; barra e setor de gráfico ECharts. Não usar a cor de marca em fundos de tabela, bordas genéricas, botões secundários nem instruções do README.

---

## Copywriting Contract

Esta fase não introduz nova cópia de produto. O roteiro de verificação deve preservar e confirmar as strings abaixo — não as renomear para coincidir com comandos do ensaio.

| Elemento | Copy |
|----------|------|
| CTA primária de entrada | `Entrar` — autentica o administrador de ensaio e leva ao shell |
| CTA primária do CRUD | `Novo item` — abre o modal de criação existente |
| Vazio de coleção — título | `Nenhum item encontrado` |
| Vazio de coleção — corpo | `Não encontramos nenhum registro com os filtros aplicados. Tente ajustar os termos de busca ou filtros selecionados.` |
| Recuperação do vazio filtrado | `Limpar filtros` |
| Erro de login | `E-mail ou senha inválidos.` |
| Erro de bloqueio | `Muitas tentativas de acesso. Por segurança, novas tentativas estão bloqueadas temporariamente — aguarde e tente novamente em alguns minutos.` |
| Erro de formulário | mensagem inline do campo, mantendo o erro retornado pelo Django; não substituir por toast genérico |
| Confirmação destrutiva | `Excluir Item`: `Tem certeza que deseja excluir o item "{item.titulo}"?` + `Esta ação não pode ser desfeita.`; CTAs `Sim, excluir item` e `Voltar sem excluir` |

---

## Interação e evidência visual obrigatória

O novo ensaio de nascimento deve manter o navegador fora da automação. Após ele passar, uma inspeção manual na cópia temporária deve confirmar, sem editar código:

1. `GET /login/` mostra campos de e-mail e senha e o CTA `Entrar`; credencial inválida mantém a tela e expõe o erro de login.
2. Após autenticar, a raiz mostra o shell; em desktop a aside continua visível mesmo sem depender de Alpine. Em viewport móvel, o botão `Abrir menu` abre a gaveta, o overlay a fecha e `Esc`/`Fechar menu` a fecham.
3. O menu leva a `Itens (CRUD)` e `Dashboard`; breadcrumbs permanecem legíveis. O logout é um `<form method="post">`, não link/GET.
4. A lista de itens permanece responsiva: tabela larga rola horizontalmente, descrição longa trunca em vez de deslocar ações, e lista sem resultado mostra o estado vazio acima. Com dados, ordenação, filtros, paginação e modais existentes continuam navegáveis.
5. O dashboard abre sem erro tanto com banco vazio quanto com dados de ensaio; cards e dois gráficos são visíveis, e clicar em barra/setor mantém o redirecionamento para a lista filtrada.

Esses passos são um checkpoint visual complementar; a prova regressiva mandatória continua sendo `manage.py test core apps.exemplo --noinput` dentro da cópia gerada. [Fonte: `05-RESEARCH.md`, padrões 1 e 2; `core/tests/`; `apps/.../tests/`.]

---

## UI Considerations

Prova determinística pós-checker: **32/32 considerações resolvidas — 17 covered, 15 backstop, 0 unresolved**. Cada item abaixo corresponde a uma combinação superfície/categoria produzida por `ui-consideration-probe.cjs`; nenhuma consideração foi descartada silenciosamente.

### Covered — critérios explícitos

- `[login-form/empty]` `GET /login/` renderiza campos de e-mail e senha vazios e o CTA `Entrar`, sem dados de sessão expostos.
- `[login-form/error]` Credencial inválida mantém a tela de login e exibe `E-mail ou senha inválidos.`; bloqueio temporário exibe a mensagem contratada.
- `[responsive-shell-navigation/overflow]` Breadcrumb usa `flex-wrap`, aside mantém 232px no desktop e a gaveta móvel não amplia o viewport.
- `[responsive-shell-navigation/long-text]` Identidade usa `min-w-0`/`truncate`; breadcrumbs quebram linha sem ocultar controles.
- `[crud-list/empty]` Zero resultados exibe `Nenhum item encontrado`, o corpo explicativo e `Limpar filtros`.
- `[crud-list/populated]` Com dados de ensaio, título, `Novo item`, filtros, tabela, ordenação, ações e paginação permanecem navegáveis.
- `[crud-list/partial]` Prazo ou descrição opcionais ausentes usam `—` sem alterar alinhamento nem ações da linha.
- `[crud-list/overflow]` Tabela larga usa `overflow-x-auto`; ações permanecem alcançáveis e breadcrumb usa `flex-wrap`.
- `[crud-list/zero-one-many]` Zero itens mostra o vazio; um item conserva a tabela; muitos itens acionam paginação e quantidade exibida.
- `[crud-list/long-text]` Descrição e identidade truncam; título e cópias auxiliares quebram linha sem deslocar ações.
- `[crud-modal-form/empty]` `Novo item` abre formulário sem dados persistidos e com CTAs de criação/fechamento visíveis.
- `[crud-modal-form/error]` Resposta 422 mantém o modal aberto e apresenta erros inline no campo correspondente.
- `[crud-modal-form/partial]` Campos opcionais podem ficar vazios; obrigatórios ausentes recebem erro sem descartar valores válidos.
- `[crud-modal-form/long-text]` Título interpolado é escapado pelo Django e quebra linha sem sobrepor os CTAs destrutivos.
- `[dashboard/empty]` Banco vazio retorna dashboard sem erro, com KPIs e contêineres de gráfico em estado neutro seguro.
- `[dashboard/populated]` Com dados de ensaio, KPIs antecedem dois gráficos ECharts e barras/setores levam à lista filtrada.
- `[dashboard/zero-one-many]` Zero registros preserva estado seguro; um produz métricas válidas; muitos preservam agregação e interação.

### Backstops — exigem evidência visual/held-out

- `{ statement: "[login-form/loading] Durante o submit síncrono, o formulário permanece visível até a navegação completar; nenhum spinner ou skeleton novo é introduzido.", verification: backstop }`
- `{ statement: "[login-form/partial] Envio com um campo preenchido mantém ambos os controles e associa validação ao campo ausente sem apagar o valor informado.", verification: backstop }`
- `{ statement: "[login-form/overflow] Em viewport móvel, o formulário fica dentro do canvas sem rolagem horizontal nem recorte do CTA.", verification: backstop }`
- `{ statement: "[login-form/long-text] Mensagens longas de bloqueio quebram linha sem sobrepor campos ou CTA.", verification: backstop }`
- `{ statement: "[responsive-shell-navigation/loading] Navegação full-page mantém o shell anterior até a resposta; nenhum estado assíncrono customizado é criado.", verification: backstop }`
- `{ statement: "[responsive-shell-navigation/error] Falha de destino não deixa gaveta/overlay presos e permite retornar à última página válida.", verification: backstop }`
- `{ statement: "[crud-list/loading] Durante swaps HTMX, a lista preserva geometria e não duplica controles; nenhum spinner novo é exigido.", verification: backstop }`
- `{ statement: "[crud-list/error] Falha HTMX não troca a tabela por vazio silencioso e mantém recuperação por nova tentativa ou recarga.", verification: backstop }`
- `{ statement: "[crud-modal-form/loading] Durante submit HTMX, o modal permanece estável, sem formulário duplicado ou confirmação destrutiva acidental.", verification: backstop }`
- `{ statement: "[crud-modal-form/overflow] Em viewport móvel ou com muitos erros, o modal permanece rolável e ambos os CTAs alcançáveis.", verification: backstop }`
- `{ statement: "[dashboard/loading] Enquanto ECharts inicializa, contêineres mantêm dimensões e não cobrem KPIs nem navegação.", verification: backstop }`
- `{ statement: "[dashboard/error] Falha de um gráfico não impede acesso a KPIs, navegação ou lista filtrada.", verification: backstop }`
- `{ statement: "[dashboard/partial] Com apenas parte das séries, KPIs e gráfico disponível continuam legíveis sem inventar valores.", verification: backstop }`
- `{ statement: "[dashboard/overflow] Em viewport estreito, cards/gráficos refluem sem rolagem horizontal de página nem corte de rótulos críticos.", verification: backstop }`
- `{ statement: "[dashboard/long-text] Rótulos longos truncam ou quebram linha sem sobrepor legenda, KPIs ou alvos clicáveis.", verification: backstop }`

---

## Registry Safety

| Registry | Blocks usados | Safety Gate |
|----------|---------------|-------------|
| shadcn official | nenhum | não aplicável — stack Django sem `components.json` |
| Terceiros | nenhum | não aplicável; nenhuma nova dependência ou registry nesta fase |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS com uma recomendação não bloqueante sobre `Entrar`
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** verified — `gsd-ui-checker`, 2026-08-18
