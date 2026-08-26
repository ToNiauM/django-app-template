# Pesquisa de Features — Guia de construção de sistemas (v0.3.0)

**Domínio:** guia didático "do template ao sistema real" (documentação de onboarding para Django + o método do template)
**Pesquisado:** 2026-08-25
**Confiança:** ALTA (padrões consolidados de documentação técnica: Diátaxis, tutorial oficial do Django, Write the Docs)

## Referências de forma

- **Diátaxis (diataxis.fr):** separa *tutorial* (aprender fazendo), *how-to* (resolver tarefa), *referência* e *explicação*. O guia pedido é um **tutorial** com apêndices *how-to*. O erro clássico é misturar os quatro num texto só.
- **Tutorial oficial do Django (polls):** o padrão-ouro de progressão — cada parte termina com algo funcionando e visível no navegador. É o modelo de ritmo a imitar (não de conteúdo: o guia ensina o *método do template*, não Django genérico).
- **Regra de ouro de tutorial:** o leitor digita/cola e vê resultado a cada passo. Nunca dois capítulos seguidos sem nada aparecer na tela.

## Paisagem de features

### Table stakes (o leitor espera)

| Feature | Por que esperada | Complexidade | Notas |
|---------|------------------|--------------|-------|
| Pré-requisitos explícitos ("você precisa de: sistema gerado rodando, acesso ao terminal") | Leitor menos técnico não sabe inferir | BAIXA | Apontar para o README (nascimento) em vez de repetir |
| Um exemplo completo conduzido do zero à tela pronta (diárias e passagens) | É o pedido central do marco | ALTA | Modelo → migração → admin → listagem → formulário modal → item na nav |
| Cada passo com resultado visível ("recarregue e veja X") | Padrão de tutorial; mantém o leitor confiante | MÉDIA | Ritmo do tutorial do Django |
| Como criar um app em `apps/` do jeito do template | É a fronteira que o template formaliza | BAIXA | `startapp` + registro em settings + convenções |
| Copiar o padrão do app `exemplo` (tabela, filtros, modal 422, dashboard) | O exemplo é a documentação viva; o guia é o mapa dela | MÉDIA | Referenciar arquivos do `exemplo` por caminho |
| Item de menu via `{% item_nav %}` em `_nav_dominio.html` | Ponto de extensão criado na Fase 7 exatamente para isso | BAIXA | Primeiro uso documentado do mecanismo |
| Quando e como remover o app `exemplo` | Protocolo de 4 passos já existe; o guia diz *quando* | BAIXA | Link para o protocolo, não duplicação |
| Linguagem simples com glossário dos termos inevitáveis (migração, ORM, template, view) | Público "menos técnico possível" | MÉDIA | Termo técnico aparece → uma frase de tradução |
| Seção "deu errado?" (troubleshooting) por capítulo | Tutorial sem socorro abandona o leitor no primeiro erro | MÉDIA | Erros reais colhidos ao construir o exemplo |

### Diferenciais

| Feature | Valor | Complexidade | Notas |
|---------|-------|--------------|-------|
| 2 exemplos resumidos (orçamento, controle de materiais) mostrando só a modelagem e o que muda | Prova que o método transfere; evita "só funciona para diárias" | MÉDIA | Formato fixo: entidades → campos → telas → o que aproveitar do completo |
| Capítulo de dashboard/gráfico usando a paleta derivada da marca | Fecha o ciclo CRUD→decisão, que é o propósito da família CFC | MÉDIA | ECharts + `json_script` + agregação via ORM, padrão da Fase 3/7 |
| "Mapa de receitas": quero X → copie Y do exemplo | Transforma o app exemplo em referência navegável | BAIXA | Tabela de 1 página |
| Orientação de modelagem em linguagem de negócio ("cada pedido de diária é uma linha; o servidor é outra tabela") | É onde o público menos técnico mais trava | MÉDIA | Analogias com planilha |
| Código do guia provado por teste na cópia gerada | Diferencial raro: o guia nunca mente | ALTA | Ver ARCHITECTURE — suíte própria em `.template-tests/` |

### Anti-features (parecem boas, criam problema)

| Feature | Apelo | Problema | Alternativa |
|---------|-------|----------|-------------|
| Ensinar Django do zero (o que é MVC, request/response...) | "guia completo" | Duplica a docs oficial, incha o guia, envelhece | Uma seção "aprenda mais" com links; o guia ensina o *método do template* |
| Repetir instruções de operação (backup, TLS, deploy) | "tudo num lugar" | Já vivem no README; duas fontes divergem | Links para as seções do README |
| Screenshots das telas | Didático à primeira vista | Apodrecem a cada mudança visual; binários no repo; quebram no tema escuro | Descrever o resultado em texto ("a tabela aparece com...") |
| Gerar o app de diárias como unidade opcional do Copier | "já vem pronto" | Viola Fora de Escopo (conteúdo de domínio no template); mais um acoplamento no update | O código vive no guia (texto) e no fixture de teste, nunca em `apps/` do template |
| Vídeo/tutorial interativo | Moderno | Fora do alcance de manutenção do time | Markdown com passos curtos |

## Dependências entre features

```
Exemplo completo (diárias)
    └──gera──> trechos de código do guia
                   └──provados por──> suíte em .template-tests/
    └──ancora──> exemplos resumidos (orçamento, materiais)
    └──usa──> {% item_nav %} (Fase 7) e padrão do app exemplo (Fase 3)
Glossário ──permeia──> todos os capítulos
Troubleshooting ──colhido de──> construção real do exemplo
```

## Definição de MVP

### Lança com (v0.3.0)

- [ ] Guia multi-arquivo com o exemplo completo de diárias e passagens, do app vazio à tela com menu
- [ ] 2 exemplos resumidos (orçamento, controle de materiais)
- [ ] Glossário + troubleshooting por capítulo
- [ ] Trechos de código provados em cópia gerada
- [ ] Link no README e chegada ao sistema gerado via `copier copy`

### Depois de validado (v0.3.x+)

- [ ] Mapa de receitas expandido conforme dúvidas reais do primeiro derivado (DividaAtiva/Orçamento)
- [ ] Capítulo de relatórios/exportação, se o primeiro uso real pedir
