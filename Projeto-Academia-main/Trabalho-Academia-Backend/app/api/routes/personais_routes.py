from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.dependencies import pegar_sessao, verificar_admin
from app.schemas.schemas import PersonalVinculoCreate, PersonalVinculoUpdate, PersonalRead, PersonalPerfilUpdate
from app.controllers import personais_controller

personais = APIRouter(prefix="/personais", tags=["personais"])


@personais.get("/", response_model=List[PersonalRead])
async def listar_personais(
    academia_id: Optional[int] = None,
    session: Session = Depends(pegar_sessao)
):
    """Catálogo público: personais disponíveis com academias e horários."""
    return personais_controller.catalogo(session, academia_id=academia_id)


@personais.get("/me")
def meu_perfil(
    usuario_logado=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    """Perfil completo do próprio personal (vínculos ativos e inativos)."""
    return personais_controller.meu_perfil(usuario_logado, session)


@personais.patch("/me")
def atualizar_meu_perfil(
    dados: PersonalPerfilUpdate,
    usuario_logado=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return personais_controller.update_meu_perfil(dados, usuario_logado, session)


@personais.post("/me/academias", status_code=status.HTTP_201_CREATED)
def vincular_minha_academia(
    dados: PersonalVinculoCreate,
    usuario_logado=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    """Personal adiciona uma academia à própria atuação (dias e horários)."""
    return personais_controller.store_vinculo_me(dados, usuario_logado, session)


@personais.post("/{personal_id}/academias", status_code=status.HTTP_201_CREATED)
def vincular_personal_a_academia(
    personal_id: int,
    dados: PersonalVinculoCreate,
    admin=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return personais_controller.store_vinculo(personal_id, dados, admin, session)


@personais.patch("/academias/{vinculo_id}")
def atualizar_vinculo(
    vinculo_id: int,
    dados: PersonalVinculoUpdate,
    admin=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return personais_controller.update_vinculo(vinculo_id, dados, admin, session)


@personais.delete("/academias/{vinculo_id}")
def remover_vinculo(
    vinculo_id: int,
    admin=Depends(verificar_admin),
    session: Session = Depends(pegar_sessao)
):
    return personais_controller.destroy_vinculo(vinculo_id, admin, session)