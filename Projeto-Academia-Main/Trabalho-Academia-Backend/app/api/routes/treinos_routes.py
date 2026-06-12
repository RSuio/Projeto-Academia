from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import pegar_sessao, verificar_token, verificar_admin
from app.schemas.schemas import TreinoCreate, TreinoRead
from app.controllers import treinos_controller

treinos = APIRouter(prefix="/treinos", tags=["treinos"])


@treinos.get("/", response_model=List[TreinoRead])
async def ver_meus_treinos(usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return treinos_controller.index(usuario_logado, session)


@treinos.post("/")
async def cadastrar_treino_com_exercicios(dados: TreinoCreate, admin=Depends(verificar_admin), session: Session = Depends(pegar_sessao)):
    return treinos_controller.store(dados, admin, session)


@treinos.delete("/{treino_id}", status_code=status.HTTP_200_OK)
def deletar_treino(treino_id: int, usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return treinos_controller.destroy(treino_id, usuario_logado, session)


@treinos.get("/aluno/{usuario_id}", response_model=List[TreinoRead])
def buscar_treinos_do_aluno(usuario_id: int, usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return treinos_controller.show(usuario_id, usuario_logado, session)


@treinos.patch("/{treino_id}/dia")
def atualizar_dia(
    treino_id: int,
    dia_semana: str | None = Body(default=None, embed=True),
    admin=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return treinos_controller.update(treino_id, dia_semana, admin, session)