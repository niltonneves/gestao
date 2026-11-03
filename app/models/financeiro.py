from datetime import datetime

from ..extensions import db


class RegistroFinanceiro(db.Model):
    __tablename__ = "registros_financeiros"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    orcamento_id = db.Column(db.Integer, db.ForeignKey("orcamentos.id"))
    os_id = db.Column(db.Integer, db.ForeignKey("ordens_servico.id"))
    cliente_id = db.Column(
        db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True
    )
    tipo = db.Column(db.String(10), nullable=False, default="entrada")
    valor = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), default="pendente")
    forma_pagamento = db.Column(db.String(30))
    parcelas = db.Column(db.Integer)
    data_vencimento = db.Column(db.Date)
    data_pagamento = db.Column(db.Date)
    descricao = db.Column(db.String(250))
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = db.relationship("Cliente", back_populates="financeiros")
    orcamento = db.relationship("Orcamento")
    os = db.relationship("OrdemServico")


class Recibo(db.Model):
    __tablename__ = "recibos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    financeiro_id = db.Column(
        db.Integer, db.ForeignKey("registros_financeiros.id"), nullable=False
    )
    numero = db.Column(db.String(20), nullable=False)
    emitido_em = db.Column(db.DateTime, default=datetime.utcnow)
    arquivo = db.Column(db.String(255))
