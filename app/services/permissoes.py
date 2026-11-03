"""Controle de permissões por nível de acesso."""

from flask import abort, current_app
from flask_login import current_user
from functools import wraps
from sqlalchemy import or_

ALL_MODULOS = [
    "dashboard",
    "clientes",
    "catalogo",
    "orcamentos",
    "ordens_servico",
    "agenda",
    "tecnicos",
    "financeiro",
    "relatorios",
    "documentos",
    "configuracoes",
    "administracao",
]


PERMISSOES = {
    "admin": set(ALL_MODULOS),
    "atendente": {
        "dashboard",
        "clientes",
        "catalogo",
        "orcamentos",
        "ordens_servico",
        "agenda",
        "documentos",
    },
    "tecnico": {
        "dashboard",
        "ordens_servico",
        "agenda",
        "tecnicos",
    },
    "financeiro": {
        "dashboard",
        "financeiro",
        "relatorios",
        "documentos",
    },
}


def modulo_permissao(usuario):
    """Retorna o conjunto de módulos permitidos para o usuário autenticado."""
    if not usuario or not getattr(usuario, "is_authenticated", False):
        return set()
    if usuario.perfil == "admin":
        return set(ALL_MODULOS)
    return set(PERMISSOES.get(usuario.perfil, set()))


def pode(usuario, modulo):
    """Verifica se o usuário pode acessar o módulo informado."""
    return modulo in modulo_permissao(usuario)


def exigir_modulo(modulo):
    """Decorator que restringe o acesso ao módulo."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not pode(current_user, modulo):
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
