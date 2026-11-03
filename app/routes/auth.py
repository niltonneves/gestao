import os

from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..extensions import db
from ..models.usuario import Usuario
from ..services.auth_service import authenticate, create_admin

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/primeiro-acesso", methods=["GET", "POST"])
def primeiro_acesso():
    """Cria o primeiro usuário administrador do sistema."""
    if Usuario.query.count() > 0:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar", "")

        if not nome or not email or not senha:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("auth_primeiro_acesso.html", form=request.form)

        if len(senha) < 6:
            flash("A senha deve ter no mínimo 6 caracteres.", "danger")
            return render_template("auth_primeiro_acesso.html", form=request.form)

        if senha != confirmar:
            flash("As senhas não coincidem.", "danger")
            return render_template("auth_primeiro_acesso.html", form=request.form)

        if Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário com este e-mail.", "danger")
            return render_template("auth_primeiro_acesso.html", form=request.form)

        create_admin(
            nome,
            email,
            senha,
            {
                "razao_social": request.form.get("razao_social", "").strip(),
                "nome_fantasia": request.form.get("nome_fantasia", ""),
                "cpf_cnpj": request.form.get("cpf_cnpj", ""),
                "inscricao_estadual": request.form.get("inscricao_estadual", ""),
                "endereco": request.form.get("endereco", ""),
                "cep": request.form.get("cep", ""),
                "telefone": request.form.get("telefone", ""),
                "whatsapp": request.form.get("whatsapp", ""),
                "email": request.form.get("email", ""),
                "site": request.form.get("site", ""),
                "responsavel": request.form.get("responsavel") or nome,
                "banco": request.form.get("banco", ""),
                "agencia": request.form.get("agencia", ""),
                "conta": request.form.get("conta", ""),
                "chave_pix": request.form.get("chave_pix", ""),
                "observacoes": request.form.get("observacoes", ""),
            },
        )
        flash("Administrador inicial criado com sucesso.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth_primeiro_acesso.html", form=request.form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from flask_login import login_user, logout_user, current_user
    from flask import session

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        usuario = authenticate(
            request.form.get("email", ""), request.form.get("senha", "")
        )
        if usuario:
            login_user(usuario, remember=bool(request.form.get("lembrar")))
            from ..models import AuditoriaLog

            db.session.add(
                AuditoriaLog(
                    usuario_id=usuario.id,
                    usuario_nome=usuario.nome,
                    acao="LOGIN",
                    modulo="seguranca",
                    registro_id=str(usuario.id),
                    detalhes="Usuário autenticado",
                    ip=request.remote_addr or "",
                )
            )
            db.session.commit()
            return redirect(url_for("dashboard.dashboard"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth_login.html")


@auth_bp.route("/logout")
def logout():
    from flask_login import logout_user

    logout_user()
    return redirect(url_for("auth.login"))
