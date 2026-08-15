from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import pegar_sessao, verificar_token
from app.controllers import auth_controller

alunos = APIRouter(prefix="/alunos", tags=["alunos"])

@alunos.get("/")
async def listar_alunos(usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return auth_controller.index(usuario_logado, session)
