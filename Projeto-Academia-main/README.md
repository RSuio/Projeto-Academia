<div align="center">

# 💪 ForgeFit

### Sistema de Gerenciamento de Academia e Treinos

Plataforma web que conecta **alunos**, **personal trainers** e **academias** — com criação de treinos, acompanhamento de progresso, metas e um **chatbot assistente** com IA gratuita opcional.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Tests](https://img.shields.io/badge/testes-34%20passando-2ea44f?style=for-the-badge&logo=pytest&logoColor=white)

</div>

---

## 📖 Sobre o projeto

O **ForgeFit** é um sistema web completo para gerenciamento de academia, desenvolvido como trabalho da disciplina de **Engenharia de Software**.

O personal trainer monta treinos personalizados, vincula alunos, cadastra as academias onde atua e define metas. O aluno visualiza seus treinos, marca treinos como realizados, acompanha o progresso e encontra seu personal. E, para completar, um **chatbot** responde dúvidas sobre treinos, progresso, metas, personal e exercícios.

> 📄 A documentação completa de engenharia (requisitos funcionais/não funcionais, regras de negócio, casos de uso, arquitetura e modelo de dados) está em [`Documento-Trabalho-Academia.txt`](./Documento-Trabalho-Academia.txt).

---

## ✨ Funcionalidades

### 👤 Aluno
- Cadastro e login com autenticação JWT
- Visualização dos treinos (exercícios, séries, repetições e carga)
- Marcar treino como realizado
- Dashboard de progresso: total, sequência de dias, frequência semanal e último treino
- Acompanhamento de meta (objetivo) com percentual e dias restantes
- Visualização dos dados do personal trainer

### 🧑‍🏫 Personal Trainer
- Criação de treinos personalizados com exercícios do catálogo
- Listagem e vínculo de alunos
- Cadastro de academias e gestão da atuação (dias e horários)
- Definição de metas para os alunos
- Exclusão de treinos e alteração do dia da semana
- Edição do próprio perfil (especialidade e bio)

### 🌐 Geral
- Catálogo público de personal trainers com filtros
- Catálogo com **124 exercícios** em português, com vídeos demonstrativos
- 🤖 **Chatbot** com arquitetura híbrida (regras + IA opcional)
- 🌗 Tema claro/escuro
- 📱 Layout responsivo

---

## 🛠️ Tecnologias

**Backend**

| Tecnologia | Uso |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | API REST |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM |
| [Alembic](https://alembic.sqlalchemy.org/) | Migrações |
| [Pydantic](https://docs.pydantic.dev/) | Validação de dados |
| [python-jose](https://github.com/mpdavis/python-jose) | Tokens JWT |
| [Passlib](https://passlib.readthedocs.io/) + Bcrypt | Hash de senhas |
| [pytest](https://docs.pytest.org/) | Testes automatizados |
| SQLite | Banco de dados |

**Frontend**

| Tecnologia | Uso |
|---|---|
| HTML5 / CSS3 / JavaScript | Interface (SPA por seções/abas) |
| [Tailwind CSS](https://tailwindcss.com/) | Estilização e responsividade |
| [Font Awesome](https://fontawesome.com/) | Ícones |

**IA (opcional e gratuita)**

| Provedor | Modelo padrão |
|---|---|
| Google Gemini | `gemini-3.5-flash-lite` |
| Groq | `openai/gpt-oss-120b` |

---

## 🏗️ Arquitetura

Arquitetura **cliente-servidor** em camadas:

```
┌────────────────────┐        HTTP/JSON        ┌────────────────────┐        ┌──────────────┐
│  Frontend (SPA)     │  ───────────────────▶   │  API REST (FastAPI) │  ───▶  │  SQLite      │
│  HTML/CSS/JS        │  ◀───────────────────   │  Controllers/ORM    │  ◀───  │  (SQLAlchemy)│
└────────────────────┘                         └────────────────────┘        └──────────────┘
```

**Camadas do backend:**

```
app/
├── api/routes/        # endpoints (rotas)
├── controllers/       # regras de negócio
├── schemas/           # contratos Pydantic (entrada/saída)
├── database/models.py # modelos ORM
├── core/security.py   # JWT, bcrypt, OAuth2
└── patterns/          # Strategy e Template Method
```

**Padrões de projeto aplicados:**
- 🧩 **Strategy** — filtros do catálogo de exercícios (nome, categoria, equipamento, músculo)
- 📊 **Template Method** — geração de relatórios de progresso (semanal e mensal)
- 💉 **Injeção de Dependência** — `Depends` do FastAPI para sessão e autenticação
- 🗂️ **DTO/Schema** — Pydantic para validação de entrada e saída

---

## 📂 Estrutura do projeto

```
Projeto-Academia-main/
├── Documento-Trabalho-Academia.txt     # Documentação de engenharia
├── README.md
│
├── Trabalho-Academia-Backend/
│   ├── main.py                         # Aplicação FastAPI
│   ├── requirements.txt
│   ├── popular_portugues.py            # Popula o catálogo (124 exercícios)
│   ├── popular_personais.py
│   ├── app/
│   │   ├── api/                        # Rotas e dependências
│   │   ├── controllers/                # Regras de negócio
│   │   ├── core/security.py            # Segurança (JWT/bcrypt)
│   │   ├── database/models.py          # Modelos ORM
│   │   ├── patterns/                   # Strategy e Template Method
│   │   └── schemas/schemas.py          # Schemas Pydantic
│   └── tests/                          # Testes (pytest)
│
└── Trabalho-Academia-Frontend/
    ├── index.html
    ├── style.css
    └── js/                             # auth, navigation, workouts, chat...
```

---

## 🚀 Como executar

### Pré-requisitos
- **Python 3.11+** (validado no 3.14)
- Navegador moderno
- *(Opcional)* Node.js, apenas para validar sintaxe dos JS

### 1️⃣ Backend

```bash
# Entre na pasta do backend
cd Trabalho-Academia-Backend

# (Recomendado) crie um ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# Instale as dependências
pip install -r requirements.txt

# Configure o .env (veja abaixo)

# Rode o servidor
python -m uvicorn main:app --reload
```

- API: <http://127.0.0.1:8000>
- Documentação (Swagger): <http://127.0.0.1:8000/docs>

> Na primeira execução, o sistema cria as tabelas e **popula automaticamente** o catálogo com 124 exercícios.

### 2️⃣ Frontend

Abra o `Trabalho-Academia-Frontend/index.html` no navegador ou use a extensão **Live Server**.

### 3️⃣ Testes

```bash
cd Trabalho-Academia-Backend
python -m pytest tests/ -q
```

---

## ⚙️ Configuração (`.env`)

Crie o arquivo `.env` dentro de `Trabalho-Academia-Backend/`:

```env
# Banco de dados
DATABASE_URL=sqlite:///app/database/banco.db

# Autenticação
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACESS_TOKEN_EXPIRE_MINUTES=1440

# Chatbot (opcional)
CHATBOT_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite
```

> ⚠️ **Nunca** versione o arquivo `.env`. Ele contém segredos.

---

## 🤖 Chatbot (IA gratuita opcional)

O chatbot funciona em **3 níveis**, garantindo que nunca quebre:

```
Pergunta do usuário
        │
        ▼
┌─────────────────────┐
│ 1. Regras de intenção│  consulta o banco local (sem internet)
└──────────┬──────────┘
           │ não encontrou
           ▼
┌─────────────────────┐
│ 2. IA (opcional)     │  Gemini ou Groq, se houver chave no .env
└──────────┬──────────┘
           │ sem chave / erro / cota
           ▼
┌─────────────────────┐
│ 3. Fallback          │  resposta padrão + menu de ajuda
└─────────────────────┘
```

**Sem chave de API, o bot já funciona apenas com regras.** Para respostas em perguntas abertas, escolha um provedor gratuito:

<details>
<summary><b>Google Gemini</b> (clique para expandir)</summary>

1. Gere uma chave em <https://aistudio.google.com/apikey>
2. No `.env`:

```env
CHATBOT_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
```

3. Reinicie o backend.

</details>

<details>
<summary><b>Groq</b> (clique para expandir)</summary>

1. Gere uma chave em <https://console.groq.com/keys>
2. No `.env`:

```env
CHATBOT_PROVIDER=groq
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=openai/gpt-oss-120b
```

3. Reinicie o backend.

</details>

> 🔒 A chave fica **apenas no backend** — o frontend nunca a vê.

📘 Detalhes técnicos do assistente (endpoints, intenções, limites) em [`README_CHATBOT.md`](./README_CHATBOT.md).

---

## 🔌 Principais endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/auth/criar_conta` | Cadastro de usuário |
| `POST` | `/auth/login` | Login (retorna JWT) |
| `GET` | `/treinos/` | Treinos do usuário logado |
| `POST` | `/treinos/` | Cria treino (personal) |
| `GET` | `/exercicios/` | Catálogo com filtros |
| `POST` | `/progresso/` | Marca treino como realizado |
| `GET` | `/progresso/` | Dashboard de progresso |
| `GET` | `/objetivos/` | Meta do aluno com progresso |
| `GET` | `/personais/` | Catálogo público de personais |
| `POST` | `/chat/` | Conversa com o chatbot |
| `GET` | `/chat/status` | Status da IA configurada |

📚 A lista completa está em <http://127.0.0.1:8000/docs>.

---

## 🧪 Testes

O projeto conta com **34 testes automatizados** (todos passando):

| Arquivo | Testes | Cobre |
|---|---|---|
| `test_cadastro.py` | 2 | Cadastro e autenticação |
| `test_chat.py` | 19 | Regras, fallback e IA simulada |
| `test_personais.py` | 13 | Personais, vínculos e catálogo |

Os testes usam banco em memória/cópias temporárias — o banco real não é alterado.

---

## 🗺️ Roadmap

- [ ] Migrar para PostgreSQL em produção
- [ ] Recuperação de senha e verificação de e-mail
- [ ] Notificações e lembretes de treino
- [ ] Gráficos de evolução de carga e medidas
- [ ] Upload de fotos de progresso
- [ ] Deploy em nuvem com CI/CD

---

## 👥 Autores

| Nome | GitHub |
|---|---|
| _Seu nome_ | [@seu-usuario](https://github.com/seu-usuario) |

> Trabalho desenvolvido para a disciplina de **Engenharia de Software**.

---

<div align="center">

Feito com 💚 e muito `café`

</div>
