from datetime import datetime

from ..extensions import db


class Anexo(db.Model):
    __tablename__ = "anexos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    tipo = db.Column(db.String(20), nullable=False)
    registro_id = db.Column(db.Integer, nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho = db.Column(db.String(500))
    mime_type = db.Column(db.String(120))
    tamanho = db.Column(db.Integer)
    descricao = db.Column(db.String(250))
    criado_por = db.Column(db.String(150))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class AuditoriaLog(db.Model):
    __tablename__ = "auditoria_logs"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    usuario_nome = db.Column(db.String(150))
    acao = db.Column(db.String(40), nullable=False)
    modulo = db.Column(db.String(40), nullable=False)
    registro_id = db.Column(db.String(50))
    detalhes = db.Column(db.Text)
    ip = db.Column(db.String(45))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
