from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import pegar_sessao, verificar_token, verificar_admin
from app.schemas.schemas import ObjetivoCreate, ObjetivoProgresso
from app.controllers import objetivo_controller

objetivos = APIRouter(prefix="/objetivos", tags=["Objetivos"])


@objetivos.post("/")
def definir_objetivo(
    dados: ObjetivoCreate,
    personal=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return objetivo_controller.store(dados, personal, session)


@objetivos.get("/", response_model=ObjetivoProgresso)
def meu_objetivo(
    usuario=Depends(verificar_token),
    session: Session = Depends(pegar_sessao)
):
    return objetivo_controller.index(usuario, session)


@objetivos.get("/aluno/{usuario_id}", response_model=ObjetivoProgresso)
def objetivo_do_aluno(
    usuario_id: int,
    personal=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return objetivo_controller.show(usuario_id, personal, session)