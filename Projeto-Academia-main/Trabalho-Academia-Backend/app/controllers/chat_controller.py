"""
Controller do chatbot do ForgeFit.

Estratégia híbrida (funciona mesmo sem internet / sem chave de API):
  1. REGRAS  -> entende perguntas do domínio e consulta os dados do aluno
                (treinos, progresso, objetivo, personal e catálogo de exercícios).
  2. IA      -> se nenhuma regra casar, tenta Gemini ou Groq (chave no .env).
  3. FALLBACK-> sem chave ou em caso de falha, devolve uma resposta padrão.

Isso garante que a demonstração do trabalho nunca quebre.
"""

import os
import re
import unicodedata

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.controllers import (
    exercicios_controller,
    objetivo_controller,
    personais_controller,
    progresso_controller,
    treinos_controller,
)
from app.database.models import Usuario

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# Palavra digitada (sem acento) -> categoria real do catálogo
CATEGORIAS = {
    "peito": "Peito",
    "costas": "Costas",
    "dorsal": "Costas",
    "perna": "Pernas",
    "pernas": "Pernas",
    "ombro": "Ombros",
    "ombros": "Ombros",
    "biceps": "Bíceps",
    "triceps": "Tríceps",
    "abdomen": "Abdômen",
    "gluteo": "Glúteos",
    "gluteos": "Glúteos",
    "panturrilha": "Panturrilha",
    "cardio": "Cardio",
}

SYSTEM_PROMPT = (
    "Você é o ForgeFit Bot, assistente virtual de um aplicativo de academia. "
    "Responda em português do Brasil, de forma curta (no máximo 5 linhas), "
    "simpática e objetiva. Ajude com dúvidas sobre treinos, exercícios, progresso, "
    "objetivos e uso do app. Não prescreva dietas, medicamentos ou suplementos e "
    "não substitua um profissional de educação física. Se a pergunta fugir do tema "
    "academia, responda brevemente e convide a pessoa a perguntar sobre treinos. "
    "Não use markdown (negrito, asteriscos); escreva em texto simples."
)


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────────────────────────────────────

def _normalizar(texto: str) -> str:
    """Minúsculas e sem acentos, para comparar palavras com segurança."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


def _tem(texto: str, *termos: str) -> bool:
    return any(termo in texto for termo in termos)


def _tem_palavra(texto: str, *palavras: str) -> bool:
    """Igual a _tem, mas exige palavra inteira (evita 'oi' casar com 'foi')."""
    return any(re.search(rf"\b{re.escape(p)}\b", texto) for p in palavras)


def _resposta(texto: str, fonte: str = "regras") -> dict:
    return {"resposta": texto, "fonte": fonte}


def _precisa_login() -> dict:
    return _resposta("Para eu consultar seus dados, faça login no app primeiro. 😉")


def _menu() -> str:
    return (
        "Posso te ajudar com:\n"
        "• Seus treinos — ex.: \"qual meu treino de segunda?\"\n"
        "• Seu progresso — ex.: \"quantos treinos eu já fiz?\"\n"
        "• Sua meta — ex.: \"como está meu objetivo?\"\n"
        "• Seu personal — ex.: \"quem é meu personal?\"\n"
        "• Exercícios — ex.: \"exercícios de peito\"\n"
        "É só perguntar!"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Regras de domínio
# ─────────────────────────────────────────────────────────────────────────────

def _regra_personal(usuario: Usuario | None, session: Session) -> dict:
    if not usuario:
        return _precisa_login()

    personal = personais_controller.meu_personal(usuario, session)
    if not personal:
        return _resposta(
            "Você ainda não está vinculado a um personal. "
            "Fale com a academia para fazer o vínculo."
        )

    linhas = [f"Seu personal é {personal['nome']}."]
    if personal.get("especialidade"):
        linhas.append(f"Especialidade: {personal['especialidade']}.")
    if personal.get("bio"):
        linhas.append(personal["bio"])

    academias = personal.get("academias") or []
    if academias:
        locais = []
        for a in academias:
            local = a["academia"]["nome"]
            if a.get("dias_semana"):
                local += f" ({a['dias_semana']})"
            locais.append(local)
        linhas.append("Atende em: " + "; ".join(locais) + ".")

    return _resposta("\n".join(linhas))


def _regra_objetivo(usuario: Usuario | None, session: Session) -> dict:
    if not usuario:
        return _precisa_login()

    try:
        dados = objetivo_controller.index(usuario, session)
    except HTTPException:
        return _resposta(
            "Você ainda não tem um objetivo definido. "
            "Seu personal pode cadastrar uma meta para você."
        )

    objetivo = dados.objetivo
    situacao = "concluído 🎉" if dados.concluido else f"{dados.percentual}% concluído"
    return _resposta(
        f"Sua meta é {objetivo.meta_treinos} treinos até "
        f"{objetivo.data_fim.strftime('%d/%m/%Y')}.\n"
        f"Você já fez {dados.treinos_realizados} treino(s) — {situacao}.\n"
        f"Faltam {dados.dias_restantes} dia(s)."
    )


def _regra_progresso(usuario: Usuario | None, session: Session) -> dict:
    if not usuario:
        return _precisa_login()

    dados = progresso_controller.index(usuario, session)
    if dados.total_realizados == 0:
        return _resposta(
            "Você ainda não marcou nenhum treino como feito. "
            "Quando concluir um treino, use o botão \"Marcar como feito\" na aba Meus Treinos. 💪"
        )

    ultimo = dados.ultimo_treino.strftime("%d/%m/%Y") if dados.ultimo_treino else "—"
    nesta_semana = sum(dados.por_semana)
    return _resposta(
        f"Você já concluiu {dados.total_realizados} treino(s). 🔥\n"
        f"Sequência atual: {dados.streak_atual} dia(s).\n"
        f"Nesta semana: {nesta_semana} treino(s).\n"
        f"Último treino: {ultimo}."
    )


def _regra_treinos(usuario: Usuario | None, session: Session, texto: str) -> dict:
    if not usuario:
        return _precisa_login()

    treinos = treinos_controller.index(usuario, session)
    if not treinos:
        return _resposta(
            "Você ainda não tem treinos cadastrados. "
            "Seu personal pode criar um treino para você."
        )

    dia = next((d for d in DIAS_SEMANA if _normalizar(d) in texto), None)
    if dia:
        treinos = [t for t in treinos if _normalizar(t.dia_semana or "") == _normalizar(dia)]
        if not treinos:
            return _resposta(f"Você não tem treino cadastrado para {dia}.")
        cabecalho = f"Seu treino de {dia}:"
    else:
        cabecalho = "Seus treinos:"

    linhas = [cabecalho]
    for treino in treinos[:5]:
        linha = f"• {treino.nome} — {treino.objetivo}"
        if treino.dia_semana:
            linha += f" ({treino.dia_semana})"

        exercicios = getattr(treino, "exercicios", []) or []
        nomes = []
        for exercicio in exercicios[:4]:
            catalogo = getattr(exercicio, "catalogo", None)
            if catalogo:
                nomes.append(f"{catalogo.nome} {exercicio.series}x{exercicio.repeticoes}")
        if nomes:
            linha += ": " + ", ".join(nomes)
            if len(exercicios) > 4:
                linha += f" (+{len(exercicios) - 4})"
        linhas.append(linha)

    if len(treinos) > 5:
        linhas.append(f"... e mais {len(treinos) - 5} treino(s).")

    return _resposta("\n".join(linhas))


def _regra_exercicios(session: Session, texto: str) -> dict:
    categoria = next((cat for chave, cat in CATEGORIAS.items() if chave in texto), "")

    busca = ""
    achado = re.search(r"como (?:fazer|executar|treinar)\s+(.+)", texto)
    if achado:
        busca = achado.group(1).strip(" ?.!")
        if categoria:
            busca = busca.replace(_normalizar(categoria), " ")
        # Remove palavras genéricas para sobrar o nome do exercício
        for generica in ("exercicio", "exercicios", "de", "do", "da", "para", "o", "a"):
            busca = re.sub(rf"\b{generica}\b", " ", busca)
        busca = " ".join(busca.split())

    exercicios = exercicios_controller.listar_catalogo(
        session, busca=busca, categoria=categoria, limit=5
    )
    if not exercicios:
        exercicios = exercicios_controller.listar_catalogo(session, limit=5)
    if not exercicios:
        return _resposta("O catálogo de exercícios está vazio no momento.")

    if busca:
        cabecalho = f"Encontrei estes exercícios para \"{busca}\":"
    elif categoria:
        cabecalho = f"Exercícios de {categoria}:"
    else:
        cabecalho = "Alguns exercícios do catálogo:"

    linhas = [cabecalho]
    for exercicio in exercicios:
        extra = f" ({exercicio.equipamento})" if exercicio.equipamento else ""
        linhas.append(f"• {exercicio.nome}{extra}")
    linhas.append('Abra a aba "Criar Treino" para ver detalhes e vídeos.')
    return _resposta("\n".join(linhas))


# ─────────────────────────────────────────────────────────────────────────────
# IA (opcional)
# ─────────────────────────────────────────────────────────────────────────────

def _provedor_ia() -> str | None:
    """Descobre qual provedor usar. Sem chave configurada, retorna None."""
    provedor = (os.getenv("CHATBOT_PROVIDER") or "").strip().lower()

    if provedor == "groq" and os.getenv("GROQ_API_KEY"):
        return "groq"
    if provedor == "gemini" and os.getenv("GEMINI_API_KEY"):
        return "gemini"

    # Auto-detecção (ou fallback se o provedor escolhido estiver sem chave)
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    return None


def _historico_para_mensagens(historico) -> list[dict]:
    mensagens = []
    for item in (historico or [])[-10:]:
        papel = "assistant" if getattr(item, "papel", "") in ("assistant", "model", "bot") else "user"
        conteudo = (getattr(item, "conteudo", "") or "").strip()
        if conteudo:
            mensagens.append({"role": papel, "content": conteudo[:2000]})
    return mensagens


def _chamar_gemini(mensagem: str, historico) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    contents = []
    for m in _historico_para_mensagens(historico):
        contents.append({
            "role": "model" if m["role"] == "assistant" else "user",
            "parts": [{"text": m["content"]}],
        })
    contents.append({"role": "user", "parts": [{"text": mensagem}]})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    resposta = httpx.post(
        url,
        params={"key": api_key},
        json={
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": contents,
            "generationConfig": {"temperature": 1.0, "maxOutputTokens": 512},
        },
        timeout=20.0,
    )
    resposta.raise_for_status()
    partes = resposta.json()["candidates"][0]["content"]["parts"]
    texto = "".join(p.get("text", "") for p in partes if not p.get("thought")).strip()
    return texto or None


def _chamar_groq(mensagem: str, historico) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    modelo = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}]
    mensagens += _historico_para_mensagens(historico)
    mensagens.append({"role": "user", "content": mensagem})

    resposta = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": modelo, "messages": mensagens, "temperature": 0.7, "max_tokens": 400},
        timeout=20.0,
    )
    resposta.raise_for_status()
    texto = (resposta.json()["choices"][0]["message"]["content"] or "").strip()
    return texto or None


def _responder_com_ia(mensagem: str, historico) -> str | None:
    provedor = _provedor_ia()
    if not provedor:
        return None
    try:
        if provedor == "gemini":
            return _chamar_gemini(mensagem, historico)
        return _chamar_groq(mensagem, historico)
    except Exception as erro:  # rede, cota, chave inválida, etc.
        print(f"⚠️ Chatbot IA indisponível ({provedor}): {erro}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Entrada principal
# ─────────────────────────────────────────────────────────────────────────────

def status() -> dict:
    provedor = _provedor_ia()
    return {"ia_configurada": provedor is not None, "provedor": provedor}


def responder(
    mensagem: str,
    usuario: Usuario | None,
    session: Session,
    historico=None,
) -> dict:
    texto = _normalizar(mensagem)

    if not texto:
        return _resposta("Escreva uma pergunta para eu poder ajudar. 🙂")

    # Ajuda
    if _tem(texto, "ajuda", "menu", "o que voce faz", "o que vc faz", "como funciona", "comandos"):
        return _resposta(_menu())

    # Segurança: dor/lesão não é assunto para o bot resolver
    if _tem_palavra(texto, "dor", "dores", "doendo", "machuquei", "machucado", "lesao", "lesionado"):
        return _resposta(
            "Se você está sentindo dor ou se machucou, pare o exercício e procure "
            "um profissional de saúde. Eu não consigo avaliar lesões. 🩺"
        )

    # Personal
    if _tem(texto, "personal"):
        return _regra_personal(usuario, session)

    # Objetivo
    if _tem_palavra(texto, "objetivo", "objetivos", "meta", "metas"):
        return _regra_objetivo(usuario, session)

    # Progresso (vem antes de "treino", pois "quantos treinos" contém "treino")
    if _tem(texto, "progresso", "quantos treinos", "historico", "sequencia",
            "streak", "ja fiz", "ja foram", "fiz"):
        return _regra_progresso(usuario, session)

    # Treinos
    if _tem(texto, "treino", "treinos"):
        return _regra_treinos(usuario, session, texto)

    # Exercícios
    if _tem(texto, "exercicio", "exercicios", "como fazer", "como executar", "como treinar",
            "peito", "costas", "dorsal", "perna", "ombro", "biceps", "triceps",
            "abdomen", "gluteo", "panturrilha", "cardio"):
        return _regra_exercicios(session, texto)

    # Saudações (só se nenhuma intenção acima casou — assim "oi, qual meu treino?"
    # ainda responde sobre o treino).
    if _tem_palavra(texto, "oi", "ola", "eai", "hey") or _tem(
        texto, "bom dia", "boa tarde", "boa noite"
    ):
        nome = f", {usuario.nome.split()[0]}" if usuario else ""
        return _resposta(f"Olá{nome}! 👋 Eu sou o assistente do ForgeFit.\n\n{_menu()}")

    # Agradecimentos / despedidas
    if _tem_palavra(texto, "obrigado", "obrigada", "valeu", "agradeco"):
        return _resposta("De nada! 💪 Se precisar de mais alguma coisa, é só chamar.")
    if _tem_palavra(texto, "tchau", "ate logo", "ate mais", "falou"):
        return _resposta("Até logo! 👋 Bons treinos!")

    # IA (se configurada)
    resposta_ia = _responder_com_ia(mensagem, historico)
    if resposta_ia:
        return _resposta(resposta_ia, "ia")

    # Fallback offline
    return _resposta(
        "Ainda não sei responder isso, mas posso ajudar com treinos, progresso, "
        "objetivos, seu personal e exercícios.\n\n" + _menu(),
        "fallback",
    )
