from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.models import ObjetivoAluno, TreinoRealizado, Usuario
from app.schemas.schemas import ObjetivoCreate, ObjetivoProgresso, ObjetivoRead
 


def store(dados: ObjetivoCreate, personal: Usuario, session: Session):
    aluno = session.query(Usuario).filter(
        Usuario.id == dados.usuario_id,
        Usuario.admin == False
    ).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    if dados.data_fim <= dados.data_inicio:
        raise HTTPException(status_code=400, detail="A data fim deve ser posterior à data início.")

    session.query(ObjetivoAluno).filter(
        ObjetivoAluno.usuario_id == dados.usuario_id
    ).delete()

    novo = ObjetivoAluno(
        usuario_id   = dados.usuario_id,
        meta_treinos = dados.meta_treinos,
        data_inicio  = dados.data_inicio,
        data_fim     = dados.data_fim,
        descricao    = dados.descricao
    )
    session.add(novo)
    session.commit()
    session.refresh(novo)

    return {"mensagem": f"Objetivo definido para {aluno.nome}: {dados.meta_treinos} treinos até {dados.data_fim.strftime('%d/%m/%Y')}."}


def index(usuario: Usuario, session: Session) -> ObjetivoProgresso:
    objetivo = session.query(ObjetivoAluno).filter(
        ObjetivoAluno.usuario_id == usuario.id
    ).first()

    if not objetivo:
        raise HTTPException(status_code=404, detail="Nenhum objetivo definido ainda.")

    treinos_feitos = session.query(TreinoRealizado).filter(
        TreinoRealizado.usuario_id  == usuario.id,
        TreinoRealizado.data_realizacao >= objetivo.data_inicio,
        TreinoRealizado.data_realizacao <= objetivo.data_fim
    ).count()

    percentual = min((treinos_feitos / objetivo.meta_treinos) * 100, 100.0)

    agora = datetime.now(timezone.utc)
    data_fim = objetivo.data_fim
    if data_fim.tzinfo is None:
        data_fim = data_fim.replace(tzinfo=timezone.utc)

    dias_restantes = max((data_fim - agora).days, 0)
    concluido      = treinos_feitos >= objetivo.meta_treinos

    return ObjetivoProgresso(
        objetivo           = ObjetivoRead.model_validate(objetivo),
        treinos_realizados = treinos_feitos,
        percentual         = round(percentual, 1),
        dias_restantes     = dias_restantes,
        concluido          = concluido
    )


def show(usuario_id: int, personal: Usuario, session: Session) -> ObjetivoProgresso:
    aluno = session.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    return index(aluno, session)