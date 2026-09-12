from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import pegar_sessao, verificar_admin
from app.schemas.schemas import AcademiaCreate, AcademiaRead
from app.controllers import academias_controller

academias = APIRouter(prefix="/academias", tags=["academias"])


@academias.get("/", response_model=List[AcademiaRead])
async def listar_academias(session: Session = Depends(pegar_sessao)):
    return academias_controller.index(session)


@academias.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_academia(
    dados: AcademiaCreate,
    admin=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return academias_controller.store(dados, session)