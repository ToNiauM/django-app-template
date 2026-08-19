# Itens adiados — Fase 06

## Testes Copier ainda pinados na tag v0.1.0 (descoberto no plano 06-01)

Desde a criação da tag de release `v0.1.0` (quick task 260818-qwd), o Copier
passou a copiar por padrão a **última tag** quando a fonte é um repositório git
— e não o estado atual da árvore de trabalho. O plano 06-01 corrigiu isso (via
`--vcs-ref=HEAD`) nos arquivos do seu escopo: `test_04_05_backup.py`,
`test_06_persistencia.py` e `test_05_nascimento.sh`.

Os testes abaixo continuam rendendo a partir de `v0.1.0` (passam hoje, mas
validam conteúdo congelado da tag, não os fontes atuais):

- `.template-tests/test_04_03_identity.py`
- `.template-tests/test_copier_copy.sh`
- `.template-tests/test_04_06_operations.py`
- `.template-tests/test_04_04_optional_exemplo.py`

**Correção sugerida:** adicionar `--vcs-ref=HEAD` aos `copier copy` desses
testes (mesmo padrão aplicado no 06-01). Fora do escopo do plano 06-01 —
arquivos não listados em `files_modified`.
