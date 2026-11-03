from ..extensions import db
from ..models import OrdemServico

OS_TRANSICOES = {
    "aberta": ["agendada", "cancelada"],
    "agendada": ["em_deslocamento", "cancelada"],
    "em_deslocamento": ["em_atendimento", "cancelada"],
    "em_atendimento": ["em_execucao", "aguardando_material", "cancelada"],
    "em_execucao": ["aguardando_material", "aguardando_cliente", "concluida", "cancelada"],
    "aguardando_material": ["em_execucao", "aguardando_cliente", "cancelada"],
    "aguardando_cliente": ["em_execucao", "concluida", "cancelada"],
    "concluida": ["entregue", "cancelada"],
    "entregue": [],
    "cancelada": [],
}


def alterar_status(ordem, novo_status, observacao=None, usuario=None):
    permitidos = OS_TRANSICOES.get(ordem.status, [])
    if novo_status not in permitidos:
        return False, "Transição inválida de status."
    ordem.status = novo_status
    ordem.updated_at = None
    registro = ordem.add_historico(novo_status, observacao=observacao, usuario=usuario)
    db.session.add(ordem)
    db.session.commit()
    return True, registro
