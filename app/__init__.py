from flask import Flask

from .config import Config
from .extensions import db, migrate, login_manager
from .services.permissoes import pode

from .models.empresa import Empresa
from .models.usuario import Usuario
from .models.tecnico import Tecnico
from .models.cliente import Cliente
from .models.produto_servico import ProdutoServico
from .models.orcamento import Orcamento, ItemOrcamento
from .models.ordem_servico import OrdemServico, HistoricoOS, ServicoExecucao
from .models.financeiro import RegistroFinanceiro, Recibo
from .models.anexo import Anexo, AuditoriaLog


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object or Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Sua sessão expirou. Faça login novamente."
    login_manager.login_message_category = "warning"

    from .routes import register_blueprints

    register_blueprints(app)

    from .models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    @app.context_processor
    def inject_globals():
        return {"pode": pode}

    @app.errorhandler(404)
    def nao_encontrado(error):
        return "Página não encontrada.", 404

    @app.errorhandler(500)
    def erro_interno(error):
        return "Erro interno do servidor.", 500

    from pathlib import Path

    (Path(app.instance_path) / "uploads").mkdir(parents=True, exist_ok=True)

    return app
