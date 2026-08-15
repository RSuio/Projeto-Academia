from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database.models import Treino, TreinoExercicio, Usuario
from app.schemas.schemas import TreinoCreate


def index(usuario_logado: Usuario, session: Session):
    treinos = (
        session.query(Treino)
        .options(joinedload(Treino.exercicios).joinedload(TreinoExercicio.catalogo))
        .filter(Treino.usuario_id == usuario_logado.id)
        .all()
    )
    return treinos


def store(dados: TreinoCreate, admin: Usuario, session: Session):
    novo_treino = Treino(
        nome=dados.nome,
        objetivo=dados.objetivo,
        usuario_id=dados.usuario_id,
        dia_semana=dados.dia_semana
    )
    session.add(novo_treino)
    session.commit()
    session.refresh(novo_treino)

    for exerc_data in dados.exercicios:
        novo_vinculo = TreinoExercicio(
            treino_id=novo_treino.id,
            exercicio_catalogo_id=exerc_data.exercicio_catalogo_id,
            series=exerc_data.series,
            repeticoes=exerc_data.repeticoes,
            carga=exerc_data.carga,
            ordem=exerc_data.ordem,
            observacao=exerc_data.observacao
        )
        session.add(novo_vinculo)

    session.commit()
    return {"mensagem": f"Treino '{novo_treino.nome}' cadastrado com sucesso!"}


def destroy(treino_id: int, usuario_logado: Usuario, session: Session):
    if not usuario_logado.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas personais (admins) podem excluir treinos."
        )

    treino = session.query(Treino).filter(Treino.id == treino_id).first()
    if not treino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treino não encontrado."
        )

    session.delete(treino)
    session.commit()
    return {"mensagem": "Treino excluído com sucesso!"}


def show(usuario_id: int, usuario_logado: Usuario, session: Session):
    if not usuario_logado.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas personais podem acessar os treinos de outros alunos."
        )

    treinos = session.query(Treino).filter(Treino.usuario_id == usuario_id).all()
    return treinos


def update(treino_id: int, dia_semana: str | None, usuario_logado, session: Session):
    if not usuario_logado.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas personais podem alterar o dia do treino."
        )
    treino = session.query(Treino).filter(Treino.id == treino_id).first()
    if not treino:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treino não encontrado.")

    treino.dia_semana = dia_semana
    session.commit()
    return {"mensagem": f"Treino movido para {dia_semana or 'sem dia definido'}."}