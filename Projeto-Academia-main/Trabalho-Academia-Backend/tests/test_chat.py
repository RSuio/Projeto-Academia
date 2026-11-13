# python -m pytest tests/test_chat.py -v

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import (
    Base,
    ExercicioCatalogo,
    Treino,
    TreinoExercicio,
    TreinoRealizado,
    Usuario,
)
from app.controllers import chat_controller


engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SessaoDeTeste = sessionmaker(bind=engine)


@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)
    sess = SessaoDeTeste()
    yield sess
    sess.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def sem_chave_de_ia(monkeypatch):
    """Garante que os testes rodem sempre no modo 'regras', sem chamar a internet."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("CHATBOT_PROVIDER", raising=False)


def criar_aluno(session, email="ana@teste.com"):
    aluno = Usuario(nome="Ana Souza", email=email, senha="x", admin=False)
    session.add(aluno)
    session.commit()
    session.refresh(aluno)
    return aluno


def test_saudacao_sem_login(session):
    resultado = chat_controller.responder("Oi", None, session)
    assert resultado["fonte"] == "regras"
    assert "forgefit" in resultado["resposta"].lower()


def test_menu_de_ajuda(session):
    resultado = chat_controller.responder("ajuda", None, session)
    assert resultado["fonte"] == "regras"
    assert "treinos" in resultado["resposta"].lower()


def test_pedido_de_treino_sem_login_pede_login(session):
    resultado = chat_controller.responder("qual meu treino de segunda?", None, session)
    assert "login" in resultado["resposta"].lower()


def test_progresso_sem_registros(session):
    aluno = criar_aluno(session)
    resultado = chat_controller.responder("quantos treinos eu já fiz?", aluno, session)
    assert resultado["fonte"] == "regras"
    assert "ainda não" in resultado["resposta"].lower()


def test_lista_treino_do_dia_com_exercicios(session):
    aluno = criar_aluno(session)
    catalogo = ExercicioCatalogo(api_id=1, nome="Supino Reto", categoria="Peito")
    session.add(catalogo)
    session.commit()
    session.refresh(catalogo)

    treino = Treino(nome="Treino A", objetivo="Hipertrofia",
                    usuario_id=aluno.id, dia_semana="Segunda")
    session.add(treino)
    session.commit()
    session.refresh(treino)

    session.add(TreinoExercicio(treino_id=treino.id, exercicio_catalogo_id=catalogo.id,
                                series=4, repeticoes=10, ordem=1))
    session.commit()

    resultado = chat_controller.responder("qual meu treino de segunda?", aluno, session)
    assert "Treino A" in resultado["resposta"]
    assert "Supino Reto 4x10" in resultado["resposta"]


def test_progresso_com_registro(session):
    aluno = criar_aluno(session)
    treino = Treino(nome="Treino B", objetivo="Força", usuario_id=aluno.id)
    session.add(treino)
    session.commit()
    session.refresh(treino)
    session.add(TreinoRealizado(treino_id=treino.id, usuario_id=aluno.id))
    session.commit()

    resultado = chat_controller.responder("meu progresso", aluno, session)
    assert "1 treino" in resultado["resposta"].lower()
    assert resultado["fonte"] == "regras"


def test_objetivo_sem_meta(session):
    aluno = criar_aluno(session)
    resultado = chat_controller.responder("como está meu objetivo?", aluno, session)
    assert "ainda não" in resultado["resposta"].lower()


def test_exercicios_por_categoria(session):
    session.add(ExercicioCatalogo(api_id=1, nome="Supino Reto", categoria="Peito"))
    session.commit()

    resultado = chat_controller.responder("quais exercícios de peito?", None, session)
    assert "Supino Reto" in resultado["resposta"]


def test_fallback_sem_ia(session):
    resultado = chat_controller.responder("qual a capital da França?", None, session)
    assert resultado["fonte"] == "fallback"
    assert "treinos" in resultado["resposta"].lower()


def test_nao_confunde_oi_no_meio_da_frase(session):
    # "foram" contém "oi"? não; "foi" sim. Garante que não vira saudação.
    aluno = criar_aluno(session)
    resultado = chat_controller.responder("quantos treinos já foram feitos?", aluno, session)
    assert resultado["fonte"] == "regras"
    assert "olá" not in resultado["resposta"].lower()


def test_meta_no_meio_da_palavra_nao_vira_objetivo(session):
    # "metade" contém "meta", mas não deve ser confundido com objetivo
    resultado = chat_controller.responder("quanto é a metade de dez?", None, session)
    assert resultado["fonte"] == "fallback"


def test_busca_por_nome_do_exercicio(session):
    session.add(ExercicioCatalogo(api_id=1, nome="Supino Reto", categoria="Peito"))
    session.commit()

    resultado = chat_controller.responder("como fazer supino?", None, session)
    assert "Supino Reto" in resultado["resposta"]


def test_saudacao_com_pergunta_responde_a_pergunta(session):
    aluno = criar_aluno(session)
    # "oi" não deve engolir a pergunta sobre treino
    resultado = chat_controller.responder("oi, qual meu treino?", aluno, session)
    assert "forgefit" not in resultado["resposta"].lower()
    assert "treino" in resultado["resposta"].lower()


def test_agradecimento(session):
    resultado = chat_controller.responder("valeu!", None, session)
    assert "de nada" in resultado["resposta"].lower()


def test_status_sem_ia_configurada(session):
    assert chat_controller.status() == {"ia_configurada": False, "provedor": None}


# ── Integração com IA (simulada, sem gastar chave real) ──────────────────────

class _RespostaFalsa:
    def __init__(self, dados):
        self._dados = dados

    def raise_for_status(self):
        pass

    def json(self):
        return self._dados


def test_ia_gemini_quando_configurada(monkeypatch, session):
    monkeypatch.setenv("CHATBOT_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")

    def post_falso(url, **kwargs):
        assert "generativelanguage.googleapis.com" in url
        assert kwargs["params"]["key"] == "chave-de-teste"
        # Formato oficial da API REST do Gemini
        assert "systemInstruction" in kwargs["json"]
        assert "generationConfig" in kwargs["json"]
        assert kwargs["json"]["contents"][-1]["role"] == "user"
        return _RespostaFalsa({
            "candidates": [{"content": {"parts": [{"text": "Resposta dinâmica da IA"}]}}]
        })

    monkeypatch.setattr(chat_controller.httpx, "post", post_falso)

    resultado = chat_controller.responder("qual a capital da França?", None, session)
    assert resultado == {"resposta": "Resposta dinâmica da IA", "fonte": "ia"}


def test_ia_groq_quando_configurada(monkeypatch, session):
    monkeypatch.setenv("CHATBOT_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-de-teste")

    def post_falso(url, **kwargs):
        assert "api.groq.com" in url
        assert kwargs["headers"]["Authorization"] == "Bearer chave-de-teste"
        return _RespostaFalsa({
            "choices": [{"message": {"content": "Resposta do Groq"}}]
        })

    monkeypatch.setattr(chat_controller.httpx, "post", post_falso)

    resultado = chat_controller.responder("qual a capital da França?", None, session)
    assert resultado == {"resposta": "Resposta do Groq", "fonte": "ia"}


def test_ia_com_erro_cai_no_fallback(monkeypatch, session):
    monkeypatch.setenv("CHATBOT_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")

    def post_com_erro(*args, **kwargs):
        raise RuntimeError("sem internet")

    monkeypatch.setattr(chat_controller.httpx, "post", post_com_erro)

    resultado = chat_controller.responder("qual a capital da França?", None, session)
    assert resultado["fonte"] == "fallback"


def test_status_com_ia_configurada(monkeypatch):
    monkeypatch.setenv("CHATBOT_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    assert chat_controller.status() == {"ia_configurada": True, "provedor": "gemini"}
