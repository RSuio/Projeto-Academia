"""
Rotas do catálogo de exercícios.
Inclua este router no seu main.py:

    from routes_exercicios import router as exercicios_router
    app.include_router(exercicios_router)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from database.models import ExercicioCatalogo
from schemas import ExercicioCatalogoRead
from routes.dependeces import pegar_sessao

router = APIRouter(prefix="/exercicios", tags=["Exercícios"])


@router.get("/catalogo", response_model=List[ExercicioCatalogoRead])
def listar_catalogo(
    busca: str = Query(default="", description="Filtra pelo nome do exercício"),
    categoria: str = Query(default="", description="Filtra por categoria (ex: Peito)"),
    equipamento: str = Query(default="", description="Filtra por equipamento (ex: Barra)"),
    limit: int = Query(default=10, le=50),
    offset: int = Query(default=0),
    db: Session = Depends(pegar_sessao),
):
    """
    Retorna exercícios do catálogo.
    Usado pelo frontend para o autocomplete na criação de treinos.
    """
    query = db.query(ExercicioCatalogo)

    if busca:
        # ilike = case-insensitive; funciona no SQLite e PostgreSQL
        query = query.filter(ExercicioCatalogo.nome.ilike(f"%{busca}%"))

    if categoria:
        query = query.filter(ExercicioCatalogo.categoria.ilike(f"%{categoria}%"))

    if equipamento:
        query = query.filter(ExercicioCatalogo.equipamento.ilike(f"%{equipamento}%"))

    return query.order_by(ExercicioCatalogo.nome).offset(offset).limit(limit).all()


@router.get("/catalogo/categorias")
def listar_categorias(db: Session = Depends(pegar_sessao)):
    """Retorna todas as categorias distintas disponíveis no catálogo."""
    rows = (
        db.query(ExercicioCatalogo.categoria)
        .filter(ExercicioCatalogo.categoria.isnot(None))
        .distinct()
        .order_by(ExercicioCatalogo.categoria)
        .all()
    )
    return [r[0] for r in rows]