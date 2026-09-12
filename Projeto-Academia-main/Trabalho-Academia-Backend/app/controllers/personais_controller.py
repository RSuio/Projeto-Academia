from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import Usuario, PersonalAcademia
from app.schemas.schemas import PersonalVinculoCreate, PersonalVinculoUpdate, PersonalPerfilUpdate


def _serializar_personal(personal: Usuario, vinculos: list, incluir_ativo: bool = False):
    return {
        "id": personal.id,
        "nome": personal.nome,
        "especialidade": personal.especialidade,
        "bio": personal.bio,
        "academias": [
            {
                "id": v.id,
                "academia": {
                    "id": v.academia.id,
                    "nome": v.academia.nome,
                    "endereco": v.academia.endereco,
                    "cidade": v.academia.cidade,
                    "telefone": v.academia.telefone,
                },
                "dias_semana": v.dias_semana,
                "horario_inicio": v.horario_inicio,
                "horario_fim": v.horario_fim,
                **({"ativo": v.ativo} if incluir_ativo else {}),
            }
            for v in vinculos
        ],
    }


def catalogo(session: Session, academia_id: int | None = None):
    """Catálogo público de personais com academias, dias e horários."""
    personais = (
        session.query(Usuario)
        .filter(Usuario.admin == True, Usuario.ativo == True)
        .order_by(Usuario.nome)
        .all()
    )

    resultado = []
    for p in personais:
        vinculos = [v for v in p.academias_atuacao if v.ativo]
        if academia_id:
            vinculos = [v for v in vinculos if v.academia_id == academia_id]
        if not vinculos:
            continue
        resultado.append(_serializar_personal(p, vinculos))

    return resultado


def store_vinculo(personal_id: int, dados: PersonalVinculoCreate, usuario_logado, session: Session):
    if not getattr(usuario_logado, "admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem vincular personais a academias."
        )

    personal = session.query(Usuario).filter(Usuario.id == personal_id).first()
    if not personal or not personal.admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal trainer não encontrado."
        )

    vinculo = PersonalAcademia(
        personal_id=personal.id,
        academia_id=dados.academia_id,
        dias_semana=dados.dias_semana,
        horario_inicio=dados.horario_inicio,
        horario_fim=dados.horario_fim,
    )
    session.add(vinculo)
    session.commit()

    return {
        "mensagem": f"Vínculo criado: {personal.nome} agora atua nesta academia.",
        "vinculo": _serializar_personal(personal, [vinculo])["academias"][0],
    }


def update_vinculo(vinculo_id: int, dados: PersonalVinculoUpdate, usuario_logado, session: Session):
    if not getattr(usuario_logado, "admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem alterar vínculos."
        )

    vinculo = session.query(PersonalAcademia).filter(PersonalAcademia.id == vinculo_id).first()
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vínculo não encontrado."
        )

    vinculo.dias_semana = dados.dias_semana
    vinculo.horario_inicio = dados.horario_inicio
    vinculo.horario_fim = dados.horario_fim
    vinculo.ativo = dados.ativo
    session.commit()

    return {"mensagem": "Vínculo atualizado com sucesso!"}


def destroy_vinculo(vinculo_id: int, usuario_logado, session: Session):
    if not getattr(usuario_logado, "admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem remover vínculos."
        )

    vinculo = session.query(PersonalAcademia).filter(PersonalAcademia.id == vinculo_id).first()
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vínculo não encontrado."
        )

    session.delete(vinculo)
    session.commit()
    return {"mensagem": "Vínculo removido com sucesso!"}


def meu_personal(aluno: Usuario, session: Session):
    """Perfil público do personal ao qual o aluno está vinculado."""
    if not getattr(aluno, "meu_personal", None):
        return None

    personal = aluno.meu_personal
    vinculos = [v for v in personal.academias_atuacao if v.ativo]
    return _serializar_personal(personal, vinculos)


def vincular_aluno(aluno_id: int, personal_id: int | None, usuario_logado, session: Session):
    if not getattr(usuario_logado, "admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas personais podem vincular alunos."
        )

    aluno = session.query(Usuario).filter(Usuario.id == aluno_id).first()
    if not aluno or aluno.admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado."
        )

    if personal_id is not None:
        personal = session.query(Usuario).filter(Usuario.id == personal_id).first()
        if not personal or not personal.admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal trainer não encontrado."
            )

    aluno.personal_id = personal_id
    session.commit()
    nome_personal = personal.nome if personal_id is not None else None
    if nome_personal:
        return {"mensagem": f"Aluno '{aluno.nome}' vinculado a '{nome_personal}'."}
    return {"mensagem": f"Aluno '{aluno.nome}' desvinculado."}


def meu_perfil(personal: Usuario, session: Session):
    """Perfil completo do próprio personal, com todos os vínculos (ativos ou não)."""
    vinculos = list(personal.academias_atuacao)
    return _serializar_personal(personal, vinculos, incluir_ativo=True)


def update_meu_perfil(dados: PersonalPerfilUpdate, personal: Usuario, session: Session):
    if dados.especialidade is not None:
        personal.especialidade = dados.especialidade
    if dados.bio is not None:
        personal.bio = dados.bio
    session.commit()
    return {"mensagem": "Perfil atualizado com sucesso!"}


def store_vinculo_me(dados: PersonalVinculoCreate, personal: Usuario, session: Session):
    vinculo = PersonalAcademia(
        personal_id=personal.id,
        academia_id=dados.academia_id,
        dias_semana=dados.dias_semana,
        horario_inicio=dados.horario_inicio,
        horario_fim=dados.horario_fim,
    )
    session.add(vinculo)
    session.commit()
    return {
        "mensagem": f"Atuação adicionada: você agora atende nesta academia.",
        "vinculo": _serializar_personal(personal, [vinculo], incluir_ativo=True)["academias"][0],
    }