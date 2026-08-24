# Retrospectiva do Projeto

*Documento vivo, atualizado a cada marco. As lições alimentam o planejamento seguinte.*

## Marco: v0.2.0 — Design system herdado do PCA

**Fechado:** 2026-08-24
**Fases:** 7 | **Planos:** 38 | **Tasks:** 77 | **Commits:** 282
**Janela:** 2026-08-17 → 2026-08-24

### O que foi construído

- Template Copier que gera um sistema Django 5.2 completo e autocontido: auth por
  e-mail, shell visual, admin isolado, PWA, auditoria, CRUD e dashboard de
  exemplo descartáveis, Docker Compose com PostgreSQL 17, backup com retenção,
  vhost TLS e runbook de migração.
- O design system do Sistema CFC inteiro nascendo com todo sistema gerado —
  tokens em variáveis CSS, tema escuro, três degraus de elevação, régua
  tipográfica com teto, paleta de gráfico derivada da marca em runtime.
- O ponto de extensão da navegação que eliminou o pior conflito de upstream da
  família de sistemas.

### O que funcionou

- **Provar dentro de uma cópia gerada, não no template.** `ensaio_django.sh` e o
  tracer de nascimento rodam a suíte dentro de uma cópia Copier real. Foi isso
  que pegou classes que o Tailwind deixava de gerar depois da migração para
  `var()` (`bg-ink/40`, `shadow-xs`, `backdrop-blur-xs`) — nada disso apareceria
  testando o template.
- **Guardas executáveis em vez de convenção escrita.** O teste que tira sha256
  de toda a subárvore `core/` e exige que o único caminho divergente seja o
  arquivo do derivado é mais forte que qualquer regra no README, e não envelhece.
- **Derivar em runtime, não em build-time.** Mover a família de marca do
  `tailwind.config.js.jinja` para `core/tema.py` fez `tailwind.config.js` chegar
  verbatim ao derivado: um arquivo a menos para conflitar no `copier update`, e
  trocar a cor virou editar o `.env` e recriar o `web`.
- **Herdar da fonte, não do irmão.** Decidir que o template herda direto do PCA
  em vez do DividaAtiva evitou implementar o mesmo sistema duas vezes e conflitar
  com o próprio trabalho do derivado no update seguinte.

### O que foi ineficiente

- **A tag ficou para trás por 37 commits.** O Copier lê a última tag, não o HEAD.
  A Fase 6 inteira — marca, logos, bind mount — nunca chegou a nenhum derivado
  porque ninguém criou uma tag depois dela. A Fase 7 teve que carregar essa
  pendência de release junto com o próprio escopo.
- **Uma tag foi criada sobre um commit com bloqueadores.** A `v0.2.0` original
  apontava para `367dd9a`, que ainda continha os quatro defeitos que a revisão de
  código encontrou. Precisou ser apagada e recriada sobre `01ced83`. Só não virou
  incidente porque a recriação aconteceu antes da publicação — a tag que foi ao
  ar (`6c7bc99` sobre `01ced83`) é a correta.
- **Os critérios de fase testavam estrutura declarada, não resultado
  renderizado.** "O token existe", "o ponto de extensão existe" — e foi nessa
  fresta que passaram cinco defeitos de contraste e de estado ativo: texto branco
  a 2,56:1 sobre a marca no escuro, a quarta fatia do donut a 1,11:1, a grade do
  eixo matematicamente idêntica ao fundo do card, dois itens de menu ativos ao
  mesmo tempo. Foram seis planos de gap closure (07-09 a 07-14) para fechar o que
  a verificação original tinha dado por verificado.
- **Datas erradas sobreviveram no ROADMAP até o fecho** (`2006-08-18` em cinco
  linhas) e seis linhas de rastreabilidade ficaram `Pending` por seis dias depois
  da fase correspondente ter fechado verificada.

### Padrões estabelecidos

- **O par fundo+texto é a unidade de cor, nunca o fundo sozinho.** Consertar
  contraste pela cor do texto (`--cor-brand-tx`) deixa o token de fundo e a
  equivalência numérica com o padrão de referência intactos.
- **Toda varredura estrutural vem em par: negativa e positiva.** Só a negativa
  ("sem `text-white`") fecharia apagando a classe; a positiva ("com
  `text-brand-tx`") exige o substituto certo.
- **Piso de contraste por função, não um número único.** Cromo (grade, separação
  de fatia) a 1,25:1; fatia que carrega dado a 1,5:1. Um piso único ou passaria
  com 1,001:1 ou obrigaria a redesenhar a rampa do padrão de referência.
- **Extensão do padrão herdado entra por acréscimo puro,** fora do dicionário de
  valores medidos — o que é herança e o que é extensão deste template têm que
  continuar distinguíveis no código.
- **Um teste copiado verbatim para todo sistema gerado não pode conter o nome do
  sistema de origem** — daí `RE_PREFIXO_HERDADO` montado por concatenação.

### Lições

1. **Criar a tag faz parte de fechar a fase, não do fecho do marco.** Uma fase que
   entrega valor ao derivado e não vira tag não entregou nada. Vale considerar um
   gate: fase não fecha sem decisão explícita de tag.
2. **Tag só depois da revisão de código, nunca antes.** A ordem correta é
   verificar → revisar → consertar → taguear. A inversão custou uma tag recriada.
3. **Critério de aceite que descreve estrutura precisa de um par que descreve
   resultado.** "O token existe" e "o token rende contraste ≥ X:1 contra o fundo
   em que é usado" são afirmações diferentes, e só a segunda é o que o usuário vê.
4. **Metadado de planejamento apodrece em silêncio.** Rastreabilidade, datas e
   status de verificação não têm teste que os pegue. Vale rodar
   `gsd-sdk query audit-open` no fim de cada fase, não só no fecho do marco.

### Observações de custo

Não instrumentado neste marco — não há registro de mix de modelo nem contagem de
sessões. Sinais indiretos, das métricas por plano em `STATE.md`: 05-01 levou
196 min (o tracer de nascimento ponta a ponta) e 07-06 levou 70 min (paleta de
gráfico servida pelo servidor); a mediana dos demais fica entre 4 e 25 min. Os
planos caros são os que sobem Docker e esperam banco.

---

## Tendências entre marcos

### Evolução do processo

| Marco | Fases | Planos | Rodadas de gap closure | Observação |
|-------|-------|--------|------------------------|------------|
| v0.2.0 | 7 | 38 | 1 (6 planos, Fase 7) | Primeiro marco; revisão de código posterior à verificação achou 5 defeitos que os critérios estruturais não pegavam |

*Preencher a partir do próximo marco.*
