# 🏋️ ForgeFit — Sistema de Gestão de Academia

Sistema web para gestão de treinos em academias, conectando **alunos** e **personal trainers**. Permite montar treinos personalizados, acompanhar progresso, definir objetivos e gerenciar o vínculo entre personais, alunos e academias.

Projeto acadêmico desenvolvido com **FastAPI** no back-end e **HTML/CSS/JavaScript puro** no front-end.

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Padrões de Projeto](#-padrões-de-projeto)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Como Executar](#-como-executar)
- [Endpoints da API](#-endpoints-da-api)
- [Testes](#-testes)
- [Autores](#-autores)

---

## ✨ Funcionalidades

**Autenticação**
- Cadastro e login com e-mail e senha (senhas criptografadas com `bcrypt`)
- Autenticação via **JWT**, com suporte a login tradicional e login via formulário OAuth2 (compatível com o Swagger UI)

**Alunos**
- Montagem de treinos personalizados, com exercícios, séries, repetições e carga
- Organização de treinos por dia da semana
- Vínculo com um personal trainer
- Registro de treinos realizados e histórico
- Definição de objetivos (meta de treinos em um período) com acompanhamento de progresso
- Relatórios de progresso semanais e mensais
- Catálogo de exercícios com filtros (nome, categoria, equipamento, músculo) e vídeos demonstrativos do YouTube

**Personal Trainers**
- Gestão dos próprios alunos
- Vínculo com uma ou mais academias, com dias e horários de atuação
- Edição de perfil (especialidade, biografia)

**Administração**
- Cadastro de academias
- Cadastro e gerenciamento do catálogo de exercícios (CRUD completo)

---

## 🛠️ Tecnologias

### Back-end
| Tecnologia | Uso |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web para a API REST |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM para acesso ao banco de dados |
| [Alembic](https://alembic.sqlalchemy.org/) | Migrações de banco de dados |
| SQLite | Banco de dados |
| [python-jose](https://github.com/mpdavis/python-jose) | Geração e validação de tokens JWT |
| [passlib](https://passlib.readthedocs.io/) + bcrypt | Hash e verificação de senhas |
| [Pydantic](https://docs.pydantic.dev/) | Validação de dados e schemas |
| [Uvicorn](https://www.uvicorn.org/) | Servidor ASGI |
| [Pytest](https://docs.pytest.org/) | Testes automatizados |

### Front-end
- HTML5, CSS3 e JavaScript (Vanilla, sem frameworks)
- Consumo da API via `fetch`

---

## 🏗️ Arquitetura

O back-end segue uma separação em camadas inspirada em **MVC**:

```
Rota (routes)  →  Controller  →  Model (SQLAlchemy)
     ↓
  Schema (Pydantic) para validação e serialização
```

- **`routes/`** — definem os endpoints, validam autenticação e delegam a lógica ao controller
- **`controllers/`** — contêm a lógica de negócio de cada domínio (autenticação, treinos, exercícios, etc.)
- **`database/models.py`** — modelos SQLAlchemy e definição das tabelas
- **`schemas/schemas.py`** — schemas Pydantic para entrada/saída da API
- **`core/security.py`** — configuração de criptografia e OAuth2
- **`api/dependencies.py`** — dependências reutilizáveis do FastAPI, como verificação de token JWT e checagem de permissão de administrador

A autenticação é feita via **Bearer Token (JWT)**: o token é obtido no login e enviado no header `Authorization` das requisições protegidas. A dependência `verificar_token` decodifica o token e injeta o usuário autenticado nas rotas.

---

## 🎨 Padrões de Projeto

O projeto aplica dois padrões de projeto clássicos, documentados no próprio código-fonte em `app/patterns/`:

### Strategy — Filtros de Exercícios
Cada critério de busca do catálogo de exercícios (nome, categoria, equipamento, músculo) é implementado como uma estratégia independente (`FiltroExercicioStrategy`). O `FiltroExercicioContext` recebe uma lista de estratégias e as aplica em sequência à query do banco, permitindo adicionar novos filtros sem alterar o controller existente.

### Template Method — Relatórios de Progresso
A geração de relatórios (semanal e mensal) segue sempre o mesmo esqueleto de passos — buscar registros, processar e formatar — definido na classe abstrata `RelatorioProgresso`. As subclasses `RelatorioPorSemana` e `RelatorioPorMes` sobrescrevem apenas os passos que mudam entre um tipo de relatório e outro.

---

## 📁 Estrutura de Pastas

```
Projeto-Academia/
├── Trabalho-Academia-Backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/          # Endpoints da API (auth, alunos, treinos, exercícios, ...)
│   │   │   └── dependencies.py  # Autenticação e injeção de dependências
│   │   ├── controllers/         # Lógica de negócio
│   │   ├── core/
│   │   │   └── security.py      # Hash de senha e configuração OAuth2
│   │   ├── database/
│   │   │   └── models.py        # Modelos SQLAlchemy
│   │   ├── patterns/            # Strategy e Template Method
│   │   └── schemas/
│   │       └── schemas.py       # Schemas Pydantic
│   ├── alembic/                 # Migrações do banco de dados
│   ├── tests/                   # Testes automatizados (pytest)
│   ├── main.py                  # Ponto de entrada da aplicação
│   ├── popular_portugues.py     # Popula o catálogo de exercícios (PT-BR)
│   ├── popular_personais.py     # Popula dados de exemplo de personais
│   └── requirements.txt
└── Trabalho-Academia-Frontend/
    ├── index.html
    ├── style.css
    └── js/                      # Scripts por funcionalidade (auth, treinos, progresso, ...)
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Um servidor de arquivos estático simples (ex: extensão *Live Server* do VS Code) para o front-end

### 1. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd Projeto-Academia
```

### 2. Configurar o back-end
```bash
cd Trabalho-Academia-Backend

# Criar e ativar um ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do back-end com as seguintes variáveis:
```env
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
DATABASE_URL=sqlite:///./app/database/banco.db
```

> ⚠️ Nunca use uma chave de exemplo em produção. Gere uma chave forte e mantenha o `.env` fora do controle de versão.

### 3. Rodar as migrações (opcional — o banco já é criado automaticamente)
```bash
alembic upgrade head
```

### 4. Iniciar o servidor
```bash
uvicorn main:app --reload
```
A API ficará disponível em `http://127.0.0.1:8000`, com a documentação interativa (Swagger) em `http://127.0.0.1:8000/docs`.

Ao subir pela primeira vez, o catálogo de exercícios em português é populado automaticamente.

### 5. Rodar o front-end
Abra `Trabalho-Academia-Frontend/index.html` com o *Live Server* (ou outro servidor estático) em `http://127.0.0.1:5500` — a URL da API já está configurada no front-end para `http://127.0.0.1:8000`.

---

## 🔌 Endpoints da API

| Recurso | Prefixo | Descrição |
|---|---|---|
| Autenticação | `/auth` | Cadastro, login (JSON e formulário OAuth2) |
| Alunos | `/alunos` | Listagem, vínculo com personal |
| Treinos | `/treinos` | CRUD de treinos e organização por dia da semana |
| Exercícios | `/exercicios` | Catálogo de exercícios, filtros e categorias |
| Progresso | `/progresso` | Registro de treinos realizados, histórico e relatórios |
| Objetivos | `/objetivos` | Metas de treino e acompanhamento |
| Academias | `/academias` | Cadastro de academias |
| Personais | `/personais` | Perfil do personal e vínculo com academias |

A lista completa de rotas e seus parâmetros está disponível na documentação interativa em `/docs` após iniciar o servidor.

---

## ✅ Testes

O projeto inclui testes automatizados com **pytest** para as regras de cadastro de usuários e personais:

```bash
cd Trabalho-Academia-Backend
python -m pytest -v
```

---

## 👥 Autores

Projeto desenvolvido como trabalho acadêmico.

> Sinta-se à vontade para adicionar aqui os nomes da equipe, a disciplina e a instituição.
