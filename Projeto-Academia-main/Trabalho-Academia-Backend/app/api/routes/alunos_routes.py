from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import pegar_sessao, verificar_token, verificar_admin
from app.schemas.schemas import VinculoAlunoPersonal
from app.controllers import auth_controller, personais_controller

alunos = APIRouter(prefix="/alunos", tags=["alunos"])

@alunos.get("/")
async def listar_alunos(usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return auth_controller.index(usuario_logado, session)

@alunos.get("/meu-personal")
async def meu_personal(usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    """Aluno logado: perfil público do personal ao qual está vinculado (ou null)."""
    return personais_controller.meu_personal(usuario_logado, session)

@alunos.patch("/{aluno_id}/personal")
async def vincular_personal(
    aluno_id: int,
    dados: VinculoAlunoPersonal,
    admin=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    """Personal vincula/desvincula um aluno (personal_id null desvincula)."""
    return personais_controller.vincular_aluno(aluno_id, dados.personal_id, admin, session)