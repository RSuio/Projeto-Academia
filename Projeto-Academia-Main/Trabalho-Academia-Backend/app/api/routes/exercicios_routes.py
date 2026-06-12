from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import pegar_sessao
from app.schemas.schemas import ExercicioCatalogoRead
from app.controllers import exercicios_controller

exercicios = APIRouter(prefix="/exercicios", tags=["Exercicios"])


@exercicios.get("/catalogo", response_model=List[ExercicioCatalogoRead])
def listar_catalogo(
    busca: str = Query(default="", description="Filtra pelo nome do exercício"),
    categoria: str = Query(default="", description="Filtra por categoria (ex: Peito)"),
    equipamento: str = Query(default="", description="Filtra por equipamento (ex: Barra)"),
    limit: int = Query(default=10, le=50),
    offset: int = Query(default=0),
    session: Session = Depends(pegar_sessao),
):
    return exercicios_controller.listar_catalogo(session, busca, categoria, equipamento, limit, offset)


@exercicios.get("/catalogo/categorias")
def listar_categorias(session: Session = Depends(pegar_sessao)):
    return exercicios_controller.listar_categorias(session)


@exercicios.post("/", response_model=ExercicioCatalogoRead, status_code=201)
def criar_exercicio(
    exercicio: ExercicioCatalogoRead,
    session: Session = Depends(pegar_sessao)
):
    return exercicios_controller.criar_exercicio(session, exercicio)

@exercicios.get("/{exercicio_id}", response_model=ExercicioCatalogoRead)
def buscar_exercicio(exercicio_id: int, session: Session = Depends(pegar_sessao)):
    return exercicios_controller.buscar_exercicio_por_id(session, exercicio_id)

@exercicios.put("/{exercicio_id}", response_model=ExercicioCatalogoRead)
def atualizar_exercicio(
    exercicio_id: int, 
    exercicio: ExercicioCatalogoRead,
    session: Session = Depends(pegar_sessao)
):
    return exercicios_controller.atualizar_exercicio(session, exercicio_id, exercicio)

@exercicios.delete("/{exercicio_id}")
def deletar_exercicio(exercicio_id: int, session: Session = Depends(pegar_sessao)):
    return exercicios_controller.deletar_exercicio(session, exercicio_id)


@exercicios.patch("/{exercicio_id}", response_model=ExercicioCatalogoRead)
def atualizar_parcial_exercicio(
    exercicio_id: int, 
    dados_parciais: dict,
    session: Session = Depends(pegar_sessao)
):
    return exercicios_controller.atualizar_exercicio_parcial(session, exercicio_id, dados_parciais)
