from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import func, or_

from ..extensions import db
from ..models import Orcamento, ItemOrcamento, OrdemServico, Cliente, ProdutoServico
from ..services.permissoes import exigir_modulo
from ..services import orcamento_service as servico
from ..services.auditoria_service import registrar_auditoria

orcamentos_bp = Blueprint("orcamentos", __name__, url_prefix="/orcamentos")


@orcamentos_bp.route("/")
@login_required
@exigir_modulo("orcamentos")
def listar():
    status = request.args.get("status")
    termo = request.args.get("q", "").strip()

    query = Orcamento.query.filter_by(empresa_id=current_user.empresa_id)
    if status:
        query = query.filter(Orcamento.status == status)
    if termo:
        query = query.join(Cliente).filter(
            or_(
                Cliente.nome.ilike(f"%{termo}%"),
                Cliente.nome_fantasia.ilike(f"%{termo}%"),
                Cliente.cpf_cnpj.ilike(f"%{termo}%"),
            )
        )
    orcamentos = query.order_by(Orcamento.numero.desc()).all()

    por_status = {}
    for o in orcamentos:
        por_status[o.status] = por_status.get(o.status, 0) + 1

    status_badge = {
        "elaboracao": "secondary",
        "enviado": "info",
        "aguardando_aprovacao": "warning",
        "aprovado": "success",
        "recusado": "danger",
        "vencido": "danger",
        "cancelado": "secondary",
    }

    return render_template(
        "orcamentos.html",
        orcamentos=orcamentos,
        por_status=por_status,
        status=status,
        q=request.args.get("q", ""),
        status_badge=status_badge,
    )


@orcamentos_bp.route("/novo", methods=["GET", "POST"])
@login_required
@exigir_modulo("orcamentos")
def criar():
    clientes = (
        Cliente.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Cliente.nome)
        .all()
    )
    produtos = (
        ProdutoServico.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(ProdutoServico.codigo)
        .all()
    )

    if request.method == "POST":
        cliente_id = int(request.form.get("cliente_id") or 0)
        cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first()
        if not cliente:
            flash("Selecione um cliente válido.", "danger")
            return redirect(url_for("orcamentos.criar"))

        dados = {
            "endereco_execucao": request.form.get("endereco_execucao", ""),
            "condicao_pagamento": request.form.get("condicao_pagamento", "Pix"),
            "prazo_execucao": request.form.get("prazo_execucao", ""),
            "garantia": request.form.get("garantia", ""),
            "observacoes": request.form.get("observacoes", ""),
        }
        orcamento = servico.criar_orcamento(
            current_user.empresa_id, cliente.id, current_user.id, dados
        )
        orcamento.cliente_id = cliente.id
        orcamento.numero = (
            db.session.query(func.max(Orcamento.numero))
            .filter(Orcamento.empresa_id == current_user.empresa_id)
            .scalar()
            or 0
        ) + 1
        db.session.add(orcamento)
        db.session.commit()

        if request.form.get("acao") == "adicionar_item":
            item = ItemOrcamento(
                orcamento_id=orcamento.id,
                codigo=request.form.get("item_codigo", ""),
                descricao=request.form.get("item_descricao", ""),
                quantidade=float(request.form.get("item_quantidade") or 1),
                unidade=request.form.get("item_unidade") or "UN",
                valor_unitario=float(request.form.get("item_valor_unitario") or 0),
                desconto=float(request.form.get("item_desconto") or 0),
                total=0,
            )
            item.total = servico._total_item(item)
            orcamento.itens.append(item)
            servico.salvar_totais(orcamento)
            flash("Item adicionado ao orçamento.", "success")
            return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))

        registrar_auditoria(current_user, "CRIACAO_ORCAMENTO", "orcamentos", orcamento.id, f"Orçamento {orcamento.numero}")
        flash("Orçamento criado com sucesso.", "success")
        return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))

    return render_template(
        "orcamento_form.html",
        form=request.form,
        edicao=False,
        orcamento=None,
        clientes=clientes,
        produtos=produtos,
        itens=[],
        condicoes=["Pix", "Dinheiro", "Cartão", "Transferência", "Parcelamento"],
        totais={
            "subtotal": 0,
            "desconto": 0,
            "liquido": 0,
            "entrada": 0,
            "total": 0,
        },
    )


@orcamentos_bp.route("/<int:orcamento_id>/editar", methods=["GET", "POST"])
@login_required
@exigir_modulo("orcamentos")
def editar(orcamento_id):
    orcamento = Orcamento.query.filter_by(
        id=orcamento_id, empresa_id=current_user.empresa_id
    ).first()
    if not orcamento:
        abort(404)

    clientes = (
        Cliente.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Cliente.nome)
        .all()
    )
    produtos = (
        ProdutoServico.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(ProdutoServico.codigo)
        .all()
    )

    if request.method == "POST":
        orcamento.endereco_execucao = request.form.get("endereco_execucao", "") or orcamento.cliente.endereco or ""
        orcamento.condicao_pagamento = request.form.get("condicao_pagamento", orcamento.condicao_pagamento) or "Pix"
        orcamento.prazo_execucao = request.form.get("prazo_execucao", "")
        orcamento.garantia = request.form.get("garantia", "")
        orcamento.observacoes = request.form.get("observacoes", "")
        orcamento.validade = (
            datetime.strptime(request.form.get("validade", ""), "%Y-%m-%d").date()
            if request.form.get("validade")
            else orcamento.validade
        )
        orcamento.desconto = float(request.form.get("desconto") or 0)
        orcamento.desconto_tipo = request.form.get("desconto_tipo") or "valor"
        orcamento.acrescimos = float(request.form.get("acrescimos") or 0)
        orcamento.entrada = float(request.form.get("entrada") or 0)
        db.session.add(orcamento)
        totais = servico.salvar_totais(orcamento)
        if request.form.get("acao") == "adicionar_item":
            item = ItemOrcamento(
                orcamento_id=orcamento.id,
                codigo=request.form.get("item_codigo", ""),
                descricao=request.form.get("item_descricao", ""),
                quantidade=float(request.form.get("item_quantidade") or 1),
                unidade=request.form.get("item_unidade") or "UN",
                valor_unitario=float(request.form.get("item_valor_unitario") or 0),
                desconto=float(request.form.get("item_desconto") or 0),
                total=servico._total_item(
                    ItemOrcamento(
                        quantidade=float(request.form.get("item_quantidade") or 1),
                        valor_unitario=float(request.form.get("item_valor_unitario") or 0),
                        desconto=float(request.form.get("item_desconto") or 0),
                    )
                ),
            )
            orcamento.itens.append(item)
            servico.salvar_totais(orcamento)
            flash("Item adicionado ao orçamento.", "success")
            return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))

        if request.form.get("acao") == "remover_item":
            item_id = int(request.form.get("item_id") or 0)
            item = orcamento.itens.filter_by(id=item_id).first()
            if item:
                orcamento.itens.remove(item)
            servico.salvar_totais(orcamento)
            flash("Item removido do orçamento.", "success")
            return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))

        db.session.commit()
        registrar_auditoria(current_user, "ATUALIZACAO_ORCAMENTO", "orcamentos", orcamento.id, f"Orçamento {orcamento.numero}")
        flash("Orçamento atualizado com sucesso.", "success")
        return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))

    itens = list(orcamento.itens)
    totais = servico.salvar_totais(orcamento)
    return render_template(
        "orcamento_form.html",
        form=request.form,
        edicao=True,
        orcamento=orcamento,
        clientes=clientes,
        produtos=produtos,
        itens=itens,
        condicoes=["Pix", "Dinheiro", "Cartão", "Transferência", "Parcelamento"],
        totais=totais,
    )


@orcamentos_bp.route("/<int:orcamento_id>/status/<status>", methods=["POST"])
@login_required
@exigir_modulo("orcamentos")
def alterar_status(orcamento_id, status):
    orcamento = Orcamento.query.filter_by(
        id=orcamento_id, empresa_id=current_user.empresa_id
    ).first()
    if not orcamento:
        abort(404)

    permitidos = servico.ORC_TRANSICOES.get(orcamento.status, [])
    if status not in permitidos:
        flash("Transição de status inválida.", "danger")
        return redirect(url_for("orcamentos.editar", orcamento_id=orcamento_id))

    from datetime import datetime

    if status == "enviado":
        orcamento.status = servico.enviar_orcamento(orcamento)
    elif status == "aguardando_aprovacao":
        orcamento.status = servico.aguardar_aprovacao(orcamento)
    elif status == "aprovado":
        orcamento.status = "aprovado"
        orcamento.aprovado = True
        orcamento.aprovado_por = current_user.nome
        orcamento.aprovado_em = datetime.utcnow()
        orcamento.updated_at = datetime.utcnow()
    elif status == "recusado":
        orcamento.status = "recusado"
        orcamento.recusado = True
        orcamento.updated_at = datetime.utcnow()
    elif status == "cancelado":
        orcamento.status = "cancelado"

    db.session.commit()
    registrar_auditoria(current_user, "STATUS_ORCAMENTO", "orcamentos", orcamento.id, f"{orcamento.numero} -> {status}")
    return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))


@orcamentos_bp.route("/<int:orcamento_id>/aprovar", methods=["POST"])
@login_required
@exigir_modulo("orcamentos")
def aprovar(orcamento_id):
    orcamento = Orcamento.query.filter_by(
        id=orcamento_id, empresa_id=current_user.empresa_id
    ).first()
    if not orcamento:
        abort(404)
    orcamento.status = "aprovado"
    orcamento.aprovado = True
    orcamento.aprovado_por = current_user.nome
    orcamento.aprovado_em = datetime.utcnow()
    orcamento.updated_at = datetime.utcnow()
    db.session.add(orcamento)
    db.session.commit()
    registrar_auditoria(current_user, "APROVACAO_ORCAMENTO", "orcamentos", orcamento.id, f"Orçamento {orcamento.numero} aprovado")
    flash("Orçamento aprovado com sucesso.", "success")
    return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))


@orcamentos_bp.route("/<int:orcamento_id>/recusar", methods=["POST"])
@login_required
@exigir_modulo("orcamentos")
def recusar(orcamento_id):
    orcamento = Orcamento.query.filter_by(
        id=orcamento_id, empresa_id=current_user.empresa_id
    ).first()
    if not orcamento:
        abort(404)
    motivo = request.form.get("motivo", "Não aprovado pelo cliente.")
    orcamento.status = "recusado"
    orcamento.recusado = True
    orcamento.motivo_recusa = motivo
    orcamento.updated_at = datetime.utcnow()
    db.session.add(orcamento)
    db.session.commit()
    registrar_auditoria(current_user, "RECUSA_ORCAMENTO", "orcamentos", orcamento.id, f"Orçamento {orcamento.numero} recusado")
    flash("Orçamento recusado.", "success")
    return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))


@orcamentos_bp.route("/<int:orcamento_id>/cancelar", methods=["POST"])
@login_required
@exigir_modulo("orcamentos")
def cancelar(orcamento_id):
    orcamento = Orcamento.query.filter_by(
        id=orcamento_id, empresa_id=current_user.empresa_id
    ).first()
    if not orcamento:
        abort(404)
    orcamento.status = "cancelado"
    orcamento.updated_at = datetime.utcnow()
    db.session.add(orcamento)
    db.session.commit()
    registrar_auditoria(current_user, "CANCELA_ORCAMENTO", "orcamentos", orcamento.id, f"Orçamento {orcamento.numero} cancelado")
    flash("Orçamento cancelado.", "success")
    return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))


@orcamentos_bp.route("/<int:orcamento_id>/converter", methods=["POST"])
@login_required
@exigir_modulo("orcamentos")
def converter(orcamento_id):
    orcamento = Orcamento.query.filter_by(
        id=orcamento_id, empresa_id=current_user.empresa_id
    ).first()
    if not orcamento:
        abort(404)
    if orcamento.status != "aprovado":
        flash("Apenas orçamentos aprovados podem gerar ordem de serviço.", "warning")
        return redirect(url_for("orcamentos.editar", orcamento_id=orcamento.id))

    seq = (db.session.query(func.max(OrdemServico.numero)).scalar() or 0) + 1
    os_ = OrdemServico(
        numero=seq,
        empresa_id=orcamento.empresa_id,
        orcamento_id=orcamento.id,
        cliente_id=orcamento.cliente_id,
        endereco=orcamento.endereco_execucao or orcamento.cliente.endereco or "",
        telefone=orcamento.cliente.whatsapp or orcamento.cliente.telefone or "",
        data_abertura=datetime.utcnow(),
        tecnico_id=int(request.form.get("tecnico_id") or 0) or None,
        status="aberta",
        descricao_solicitacao=orcamento.observacoes or "",
    )
    db.session.add(os_)
    db.session.commit()
    registrar_auditoria(current_user, "CONVERSAO_OS", "orcamentos", orcamento.id, f"Orçamento {orcamento.numero} convertido em OS {os_.numero}")
    flash("Ordem de serviço gerada com sucesso.", "success")
    return redirect(url_for("ordens_servico.editar", ordem_id=os_.id))
