from datetime import datetime

from sqlalchemy import func

from ..extensions import db
from ..models import Orcamento, ItemOrcamento, OrdemServico

ORC_STATUSES = [
    "elaboracao",
    "enviado",
    "aguardando_aprovacao",
    "aprovado",
    "recusado",
    "vencido",
    "cancelado",
]

ORC_TRANSICOES = {
    "elaboracao": ["enviado", "cancelado"],
    "enviado": ["aguardando_aprovacao", "cancelado"],
    "aguardando_aprovacao": ["aprovado", "recusado", "cancelado"],
    "aprovado": [],
    "recusado": [],
    "vencido": [],
    "cancelado": [],
}


def _total_item(item):
    base = (item.quantidade or 0) * (item.valor_unitario or 0)
    desconto = item.desconto or 0
    if desconto and desconto > 0:
        base = base * (1 - min(desconto, 100) / 100.0)
    return base


def calcular_totais(orcamento):
    subtotal = sum((_total_item(i) for i in orcamento.itens), 0)
    desconto = orcamento.desconto or 0
    desconto_valor = (
        subtotal * desconto / 100.0 if orcamento.desconto_tipo == "percentual" else desconto
    )
    liquido = subtotal - desconto_valor + (orcamento.acrescimos or 0)
    entrada = orcamento.entrada or 0
    total = max(liquido - entrada, 0)
    return {
        "subtotal": subtotal,
        "desconto": desconto_valor,
        "liquido": liquido,
        "entrada": min(entrada, liquido),
        "total": total,
    }


def salvar_totais(orcamento):
    totais = calcular_totais(orcamento)
    orcamento.subtotal = totais["subtotal"]
    orcamento.desconto = totais["desconto"]
    orcamento.acrescimos = orcamento.acrescimos or 0
    orcamento.entrada = totais["entrada"]
    orcamento.total = totais["total"]
    db.session.add(orcamento)
    db.session.commit()
    return totais


def enviar_orcamento(orcamento):
    if orcamento.status in ORC_TRANSICOES.get("elaboracao", []):
        orcamento.status = "enviado"
        orcamento.updated_at = datetime.utcnow()
        db.session.add(orcamento)
        db.session.commit()
    return orcamento.status


def aguardar_aprovacao(orcamento):
    if orcamento.status == "enviado":
        orcamento.status = "aguardando_aprovacao"
        orcamento.updated_at = datetime.utcnow()
        db.session.add(orcamento)
        db.session.commit()
    return orcamento.status


def aprovar_orcamento(orcamento, aprovador, observacoes=None):
    orcamento.status = "aprovado"
    orcamento.aprovado = True
    orcamento.aprovado_por = aprovador
    orcamento.aprovado_em = datetime.utcnow()
    orcamento.aprovacao_observacoes = observacoes
    orcamento.updated_at = datetime.utcnow()
    db.session.add(orcamento)
    db.session.commit()
    return orcamento


def recusar_orcamento(orcamento, motivo, aprovador=None):
    orcamento.status = "recusado"
    orcamento.recusado = True
    orcamento.motivo_recusa = motivo
    orcamento.aprovado_por = aprovador
    orcamento.updated_at = datetime.utcnow()
    db.session.add(orcamento)
    db.session.commit()
    return orcamento


def cancelar_orcamento(orcamento):
    orcamento.status = "cancelado"
    orcamento.updated_at = datetime.utcnow()
    db.session.add(orcamento)
    db.session.commit()
    return orcamento.status


def verificar_vencimento(orcamento):
    hoje = datetime.utcnow().date()
    if orcamento.status in ("enviado", "aguardando_aprovacao") and orcamento.validade:
        if orcamento.validade < hoje:
            orcamento.status = "vencido"
            orcamento.updated_at = datetime.utcnow()
            db.session.add(orcamento)
            db.session.commit()
    return orcamento.status


def gerar_numero(prefixo, empresa_id):
    """Gera número sequencial por empresa, ex.: ORC-0001."""
    ultimo = (
        db.session.query(func.max(Orcamento.numero))
        .filter(Orcamento.empresa_id == empresa_id)
        .scalar()
    )
    seq = (ultimo or 0) + 1
    return f"{prefixo}-{seq:05d}"


def criar_orcamento(empresa_id, cliente_id, usuario_id, dados):
    orcamento = Orcamento(
        numero=1,
        empresa_id=empresa_id,
        cliente_id=cliente_id,
        endereco_execucao=dados.get("endereco_execucao") or "",
        responsavel_id=usuario_id,
        status="elaboracao",
        data_emissao=datetime.utcnow(),
        validade=dados.get("validade"),
        condicao_pagamento=dados.get("condicao_pagamento") or "Pix",
        prazo_execucao=dados.get("prazo_execucao") or "",
        garantia=dados.get("garantia") or "",
        observacoes=dados.get("observacoes") or "",
        subtotal=0,
        desconto=0,
        desconto_tipo=dados.get("desconto_tipo") or "valor",
        acrescimos=0,
        entrada=0,
        total=0,
    )
    db.session.add(orcamento)
    db.session.commit()
    return orcamento


def adicionar_item(orcamento, produto_servico_id=None, codigo="", descricao="", quantidade=1, unidade="UN", valor_unitario=0, desconto=0):
    item = ItemOrcamento(
        orcamento_id=orcamento.id,
        produto_servico_id=produto_servico_id,
        codigo=codigo,
        descricao=descricao,
        quantidade=quantidade,
        unidade=unidade,
        valor_unitario=valor_unitario,
        desconto=desconto,
        total=_total_item(
            ItemOrcamento(
                quantidade=quantidade,
                valor_unitario=valor_unitario,
                desconto=desconto,
            )
        ),
    )
    orcamento.itens.append(item)
    db.session.add(orcamento)
    db.session.commit()
    return item


def converter_em_os(orcamento, tecnico_id, usuario_id):
    seq = (db.session.query(func.max(OrdemServico.numero)).scalar() or 0) + 1
    os_ = OrdemServico(
        numero=seq,
        empresa_id=orcamento.empresa_id,
        orcamento_id=orcamento.id,
        cliente_id=orcamento.cliente_id,
        endereco=orcamento.endereco_execucao or orcamento.cliente.endereco or "",
        telefone=orcamento.cliente.whatsapp or orcamento.cliente.telefone or "",
        data_abertura=datetime.utcnow(),
        tecnico_id=tecnico_id,
        status="aberta",
        descricao_solicitacao=orcamento.observacoes or "",
    )
    db.session.add(os_)
    db.session.commit()
    return os_
