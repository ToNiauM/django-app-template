import simple_history
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import Usuario

# User model customizado NÃO pode declarar `HistoricalRecords()` no próprio
# modelo: a FK de `history_user` da tabela histórica aponta para o user model,
# criando dependência circular num model swappable. A forma oficial documentada
# pelo django-simple-history é registrar via `register()` (D-22). Os modelos de
# domínio comuns seguem a convenção normal — `history = HistoricalRecords()`
# declarado no modelo (D-23, ver core/README.md).
simple_history.register(Usuario)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """`UserAdmin` padrão do Django adaptado para login por e-mail.

    Os `fieldsets`/`add_fieldsets` herdados referenciam o campo de login
    padrão do Django, que `core.Usuario` não tem — por isso são reescritos
    aqui. Sem ações em massa (D-15); se alguma entrar no futuro, deve
    persistir via `bulk_update_with_history` (queryset.update() não gera
    histórico).
    """

    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
    )
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações pessoais", {"fields": ("first_name", "last_name")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
