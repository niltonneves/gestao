from datetime import datetime

from ..extensions import db


class ProdutoServico(db.Model):
    __tablename__ = "produtos_servicos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    codigo = db.Column(db.String(30))
    descricao = db.Column(db.String(250), nullable=False)
    categoria = db.Column(db.String(60), default="Outros")
    tipo = db.Column(db.String(20), nullable=False, default="servico")
    unidade = db.Column(db.String(10), default="UN")
    custo = db.Column(db.Float, default=0)
    preco_venda = db.Column(db.Float, default=0)
    tempo_estimado = db.Column(db.Integer)
    garantia = db.Column(db.String(30))
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    orcamentos_itens = db.relationship(
        "ItemOrcamento", back_populates="produto_servico", lazy=True
    )
