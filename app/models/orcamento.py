from datetime import datetime

from ..extensions import db


class Orcamento(db.Model):
    __tablename__ = "orcamentos"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False, index=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    cliente_id = db.Column(
        db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True
    )
    endereco_execucao = db.Column(db.String(200))
    responsavel_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    status = db.Column(db.String(20), default="elaboracao")
    data_emissao = db.Column(db.DateTime, default=datetime.utcnow)
    validade = db.Column(db.Date)
    condicao_pagamento = db.Column(db.String(40), default="Pix")
    prazo_execucao = db.Column(db.String(40))
    garantia = db.Column(db.String(40))
    observacoes = db.Column(db.Text)
    subtotal = db.Column(db.Float, default=0)
    desconto = db.Column(db.Float, default=0)
    desconto_tipo = db.Column(db.String(10), default="valor")
    acrescimos = db.Column(db.Float, default=0)
    entrada = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    aprovado = db.Column(db.Boolean, default=False)
    recusado = db.Column(db.Boolean, default=False)
    motivo_recusa = db.Column(db.Text)
    aprovado_por = db.Column(db.String(150))
    aprovado_em = db.Column(db.DateTime)
    aprovacao_observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = db.relationship("Cliente", back_populates="orcamentos")
    itens = db.relationship(
        "ItemOrcamento", back_populates="orcamento", cascade="all, delete-orphan", lazy=True
    )
    os_gerados = db.relationship("OrdemServico", back_populates="orcamento", lazy=True)


class ItemOrcamento(db.Model):
    __tablename__ = "itens_orcamento"

    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(
        db.Integer, db.ForeignKey("orcamentos.id"), nullable=False, index=True
    )
    produto_servico_id = db.Column(
        db.Integer, db.ForeignKey("produtos_servicos.id"), nullable=True
    )
    codigo = db.Column(db.String(30))
    descricao = db.Column(db.String(250), nullable=False)
    quantidade = db.Column(db.Float, default=1)
    unidade = db.Column(db.String(10), default="UN")
    valor_unitario = db.Column(db.Float, default=0)
    desconto = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)

    orcamento = db.relationship("Orcamento", back_populates="itens")
    produto_servico = db.relationship("ProdutoServico", back_populates="orcamentos_itens")
