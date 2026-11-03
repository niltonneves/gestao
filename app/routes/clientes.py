from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Cliente, Orcamento, OrdemServico, RegistroFinanceiro
from ..services.permissoes import exigir_modulo
from ..services.auditoria_service import registrar_auditoria

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@clientes_bp.route("/")
@login_required
@exigir_modulo("clientes")
def listar():
    clientes = (
        Cliente.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Cliente.nome)
        .all()
    )
    return render_template("clientes.html", clientes=clientes)


@clientes_bp.route("/novo", methods=["GET", "POST"])
@login_required
@exigir_modulo("clientes")
def criar():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        cpf_cnpj = request.form.get("cpf_cnpj", "").strip()
        if not nome:
            flash("Informe o nome do cliente.", "danger")
            return render_template("cliente_form.html", form=request.form)

        if cpf_cnpj:
            if Cliente.query.filter_by(
                empresa_id=current_user.empresa_id, cpf_cnpj=cpf_cnpj
            ).first():
                flash("Já existe um cliente cadastrado com este CPF/CNPJ.", "danger")
                return render_template("cliente_form.html", form=request.form)

        cliente = Cliente(
            empresa_id=current_user.empresa_id,
            tipo=request.form.get("tipo", "pf"),
            nome=nome,
            nome_fantasia=request.form.get("nome_fantasia", ""),
            cpf_cnpj=cpf_cnpj,
            rg=request.form.get("rg", ""),
            inscricao_estadual=request.form.get("inscricao_estadual", ""),
            telefone=request.form.get("telefone", ""),
            whatsapp=request.form.get("whatsapp", ""),
            email=request.form.get("email", ""),
            cep=request.form.get("cep", ""),
            endereco=request.form.get("endereco", ""),
            numero=request.form.get("numero", ""),
            complemento=request.form.get("complemento", ""),
            bairro=request.form.get("bairro", ""),
            cidade=request.form.get("cidade", ""),
            estado=request.form.get("estado", ""),
            contato_responsavel=request.form.get("contato_responsavel", ""),
            observacoes=request.form.get("observacoes", ""),
        )
        db.session.add(cliente)
        db.session.commit()
        registrar_auditoria(
            current_user, "CRIACAO_CLIENTE", "clientes", cliente.id, nome
        )
        flash("Cliente cadastrado com sucesso.", "success")
        return redirect(url_for("clientes.listar"))

    return render_template("cliente_form.html", form=request.form, edicao=False)


@clientes_bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
@login_required
@exigir_modulo("clientes")
def editar(cliente_id):
    cliente = Cliente.query.filter_by(
        id=cliente_id, empresa_id=current_user.empresa_id
    ).first()
    if not cliente:
        abort(404)

    if request.method == "POST":
        cliente.nome = request.form.get("nome", "").strip()
        cliente.tipo = request.form.get("tipo", "pf")
        cliente.nome_fantasia = request.form.get("nome_fantasia", "")
        cliente.cpf_cnpj = request.form.get("cpf_cnpj", "").strip()
        cliente.rg = request.form.get("rg", "")
        cliente.inscricao_estadual = request.form.get("inscricao_estadual", "")
        cliente.telefone = request.form.get("telefone", "")
        cliente.whatsapp = request.form.get("whatsapp", "")
        cliente.email = request.form.get("email", "")
        cliente.cep = request.form.get("cep", "")
        cliente.endereco = request.form.get("endereco", "")
        cliente.numero = request.form.get("numero", "")
        cliente.complemento = request.form.get("complemento", "")
        cliente.bairro = request.form.get("bairro", "")
        cliente.cidade = request.form.get("cidade", "")
        cliente.estado = request.form.get("estado", "")
        cliente.contato_responsavel = request.form.get("contato_responsavel", "")
        cliente.observacoes = request.form.get("observacoes", "")
        db.session.commit()
        registrar_auditoria(
            current_user, "ATUALIZACAO_CLIENTE", "clientes", cliente.id, cliente.nome
        )
        flash("Cliente atualizado com sucesso.", "success")
        return redirect(url_for("clientes.listar"))

    return render_template("cliente_form.html", form=request.form, edicao=True, cliente=cliente)


@clientes_bp.route("/<int:cliente_id>/excluir", methods=["POST"])
@login_required
@exigir_modulo("clientes")
def excluir(cliente_id):
    cliente = Cliente.query.filter_by(
        id=cliente_id, empresa_id=current_user.empresa_id
    ).first()
    if not cliente:
        abort(404)

    if (
        Orcamento.query.filter_by(cliente_id=cliente.id).first()
        or OrdemServico.query.filter_by(cliente_id=cliente.id).first()
        or RegistroFinanceiro.query.filter_by(cliente_id=cliente.id).first()
    ):
        flash("Não é possível excluir: existem orçamentos, ordens de serviço ou registros financeiros vinculados a este cliente.", "warning")
        return redirect(url_for("clientes.listar"))

    db.session.delete(cliente)
    db.session.commit()
    registrar_auditoria(current_user, "EXCLUSAO_CLIENTE", "clientes", cliente.id, cliente.nome)
    flash("Cliente excluído com sucesso.", "success")
    return redirect(url_for("clientes.listar"))
