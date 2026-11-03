from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..extensions import db
from ..models import Empresa, Usuario
from werkzeug.security import generate_password_hash

install_bp = Blueprint("install", __name__, url_prefix="/install")


@install_bp.route("/")
def index():
    if Empresa.query.first() is not None:
        return redirect(url_for("auth.login"))
    return render_template("install.html", form=request.form)


@install_bp.route("/executar", methods=["POST"])
def executar():
    if not request.form.get("razao_social", "").strip():
        flash("Informe a razão social da empresa.", "danger")
        return render_template("install.html", form=request.form)

    db.create_all()

    empresa = Empresa(
        razao_social=request.form.get("razao_social", "").strip(),
        nome_fantasia=request.form.get("nome_fantasia", ""),
        cpf_cnpj=request.form.get("cpf_cnpj", ""),
        inscricao_estadual=request.form.get("inscricao_estadual", ""),
        endereco=request.form.get("endereco", ""),
        cep=request.form.get("cep", ""),
        telefone=request.form.get("telefone", ""),
        whatsapp=request.form.get("whatsapp", ""),
        email=request.form.get("email", ""),
        site=request.form.get("site", ""),
        responsavel=request.form.get("responsavel", ""),
        banco=request.form.get("banco", ""),
        agencia=request.form.get("agencia", ""),
        conta=request.form.get("conta", ""),
        chave_pix=request.form.get("chave_pix", ""),
        observacoes=request.form.get("observacoes", ""),
    )
    db.session.add(empresa)
    db.session.commit()

    admin = Usuario(
        empresa_id=empresa.id,
        nome=request.form.get("admin_nome", "Administrador"),
        email=request.form.get("admin_email", "admin@empresa.com").strip().lower(),
        senha_hash=generate_password_hash(request.form.get("admin_senha", "123456")),
        perfil="admin",
        ativo=True,
    )
    db.session.add(admin)
    db.session.commit()

    return redirect(url_for("auth.login"))
