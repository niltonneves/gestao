from io import BytesIO

from flask import Blueprint, render_template, send_file, abort
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Orcamento
from ..services.permissoes import exigir_modulo

relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


@relatorios_bp.route("/")
@login_required
@exigir_modulo("relatorios")
def index():
    return render_template("relatorios.html")


@relatorios_bp.route("/excel/orcamentos")
@login_required
@exigir_modulo("relatorios")
def excel_orcamentos():
    from openpyxl import Workbook

    orcamentos = (
        Orcamento.query.filter_by(empresa_id=current_user.empresa_id)
        .order_by(Orcamento.numero.desc())
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Orcamentos"
    ws.append(
        [
            "Nº",
            "Cliente",
            "Status",
            "Emissão",
            "Validade",
            "Total",
            "Desconto",
            "Entrada",
            "Acréscimos",
        ]
    )
    for o in orcamentos:
        ws.append(
            [
                f"{o.numero:05d}",
                o.cliente.nome if o.cliente else "",
                o.status,
                o.data_emissao.strftime("%d/%m/%Y") if o.data_emissao else "",
                o.validade.strftime("%d/%m/%Y") if o.validade else "",
                float(o.total or 0),
                float(o.desconto or 0),
                float(o.entrada or 0),
                float(o.acrescimos or 0),
            ]
        )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="orcamentos.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@relatorios_bp.route("/pdf/orcamento/<int:orcamento_id>")
@login_required
@exigir_modulo("relatorios")
def pdf_orcamento(orcamento_id):
    from io import BytesIO as _BytesIO

    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    orcamento = Orcamento.query.filter_by(
        id=orcamento_id, empresa_id=current_user.empresa_id
    ).first()
    if not orcamento:
        abort(404)

    buffer = _BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFillColor(HexColor("#082E68"))
    c.rect(0, height - 90, width, 90, fill=1, stroke=0)
    c.setFillColor(HexColor("#F8E71C"))
    c.circle(width - 60, height - 45, 18, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(20, height - 45, "N7 GESTÃO")
    c.setFont("Helvetica", 10)
    c.drawString(20, height - 65, "Uma solução N7 Info")

    c.setFillColor(HexColor("#1F3D7C"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, height - 120, f"Orçamento Nº {orcamento.numero:05d}")
    c.setFont("Helvetica", 10)
    c.drawString(20, height - 140, f"Data: {orcamento.data_emissao.strftime('%d/%m/%Y') if orcamento.data_emissao else '-'}")
    c.drawString(20, height - 155, f"Validade: {orcamento.validade.strftime('%d/%m/%Y') if orcamento.validade else '-'}")
    c.drawString(20, height - 170, f"Status: {orcamento.status}")

    cliente = orcamento.cliente
    y = height - 215
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, y, "Dados do Cliente")
    c.setFont("Helvetica", 10)
    y -= 15
    c.drawString(20, y, f"Cliente: {cliente.nome if cliente else '-'}")
    c.drawString(20, y - 12, f"CPF/CNPJ: {cliente.cpf_cnpj if cliente else '-'}")
    c.drawString(20, y - 24, f"Endereço: {orcamento.endereco_execucao or (cliente.endereco if cliente else '') or '-'}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, y, "Valores")
    c.setFont("Helvetica", 10)
    y -= 15
    c.drawString(20, y, f"Subtotal: R$ {float(orcamento.subtotal or 0):.2f}")
    c.drawString(20, y - 12, f"Desconto: R$ {float(orcamento.desconto or 0):.2f}")
    c.drawString(20, y - 24, f"Acréscimos: R$ {float(orcamento.acrescimos or 0):.2f}")
    c.drawString(20, y - 36, f"Entrada: R$ {float(orcamento.entrada or 0):.2f}")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, y - 50, f"Total: R$ {float(orcamento.total or 0):.2f}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, y - 70, "Condições")
    c.setFont("Helvetica", 10)
    c.drawString(20, y - 85, f"Pagamento: {orcamento.condicao_pagamento}")
    c.drawString(20, y - 97, f"Prazo: {orcamento.prazo_execucao}")
    c.drawString(20, y - 109, f"Garantia: {orcamento.garantia}")

    c.setFillColor(HexColor("#082E68"))
    c.rect(0, 40, width, 40, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(20, 50, "N7 Gestão – Uma solução N7 Info")

    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"orcamento_{orcamento.numero:05d}.pdf",
        mimetype="application/pdf",
    )
