from datetime import datetime

from ..extensions import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    tipo = db.Column(db.String(10), nullable=False, default="pf")
    nome = db.Column(db.String(150), nullable=False)
    nome_fantasia = db.Column(db.String(150))
    cpf_cnpj = db.Column(db.String(20), index=True)
    rg = db.Column(db.String(20))
    inscricao_estadual = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(150))
    cep = db.Column(db.String(10))
    endereco = db.Column(db.String(150))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(50))
    bairro = db.Column(db.String(80))
    cidade = db.Column(db.String(80))
    estado = db.Column(db.String(20))
    contato_responsavel = db.Column(db.String(150))
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orcamentos = db.relationship("Orcamento", back_populates="cliente", lazy=True)
    ordens = db.relationship("OrdemServico", back_populates="cliente", lazy=True)
    financeiros = db.relationship("RegistroFinanceiro", back_populates="cliente", lazy=True)
