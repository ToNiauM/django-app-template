---
phase: quick-260818-qoy
plan: 01
type: execute
wave: 1
depends_on: []
files_modified: [README.md]
autonomous: true
requirements: [QUICK-260818-QOY]

must_haves:
  truths:
    - "Quem lê o README do template descobre, logo após a introdução, qual dos três ciclos (evoluir / nascer / operar) se aplica antes de rodar qualquer comando"
    - "A seção orienta por links de âncora para as seções existentes, sem duplicar nenhum bloco de comandos"
    - "A regra-resumo deixa explícito: .sh só antes de tag; copier copy só no nascimento; copier update só ao puxar versão nova para sistema existente"
  artifacts:
    - path: "README.md"
      provides: "Seção '## Os três ciclos de trabalho' entre a introdução e '## Ferramenta isolada e versão aprovada'"
      contains: "## Os três ciclos de trabalho"
  key_links:
    - from: "README.md (nova seção)"
      to: "README.md (seções existentes)"
      via: "âncoras markdown"
      pattern: "#nascimento-local-de-um-sistema"
---

<objective>
Adicionar ao README.md do template-fonte (raiz do repo) a seção "Os três ciclos
de trabalho", logo após o parágrafo introdutório, explicando quando cada grupo
de comandos é usado — evoluir o template, nascer um sistema, operar um sistema —
com links por âncora para as seções existentes em vez de duplicar comandos.

Purpose: o README já documenta cada procedimento em detalhe, mas não diz ao
leitor QUAL ciclo se aplica à sua situação; operadores confundem scripts de
regressão (por release) com comandos de nascimento (por sistema) e com operação
cotidiana (no sistema gerado).
Output: README.md com a nova seção de orientação, doc-only, pt-BR.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@README.md
@.planning/STATE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Inserir seção "Os três ciclos de trabalho" no README.md</name>
  <files>README.md</files>
  <action>
Inserir uma nova seção `## Os três ciclos de trabalho` no README.md da raiz do
repositório (template-fonte), imediatamente após o parágrafo introdutório que
termina em "...guia da operação cotidiana daquele sistema específico." (linha 9
do arquivo atual) e antes de `## Ferramenta isolada e versão aprovada`
(linha 11 atual). Manter uma linha em branco antes e depois da nova seção.

Conteúdo da seção (pt-BR, prosa própria — NÃO copiar blocos de comando de
outras seções; comandos aparecem apenas como menções inline em `código`):

1. Frase de abertura: todo comando deste README pertence a exatamente um de
   três ciclos, com frequências muito diferentes; identificar o ciclo antes de
   digitar qualquer comando evita rodar script de release dentro de um sistema
   ou comando de runtime na raiz do template.

2. **Evoluir o template** — raro, só ao mexer no core. Rodar a regressão
   completa de `.template-tests/` e só então criar a tag semver. Deixar
   explícito: os scripts `.sh` do template rodam uma vez por release, nunca por
   sistema. Referenciar por âncora: [Regressão do template](#regressão-do-template)
   e [Releases e atualização do núcleo](#releases-e-atualização-do-núcleo).

3. **Nascer um sistema** — uma vez por sistema: `copier copy` da tag estável +
   `.env` + Compose + migrate + createsuperuser e, quando for publicar,
   proxy/TLS. Deixar explícito: nenhum script do template é executado no
   nascimento — a tag já foi validada pela regressão. Referenciar por âncora:
   [Nascimento local de um sistema](#nascimento-local-de-um-sistema) e
   [Publicação com proxy, TLS e DNS](#publicação-com-proxy-tls-e-dns).

4. **Operar um sistema** — dia a dia: `docker compose logs/exec/restart` e a
   suíte Django do próprio sistema (`manage.py test`), guiado pelo README
   renderizado dentro do sistema gerado. Deixar explícito: os
   `.template-tests/` nem existem no sistema gerado.

5. Tabela dos três ciclos para leitura rápida, com colunas:
   ciclo | quando | comandos-chave | seção de referência. Comandos-chave como
   menções inline (ex.: `.template-tests/*.sh` + tag semver; `copier copy` +
   `.env` + `docker compose up`; `docker compose logs/exec` + `manage.py test`).
   A coluna de referência usa os mesmos links de âncora; para "Operar", indicar
   o README renderizado do sistema gerado (não há âncora local — texto simples
   ou referência ao parágrafo introdutório).

6. Fechar com a regra-resumo em uma linha destacada (parágrafo com negrito ou
   blockquote): `.sh` = só antes de tag; `copier copy` = só no nascimento;
   `copier update` = só ao puxar uma versão nova do template para um sistema
   existente.

Âncoras exatas (estilo GitHub — minúsculas, acentos preservados, pontuação
removida, espaços viram hífen; conferir contra os headings reais do arquivo):
- `## Nascimento local de um sistema` → `#nascimento-local-de-um-sistema`
- `## Publicação com proxy, TLS e DNS` → `#publicação-com-proxy-tls-e-dns`
- `## Regressão do template` → `#regressão-do-template`
- `## Releases e atualização do núcleo` → `#releases-e-atualização-do-núcleo`

Restrições:
- Somente README.md pode ser modificado; nenhum outro arquivo.
- Nenhum bloco de código cercado (```) dentro da nova seção — orientação, não
  duplicação de comandos.
- Não alterar nenhuma seção existente; a mudança é puramente aditiva.
- Estilo consistente com o restante do arquivo: pt-BR, linhas quebradas
  (~78 colunas), negrito para os nomes dos ciclos.
  </action>
  <verify>
    <automated>grep -c '^## Os três ciclos de trabalho$' README.md | grep -qx 1 && awk '/^## Os três ciclos de trabalho$/{f=1;next} /^## Ferramenta isolada e versão aprovada$/{exit} f' README.md | grep -q '#regressão-do-template' && awk '/^## Os três ciclos de trabalho$/{f=1;next} /^## Ferramenta isolada e versão aprovada$/{exit} f' README.md | grep -q '#nascimento-local-de-um-sistema' && awk '/^## Os três ciclos de trabalho$/{f=1;next} /^## Ferramenta isolada e versão aprovada$/{exit} f' README.md | grep -q '#publicação-com-proxy-tls-e-dns' && awk '/^## Os três ciclos de trabalho$/{f=1;next} /^## Ferramenta isolada e versão aprovada$/{exit} f' README.md | grep -q '#releases-e-atualização-do-núcleo' && [ "$(awk '/^## Os três ciclos de trabalho$/{f=1;next} /^## Ferramenta isolada e versão aprovada$/{exit} f' README.md | grep -c '^```')" -eq 0 ] && git diff --name-only | grep -qx 'README.md' && [ "$(git diff --name-only | wc -l)" -eq 1 ]</automated>
  </verify>
  <done>
README.md contém a seção "## Os três ciclos de trabalho" posicionada entre o
parágrafo introdutório e "## Ferramenta isolada e versão aprovada"; a seção
descreve os três ciclos (evoluir/nascer/operar) com suas frequências, inclui a
tabela ciclo|quando|comandos-chave|referência, fecha com a regra-resumo
(.sh = antes de tag; copier copy = nascimento; copier update = puxar versão
nova), referencia as quatro seções existentes por âncoras corretas, não contém
nenhum bloco de código cercado, e nenhum outro arquivo foi modificado.
  </done>
</task>

</tasks>

<verification>
- A nova seção aparece exatamente uma vez, no local correto (após a introdução,
  antes de "## Ferramenta isolada e versão aprovada").
- Os quatro links de âncora correspondem letra a letra aos headings existentes
  transformados pela regra de âncoras do GitHub.
- `git diff --stat` mostra somente README.md alterado, apenas com adições na
  região da nova seção.
</verification>

<success_criteria>
- Leitor identifica em menos de um minuto qual ciclo se aplica a ele e para
  qual seção do README deve navegar.
- Nenhum comando duplicado: a seção só menciona comandos inline e aponta para
  as seções canônicas.
- Regra-resumo presente e fiel: `.sh` = só antes de tag; `copier copy` = só no
  nascimento; `copier update` = só ao atualizar sistema existente para tag nova.
</success_criteria>

<output>
Create `.planning/quick/260818-qoy-adicionar-se-o-os-tr-s-ciclos-de-trabalh/260818-qoy-SUMMARY.md` when done
</output>
