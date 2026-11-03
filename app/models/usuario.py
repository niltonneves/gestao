from datetime import datetime

from flask_login import UserMixin

from ..extensions import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default="atendente")
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    ultimo_login = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship("Empresa", back_populates="usuarios", lazy=True)
    tecnico = db.relationship("Tecnico", back_populates="usuario", lazy=True)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<Usuario {self.email}>"
