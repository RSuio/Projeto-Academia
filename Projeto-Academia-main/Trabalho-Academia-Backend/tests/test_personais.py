# python -m pytest tests/test_personais.py -v


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Usuario, Academia, PersonalAcademia
from app.controllers import personais_controller, academias_controller
from app.schemas.schemas import AcademiaCreate, PersonalVinculoCreate, PersonalPerfilUpdate
from fastapi import HTTPException


engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SessaoDeTeste = sessionmaker(bind=engine)


@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)
    sess = SessaoDeTeste()
    yield sess
    sess.close()
    Base.metadata.drop_all(bind=engine)


def criar_personal(session, nome="Carlos Mendonça", email="carlos@teste.com", admin=True):
    personal = Usuario(nome=nome, email=email, senha="x", admin=admin,
                       especialidade="Hipertrofia", bio="10 anos de experiência")
    session.add(personal)
    session.commit()
    return personal


def criar_academia(session, nome="ForgeFit Matriz"):
    academia = Academia(nome=nome, cidade="São Paulo", endereco="Rua A, 1", telefone="(11) 4002-8900")
    session.add(academia)
    session.commit()
    return academia


def test_catalogo_lista_personais_com_academias(session):
    personal = criar_personal(session)
    academia = criar_academia(session)
    session.add(PersonalAcademia(personal_id=personal.id, academia_id=academia.id,
                                 dias_semana="Segunda, Quarta", horario_inicio="07:00", horario_fim="12:00"))
    session.commit()

    catalogo = personais_controller.catalogo(session)
    assert len(catalogo) == 1
    item = catalogo[0]
    assert item["nome"] == "Carlos Mendonça"
    assert item["especialidade"] == "Hipertrofia"
    assert len(item["academias"]) == 1
    assert item["academias"][0]["academia"]["nome"] == "ForgeFit Matriz"
    assert item["academias"][0]["horario_inicio"] == "07:00"


def test_catalogo_ignora_nao_admin_e_vinculos_inativos(session):
    aluno = criar_personal(session, nome="Aluno", email="aluno@teste.com", admin=False)
    academia = criar_academia(session)
    personal = Usuario(nome="Inativo", email="ini@teste.com", senha="x", admin=True)
    session.add(personal)
    session.commit()
    session.add(PersonalAcademia(personal_id=personal.id, academia_id=academia.id, ativo=False))
    session.commit()

    catalogo = personais_controller.catalogo(session)
    assert catalogo == []


def test_catalogo_filtra_por_academia(session):
    p = criar_personal(session)
    a1 = criar_academia(session, "ForgeFit Matriz")
    a2 = criar_academia(session, "ForgeFit Norte")
    session.add(PersonalAcademia(personal_id=p.id, academia_id=a1.id))
    session.add(PersonalAcademia(personal_id=p.id, academia_id=a2.id))
    session.commit()

    so_matriz = personais_controller.catalogo(session, academia_id=a1.id)
    assert len(so_matriz) == 1
    assert [a["academia"]["nome"] for a in so_matriz[0]["academias"]] == ["ForgeFit Matriz"]


def test_store_academia(session):
    resultado = academias_controller.store(AcademiaCreate(nome="ForgeFit Sul"), session)
    assert "sucesso" in resultado["mensagem"].lower()
    assert session.query(Academia).count() == 1


def test_store_vinculo_apenas_personal_sendo_admin(session):
    admin = criar_personal(session)
    academia = criar_academia(session)

    resultado = personais_controller.store_vinculo(admin.id, PersonalVinculoCreate(academia_id=academia.id), admin, session)
    assert "criado" in resultado["mensagem"].lower()
    assert session.query(PersonalAcademia).count() == 1


def test_store_vinculo_negado_para_nao_admin(session):
    aluno = criar_personal(session, nome="Aluno", email="aluno@teste.com", admin=False)
    academia = criar_academia(session)

    with pytest.raises(HTTPException) as erro:
        personais_controller.store_vinculo(aluno.id, PersonalVinculoCreate(academia_id=academia.id), aluno, session)
    assert erro.value.status_code == 403


def test_meu_personal_retorna_none_sem_vinculo(session):
    aluno = criar_personal(session, nome="Aluno", email="aluno@teste.com", admin=False)
    assert personais_controller.meu_personal(aluno, session) is None


def test_meu_personal_retorna_apenas_vinculos_ativos(session):
    aluno = criar_personal(session, nome="Aluno", email="aluno@teste.com", admin=False)
    personal = criar_personal(session, nome="Personal", email="p@teste.com", admin=True)
    a1 = criar_academia(session, "ForgeFit Matriz")
    a2 = criar_academia(session, "ForgeFit Norte")
    aluno.personal_id = personal.id
    session.add(PersonalAcademia(personal_id=personal.id, academia_id=a1.id))
    session.add(PersonalAcademia(personal_id=personal.id, academia_id=a2.id, ativo=False))
    session.commit()

    perfil = personais_controller.meu_personal(aluno, session)
    assert perfil["nome"] == "Personal"
    assert len(perfil["academias"]) == 1
    assert perfil["academias"][0]["academia"]["nome"] == "ForgeFit Matriz"


def test_vincular_aluno_e_desvincular(session):
    aluno = criar_personal(session, nome="Aluno", email="aluno@teste.com", admin=False)
    personal = criar_personal(session, nome="Personal", email="p@teste.com", admin=True)

    resultado = personais_controller.vincular_aluno(aluno.id, personal.id, personal, session)
    assert "vinculado" in resultado["mensagem"]
    assert aluno.personal_id == personal.id

    resultado = personais_controller.vincular_aluno(aluno.id, None, personal, session)
    assert aluno.personal_id is None


def test_vincular_negado_para_aluno(session):
    aluno = criar_personal(session, nome="Aluno", email="aluno@teste.com", admin=False)
    outro_aluno = criar_personal(session, nome="Outro", email="outro@teste.com", admin=False)

    with pytest.raises(HTTPException) as erro:
        personais_controller.vincular_aluno(outro_aluno.id, 1, aluno, session)
    assert erro.value.status_code == 403


def test_store_vinculo_me_atribui_ao_proprio_personal(session):
    personal = criar_personal(session)
    academia = criar_academia(session)

    resultado = personais_controller.store_vinculo_me(
        PersonalVinculoCreate(academia_id=academia.id, dias_semana="Sexta", horario_inicio="07:00", horario_fim="11:00"),
        personal,
        session,
    )
    vinculo = session.query(PersonalAcademia).filter(PersonalAcademia.personal_id == personal.id).one()
    assert vinculo.dias_semana == "Sexta"
    assert vinculo.horario_inicio == "07:00"


def test_meu_perfil_inclui_flag_ativo(session):
    personal = criar_personal(session)
    academia = criar_academia(session)
    session.add(PersonalAcademia(personal_id=personal.id, academia_id=academia.id, ativo=False))
    session.commit()

    perfil = personais_controller.meu_perfil(personal, session)
    assert perfil["academias"][0]["ativo"] is False


def test_update_meu_perfil(session):
    personal = criar_personal(session)
    resultado = personais_controller.update_meu_perfil(
        PersonalPerfilUpdate(bio="Nova bio", especialidade="Funcional"), personal, session
    )
    assert "sucesso" in resultado["mensagem"]
    assert personal.bio == "Nova bio"
    assert personal.especialidade == "Funcional"