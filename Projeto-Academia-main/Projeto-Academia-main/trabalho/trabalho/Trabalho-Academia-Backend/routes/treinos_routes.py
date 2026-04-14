from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from routes.dependeces import pegar_sessao, verificar_admin, verificar_token
from routes.auth_routes import verificar_token
from database.models import Treino, ExercicioCatalogo
from schemas import TreinoCreate, TreinoRead, List

treinos_routes = APIRouter(prefix="/treinos", tags=["treinos"])

@treinos_routes.get("/meus-treinos", response_model=List[TreinoRead])
async def ver_meus_treinos(
    objetivo: str = Query(None, description="Filtrar por objetivo (ex: Hipertrofia)"),
    usuario_logado = Depends(verificar_token),
    session: Session = Depends(pegar_sessao)
):
    query = session.query(Treino).filter(Treino.usuario_id == usuario_logado.id)
    
    if objetivo:
        query = query.filter(Treino.objetivo.ilike(f"%{objetivo}%")) 
    
    treinos = query.all()
    
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
        novo_exercicio = ExercicioCatalogo(
            nome=exerc_data.nome,
            series=exerc_data.series,
            repeticoes=exerc_data.repeticoes,
            carga=exerc_data.carga,
            treino_id=novo_treino.id 
        )
        session.add(novo_exercicio)
    
    session.commit()

    return {"mensagem": f"Treino '{novo_treino.nome}' cadastrado com {len(dados.exercicios)} exercícios para o aluno ID {dados.usuario_id}!"}


@treinos_routes.delete("/deletar/{treino_id}")
async def deletar_treino(
    treino_id: int, 
    admin_logado = Depends(verificar_admin), 
    session: Session = Depends(pegar_sessao)
):
    treino = session.query(Treino).filter(Treino.id == treino_id).first()
    
    if not treino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Treino não encontrado no sistema."
        )
    
    try:
        session.delete(treino)
        session.commit()
        return {
            "mensagem": f"Treino '{treino.nome}' removido com sucesso!",
            "deletado_por": admin_logado.nome
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Erro ao tentar excluir o treino."
        )