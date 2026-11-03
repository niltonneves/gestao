from datetime import datetime

from ..extensions import db


class OrdemServico(db.Model):
    __tablename__ = "ordens_servico"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False, index=True)
    empresa_id = db.Column(
        db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True
    )
    orcamento_id = db.Column(db.Integer, db.ForeignKey("orcamentos.id"))
    cliente_id = db.Column(
        db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True
    )
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_agendada = db.Column(db.DateTime)
    horario = db.Column(db.String(10))
    tecnico_id = db.Column(db.Integer, db.ForeignKey("tecnicos.id"))
    status = db.Column(db.String(25), default="aberta")
    descricao_solicitacao = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    orcamento = db.relationship("Orcamento", back_populates="os_gerados")
    cliente = db.relationship("Cliente", back_populates="ordens")
    tecnico = db.relationship("Tecnico", back_populates="ordens")
    historicos = db.relationship(
        "HistoricoOS", back_populates="ordem", cascade="all, delete-orphan", lazy=True
    )
    execucao = db.relationship(
        "ServicoExecucao", back_populates="ordem", cascade="all, delete-orphan"
    )

    @property
    def numero_exibicao(self):
        return f"OS-{self.numero:05d}"

    def add_historico(self, status_novo, observacao=None, usuario=None):
        anterior = self.status
        self.status = status_novo
        registro = HistoricoOS(
            os_id=self.id,
            status_anterior=anterior,
            status_novo=status_novo,
            observacao=observacao,
            usuario_id=getattr(usuario, "id", None),
            usuario_nome=getattr(usuario, "nome", None),
            data_hora=datetime.utcnow(),
        )
        self.historicos.append(registro)
        self.updated_at = datetime.utcnow()
        return registro


class HistoricoOS(db.Model):
    __tablename__ = "historico_os"

    id = db.Column(db.Integer, primary_key=True)
    os_id = db.Column(
        db.Integer, db.ForeignKey("ordens_servico.id"), nullable=False, index=True
    )
    status_anterior = db.Column(db.String(25))
    status_novo = db.Column(db.String(25), nullable=False)
    observacao = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    usuario_nome = db.Column(db.String(150))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    ordem = db.relationship("OrdemServico", back_populates="historicos")


class ServicoExecucao(db.Model):
    __tablename__ = "servicos_execucao"

    id = db.Column(db.Integer, primary_key=True)
    os_id = db.Column(
        db.Integer, db.ForeignKey("ordens_servico.id"), nullable=False, unique=True
    )
    diagnostico = db.Column(db.Text)
    servicos_executados = db.Column(db.Text)
    materiais_utilizados = db.Column(db.Text)
    equipamentos_instalados = db.Column(db.Text)
    problemas_encontrados = db.Column(db.Text)
    recomendacoes = db.Column(db.Text)
    fotos = db.Column(db.Text)
    inicio_em = db.Column(db.DateTime)
    termino_em = db.Column(db.DateTime)
    assinatura_cliente = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    ordem = db.relationship("OrdemServico", back_populates="execucao")
