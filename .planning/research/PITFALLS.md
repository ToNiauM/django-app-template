# Pesquisa de Armadilhas — Guia de construção de sistemas (v0.3.0)

**Marco:** v0.3.0 — Guia de construção de sistemas
**Foco:** erros comuns ao ADICIONAR documentação didática a um template Copier existente.
**Pesquisado:** 2026-08-25
**Confiança:** ALTA (metade das armadilhas já tem precedente registrado neste repositório)

## Armadilhas

### 1. Código de exemplo que quebra em silêncio (documentation rot)

- **Sinal:** trecho do guia deixa de rodar após uma mudança no core e ninguém percebe até um usuário travar no capítulo 2.
- **Por quê:** Markdown não compila; sem prova executável, cada refactor do template é uma chance de mentir.
- **Prevenção:** o código do guia vive em fixture (`.template-tests/fixtures/guia/`) provado na cópia gerada, e um teste exige igualdade byte a byte entre a cerca de código do guia e o arquivo do fixture. É a lição central da v0.2.0 aplicada a docs: *guarda executável em vez de convenção escrita*.
- **Fase que trata:** a primeira fase de construção (fixture + suíte antes do texto).

### 2. Conteúdo de domínio vazando para o template

- **Sinal:** `apps/diarias/` aparece no repositório do template ou na cópia gerada.
- **Por quê:** a tentação de "entregar o exemplo pronto" viola o Fora de Escopo (template agnóstico de domínio) e cria uma segunda unidade opcional para conflitar no `copier update`.
- **Prevenção:** o código do exemplo só existe em dois lugares — no texto do guia e em `.template-tests/fixtures/` (que o `_exclude` já barra). Teste negativo: a cópia gerada não contém `apps/diarias`.
- **Fase que trata:** fixture/suíte, com guarda negativa.

### 3. O guia virar novo ponto de conflito no `copier update`

- **Sinal:** derivado anota algo em `docs/guia/` e o próximo `copier update` grava marcador de conflito dentro do capítulo.
- **Por quê:** merge de 3 vias do Copier — o mesmo mecanismo que fazia do `_nav.html` o pior conflito da família (79 linhas).
- **Prevenção:** (a) o guia declara na abertura que `docs/guia/` pertence ao núcleo; (b) o ensaio de `copier update` existente passa a cobrir a árvore `docs/` (exit 0, zero marcador, zero `.rej`); (c) **não** usar `_skip_if_exists` — congelaria o guia (ver ARCHITECTURE).
- **Fase que trata:** integração/release.

### 4. Registro técnico escapando para o texto "acessível"

- **Sinal:** capítulo 1 já fala em "QuerySet", "middleware", "context processor" sem tradução.
- **Por quê:** quem escreve conhece demais; jargão é o modo default. É o requisito mais difícil de testar do marco.
- **Prevenção:** (a) glossário no capítulo 0 e regra editorial "termo técnico novo → uma frase de tradução na primeira ocorrência"; (b) critério de aceite de *resultado*, não de estrutura (lição 3 da retrospectiva): revisão de leitura dedicada, com persona explícita ("colega que sabe planilha, não sabe Django"); (c) varredura simples de termos proibidos sem glossa é possível, mas não substitui a leitura.
- **Fase que trata:** escrita + revisão editorial como gate próprio.

### 5. Duplicar o README (e divergir dele)

- **Sinal:** o guia re-explica backup, TLS, `copier copy`, remoção do app exemplo — e uma das cópias desatualiza.
- **Por quê:** "tudo num documento só" parece conveniência; vira duas fontes da verdade.
- **Prevenção:** fronteira editorial fixa — o README responde "como nasce e como opera o sistema"; o guia responde "como construir o domínio depois de nascido". Toda sobreposição vira link. O protocolo de remoção do exemplo continua no `apps/exemplo/README.md`; o guia só diz *quando* removê-lo.
- **Fase que trata:** escrita (fronteira definida no outline antes do texto).

### 6. A tag ficar para trás de novo

- **Sinal:** marco "fechado", guia em `main`, e nenhum derivado o recebe — porque o Copier lê a última tag, não o HEAD.
- **Por quê:** exatamente o que aconteceu com a Fase 6 na v0.2.0 (37 commits sem tag).
- **Prevenção:** o roadmap já nasce com a publicação da tag `v0.3.0` como critério de fase, na ordem provada: verificar → revisar → consertar → taguear.
- **Fase que trata:** fase final (release).

### 7. Tutorial sem resultado visível (o leitor se perde)

- **Sinal:** dois capítulos seguidos de edição de arquivos sem nada mudar na tela.
- **Por quê:** para o público menos técnico, o feedback visual é o que confirma "estou no caminho".
- **Prevenção:** regra estrutural — todo capítulo termina com "recarregue e veja"; troubleshooting por capítulo com os erros reais colhidos ao construir o fixture.
- **Fase que trata:** escrita (padrão de capítulo).

### 8. Screenshots como prova didática

- **Sinal:** PNGs de telas no repo do template.
- **Por quê:** apodrecem a cada ajuste visual (a v0.2.0 mudou a cara de tudo), pesam o repo, e quebram na alternância claro/escuro.
- **Prevenção:** descrever resultados em texto; a aparência real o leitor tem no próprio sistema rodando ao lado.

## Sinais de alerta transversais

- Cerca de código no guia sem arquivo correspondente no fixture → trecho não provado.
- Capítulo que só faz sentido para quem leu o código do `core` → registro errado.
- Qualquer instrução do guia que não funcione numa cópia recém-gerada com `.env` default → quebra do contrato "código real testado".
