# Phase 6: Customização Visual e Persistência de Dados - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-19
**Phase:** 6-Customização Visual e Persistência de Dados
**Areas discussed:** Mecanismo e local dos logos, Posicionamento dos logos no UI, PWA (logo e nome), Persistência do banco no host, Documentação da customização
**Mode:** `--auto` — todas as áreas auto-selecionadas; em cada questão a opção recomendada foi escolhida sem prompt interativo.

---

## Mecanismo e local dos logos

| Option | Description | Selected |
|--------|-------------|----------|
| Arquivos estáticos em caminhos fixos | `core/static/img/logo-entidade.svg` e `logo-subsistema.svg`, placeholders substituíveis — coerente com D-20 e portabilidade | ✓ |
| Caminhos configuráveis via `.env` | Indireção extra sem benefício; o nome fixo é o contrato | |
| Upload via admin | Exigiria media storage — nova capacidade, fora do escopo | |

**Choice:** Arquivos estáticos em caminhos fixos (recommended default)
**Notes:** Placeholders SVG neutros sempre presentes; texto de identidade (D-16) permanece ao lado.

---

## Posicionamento dos logos no UI

| Option | Description | Selected |
|--------|-------------|----------|
| Subsistema no shell, entidade no login + rodapé da aside; admin intocado | Preserva o override cirúrgico do admin (D-14) | ✓ |
| Logo também no admin | Amplia a superfície tocada do admin sem pedido do usuário | |

**Choice:** Subsistema no shell, entidade no login/rodapé (recommended default)

---

## PWA — logo e nome

| Option | Description | Selected |
|--------|-------------|----------|
| Manter mecanismo atual e documentá-lo | Nome via `.env` (manifest_view, D-16/D-18); ícones = substituir arquivos de nome fixo ou regenerar via `ops/gerar_icones_pwa.py` | ✓ |
| Nova variável/asset pipeline para ícones | Automatismo pós-geração contraria D-40 | |

**Choice:** Mecanismo atual documentado como local único (recommended default)

---

## Persistência do banco no host

| Option | Description | Selected |
|--------|-------------|----------|
| Bind mount com path via `.env` (default `./dados/pg`) | Sobrevive a `down -v` por construção; aplica D-50 ".env primeiro" | ✓ |
| Named volume `external: true` | Sobrevive a `down -v`, mas exige criação manual do volume (passo extra = acoplamento indevido) e dados ficam escondidos em `/var/lib/docker` | |
| Manter named volume + só documentar o risco | Não atende o pedido explícito do usuário | |

**Choice:** Bind mount configurável via `.env` (recommended default)
**Notes:** Diretório de dados entra no `.gitignore`; runbook de migração continua via dump.

---

## Documentação da customização

| Option | Description | Selected |
|--------|-------------|----------|
| Seção única "Customização de marca" no README gerado + core/README.md | Um só lugar para achar todos os pontos | ✓ |
| Espalhar notas por arquivo | Contraria o pedido de clareza | |

**Choice:** Seção única (recommended default)

## Claude's Discretion

- Desenho dos placeholders SVG e classes de exibição
- PNG como formato alternativo dos logos
- Favicon (se entrar, mesmo contrato de arquivo fixo)
- Extensão opcional do `gerar_icones_pwa.py` para partir do logo do subsistema
- Nome exato da variável de dados (`PGDATA_DIR`) e diretório default
- Asserções de teste novas

## Deferred Ideas

- Upload de logos via admin (media storage) — fase própria futura
- Variantes de logo para dark mode — template não tem dark mode
