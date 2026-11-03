from flask import Blueprint

from . import (  # noqa: E402,F401
    auth,
    dashboard,
    clientes,
    catalogo,
    orcamentos,
    ordens_servico,
    financeiro,
    relatorios,
    configuracoes,
    administracao,
    install,
)


def register_blueprints(app):
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(dashboard.dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(clientes.clientes_bp, url_prefix="/clientes")
    app.register_blueprint(catalogo.catalogo_bp, url_prefix="/catalogo")
    app.register_blueprint(orcamentos.orcamentos_bp, url_prefix="/orcamentos")
    app.register_blueprint(ordens_servico.ordens_servico_bp, url_prefix="/ordens_servico")
    app.register_blueprint(financeiro.financeiro_bp, url_prefix="/financeiro")
    app.register_blueprint(relatorios.relatorios_bp, url_prefix="/relatorios")
    app.register_blueprint(configuracoes.configuracoes_bp, url_prefix="/configuracoes")
    app.register_blueprint(administracao.administracao_bp, url_prefix="/administracao")
    app.register_blueprint(install.install_bp, url_prefix="/install")
