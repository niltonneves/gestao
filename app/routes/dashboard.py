from datetime import datetime

from flask import Blueprint, render_template, jsonify
from flask_login import login_required

from ..extensions import db
from ..models import (
    Cliente,
    Orcamento,
    OrdemServico,
    RegistroFinanceiro,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def dashboard():
    from flask_login import current_user

    from ..services.permissoes import pode

    if not pode(current_user, "dashboard"):
        from flask import abort

        abort(403)

    hoje = datetime.utcnow().date()
    empresa_id = current_user.empresa_id

    total_clientes = Cliente.query.filter_by(empresa_id=empresa_id).count()
    orcamentos_abertos = Orcamento.query.filter(
        Orcamento.empresa_id == empresa_id,
        Orcamento.status.notin_(["aprovado", "recusado", "cancelado", "vencido"]),
    ).count()
    orcamentos_enviados = Orcamento.query.filter(
        Orcamento.empresa_id == empresa_id, Orcamento.status == "enviado"
    ).count()
    orcamentos_aprovados = Orcamento.query.filter(
        Orcamento.empresa_id == empresa_id, Orcamento.status == "aprovado"
    ).count()
    orcamentos_vencidos = Orcamento.query.filter(
        Orcamento.empresa_id == empresa_id, Orcamento.validade < hoje
    ).count()
    os_abertas = OrdemServico.query.filter(
        OrdemServico.empresa_id == empresa_id, OrdemServico.status == "aberta"
    ).count()
    os_andamento = OrdemServico.query.filter(
        OrdemServico.empresa_id == empresa_id, OrdemServico.status == "em_atendimento"
    ).count()
    os_concluidas = OrdemServico.query.filter(
        OrdemServico.empresa_id == empresa_id, OrdemServico.status == "concluida"
    ).count()
    os_atrasadas = OrdemServico.query.filter(
        OrdemServico.empresa_id == empresa_id,
        OrdemServico.status.notin_(["concluida", "cancelada", "entregue"]),
        OrdemServico.data_agendada < hoje,
    ).count()
    recebidos = RegistroFinanceiro.query.filter(
        RegistroFinanceiro.empresa_id == empresa_id,
        RegistroFinanceiro.tipo == "entrada",
        RegistroFinanceiro.status == "pago",
    ).count()

    dados = {
        "total_clientes": total_clientes,
        "orcamentos_abertos": orcamentos_abertos,
        "orcamentos_enviados": orcamentos_enviados,
        "orcamentos_aprovados": orcamentos_aprovados,
        "orcamentos_vencidos": orcamentos_vencidos,
        "os_abertas": os_abertas,
        "os_andamento": os_andamento,
        "os_concluidas": os_concluidas,
        "os_atrasadas": os_atrasadas,
        "registros_recebidos": recebidos,
    }

    return render_template("dashboard.html", dados=dados)
