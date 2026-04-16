from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from routes.dependeces import pegar_sessao, verificar_admin, verificar_token
from routes.auth_routes import verificar_token
from database.models import Treino, TreinoExercicio, ExercicioCatalogo
from schemas import TreinoCreate, TreinoRead, List

treinos_routes = APIRouter(prefix="/treinos", tags=["treinos"])

@treinos_routes.get("/meus-treinos", response_model=List[TreinoRead])
async def ver_meus_treinos(
    usuario_logado = Depends(verificar_token),
    session: Session = Depends(pegar_sessao)
):
    treinos = session.query(Treino)\
        .options(joinedload(Treino.exercicios).joinedload(TreinoExercicio.catalogo))\
        .filter(Treino.usuario_id == usuario_logado.id)\
        .all()
    
    return treinos
    
@treinos_routes.post("/cadastrar-completo")
async def cadastrar_treino_com_exercicios(
    dados: TreinoCreate, 
    admin = Depends(verificar_admin), 
    session: Session = Depends(pegar_sessao)
):
    novo_treino = Treino(
        nome=dados.nome, 
        objetivo=dados.objetivo, 
        usuario_id=dados.usuario_id
    )
    
    session.add(novo_treino)
    session.commit()
    session.refresh(novo_treino)

    for exerc_data in dados.exercicios:
        novo_vinc_exercicio = TreinoExercicio(
            treino_id=novo_treino.id,
            exercicio_catalogo_id=exerc_data.exercicio_catalogo_id, 
            series=exerc_data.series,
            repeticoes=exerc_data.repeticoes,
            carga=exerc_data.carga,
            ordem=exerc_data.ordem if hasattr(exerc_data, 'ordem') else None,
            observacao=exerc_data.observacao if hasattr(exerc_data, 'observacao') else None
        )
        session.add(novo_vinc_exercicio)
    
    session.commit()

    return {"mensagem": f"Treino '{novo_treino.nome}' cadastrado com sucesso!"}

@treinos_routes.delete("/{treino_id}", status_code=status.HTTP_200_OK)
def deletar_treino(
    treino_id: int, 
    db: Session = Depends(pegar_sessao), 
    usuario_logado = Depends(verificar_token)
):
    
    eh_admin = usuario_logado.get("admin") if isinstance(usuario_logado, dict) else usuario_logado.admin

    if not eh_admin: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Apenas personais (admins) podem excluir treinos."
        )

    treino = db.query(Treino).filter(Treino.id == treino_id).first()

    if not treino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Treino não encontrado."
        )

    db.delete(treino)
    db.commit()

    return {"mensagem": "Treino excluído com sucesso!"}

@treinos_routes.get("/usuario/{usuario_id}")
def buscar_treinos_do_aluno(
    usuario_id: int, 
    db: Session = Depends(pegar_sessao), 
    usuario_logado: dict = Depends(verificar_token)
):
    if not usuario_logado.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Apenas personais podem acessar os treinos de outros alunos."
        )
    treinos = db.query(Treino).filter(Treino.usuario_id == usuario_id).all()
    
    return treinos