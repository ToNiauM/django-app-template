# Template Django com Copier

Este repositório é o **template-fonte** de uma família de sistemas Django. Ele
não deve ser executado diretamente: use o Copier para criar um repositório
derivado, autocontido e versionado. O `README.md` que aparece no sistema
gerado é outro arquivo, renderizado a partir de `README.md.jinja`.

## Ferramenta isolada e versão aprovada

Instale o CLI somente no ambiente local do template; ele não pertence a
`requirements.txt` nem ao Python global:

```bash
python3 -m venv .venv-template
.venv-template/bin/pip install 'copier==9.17.1'
.venv-template/bin/copier --version
```

O diretório `.venv-template/` é ignorado pelo Git. Não substitua a versão
pinada sem uma nova avaliação de procedência e uma atualização explícita deste
contrato.

## Nascimento de um sistema

1. Parta de uma tag estável do template, por exemplo `v0.1.0`.
2. Execute a cópia a partir de um diretório de trabalho fora do destino:

   ```bash
   /caminho/para/template/.venv-template/bin/copier copy /caminho/para/template /caminho/para/novo-sistema
   ```

   Responda as oito perguntas: nome, slug, hostname, porta, banco, sigla, cor
   e inclusão do app exemplo. Os validators recusam valores fora do contrato
   antes de renderizar arquivos.
3. Entre no diretório gerado, copie `.env.example` para `.env` e preencha os
   segredos. As respostas Copier ficam em `.copier-answers.yml` e não contêm
   segredos.
4. Inicie o repositório do sistema e faça o primeiro commit, preservando o
   arquivo de respostas necessário para updates:

   ```bash
   cd /caminho/para/novo-sistema
   cp .env.example .env
   git init
   git add .
   git commit -m "chore: inicia sistema gerado pelo Copier"
   ```

5. Siga o README renderizado para configurar Docker Compose, migrações, proxy
   e DNS. Não há `_tasks`, migrations Copier ou qualquer automação oculta após
   a cópia: cada passo é consciente e auditável.

### Segredos locais

Gere a chave Django sem a colocar em respostas Copier:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Cole o resultado diretamente em `SECRET_KEY` no `.env`. Preencha também
`POSTGRES_PASSWORD`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` e `R2_BUCKET`
diretamente no `.env`; nunca crie perguntas Copier, valores padrão reais ou
commits para essas credenciais.

### Convenção de portas da família

A porta 8000 é apenas o default e pode ser sobrescrita pela pergunta Copier.
Mantenha uma alocação documentada para evitar colisões no host:

| Faixa | Uso convencional |
| --- | --- |
| 8000 | Novo sistema / desenvolvimento local |
| 8001 | Primeiro sistema publicado da família |
| 8002 | Segundo sistema publicado da família |
| 8003–8099 | Próximos sistemas, por registro operacional |

O Compose continua ligado a `127.0.0.1`; o proxy do host é a única fronteira
de exposição externa.

## Releases e atualização do núcleo

Publique mudanças conscientes do template em tags semver (`v0.1.0`, `v0.2.0`
etc.). Antes de criar uma tag, revise o diff gerado, execute as verificações
cabíveis e só então registre a release. Sistemas derivados só recebem mudanças
quando o operador decide atualizar para uma tag posterior.

Faça `copier update` exclusivamente com o Git limpo:

```bash
git status --short
# sem saída: árvore limpa
/caminho/para/template/.venv-template/bin/copier update
```

Para mudar uma resposta, use o próprio Copier, nunca edite
`.copier-answers.yml` manualmente. Por exemplo, para remover o app exemplo:

```bash
/caminho/para/template/.venv-template/bin/copier update --data incluir_app_exemplo=false
```

Se houver conflitos, revise os marcadores inline `<<<<<<<`, `=======` e
`>>>>>>>`, escolha a versão correta, rode testes e faça um commit do resultado.
O ensaio contratual desta evolução é A → B: copie na tag A, altere o núcleo e
tageie B, execute `copier update`, valide a mudança e confirme que o app
exemplo removido não reaparece. Quando disponível, execute também:

```bash
.template-tests/test_copier_update.sh
```

Esse roteiro prova o mecanismo de atualização; ele não substitui revisão,
testes e commit em cada sistema derivado.
