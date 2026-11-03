from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import func, or_

from ..extensions import db
from ..models import OrdemServico, HistoricoOS, ServicoExecucao, Cliente, Tecnico
from ..services.permissoes import exigir_modulo
from ..services import os_service as servico
from ..services.auditoria_service import registrar_auditoria

ordens_servico_bp = Blueprint("ordens_servico", __name__, url_prefix="/ordens_servico")

STATUS_LABELS = {
    "aberta": "Aberta",
    "agendada": "Agendada",
    "em_deslocamento": "Em deslocamento",
    "em_atendimento": "Em atendimento",
    "em_execucao": "Em execução",
    "aguardando_material": "Aguardando material",
    "aguardando_cliente": "Aguardando cliente",
    "concluida": "Concluída",
    "entregue": "Entregue",
    "cancelada": "Cancelada",
}


@ordens_servico_bp.route("/")
@login_required
@exigir_modulo("ordens_servico")
def listar():
    status = request.args.get("status")
    tecnico_id = request.args.get("tecnico_id")
    termo = request.args.get("q", "").strip()

    query = OrdemServico.query.filter_by(empresa_id=current_user.empresa_id)
    if status:
        query = query.filter(OrdemServico.status == status)
    if tecnico_id:
        query = query.filter(OrdemServico.tecnico_id == int(tecnico_id))
    if termo:
        query = query.filter(
            or_(
                OrdemServico.numero.ilike(f"%{termo}%"),
                OrdemServico.descricao_solicitacao.ilike(f"%{termo}%"),
            )
        )
    ordens = query.order_by(OrdemServico.numero.desc()).all()

    tecnicos = (
        Tecnico.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Tecnico.nome)
        .all()
    )
    return render_template(
        "ordens_servico.html",
        ordens=ordens,
        status=status,
        tecnico_id=tecnico_id,
        q=termo,
        tecnicos=tecnicos,
        status_labels=STATUS_LABELS,
        badge_classes={
            "aberta": "secondary",
            "agendada": "info",
            "em_deslocamento": "primary",
            "em_atendimento": "warning",
            "em_execucao": "danger",
            "aguardando_material": "secondary",
            "aguardando_cliente": "secondary",
            "concluida": "success",
            "entregue": "success",
            "cancelada": "secondary",
        },
    )


@ordens_servico_bp.route("/novo", methods=["GET", "POST"])
@login_required
@exigir_modulo("ordens_servico")
def criar():
    clientes = (
        Cliente.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Cliente.nome)
        .all()
    )
    tecnicos = (
        Tecnico.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Tecnico.nome)
        .all()
    )

    if request.method == "POST":
        cliente_id = int(request.form.get("cliente_id") or 0)
        cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first()
        if not cliente:
            flash("Selecione um cliente válido.", "danger")
            return redirect(url_for("ordens_servico.criar"))

        seq = (db.session.query(func.max(OrdemServico.numero)).scalar() or 0) + 1
        os_ = OrdemServico(
            numero=seq,
            empresa_id=current_user.empresa_id,
            cliente_id=cliente.id,
            endereco=request.form.get("endereco") or cliente.endereco or "",
            telefone=request.form.get("telefone") or cliente.telefone or "",
            data_abertura=datetime.utcnow(),
            data_agendada=request.form.get("data_agendada") or None,
            horario=request.form.get("horario") or "",
            tecnico_id=int(request.form.get("tecnico_id") or 0) or None,
            status="aberta",
            descricao_solicitacao=request.form.get("descricao_solicitacao") or "",
            observacoes=request.form.get("observacoes") or "",
        )
        db.session.add(os_)
        db.session.commit()
        registrar_auditoria(current_user, "CRIACAO_OS", "ordens_servico", os_.id, f"OS {os_.numero}")
        flash("Ordem de serviço criada com sucesso.", "success")
        return redirect(url_for("ordens_servico.editar", ordem_id=os_.id))

    return render_template(
        "ordem_servico_form.html",
        form=request.form,
        edicao=False,
        os_reg=None,
        clientes=clientes,
        tecnicos=tecnicos,
        status_labels=STATUS_LABELS,
    )


@ordens_servico_bp.route("/<int:ordem_id>/editar", methods=["GET", "POST"])
@login_required
@exigir_modulo("ordens_servico")
def editar(ordem_id):
    os_reg = OrdemServico.query.filter_by(
        id=ordem_id, empresa_id=current_user.empresa_id
    ).first()
    if not os_reg:
        abort(404)

    clientes = (
        Cliente.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Cliente.nome)
        .all()
    )
    tecnicos = (
        Tecnico.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Tecnico.nome)
        .all()
    )

    if request.method == "POST":
        os_reg.endereco = request.form.get("endereco") or os_reg.cliente.endereco or ""
        os_reg.telefone = request.form.get("telefone") or os_reg.cliente.telefone or ""
        os_reg.data_agendada = None
        if request.form.get("data_agendada"):
            from datetime import datetime as dt

            os_reg.data_agendada = dt.strptime(request.form.get("data_agendada"), "%Y-%m-%d").date()
        if request.form.get("horario"):
            os_reg.horario = request.form.get("horario")
        if request.form.get("tecnico_id"):
            os_reg.tecnico_id = int(request.form["tecnico_id"])
        os_reg.descricao_solicitacao = request.form.get("descricao_solicitacao") or ""
        os_reg.observacoes = request.form.get("observacoes") or ""
        db.session.add(os_reg)
        db.session.commit()
        registrar_auditoria(current_user, "ATUALIZACAO_OS", "ordens_servico", os_reg.id, f"OS {os_reg.numero}")
        flash("Ordem de serviço atualizada com sucesso.", "success")
        return redirect(url_for("ordens_servico.editar", ordem_id=os_reg.id))

    return render_template(
        "ordem_servico_form.html",
        form=request.form,
        edicao=True,
        os_reg=os_reg,
        clientes=clientes,
        tecnicos=tecnicos,
        status_labels=STATUS_LABELS,
    )


@ordens_servico_bp.route("/<int:ordem_id>/status/<status>", methods=["POST"])
@login_required
@exigir_modulo("ordens_servico")
def alterar_status(ordem_id, status):
    os_reg = OrdemServico.query.filter_by(
        id=ordem_id, empresa_id=current_user.empresa_id
    ).first()
    if not os_reg:
        abort(404)

    ok, resultado = servico.alterar_status(os_reg, status, observacao=request.form.get("observacao"), usuario=current_user)
    if not ok:
        flash("Transição de status inválida.", "danger")
        return redirect(url_for("ordens_servico.editar", ordem_id=ordem_id))

    registrar_auditoria(current_user, "STATUS_OS", "ordens_servico", os_reg.id, f"OS {os_reg.numero} -> {status}")
    return redirect(url_for("ordens_servico.editar", ordem_id=ordem_id))


@ordens_servico_bp.route("/<int:ordem_id>/execucao", methods=["GET", "POST"])
@login_required
@exigir_modulo("ordens_servico")
def execucao(ordem_id):
    os_reg = OrdemServico.query.filter_by(
        id=ordem_id, empresa_id=current_user.empresa_id
    ).first()
    if not os_reg:
        abort(404)

    exec_registro = ServicoExecucao.query.filter_by(os_id=os_reg.id).first()

    if request.method == "POST":
        if not exec_registro:
            exec_registro = ServicoExecucao(os_id=os_reg.id)
        exec_registro.diagnostico = request.form.get("diagnostico") or ""
        exec_registro.servicos_executados = request.form.get("servicos_executados") or ""
        exec_registro.materiais_utilizados = request.form.get("materiais_utilizados") or ""
        exec_registro.equipamentos_instalados = request.form.get("equipamentos_instalados") or ""
        exec_registro.problemas_encontrados = request.form.get("problemas_encontrados") or ""
        exec_registro.recomendacoes = request.form.get("recomendacoes") or ""
        exec_registro.fotos = request.form.get("fotos") or ""
        exec_registro.inicio_em = None
        from datetime import datetime as dt

        if request.form.get("inicio_em"):
            exec_registro.inicio_em = dt.strptime(
                request.form.get("inicio_em"), "%Y-%m-%dT%H:%M"
            )
        if request.form.get("termino_em"):
            exec_registro.termino_em = dt.strptime(
                request.form.get("termino_em"), "%Y-%m-%dT%H:%M"
            )
        exec_registro.assinatura_cliente = request.form.get("assinatura_cliente") or None
        db.session.add(exec_registro)
        db.session.commit()
        registrar_auditoria(current_user, "EXECUICAO_OS", "ordens_servico", os_reg.id, f"Execução registrada na OS {os_reg.numero}")
        flash("Execução técnica registrada com sucesso.", "success")
        return redirect(url_for("ordens_servico.editar", ordem_id=ordem_id))

    return render_template(
        "ordem_execucao_form.html",
        form=request.form,
        os_reg=os_reg,
        exec_registro=exec_registro,
        status_labels=STATUS_LABELS,
    )


@ordens_servico_bp.route("/<int:ordem_id>/excluir", methods=["POST"])
@login_required
@exigir_modulo("ordens_servico")
def excluir(ordem_id):
    os_reg = OrdemServico.query.filter_by(
        id=ordem_id, empresa_id=current_user.empresa_id
    ).first()
    if not os_reg:
        abort(404)
    db.session.delete(os_reg)
    db.session.commit()
    registrar_auditoria(current_user, "EXCLUSAO_OS", "ordens_servico", os_reg.id, f"OS {os_reg.numero}")
    flash("Ordem de serviço excluída.", "success")
    return redirect(url_for("ordens_servico.listar"))
