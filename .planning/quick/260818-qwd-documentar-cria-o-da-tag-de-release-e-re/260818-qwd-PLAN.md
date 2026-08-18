---
phase: quick-260818-qwd
plan: 01
type: execute
wave: 1
depends_on: []
files_modified: [README.md]
autonomous: true
requirements: [QUICK-260818-QWD]

must_haves:
  truths:
    - "Leitor da seção 'Releases e atualização do núcleo' encontra a subseção 'Criando a tag de release' com pré-condições (árvore limpa + regressão verde) e os comandos git tag -a / git tag / git show --stat"
    - "Leitor entende como o Copier resolve a versão: última tag por ordenação PEP 440 sem --vcs-ref; fallback para HEAD com versão sintética 0.0.0.postN.dev0+hash quando não há tag; DirtyLocalWarning em árvore suja; --vcs-ref=HEAD só para ensaio/depuração"
    - "Passo 2 do 'Nascimento local de um sistema' linka por âncora a nova subseção"
    - "Última seção do README é '## Resumo: nascimento completo em comandos' cobrindo a jornada inteira do sistema financeiro, da tag ao curl HTTPS, só com comandos e comentários de uma linha"
    - "Comandos-chave do Resumo são cópia fiel (mesmas flags) dos comandos das seções detalhadas, apenas com valores concretos do financeiro substituídos"
    - "Nenhuma seção existente foi removida ou alterada além do link no passo 2"
  artifacts:
    - path: "README.md"
      provides: "Subseção 'Criando a tag de release' dentro de Releases"
      contains: "### Criando a tag de release"
    - path: "README.md"
      provides: "Explicação da resolução de versão do Copier"
      contains: "DirtyLocalWarning"
    - path: "README.md"
      provides: "Seção final de resumo executável"
      contains: "## Resumo: nascimento completo em comandos"
  key_links:
    - from: "Passo 2 do Nascimento local"
      to: "### Criando a tag de release"
      via: "âncora markdown"
      pattern: "#criando-a-tag-de-release"
    - from: "Resumo (comandos concretos do financeiro)"
      to: "Seções detalhadas (comandos com placeholders)"
      via: "strings de comando idênticas exceto valores"
      pattern: "docker compose exec -T web python manage.py migrate --noinput"
---

<objective>
Duas mudanças doc-only no README.md do template-fonte (raiz do repo):
(1) subseção "### Criando a tag de release" na seção "Releases e atualização
do núcleo", documentando pré-condições, comandos git tag e como o Copier
resolve a versão; (2) seção final "## Resumo: nascimento completo em
comandos" — a jornada inteira, do template ao HTTPS, em blocos de comandos
com comentários de uma linha, usando o exemplo concreto do sistema
financeiro (hostname financeiro.sistemascfc.org, porta 12010, Caminho A).

Purpose: fechar o buraco documental entre "sistemas nascem de releases" e
"como criar a release", e dar a quem já entendeu os detalhes uma conclusão
executável de ponta a ponta.
Output: README.md atualizado; dois commits atômicos (um por parte).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@README.md
@.planning/STATE.md
</context>

<constraints>
- Doc-only: SOMENTE README.md pode ser modificado.
- Idioma: pt-BR, mesmo tom e largura de linha (~79 colunas) do restante do arquivo.
- O Resumo não substitui as seções detalhadas; nenhuma seção existente é
  removida ou reescrita — a única alteração fora das inserções é o link no
  passo 2 do nascimento.
- Comandos do Resumo devem ser cópia caractere a caractere dos comandos das
  seções detalhadas (mesmas flags e mesma forma), trocando apenas
  placeholders (`<hostname>`, `<porta>`, `/caminho/para/novo-sistema`) pelos
  valores concretos do financeiro.
- Um commit por task: `docs(quick-260818-qwd): ...`.
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Subseção "Criando a tag de release" + link no passo 2</name>
  <files>README.md</files>
  <action>
Inserir a subseção `### Criando a tag de release` na seção
`## Releases e atualização do núcleo`, imediatamente APÓS o primeiro
parágrafo dessa seção (o parágrafo "Publique mudanças conscientes ... decide
atualizar para uma tag posterior.") e ANTES do parágrafo "Faça `copier
update` exclusivamente com o Git limpo". Todo o conteúdo existente da seção
permanece intacto abaixo da subseção (a aninhamento estrutural resultante é
aceito — a colocação foi decisão do usuário).

Conteúdo da subseção, em prosa pt-BR no tom do arquivo:

1. Pré-condição, em um parágrafo curto: árvore limpa (`git status --short`
   sem nenhuma saída) e a regressão completa de
   [Regressão do template](#regressão-do-template) verde, incluindo o ensaio
   de nascimento.

2. Um bloco bash com os três comandos, cada um precedido de um comentário
   `#` de uma linha: criar a tag anotada com
   `git tag -a v0.1.0 -m "descrição da release"`; listar as tags existentes
   com `git tag`; inspecionar a release com `git show v0.1.0 --stat`.

3. Um ou dois parágrafos explicando como o Copier resolve a versão, cobrindo
   exatamente estes pontos:
   - Sem `--vcs-ref`, tanto `copier copy` quanto `copier update` renderizam
     a ÚLTIMA TAG do template (ordenação PEP 440), nunca o HEAD — é por isso
     que sistemas nascem de releases.
   - Se o repositório não tem nenhuma tag, o Copier cai no HEAD com uma
     versão sintética no formato `0.0.0.postN.dev0+hash`; se além disso a
     árvore estiver suja, ele emite `DirtyLocalWarning` e inclui as mudanças
     não commitadas na cópia — nunca gerar um sistema real nesse estado.
   - `--vcs-ref=HEAD` existe apenas para ensaio/depuração do template, nunca
     para nascimento de produção.

4. Atualizar o passo 2 de `## Nascimento local de um sistema` ("Escolha uma
   tag estável do template..."), acrescentando ao final do item uma frase
   com link por âncora, por exemplo: "Veja
   [Criando a tag de release](#criando-a-tag-de-release)." Nada mais nesse
   passo muda.

Commit: `docs(quick-260818-qwd): documentar criação da tag de release`
  </action>
  <verify>
    <automated>test "$(grep -c '^### Criando a tag de release$' README.md)" -eq 1 && test "$(grep -c '#criando-a-tag-de-release' README.md)" -eq 1 && grep -q 'git tag -a v0.1.0' README.md && grep -q 'git show v0.1.0 --stat' README.md && grep -q 'PEP 440' README.md && grep -q 'DirtyLocalWarning' README.md && grep -q '0\.0\.0\.postN\.dev0' README.md && grep -q -- '--vcs-ref=HEAD' README.md && test "$(grep -c '^## ' README.md)" -eq 6</automated>
  </verify>
  <done>Subseção presente logo após o primeiro parágrafo de Releases com pré-condição, os três comandos git e a explicação de resolução de versão (última tag PEP 440 / fallback HEAD / DirtyLocalWarning / --vcs-ref=HEAD só ensaio); passo 2 linka `#criando-a-tag-de-release`; nenhuma seção `##` adicionada ou removida nesta task (contagem de `##` permanece 6); commit atômico feito.</done>
</task>

<task type="auto">
  <name>Task 2: Seção final "Resumo: nascimento completo em comandos"</name>
  <files>README.md</files>
  <action>
Acrescentar ao FINAL do README (após todo o conteúdo da seção Releases,
tornando-se a última seção `##` do arquivo) a seção
`## Resumo: nascimento completo em comandos`.

Abertura: 1-2 frases declarando o propósito — quem já entendeu (ou não
precisa entender) os detalhes encontra aqui a jornada inteira só em
comandos, uma conclusão executável; o resumo não substitui as seções
detalhadas acima.

Formato obrigatório: blocos de comandos onde CADA comando (ou pequeno grupo
coeso) é precedido de UMA linha de comentário `#` curta. Sem parágrafos
explicativos entre os blocos — só comandos e comentários de uma linha. A
primeira linha de comentário do primeiro bloco deixa claro que os valores
são um exemplo e basta trocar nome/hostname/porta (ex.:
`# exemplo completo do sistema "financeiro" — troque nome, hostname e porta para o seu caso`).

Valores concretos do exemplo (decisões travadas pelo usuário): sistema
**financeiro**, hostname **financeiro.sistemascfc.org**, porta **12010**,
banco **financeiro**, publicação pelo Caminho A (conf.d + `certbot
--nginx`). A porta 12010 é o valor do exemplo mesmo estando fora da tabela
de convenção 8000–8099 — não "corrigir".

REGRA DE FIDELIDADE: cada comando é cópia caractere a caractere do comando
correspondente na seção detalhada, com apenas os placeholders substituídos.
Fontes: seção "Nascimento local de um sistema" (passos 3, 5, 6, 9, 10, 11,
12, 13, 14, 15), "Caminho A" (bloco nginx, nginx -t/reload, certbot) e a
Task 1 (git tag). Não inventar flags novas nem omitir flags existentes.

Ordem e conteúdo dos blocos:

1. `# criar a tag da release (uma vez, no template; pule se a tag já existe)`
   → `git tag -a v0.1.0 -m "descrição da release"` (idêntico à Task 1).
2. `# gerar a cópia` →
   `/caminho/para/template/.venv-template/bin/copier copy /caminho/para/template /caminho/para/financeiro`
   (mesma forma do passo 3, destino concreto).
3. As oito respostas do financeiro como bloco de texto (```text), uma por
   linha, precedido de comentário/introdução de uma linha. Valores: nome
   `Sistema Financeiro`; slug `financeiro`; hostname
   `financeiro.sistemascfc.org`; porta `12010`; banco `financeiro`; sigla
   `FIN`; cor primária `#0F5132`; incluir app exemplo `true` (sigla, cor e
   app exemplo são escolha de exemplo a critério do executor, desde que
   passem nos validators descritos no passo 4: cor `#RRGGBB`, sigla curta).
4. `# entrar no sistema gerado e criar o ambiente local` →
   `cd /caminho/para/financeiro` e `cp .env.example .env`.
5. `# gerar a SECRET_KEY (colar no .env)` →
   `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` (idêntico
   ao passo 6); `# gerar a senha do Postgres (colar em POSTGRES_PASSWORD e no DATABASE_URL)`
   → `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`.
6. `# editar o .env: SECRET_KEY, POSTGRES_PASSWORD e a mesma senha no DATABASE_URL`
   (linha de comentário; sem comando ou com o editor de preferência em
   comentário).
7. `# iniciar o repositório do sistema` → `git init`, `git add .`,
   `git commit -m "chore: inicia sistema gerado pelo Copier"` (mensagem
   idêntica ao passo 9).
8. `# validar a configuração resolvida do Compose` →
   `docker compose --env-file .env config -q`.
9. `# subir banco e aplicação (backup fica de fora até existirem credenciais R2)`
   → `docker compose up -d --build db web`.
10. `# acompanhar a inicialização` → `docker compose logs -f web`.
11. `# aplicar as migrações` →
    `docker compose exec -T web python manage.py migrate --noinput`.
12. `# criar o administrador (interativo)` →
    `docker compose exec web python manage.py createsuperuser`.
13. `# confirmar a saúde local` →
    `curl -fsS http://127.0.0.1:12010/healthz`.
14. `# criar o registro DNS: financeiro.sistemascfc.org -> IP público da VM (aguardar propagação)`
    (linha de comentário, sem comando).
15. `# criar /etc/nginx/conf.d/financeiro.sistemascfc.org.conf com o bloco :80`
    seguido do bloco nginx (```nginx) copiado VERBATIM do Caminho A, com
    `<hostname>` → `financeiro.sistemascfc.org` e `<porta>` → `12010`
    (`proxy_pass http://127.0.0.1:12010;` e todas as diretivas
    `proxy_set_header`/`proxy_http_version`/`proxy_read_timeout` idênticas).
16. `# validar e recarregar o nginx` → `sudo nginx -t` e
    `sudo systemctl reload nginx`.
17. `# emitir o certificado sem parar o nginx` →
    `sudo certbot --nginx -d financeiro.sistemascfc.org`.
18. `# validar de fora da VM` →
    `curl -fsS https://financeiro.sistemascfc.org/healthz`.

Commit: `docs(quick-260818-qwd): resumo executável do nascimento completo`
  </action>
  <verify>
    <automated>test "$(grep -c '^## Resumo: nascimento completo em comandos$' README.md)" -eq 1 && test "$(grep '^## ' README.md | tail -1)" = "## Resumo: nascimento completo em comandos" && test "$(grep -c '^## ' README.md)" -eq 7 && test "$(grep -c 'bin/copier copy' README.md)" -eq 2 && test "$(grep -c 'docker compose exec -T web python manage.py migrate --noinput' README.md)" -eq 2 && test "$(grep -c 'sudo certbot --nginx -d' README.md)" -eq 2 && test "$(grep -c 'docker compose --env-file .env config -q' README.md)" -eq 2 && test "$(grep -c 'docker compose up -d --build db web' README.md)" -eq 2 && test "$(grep -c 'chore: inicia sistema gerado pelo Copier' README.md)" -eq 2 && grep -q 'proxy_pass http://127.0.0.1:12010;' README.md && grep -q 'certbot --nginx -d financeiro.sistemascfc.org' README.md && grep -q 'curl -fsS https://financeiro.sistemascfc.org/healthz' README.md && grep -q 'curl -fsS http://127.0.0.1:12010/healthz' README.md && test "$(grep -c 'git tag -a v0.1.0' README.md)" -eq 2</automated>
  </verify>
  <done>Resumo é a última seção `##` do README (7 seções `##` no total); jornada completa tag → copier copy → respostas → .env/segredos → git init → compose config/up/logs → migrate → createsuperuser → healthz local → DNS → vhost conf.d :80 com proxy_pass 12010 → nginx -t/reload → certbot --nginx → healthz HTTPS externo, só com comandos e comentários de uma linha; comandos-chave aparecem exatamente 2 vezes no arquivo (seção detalhada + resumo), provando cópia fiel; commit atômico feito.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| README → operador | Documentação instrui comandos executados com sudo em VM de produção |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-qwd-01 | Tampering | Comandos do Resumo divergirem das seções auditadas | mitigate | Regra de fidelidade caractere a caractere + gates grep de contagem exata (== 2) por comando-chave |
| T-qwd-02 | Information Disclosure | Exemplo induzir segredo no Git | mitigate | Resumo mantém segredos apenas no .env (gerados localmente), reproduzindo o contrato das seções detalhadas; nenhum valor de segredo aparece no exemplo |
</threat_model>

<verification>
- `test "$(git status --short | grep -v '^??' | awk '{print $2}' | grep -vc '^README.md$')" -eq 0` — nenhum arquivo rastreado além de README.md modificado (doc-only).
- Ambos os gates automatizados das tasks passam sobre o README final.
- Seções pré-existentes intactas: os 6 títulos `##` originais e os 4 títulos `###` originais continuam presentes com o mesmo texto (`grep -c '^### ' README.md` retorna 5 ao final: 4 originais + Criando a tag de release).
- Dois commits atômicos com prefixo `docs(quick-260818-qwd):`.
</verification>

<success_criteria>
- Subseção "Criando a tag de release" documenta pré-condições, os três comandos git e a semântica de resolução de versão do Copier (última tag PEP 440, fallback `0.0.0.postN.dev0+hash`, `DirtyLocalWarning`, `--vcs-ref=HEAD` só para ensaio).
- Passo 2 do nascimento linka `#criando-a-tag-de-release`.
- README termina com "## Resumo: nascimento completo em comandos": exemplo financeiro completo (financeiro.sistemascfc.org, porta 12010, Caminho A), do `git tag` ao `curl` HTTPS, só comandos + comentários `#` de uma linha.
- Comandos-chave do Resumo idênticos aos das seções detalhadas (verificado por contagem grep == 2).
- Nenhuma seção existente removida ou alterada além do link no passo 2.
</success_criteria>

<output>
Create `.planning/quick/260818-qwd-documentar-cria-o-da-tag-de-release-e-re/260818-qwd-SUMMARY.md` when done
</output>
