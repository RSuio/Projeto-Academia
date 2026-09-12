from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import pegar_sessao, verificar_token
from app.schemas.schemas import TreinoRealizadoCreate, TreinoRealizadoRead, DashboardProgresso
from app.controllers import progresso_controller

progresso = APIRouter(prefix="/progresso", tags=["Progresso"])


@progresso.post("/")
def marcar_treino(dados: TreinoRealizadoCreate, usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return progresso_controller.store(dados, usuario_logado, session)


@progresso.get("/", response_model=DashboardProgresso)
def dashboard(usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return progresso_controller.index(usuario_logado, session)


@progresso.get("/historico", response_model=List[TreinoRealizadoRead])
def historico(usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return progresso_controller.show_historico(usuario_logado, session)


@progresso.get("/relatorio-mensal")
def relatorio_mensal(usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return progresso_controller.show_relatorio_mensal(usuario_logado, session)
