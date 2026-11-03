from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Empresa
from ..services.permissoes import exigir_modulo
from ..services.auditoria_service import registrar_auditoria

configuracoes_bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")


@configuracoes_bp.route("/")
@login_required
@exigir_modulo("configuracoes")
def index():
    empresa = Empresa.query.first()
    if not empresa:
        abort(404)
    return render_template("configuracoes.html", empresa=empresa)


@configuracoes_bp.route("/editar", methods=["GET", "POST"])
@login_required
@exigir_modulo("configuracoes")
def editar():
    empresa = Empresa.query.first()
    if not empresa:
        abort(404)

    if request.method == "POST":
        empresa.razao_social = request.form.get("razao_social", "").strip()
        empresa.nome_fantasia = request.form.get("nome_fantasia", "")
        empresa.cpf_cnpj = request.form.get("cpf_cnpj", "")
        empresa.inscricao_estadual = request.form.get("inscricao_estadual", "")
        empresa.endereco = request.form.get("endereco", "")
        empresa.cep = request.form.get("cep", "")
        empresa.telefone = request.form.get("telefone", "")
        empresa.whatsapp = request.form.get("whatsapp", "")
        empresa.email = request.form.get("email", "")
        empresa.site = request.form.get("site", "")
        empresa.responsavel = request.form.get("responsavel", "")
        empresa.banco = request.form.get("banco", "")
        empresa.agencia = request.form.get("agencia", "")
        empresa.conta = request.form.get("conta", "")
        empresa.chave_pix = request.form.get("chave_pix", "")
        empresa.observacoes = request.form.get("observacoes", "")
        db.session.commit()
        registrar_auditoria(current_user, "ATUALIZACAO_EMPRESA", "configuracoes", empresa.id, empresa.razao_social)
        flash("Dados da empresa atualizados com sucesso.", "success")
        return redirect(url_for("configuracoes.index"))

    return render_template("configuracoes.html", empresa=empresa, form=request.form, edicao=True)
