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

Pesos permitidos: regular 400 e semibold 600. A ocorrência legada de `text-xl` (20px) no cabeçalho padrão do shell é uma exceção herdada, congelada para compatibilidade; não adotar 20px em novos artefatos da Fase 5.

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
| Confirmação destrutiva | `Excluir Item`: `Tem certeza que deseja excluir o item "{item.titulo}"?` + `Esta ação não pode ser desfeita.`; CTAs `Sim, excluir item` e `Cancelar` |

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

Aplicáveis resolvidos: **7 covered, 1 dismissed, 0 unresolved**. A fase não acrescenta uma superfície assíncrona ou um estado novo; as linhas abaixo definem o que a prova deve preservar nas telas existentes.

| Categoria | Elemento(s) | Status | Resolução / razão |
|-----------|-------------|--------|-------------------|
| empty | coleção CRUD; dashboard | ✅ covered | Lista sem objetos mostra a cópia de vazio contratada; dashboard com banco vazio responde com segurança. A inspeção manual e os testes existentes cobrem ambos. |
| loading | login, filtros HTMX, modais | — dismissed | Nenhum indicador de carregamento é introduzido nesta fase; o contrato é preservar o swap HTMX existente, sem criar spinner ou estado novo fora de escopo. |
| error | login e formulário modal | ✅ covered | Login inválido mantém a página/fragmento e exibe a cópia contratada; validação 422 mantém os erros de campo no modal. |
| populated | shell, CRUD e dashboard | ✅ covered | Após criar o administrador e os dados de ensaio, shell, tabela, cards e gráficos renderizam navegáveis na cópia derivada. |
| partial | linha de tabela com prazo/descrição ausente | ✅ covered | Campo opcional ausente mantém `—`; descrição ausente não cria bloco vazio nem altera o alinhamento. |
| overflow | tabela, breadcrumb, nav e descrição | ✅ covered | Tabela usa `overflow-x-auto`; textos longos da descrição e identidade aplicam truncamento; breadcrumb usa `flex-wrap`. |
| zero-one-many | coleção paginada | ✅ covered | Zero apresenta vazio; um item mantém a tabela; muitos itens preservam paginação e quantidade exibida. |
| long-text | título do item, descrição e identidade | ✅ covered | Ações não saem da área visível; descrição usa `truncate`, identidade do shell usa `min-w-0`/`truncate` e o texto de confirmação interpola título com escape Django. |

---

## Registry Safety

| Registry | Blocks usados | Safety Gate |
|----------|---------------|-------------|
| shadcn official | nenhum | não aplicável — stack Django sem `components.json` |
| Terceiros | nenhum | não aplicável; nenhuma nova dependência ou registry nesta fase |

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
