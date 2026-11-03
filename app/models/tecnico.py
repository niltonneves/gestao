from datetime import datetime

from ..extensions import db


class Tecnico(db.Model):
    __tablename__ = "tecnicos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=True
    )
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    especialidade = db.Column(db.String(80))
    situacao = db.Column(db.String(15), default="ativo")
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="tecnico", lazy=True)
    ordens = db.relationship("OrdemServico", back_populates="tecnico", lazy=True)
