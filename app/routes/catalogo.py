from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..extensions import db
from ..models import ProdutoServico
from ..services.permissoes import exigir_modulo
from ..services.auditoria_service import registrar_auditoria

catalogo_bp = Blueprint("catalogo", __name__, url_prefix="/catalogo")


CATEGORIAS = [
    "Informática",
    "Redes",
    "Telefonia",
    "Elétrica",
    "CFTV",
    "Segurança eletrônica",
    "Manutenção",
    "Instalação",
    "Infraestrutura",
    "Outros",
]

TIPOS = ["material", "equipamento", "mao_obra", "servico", "adicional", "deslocamento"]


@catalogo_bp.route("/")
@login_required
@exigir_modulo("catalogo")
def listar():
    produtos = (
        ProdutoServico.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(ProdutoServico.codigo, ProdutoServico.descricao)
        .all()
    )
    return render_template("catalogo.html", produtos=produtos)


@catalogo_bp.route("/novo", methods=["GET", "POST"])
@login_required
@exigir_modulo("catalogo")
def criar():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        if not descricao:
            flash("Informe a descrição do produto ou serviço.", "danger")
            return render_template("produto_form.html", form=request.form, edicao=False, categorias=CATEGORIAS, tipos=TIPOS)

        existente = ProdutoServico.query.filter_by(
            empresa_id=current_user.empresa_id, codigo=codigo
        ).first() if codigo else None
        if existente:
            flash("Já existe um produto/serviço com este código.", "danger")
            return render_template("produto_form.html", form=request.form, edicao=False, categorias=CATEGORIAS, tipos=TIPOS)

        produto = ProdutoServico(
            empresa_id=current_user.empresa_id,
            codigo=codigo,
            descricao=descricao,
            categoria=request.form.get("categoria", "Outros"),
            tipo=request.form.get("tipo", "servico"),
            unidade=request.form.get("unidade", "UN") or "UN",
            custo=float(request.form.get("custo") or 0),
            preco_venda=float(request.form.get("preco_venda") or 0),
            tempo_estimado=int(request.form.get("tempo_estimado") or 0),
            garantia=request.form.get("garantia", ""),
            observacoes=request.form.get("observacoes", ""),
        )
        db.session.add(produto)
        db.session.commit()
        registrar_auditoria(current_user, "CRIACAO_PRODUTO", "catalogo", produto.id, descricao)
        flash("Produto/serviço cadastrado com sucesso.", "success")
        return redirect(url_for("catalogo.listar"))

    return render_template("produto_form.html", form=request.form, edicao=False, categorias=CATEGORIAS, tipos=TIPOS)


@catalogo_bp.route("/<int:produto_id>/editar", methods=["GET", "POST"])
@login_required
@exigir_modulo("catalogo")
def editar(produto_id):
    produto = ProdutoServico.query.filter_by(
        id=produto_id, empresa_id=current_user.empresa_id
    ).first()
    if not produto:
        abort(404)

    if request.method == "POST":
        descricao = request.form.get("descricao", "").strip()
        if not descricao:
            flash("Informe a descrição do produto ou serviço.", "danger")
            return render_template("produto_form.html", form=request.form, edicao=True, produto=produto, categorias=CATEGORIAS, tipos=TIPOS)

        produto.descricao = descricao
        produto.categoria = request.form.get("categoria", "Outros")
        produto.tipo = request.form.get("tipo", "servico")
        produto.unidade = request.form.get("unidade", "UN") or "UN"
        produto.custo = float(request.form.get("custo") or 0)
        produto.preco_venda = float(request.form.get("preco_venda") or 0)
        produto.tempo_estimado = int(request.form.get("tempo_estimado") or 0)
        produto.garantia = request.form.get("garantia", "")
        produto.observacoes = request.form.get("observacoes", "")
        db.session.commit()
        registrar_auditoria(current_user, "ATUALIZACAO_PRODUTO", "catalogo", produto.id, descricao)
        flash("Produto/serviço atualizado com sucesso.", "success")
        return redirect(url_for("catalogo.listar"))

    return render_template("produto_form.html", form=request.form, edicao=True, produto=produto, categorias=CATEGORIAS, tipos=TIPOS)
