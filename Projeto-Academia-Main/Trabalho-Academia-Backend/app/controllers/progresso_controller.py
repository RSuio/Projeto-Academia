"""
Controller de Progresso.
Usa os dois padrões de projeto:
  - Template Method → via RelatorioPorSemana / RelatorioPorMes
  - Strategy        → (aplicado em exercicios_controller, mas ambos vivem em /patterns)
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.database.models import TreinoRealizado, Treino, Usuario
from app.schemas.schemas import TreinoRealizadoCreate, DashboardProgresso
from app.patterns.template_method_relatorio import RelatorioPorSemana, RelatorioPorMes


def store(dados: TreinoRealizadoCreate, usuario_logado: Usuario, session: Session):
    treino = session.query(Treino).filter(
        Treino.id == dados.treino_id,
        Treino.usuario_id == usuario_logado.id
    ).first()

    if not treino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treino não encontrado ou não pertence a você."
        )

    novo = TreinoRealizado(
        treino_id=dados.treino_id,
        usuario_id=usuario_logado.id,
        observacao=dados.observacao
    )
    session.add(novo)
    session.commit()
    session.refresh(novo)
    return {"mensagem": "Treino marcado como realizado! 💪", "id": novo.id}


def index(usuario_logado: Usuario, session: Session) -> DashboardProgresso:
    todos = (
        session.query(TreinoRealizado)
        .filter(TreinoRealizado.usuario_id == usuario_logado.id)
        .order_by(TreinoRealizado.data_realizacao.desc())
        .all()
    )

    total = len(todos)
    ultimo = todos[0].data_realizacao if todos else None
    streak = 0
    if todos:
        hoje   = datetime.now(timezone.utc).date()
        dia    = hoje
        datas  = {r.data_realizacao.date() for r in todos}

        while dia in datas:
            streak += 1
            dia -= timedelta(days=1)

    relatorio_semana = RelatorioPorSemana(usuario_logado.id, session).gerar()
    por_semana = [d["treinos"] for d in relatorio_semana["dias"]]

    return DashboardProgresso(
        total_realizados=total,
        streak_atual=streak,
        por_semana=por_semana,
        ultimo_treino=ultimo
    )


def show_historico(usuario_logado: Usuario, session: Session):
    return (
        session.query(TreinoRealizado)
        .filter(TreinoRealizado.usuario_id == usuario_logado.id)
        .order_by(TreinoRealizado.data_realizacao.desc())
        .all()
    )


def show_relatorio_mensal(usuario_logado: Usuario, session: Session):
    return RelatorioPorMes(usuario_logado.id, session).gerar()
