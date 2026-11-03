from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from ..extensions import db
from ..models import Usuario, Tecnico
from ..services.permissoes import exigir_modulo
from ..services.auth_service import create_admin

administracao_bp = Blueprint("administracao", __name__, url_prefix="/administracao")


@administracao_bp.route("/")
@login_required
@exigir_modulo("administracao")
def index():
    usuarios = Usuario.query.filter_by(empresa_id=current_user.empresa_id).all()
    tecnicos = Tecnico.query.filter_by(empresa_id=current_user.empresa_id).all()
    return render_template("administracao.html", usuarios=usuarios, tecnicos=tecnicos)


@administracao_bp.route("/usuario/novo", methods=["GET", "POST"])
@login_required
@exigir_modulo("administracao")
def usuario_novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        perfil = request.form.get("perfil", "atendente")
        if not nome or not email or not senha:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("usuario_form.html", form=request.form, edicao=False, perfis=["admin", "atendente", "tecnico", "financeiro"])
        if Usuario.query.filter_by(empresa_id=current_user.empresa_id, email=email).first():
            flash("Já existe um usuário com este e-mail.", "danger")
            return render_template("usuario_form.html", form=request.form, edicao=False, perfis=["admin", "atendente", "tecnico", "financeiro"])
        if perfil == "admin" and current_user.perfil != "admin":
            abort(403)
        if perfil != "admin":
            usuario = Usuario(
                nome=nome,
                email=email,
                senha_hash=generate_password_hash(senha),
                perfil=perfil,
                ativo=True,
                empresa_id=current_user.empresa_id,
            )
            db.session.add(usuario)
            db.session.commit()
            flash(f"Usuário {nome} criado com sucesso.", "success")
            return redirect(url_for("administracao.index"))

        # perfis distintos de admin exigem cadastro manual de tecnico correspondente
        flash("Perfil administrativo não pode ser criado neste fluxo; utilize o cadastro de técnicos.", "warning")
        return redirect(url_for("administracao.index"))

    return render_template("usuario_form.html", form=request.form, edicao=False, perfis=["admin", "atendente", "tecnico", "financeiro"])


@administracao_bp.route("/usuario/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@exigir_modulo("administracao")
def usuario_editar(usuario_id):
    usuario = Usuario.query.filter_by(
        id=usuario_id, empresa_id=current_user.empresa_id
    ).first()
    if not usuario:
        abort(404)

    if request.method == "POST":
        usuario.nome = request.form.get("nome", "").strip()
        usuario.perfil = request.form.get("perfil", usuario.perfil)
        usuario.ativo = "ativo" in request.form
        if usuario.perfil != "admin" and usuario.id != current_user.id:
            senha = request.form.get("senha", "")
            if senha:
                usuario.senha_hash = generate_password_hash(senha)
        db.session.commit()
        registrar_auditoria(current_user, "ATUALIZACAO_USUARIO", "administracao", usuario.id, usuario.email)
        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for("administracao.index"))

    return render_template("usuario_form.html", form=request.form, edicao=True, usuario=usuario, perfis=["admin", "atendente", "tecnico", "financeiro"])
