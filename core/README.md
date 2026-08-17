# `core/` — convenções não-óbvias

Este documento registra 3 convenções do kernel `core/` que não são óbvias a
partir da leitura do código sozinho — quebrá-las produz bugs silenciosos.

## 1. "Hoje" sempre via `timezone.localdate()`

Toda lógica que precisar da data atual **deve** usar
`django.utils.timezone.localdate()` — nunca `timezone.now().date()` nem
`datetime.date.today()`.

Com `USE_TZ=True`, `timezone.now()` sempre retorna um datetime em UTC,
independente de `TIME_ZONE`. Às 21h de um dia em Brasília (UTC−3),
`timezone.now().date()` já retorna o dia seguinte. `datetime.date.today()`
tem o problema oposto: usa o fuso horário do sistema operacional, e dentro
do container Docker o SO está em UTC mesmo com
`TIME_ZONE="America/Sao_Paulo"` configurado no settings. `localdate()` é o
único caminho que converte corretamente para o fuso configurado antes de
extrair a data.

## 2. `AXES_USERNAME_FORM_FIELD = "username"` é proposital

Em `config/settings/base.py`, `AXES_USERNAME_FORM_FIELD` está fixado como
`"username"` — mesmo o projeto usando login por e-mail
(`USERNAME_FIELD = "email"` em `core.Usuario`). **Não "corrigir" para
`"email"`.**

Django sempre usa o kwarg literal `username=` ao chamar `authenticate()`,
independente do `USERNAME_FIELD` do model customizado. Se
`AXES_USERNAME_FORM_FIELD` fosse `"email"`, o django-axes procuraria a
chave `"email"` no dicionário de credenciais — chave que nunca existe nesse
dicionário — e gravaria toda tentativa de login com `username=None`,
quebrando o lockout por usuário+IP sem levantar nenhum erro visível.

## 3. `AUTH_USER_MODEL` nunca muda depois da migração `0001`

`AUTH_USER_MODEL = "core.Usuario"` está definido desde antes de qualquer
migração existir (Plan 01-01), e `core.Usuario` é o próprio modelo migrado
na `0001` (Plan 01-03). Trocar `AUTH_USER_MODEL` depois disso é uma
operação destrutiva no Django — não há caminho suportado de migração
in-place para outro modelo de usuário num banco com dados reais.

Essa é justamente a razão de o `Usuario` customizado existir desde o
primeiro momento do template: preserva a viabilidade de SSO futuro entre os
sistemas da família sem exigir uma reescrita de banco mais adiante.
