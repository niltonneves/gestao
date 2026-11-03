from datetime import datetime

from ..extensions import db


class Empresa(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(120))
    cpf_cnpj = db.Column(db.String(20))
    inscricao_estadual = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cep = db.Column(db.String(10))
    telefone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(120))
    site = db.Column(db.String(100))
    logotipo = db.Column(db.String(255))
    responsavel = db.Column(db.String(120))
    banco = db.Column(db.String(60))
    agencia = db.Column(db.String(20))
    conta = db.Column(db.String(30))
    chave_pix = db.Column(db.String(60))
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuarios = db.relationship("Usuario", back_populates="empresa", lazy=True)
