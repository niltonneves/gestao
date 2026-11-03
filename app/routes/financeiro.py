from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import RegistroFinanceiro, Recibo, Orcamento, OrdemServico, Cliente
from ..services.permissoes import exigir_modulo
from ..services.auditoria_service import registrar_auditoria

financeiro_bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")


@financeiro_bp.route("/")
@login_required
@exigir_modulo("financeiro")
def listar():
    registros = (
        RegistroFinanceiro.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(RegistroFinanceiro.id.desc())
        .all()
    )
    recebidos = sum(
        r.valor
        for r in registros
        if r.tipo == "entrada" and r.status == "pago"
    )
    pendentes = sum(
        r.valor
        for r in registros
        if r.tipo == "entrada" and r.status in ("pendente", "parcialmente_pago")
    )
    saidas = sum(r.valor for r in registros if r.tipo == "saida" and r.status == "pago")

    return render_template(
        "financeiro.html",
        registros=registros,
        recebidos=recebidos,
        pendentes=pendentes,
        saidas=saidas,
        badge_classes={
            "pendente": "warning",
            "parcialmente_pago": "info",
            "pago": "success",
            "atrasado": "danger",
            "cancelado": "secondary",
        },
    )


@financeiro_bp.route("/novo", methods=["GET", "POST"])
@login_required
@exigir_modulo("financeiro")
def criar():
    orcamentos = Orcamento.query.filter_by(empresa_id=current_user.empresa_id).all()
    ordens = OrdemServico.query.filter_by(empresa_id=current_user.empresa_id).all()
    clientes = Cliente.query.filter_by(empresa_id=current_user.empresa_id).all()

    if request.method == "POST":
        cliente_id = int(request.form.get("cliente_id") or 0)
        cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first()
        if not cliente:
            flash("Selecione um cliente válido.", "danger")
            return redirect(url_for("financeiro.novo"))

        orcamento_id = None
        os_id = None
        if request.form.get("orcamento_id"):
            orcamento_id = int(request.form["orcamento_id"])
        if request.form.get("ordem_servico_id"):
            os_id = int(request.form["ordem_servico_id"])

        registro = RegistroFinanceiro(
            empresa_id=current_user.empresa_id,
            orcamento_id=orcamento_id,
            os_id=os_id,
            cliente_id=cliente.id,
            tipo=request.form.get("tipo", "entrada"),
            valor=float(request.form.get("valor") or 0),
            status=request.form.get("status", "pendente"),
            forma_pagamento=request.form.get("forma_pagamento", ""),
            parcelas=int(request.form.get("parcelas") or 0) or None,
            data_vencimento=None,
            data_pagamento=None,
            descricao=request.form.get("descricao", ""),
            observacoes=request.form.get("observacoes", ""),
        )
        db.session.add(registro)
        db.session.commit()
        registrar_auditoria(current_user, "CRIACAO_FINANCEIRO", "financeiro", registro.id, registro.descricao)
        flash("Registro financeiro criado com sucesso.", "success")
        return redirect(url_for("financeiro.listar"))

    return render_template(
        "financeiro_form.html",
        form=request.form,
        orcamentos=orcamentos,
        ordens=ordens,
        clientes=clientes,
        edicao=False,
    )


@financeiro_bp.route("/<int:registro_id>/pagamento", methods=["POST"])
@login_required
@exigir_modulo("financeiro")
def registrar_pagamento(registro_id):
    registro = RegistroFinanceiro.query.filter_by(
        id=registro_id, empresa_id=current_user.empresa_id
    ).first()
    if not registro:
        abort(404)

    valor = float(request.form.get("valor") or 0)
    registro.valor -= valor
    if registro.valor <= 0:
        registro.status = "pago"
        registro.data_pagamento = request.form.get("data_pagamento") or None
    else:
        registro.status = "parcialmente_pago"
        registro.data_pagamento = request.form.get("data_pagamento") or None

    db.session.commit()
    registrar_auditoria(current_user, "PAGAMENTO_FINANCEIRO", "financeiro", registro.id, f"Valor pago: {valor}")
    flash("Pagamento registrado com sucesso.", "success")
    return redirect(url_for("financeiro.listar"))


@financeiro_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
@exigir_modulo("financeiro")
def editar(registro_id):
    registro = RegistroFinanceiro.query.filter_by(
        id=registro_id, empresa_id=current_user.empresa_id
    ).first()
    if not registro:
        abort(404)

    if request.method == "POST":
        registro.cliente_id = int(request.form.get("cliente_id") or registro.cliente_id)
        registro.orcamento_id = (
            int(request.form["orcamento_id"]) if request.form.get("orcamento_id") else None
        )
        registro.os_id = (
            int(request.form["ordem_servico_id"]) if request.form.get("ordem_servico_id") else None
        )
        registro.tipo = request.form.get("tipo", registro.tipo)
        registro.valor = float(request.form.get("valor") or 0)
        registro.status = request.form.get("status", registro.status)
        registro.forma_pagamento = request.form.get("forma_pagamento", "")
        registro.parcelas = int(request.form.get("parcelas") or 0) or None
        registro.descricao = request.form.get("descricao", "")
        registro.observacoes = request.form.get("observacoes", "")
        db.session.commit()
        registrar_auditoria(current_user, "ATUALIZACAO_FINANCEIRO", "financeiro", registro.id, registro.descricao)
        flash("Registro financeiro atualizado com sucesso.", "success")
        return redirect(url_for("financeiro.listar"))

    return render_template("financeiro_form.html", form=request.form, edicao=True, registro=registro)
