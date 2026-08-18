# Phase 4: Templatização Copier - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-18
**Phase:** 4-Templatização Copier
**Areas discussed:** Estrutura do template, Variáveis e defaults, Estratégia copier update, ops/ — backup e nginx

---

## Estrutura do template

| Option | Description | Selected |
|--------|-------------|----------|
| In-place na raiz | copier.yml na raiz, .jinja só onde há variáveis; repo deixa de rodar direto, validação via copier copy | ✓ |
| _subdirectory: template/ | Projeto movido para template/; separação mais limpa, mexe em todos os paths | |
| Manter repo executável | Manutenção dupla modelo + template | |

**User's choice:** In-place na raiz (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| _exclude no copier.yml | .planning/, CLAUDE.md, IDEIA.md, REVIEW.md ficam no template, nunca chegam ao gerado | ✓ |
| Copiar tudo | Gerado herda artefatos de planejamento | |
| Você decide | Claude define a lista de exclusões | |

**User's choice:** _exclude no copier.yml (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Dois READMEs | README.md raiz = doc do template (no _exclude); README.md.jinja gera o do sistema | ✓ |
| README único templatizado | Um só README.md.jinja para os dois papéis | |
| Você decide | Claude define a estrutura de documentação | |

**User's choice:** Dois READMEs (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Passo manual documentado | README instrui git init + primeiro commit (com .copier-answers.yml); Copier não executa nada | ✓ |
| _tasks automático | copier.yml roda git init + commit inicial | |
| Você decide | Claude escolhe no planejamento | |

**User's choice:** Passo manual documentado (Recomendado)

---

## Variáveis e defaults

| Option | Description | Selected |
|--------|-------------|----------|
| Mínimas + defaults derivados | Pergunta tudo com defaults inteligentes (slug do nome, banco=slug, subdomínio=slug) | ✓ |
| Perguntar tudo sem derivação | Cada variável independente, sem defaults derivados | |
| Só nome e cor | Resto derivado sem sobrescrever | |

**User's choice:** Mínimas + defaults derivados (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Validators no copier.yml | Regex #RRGGBB, slug, porta 1024-65535; erro na hora do copy | ✓ |
| Só validação no boot | Confiar na validação do Django na subida | |
| Você decide | Claude define as regras por variável | |

**User's choice:** Validators no copier.yml (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Placeholder + comando documentado | .env.example com placeholders; README instrui gerar SECRET_KEY; nada passa pelo Copier | ✓ |
| Pergunta no copier copy | Segredos vazariam para o .copier-answers.yml commitado | |
| Script gerar_env | Script em ops/ cria .env com segredos aleatórios | |

**User's choice:** Placeholder + comando documentado (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Script + passo documentado | Gerado herda placeholders; README lista rodar ops/gerar_icones_pwa.py como passo opcional | ✓ |
| Placeholders permanentes | Ícones neutros até troca manual por arte própria | |
| Você decide | Claude define o fluxo de ícones | |

**User's choice:** Script + passo documentado (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Só [a-z0-9] | Slug sem separador — válido em banco, DNS e diretório sem conversão | ✓ |
| Underscore + conversão p/ DNS | '_' permitido, convertido para '-' no subdomínio | |
| Dois slugs perguntados | Slug técnico e slug DNS separados | |

**User's choice:** Só [a-z0-9] (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Hostname completo | Uma variável com host completo (orcamento.cfc.org.br), default {slug}.exemplo.gov.br | ✓ |
| Rótulo + domínio-base | Duas variáveis compostas automaticamente | |
| Você decide | Claude escolhe no planejamento | |

**User's choice:** Hostname completo (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Pergunta + tabela no README | Default 8000 + tabela de alocação da família no README do template | ✓ |
| Só pergunta com default | Sem registro central de alocação | |
| Você decide | Claude define a convenção | |

**User's choice:** Pergunta + tabela no README (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Sim, com default derivado | Sigla perguntada com default das iniciais do nome | ✓ |
| Não — só no .env | Sigla fora do copier.yml | |
| Você decide | Claude decide no planejamento | |

**User's choice:** Sim, com default derivado (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Fixar name: {slug} | compose.yml gerado com name interpolado — isolamento independente do diretório | ✓ |
| Continuar herdando do diretório | Sem name:, como hoje | |
| Você decide | Claude decide no planejamento | |

**User's choice:** Fixar name: {slug} (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| .env primeiro, .jinja mínimo | Runtime via .env; .jinja só onde .env não alcança (tailwind, .env.example, README, vhost, copier.yml) | ✓ |
| Jinja-izar todo valor variável | Interpolar diretamente em cada arquivo | |
| Você decide | Claude aplica caso a caso | |

**User's choice:** .env primeiro, .jinja mínimo (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Hex livre com default atual | #RRGGBB com validator, default #1e40af | ✓ |
| Choices de paleta da família | Opções nomeadas pré-validadas | |
| Você decide | Claude define no planejamento | |

**User's choice:** Hex livre com default atual (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Sim, pré-preenchido | .env.example.jinja com POSTGRES_DB={slug}, WEB_PORT={porta}, hosts reais comentados | ✓ |
| Genérico como hoje | Valores sistema_base/localhost trocados à mão | |
| Você decide | Claude define quais chaves interpolar | |

**User's choice:** Sim, pré-preenchido (Recomendado)

---

## Estratégia copier update

| Option | Description | Selected |
|--------|-------------|----------|
| Tags semver | Releases tageadas v0.1.0...; copy/update usam a última tag estável | ✓ |
| Sempre HEAD | --vcs-ref HEAD sem disciplina de tags | |
| Você decide | Claude define o esquema | |

**User's choice:** Tags semver (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Pergunta booleana no Copier | incluir_app_exemplo (default sim) gera condicionalmente app + 3 pontos de acoplamento | ✓ |
| Re-remoção documentada | Re-executar protocolo de remoção após cada update | |
| Excluir exemplo dos updates | Update nunca toca apps/exemplo | |

**User's choice:** Pergunta booleana no Copier (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Marcadores inline | Conflitos estilo git nos arquivos (padrão do Copier moderno) | ✓ |
| Arquivos .rej separados | Diferenças rejeitadas em arquivos .rej | |
| Você decide | Claude escolhe e documenta | |

**User's choice:** Marcadores inline (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Ensaio roteirizado na fase | Ciclo completo uma vez (copy tag A → mudança → tag B → update → verificar) com roteiro no README | ✓ |
| Só documentar, provar na Fase 5 | Ensaio prático adiado | |
| Teste automatizado permanente | Script/CI rodando copy+update a cada mudança | |

**User's choice:** Ensaio roteirizado na fase (Recomendado)

---

## ops/ — backup e nginx

| Option | Description | Selected |
|--------|-------------|----------|
| Padrão PCA completo | Backup containerizado + retenção + ensaio de restore, generalizados | ✓ |
| Só pg_dump mínimo | Script simples + crontab de exemplo | |
| Você decide | Claude define o recorte | |

**User's choice:** Padrão PCA completo (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Serviço no compose | Container de backup no compose.yml — zero dependência do host | ✓ |
| Script manual / cron do host | Agendamento no cron do host (viola portabilidade) | |
| Você decide | Claude segue o padrão da PCA | |

**User's choice:** Serviço no compose (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Interpolado, pronto p/ copiar | ops/nginx/{slug}.conf com server_name e proxy_pass preenchidos | ✓ |
| Exemplo genérico com placeholders | <SUBDOMINIO>/<PORTA> para trocar à mão | |
| Você decide | Claude decide com base no pca.conf | |

**User's choice:** Interpolado, pronto p/ copiar (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Sim, generalizado em ops/ | MIGRACAO.md da PCA generalizado no gerado — prova documental do INF-04 | ✓ |
| Só seção no README | Fluxo de migração como seção do README | |
| Você decide | Claude avalia e decide o formato | |

**User's choice:** Sim, generalizado em ops/ (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Padrão PCA como default | Mesmo destino e política de retenção provados em produção | ✓ |
| Redefinir política no template | Política nova divergindo da operação validada | |
| Você decide | Claude replica o que encontrar | |

**User's choice:** Padrão PCA como default (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Sim, com defaults da PCA | Knobs (horário, retenção) via .env com defaults da PCA | ✓ |
| Fixo como na PCA | Valores hard-coded nos scripts | |
| Você decide | Claude define quais knobs expor | |

**User's choice:** Sim, com defaults da PCA (Recomendado)

| Option | Description | Selected |
|--------|-------------|----------|
| Espelhar o pca.conf | Vhost completo com HTTPS/redirect/certificados generalizados | ✓ |
| Só HTTP + nota sobre TLS | Vhost mínimo com comentário para adicionar TLS | |
| Você decide | Claude decide com base no pca.conf real | |

**User's choice:** Espelhar o pca.conf (Recomendado)
**Notes:** O usuário pediu explicação de vhost/proxy e TLS antes de decidir; a pergunta foi reapresentada após a explicação e a opção recomendada foi confirmada.

| Option | Description | Selected |
|--------|-------------|----------|
| Script + rotina documentada | Ensaio de restore generalizado + recomendação de periodicidade no runbook | ✓ |
| Só o script | Sem recomendação de periodicidade | |
| Você decide | Claude define o formato da recomendação | |

**User's choice:** Script + rotina documentada (Recomendado)

---

## Claude's Discretion

- Nomes exatos das variáveis e textos das perguntas do copier.yml
- Lista completa do _exclude além dos artefatos citados
- Filtros jinja de derivação (slug, sigla) e mensagens dos validators
- Recorte fino dos scripts auxiliares do ops/backup da PCA
- _min_copier_version e chaves técnicas do copier.yml
- Mecânica da condicional incluir_app_exemplo (blocos jinja vs arquivos condicionais)

## Deferred Ideas

None — discussion stayed within phase scope.
