def usuario_atual(request):
    """Expõe o usuário autenticado ao template — usado no layout base (ex.:
    nome/e-mail no cabeçalho) sem cada view precisar passá-lo explicitamente."""
    return {"usuario_atual": getattr(request, "user", None)}
