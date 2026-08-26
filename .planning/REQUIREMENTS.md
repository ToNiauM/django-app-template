# Requisitos — Marco v0.3.0: Guia de construção de sistemas

**Definido:** 2026-08-25
**Fonte:** conversa de abertura do marco + pesquisa em `.planning/research/`
**Marco anterior:** v0.2.0 (36/36 requisitos fechados; arquivo em `.planning/milestones/v0.2.0-REQUIREMENTS.md`)

O guia ensina quem gerou um sistema pelo template a construir seus próprios apps
de domínio — em linguagem simples e acessível, com um exemplo completo (diárias
e passagens) e dois resumidos (orçamento, controle de materiais). Todo código
mostrado é real e provado numa cópia gerada.

## Requisitos v0.3.0

### Guia — exemplo completo (GUIA)

- [ ] **GUIA-01**: Leitor cria o app de diárias em `apps/` seguindo o guia (modelo, migração, admin) e vê seus registros no admin
- [ ] **GUIA-02**: Leitor constrói a listagem paginada com filtros copiando o padrão do app exemplo e a vê funcionando na tela
- [ ] **GUIA-03**: Leitor cria e edita registros pelo formulário em modal (padrão HTMX 422 + `HX-Trigger`) seguindo o guia
- [ ] **GUIA-04**: Leitor põe o item do seu sistema no menu criando `_nav_dominio.html` com `{% item_nav %}`, com estado ativo correto
- [ ] **GUIA-05**: Leitor monta um painel com gráfico ECharts usando a paleta da marca, com dados agregados via ORM
- [ ] **GUIA-06**: Todo capítulo termina com um resultado visível na tela e traz uma seção "deu errado?" com os erros reais do percurso
- [ ] **GUIA-07**: Capítulo de abertura diz para quem é o guia, o que é preciso ter pronto, como ler, e que `docs/guia/` pertence ao núcleo (não editar)
- [ ] **GUIA-08**: Mapa de receitas "quero X → copie Y do app exemplo" em uma página
- [ ] **GUIA-09**: Capítulo final orienta quando remover o app exemplo (link para o protocolo), como crescer o sistema e onde aprender mais Django

### Exemplos resumidos (EX)

- [ ] **EX-01**: Sistema de orçamento resumido — entidades, campos, telas e o que aproveitar do exemplo completo
- [ ] **EX-02**: Sistema de controle de materiais resumido — mesmo formato

### Linguagem acessível (LNG)

- [ ] **LNG-01**: Glossário em linguagem simples no capítulo de abertura
- [ ] **LNG-02**: Todo termo técnico é traduzido em uma frase na primeira ocorrência
- [ ] **LNG-03**: Revisão editorial de acessibilidade com persona explícita ("sabe planilha, não sabe Django") aprovada como gate

### Prova executável (PRV)

- [x] **PRV-01**: O código do exemplo completo (fixture em `.template-tests/fixtures/`) instala numa cópia Copier real e passa: migração, testes do app e smoke das telas
- [ ] **PRV-02**: Toda cerca de código do guia é byte-idêntica ao arquivo correspondente do fixture — provado por teste
- [x] **PRV-03**: Teste negativo prova que nenhum código de domínio (`apps/diarias`) chega ao template nem à cópia gerada

### Distribuição e release (DST / REL)

- [ ] **DST-01**: `docs/guia/` chega ao sistema gerado via `copier copy`
- [ ] **DST-02**: `copier update` v0.2.0 → v0.3.0 sai limpo cobrindo `docs/` — exit 0, zero marcador de conflito, zero `.rej`
- [ ] **DST-03**: `README.md` e `README.md.jinja` linkam o guia numa seção curta, sem duplicar conteúdo
- [ ] **REL-02**: Tag `v0.3.0` anotada e publicada em `origin` após verificação e revisão de código (ordem: verificar → revisar → consertar → taguear)

## Requisitos futuros (adiados)

- Mapa de receitas expandido com as dúvidas reais do primeiro derivado a usar o guia (DividaAtiva/Orçamento) — gatilho: primeiro `copier update` de derivado com o guia
- Capítulo de relatórios/exportação — gatilho: o primeiro uso real pedir

## Fora de escopo

- **Ensinar Django do zero** (request/response, o que é MVC…) — duplicaria a documentação oficial e envelhece; o guia ensina o método do template e linka o resto
- **Repetir conteúdo de operação do README** (backup, TLS, deploy, nascimento) — duas fontes divergem; toda sobreposição vira link
- **Screenshots de telas** — apodrecem a cada mudança visual, pesam o repo e quebram entre temas; resultados são descritos em texto
- **Entregar o app de diárias como unidade opcional do Copier** — violaria o "template agnóstico de domínio" e criaria novo acoplamento no `copier update`; o código vive só no texto do guia e no fixture de teste
- **Gerador de site de docs (MkDocs/Sphinx)** — passo de build para texto viola a invariante de portabilidade

## Rastreabilidade

| REQ-ID | Fase | Status |
|--------|------|--------|
| GUIA-01 | Fase 9 | Mapped |
| GUIA-02 | Fase 9 | Mapped |
| GUIA-03 | Fase 9 | Mapped |
| GUIA-04 | Fase 9 | Mapped |
| GUIA-05 | Fase 9 | Mapped |
| GUIA-06 | Fase 9 | Mapped |
| GUIA-07 | Fase 9 | Mapped |
| GUIA-08 | Fase 9 | Mapped |
| GUIA-09 | Fase 9 | Mapped |
| EX-01 | Fase 9 | Mapped |
| EX-02 | Fase 9 | Mapped |
| LNG-01 | Fase 9 | Mapped |
| LNG-02 | Fase 9 | Mapped |
| LNG-03 | Fase 9 | Mapped |
| PRV-01 | Fase 8 | Mapped |
| PRV-02 | Fase 9 | Mapped |
| PRV-03 | Fase 8 | Mapped |
| DST-01 | Fase 10 | Mapped |
| DST-02 | Fase 10 | Mapped |
| DST-03 | Fase 10 | Mapped |
| REL-02 | Fase 10 | Mapped |
