---
task: 260818-qwd
status: complete
date: 2026-08-18
commits: [d39c357, 44ae507]
key-files:
  modified:
    - README.md
---

# Summary: documentar tag de release + resumo executável no README

## O que foi feito

**Task 1 (`d39c357`)** — Subseção `### Criando a tag de release` em "Releases e atualização do núcleo": pré-condições (árvore limpa + regressão verde), comandos `git tag -a v0.1.0 -m ...`, `git tag` e `git show v0.1.0 --stat`, e a explicação de como o Copier resolve a versão — sempre a última tag (PEP 440), nunca o HEAD; sem tag nenhuma cai no HEAD com versão sintética `0.0.0.postN.dev0+hash` e `DirtyLocalWarning` em árvore suja; `--vcs-ref=HEAD` apenas para ensaio/depuração. O passo 2 do "Nascimento local de um sistema" agora linka a subseção por âncora.

**Task 2 (`44ae507`)** — Seção final `## Resumo: nascimento completo em comandos`: jornada inteira só em comandos com uma linha de comentário `#` cada, exemplo concreto **financeiro** (`financeiro.sistemascfc.org`, porta `12010`, banco `financeiro`, sigla FIN, cor `#0F5132`, app exemplo incluído), da criação da tag ao `curl` HTTPS externo, pelo Caminho A de publicação (conf.d + `certbot --nginx`).

## Verificação

- Comandos-chave do Resumo são cópia fiel das seções detalhadas: `bin/copier copy`, `migrate --noinput`, `certbot --nginx -d`, `config -q`, `up -d --build db web`, mensagem do commit inicial e `git tag -a v0.1.0` aparecem exatamente 2 vezes cada (seção detalhada + Resumo).
- 7 seções `## `; a última é o Resumo; nenhuma seção existente removida ou alterada além do link no passo 2.
- Diff das duas tasks restrito a `README.md`.

## Desvios

Execução inline pelo orquestrador (sem executor em worktree) por restrição de limite de uso no momento do dispatch — mesmos commits atômicos e mesmos gates do plano aplicados.
