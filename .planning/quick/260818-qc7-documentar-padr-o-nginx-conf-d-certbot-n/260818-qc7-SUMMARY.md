---
phase: quick-260818-qc7
plan: 01
subsystem: docs
tags: [readme, nginx, certbot, tls, publicacao]
requires: []
provides:
  - "README.md com os dois caminhos de publicação de vhost + TLS documentados"
affects: []
tech-stack:
  added: []
  patterns:
    - "conf.d + certbot --nginx como padrão operacional da família CFC"
key-files:
  created: []
  modified:
    - README.md
decisions:
  - "Caminho A (conf.d + certbot --nginx) apresentado como padrão operacional; Caminho B (sites-enabled + standalone) preservado como alternativa válida com o vhost renderizado como referência"
  - "Lista numerada encerrada no passo 5 (escolha de caminho), subseções h3 para os dois caminhos, validação externa retomada como passo 6"
metrics:
  duration: 1min
  completed: 2026-08-18
---

# Quick Task 260818-qc7: Documentar padrão nginx conf.d + certbot --nginx — Summary

**One-liner:** README passa a documentar o fluxo real da VM da família CFC (vhost `:80` em `/etc/nginx/conf.d/<hostname>.conf` + `sudo certbot --nginx` sem parar o nginx) como Caminho A, preservando o fluxo standalone com `ops/nginx/<slug>.conf` como Caminho B.

## O que foi feito

A seção "Publicação com proxy, TLS e DNS" do README.md foi reestruturada:

- **Passos 1-4 intactos** (preparar VM, `WEB_BIND_ADDRESS=127.0.0.1`, DNS, firewall 80/443), assim como o parágrafo introdutório sobre loopback e o parágrafo final sobre `ops/MIGRACAO.md`.
- **Passo 5** apresenta a escolha entre os dois caminhos e explica a diferença estrutural: no A o Certbot gera os blocos TLS a partir do bloco `:80` ativo; no B o vhost renderizado já nasce com 443 + redirect 301 e exige certificado emitido antes, com o Nginx parado.
- **Caminho A (h3)** — padrão operacional da família CFC: snippet nginx do bloco `:80` no formato real da PCA (`proxy_pass http://127.0.0.1:<porta>`, headers X-Forwarded-*, `proxy_read_timeout 60s`), `sudo nginx -t` + `sudo systemctl reload nginx`, e `sudo certbot --nginx -d <hostname>` — com a explicação de que o Certbot reescreve o próprio arquivo adicionando o bloco 443 e o redirect 301 ("managed by Certbot").
- **Caminho B (h3)** — conteúdo dos antigos passos 5-7 preservado: `certbot certonly --standalone` com nginx parado, `install` + `ln -sf` em sites-available/sites-enabled, `nginx -t` + restart, e a menção de que `ops/nginx/<slug>.conf` é renderizado pelo Copier e serve de referência do formato final do vhost.
- **Passo 6** — validação externa via `https://<hostname>/healthz` valendo para ambos os caminhos, com as invariantes reforçadas (loopback, Nginx como única fronteira, somente 80/443 públicas).

## Verificação

- Todos os greps do plano passam: `conf.d/<hostname>.conf`, `certbot --nginx -d <hostname>`, `certbot certonly --standalone`, `ops/nginx/<slug>.conf`, `managed by Certbot`.
- `grep -c 'certbot' README.md` = 3 (>= 3).
- `git diff --name-only` mostrou somente `README.md` (mudança doc-only).
- Lista numerada coerente: 1-5 + subseções + 6, sem passos órfãos; texto em pt-BR no tom impessoal-imperativo.

## Commits

| Task | Commit | Descrição |
|------|--------|-----------|
| 1 | 8a52155 | docs(quick-260818-qc7): documentar caminho conf.d + certbot --nginx na publicação |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

Nenhum — mudança exclusivamente documental.

## Self-Check: PASSED

- FOUND: README.md
- FOUND: commit 8a52155
