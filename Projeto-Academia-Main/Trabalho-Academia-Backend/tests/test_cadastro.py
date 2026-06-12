
# python -m pytest tests/test_cadastro.py -v


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.controllers.auth_controller import store as cadastrar_usuario
from app.schemas.schemas import UsuarioSchema
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


def test_cadastrar_usuario_com_sucesso(session):
    schema = UsuarioSchema(
        nome="João Silva",
        email="joao@teste.com",
        senha="senha123"
    )

    resultado = cadastrar_usuario(schema, session)
    assert "sucesso" in resultado["mensagem"].lower()


def test_cadastrar_email_duplicado_deve_falhar(session):
    schema = UsuarioSchema(
        nome="João Silva",
        email="joao@teste.com",
        senha="senha123"
    )

    cadastrar_usuario(schema, session)
    with pytest.raises(HTTPException) as erro:
        cadastrar_usuario(schema, session)

    assert erro.value.status_code == 400