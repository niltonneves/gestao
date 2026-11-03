from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import Empresa, Usuario


def authenticate(email, senha):
    """Autentica um usuário a partir do e-mail e senha."""
    if not email or not senha:
        return None
    usuario = Usuario.query.filter(Usuario.email == email.strip().lower()).first()
    if usuario and usuario.ativo and check_password_hash(usuario.senha_hash, senha):
        return usuario
    return None


def create_admin(nome, email, senha, dados_empresa=None):
    """Cria a empresa e o primeiro usuário administrador (primeiro acesso)."""
    dados = dados_empresa or {}
    empresa = Empresa(
        razao_social=dados.get("razao_social") or f"{nome} – Serviços",
        nome_fantasia=dados.get("nome_fantasia") or "",
        cpf_cnpj=dados.get("cpf_cnpj") or "",
        inscricao_estadual=dados.get("inscricao_estadual") or "",
        endereco=dados.get("endereco") or "",
        cep=dados.get("cep") or "",
        telefone=dados.get("telefone") or "",
        whatsapp=dados.get("whatsapp") or "",
        email=dados.get("email") or email,
        site=dados.get("site") or "",
        responsavel=dados.get("responsavel") or nome,
        banco=dados.get("banco") or "",
        agencia=dados.get("agencia") or "",
        conta=dados.get("conta") or "",
        chave_pix=dados.get("chave_pix") or "",
        observacoes=dados.get("observacoes") or "",
    )
    db.session.add(empresa)
    db.session.commit()

    usuario = Usuario(
        empresa_id=empresa.id,
        nome=nome,
        email=email.strip().lower(),
        senha_hash=generate_password_hash(senha),
        perfil="admin",
        ativo=True,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario
