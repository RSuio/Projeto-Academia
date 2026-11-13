# 🤖 Chatbot ForgeFit

Assistente virtual do projeto de academia. Responde perguntas sobre **treinos,
progresso, objetivo, personal e catálogo de exercícios**, direto no app.

## Como funciona (arquitetura híbrida)

```
Pergunta do usuário
        │
        ▼
┌─────────────────────────────┐
│ 1. Regras de intenção       │  consulta o banco (dados do aluno)
│    (sempre disponível)      │  e responde na hora, sem internet
└─────────────┬───────────────┘
              │ não encontrou
              ▼
┌─────────────────────────────┐
│ 2. IA opcional              │  Gemini ou Groq, se houver chave no .env
└─────────────┬───────────────┘
              │ sem chave / erro / cota
              ▼
┌─────────────────────────────┐
│ 3. Fallback                 │  resposta padrão + menu de ajuda
└─────────────────────────────┘
```

Isso garante que a apresentação do trabalho **nunca quebre**: mesmo sem internet
ou sem chave de API, o chatbot continua respondendo.

## O que ele responde

| Pergunta | O que acontece |
|---|---|
| "oi" / "bom dia" | Saudação + menu |
| "qual meu treino de segunda?" | Lista o treino do dia com séries e repetições |
| "quantos treinos eu já fiz?" | Total, sequência e treinos da semana |
| "como está meu objetivo?" | Meta, % concluído e dias restantes |
| "quem é meu personal?" | Nome, especialidade e academias |
| "exercícios de peito" | Busca no catálogo por categoria |
| "como fazer supino?" | Busca no catálogo pelo nome |
| "estou com dor no joelho" | Orienta procurar um profissional (segurança) |
| "obrigado" / "tchau" | Agradecimento / despedida |
| Pergunta fora do tema | IA (se configurada) ou fallback |

Sem login, o bot responde dúvidas gerais e pede login para consultar dados pessoais.

## Endpoints

### `GET /chat/status`
Informa se alguma IA está configurada.

```json
{ "ia_configurada": false, "provedor": null }
```

### `POST /chat/`
O token é **opcional**. Com token, o bot consulta os dados do aluno logado.

```json
{
  "mensagem": "qual meu treino de segunda?",
  "historico": [
    { "papel": "user", "conteudo": "oi" },
    { "papel": "assistant", "conteudo": "Olá! ..." }
  ]
}
```

Resposta:

```json
{
  "resposta": "Seu treino de Segunda:\n• Treino A — Hipertrofia: Supino Reto 4x10",
  "fonte": "regras"
}
```

`fonte` pode ser `"regras"`, `"ia"` ou `"fallback"`.

## Como rodar

**Backend** (na pasta `Trabalho-Academia-Backend`):

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**Frontend**: abra o `index.html` (ou use a extensão Live Server). O widget de
chat aparece no canto inferior direito.

## Ativar a IA gratuita (opcional)

Sem chave, o bot funciona só com regras. Para respostas dinâmicas em perguntas
abertas, escolha **um** provedor e preencha o `.env`:

### Gemini (Google AI Studio — plano gratuito)

1. Gere uma chave em <https://aistudio.google.com/apikey>.
2. No `.env`:

```env
CHATBOT_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
```

3. Reinicie o backend.

> Os nomes dos modelos mudam com o tempo. Se o modelo padrão não estiver mais
> disponível, veja a lista atual em <https://ai.google.dev/gemini-api/docs/models>
> e ajuste `GEMINI_MODEL`. Enquanto isso, o bot continua funcionando por regras.

### Groq (plano gratuito)

1. Gere uma chave em <https://console.groq.com/keys>.
2. No `.env`:

```env
CHATBOT_PROVIDER=groq
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=openai/gpt-oss-120b
```

3. Reinicie o backend.

> A chave fica **apenas no backend**. O frontend nunca vê a chave.

## Testes

```bash
python -m pytest tests/ -q
```

A suíte cobre as regras, o fallback e a integração com Gemini/Groq **simulada**
(não gasta chave real). O fluxo completo também foi validado com um teste
ponta-a-ponta via HTTP (login, treino, progresso, objetivo e personal).

## Estrutura dos arquivos

```
Trabalho-Academia-Backend/
├── app/
│   ├── controllers/chat_controller.py   # regras + IA + fallback
│   ├── api/routes/chat_routes.py        # POST /chat/ e GET /chat/status
│   └── schemas/schemas.py               # ChatMensagem, ChatResposta...
├── tests/test_chat.py                   # 19 testes do chatbot
└── .env                                 # chaves (opcionais)

Trabalho-Academia-Frontend/
├── index.html                           # widget flutuante
└── js/chat.js                           # abrir/fechar, enviar, histórico
```

## Segurança e limites

- Não prescreve dietas, medicamentos ou suplementos.
- Em caso de dor/lesão, orienta procurar um profissional de saúde.
- A IA recebe apenas a mensagem e o histórico da conversa; os dados do banco são
  consultados localmente pelas regras.
- Limite de 1.000 caracteres por mensagem e 10 mensagens de histórico.
- A chave da IA fica no `.env` do backend (não versionar esse arquivo).
