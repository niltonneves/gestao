from ..extensions import db
from ..models import AuditoriaLog


def registrar_auditoria(usuario, acao, modulo, registro_id=None, detalhes=None):
    db.session.add(
        AuditoriaLog(
            usuario_id=getattr(usuario, "id", None),
            usuario_nome=getattr(usuario, "nome", None) or "sistema",
            acao=acao,
            modulo=modulo,
            registro_id=str(registro_id) if registro_id is not None else None,
            detalhes=detalhes,
            ip=None,
        )
    )
    db.session.commit()
    return True
