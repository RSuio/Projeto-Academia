from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import pegar_sessao, verificar_token_opcional
from app.controllers import chat_controller
from app.schemas.schemas import ChatMensagem, ChatResposta

chat = APIRouter(prefix="/chat", tags=["Chatbot"])


@chat.get("/status")
def status_chat():
    """Informa se alguma IA está configurada (o chatbot por regras funciona sempre)."""
    return chat_controller.status()


@chat.post("/", response_model=ChatResposta)
def conversar(
    dados: ChatMensagem,
    usuario=Depends(verificar_token_opcional),
    session: Session = Depends(pegar_sessao),
):
    """
    Conversa com o chatbot.

    O token é opcional: se o usuário estiver logado, o bot consulta os dados dele
    (treinos, progresso, objetivo e personal). Sem login, responde dúvidas gerais.
    """
    return chat_controller.responder(dados.mensagem, usuario, session, dados.historico)
