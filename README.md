# ForgeFit — Plataforma de Gestão de Academia

Sistema web completo para gerenciamento de academias, com cadastro de alunos e personal trainers, criação e acompanhamento de treinos, relatórios de progresso e um **catálogo público de personal trainers** com academias e horários de atuação.

O projeto é dividido em duas partes:

- **`Trabalho-Academia-Backend`** — API REST em FastAPI (Python) com SQLite, autenticação JWT, migrações Alembic e testes automatizados.
- **`Trabalho-Academia-Frontend`** — interface single page em HTML + Tailwind CSS + JavaScript puro.

---

## Funcionalidades

### Para o aluno

- Criar conta e receber treinos criados pelo personal trainer.
- Visualizar seus treinos e marcar os treinos realizados.
- Acompanhar progresso diário e mensal (frequência).
- Definir e acompanhar seu objetivo de treinos.
- Ver o **Meu Personal** vinculado: nome, especialidade, bio e as academias/horários em que ele atua.

### Para o personal trainer (admin)

- Criar conta com especialidade e bio.
- Cadastrar **Minha Atuação**: academias onde atende, dias da semana e horários (adicionar, editar e remover).
- Cadastrar novas academias.
- Gerenciar lista de alunos e **vincular/desvincular** alunos ao próprio acompanhamento.
- Criar treinos completos a partir de um catálogo de exercícios com séries, repetições, carga e observações.
- Definir objetivos e consultar o progresso de cada aluno.

### Público (sem login)

- Vitrine de personal trainers disponíveis, com filtro por academia e busca por nome/especialidade.
- Lista de academias da rede.

---

## Estrutura do projeto

```
Projeto-Academia/
├── Trabalho-Academia-Backend/
│   ├── app/
│   │   ├── api/routes/         # Endpoints (auth, alunos, treinos, exercícios, progresso, objetivos, academias, personais)
│   │   ├── controllers/        # Regras de negócio
│   │   ├── core/               # Segurança (JWT, bcrypt)
│   │   ├── database/           # Modelos SQLAlchemy + banco SQLite
│   │   ├── patterns/           # Padrões de projeto (Strategy e Template Method)
│   │   └── schemas/            # Schemas Pydantic
│   ├── alembic/versions/       # Migrações de banco
│   ├── tests/                  # Testes automatizados (pytest)
│   ├── main.py                 # Aplicação FastAPI
│   ├── popular_personais.py    # Seed de academias e personais de demonstração
│   ├── popular_portugues.py    # Catálogo de exercícios em português
│   └── requirements.txt
└── Trabalho-Academia-Frontend/
    ├── index.html              # Página única (Tailwind CSS)
    ├── style.css
    └── js/                     # Módulos JS por funcionalidade (auth, navegação, treinos, personais, atuação, alunos, progresso...)
```

## Tecnologias

| Camada    | Tecnologias |
|-----------|-------------|
| Backend   | Python 3.11+, FastAPI, SQLAlchemy, Pydantic, JWT (python-jose), bcrypt/passlib |
| Banco     | SQLite, Alembic (migrações) |
| Frontend  | HTML5, Tailwind CSS (CDN), JavaScript puro |
| Testes    | pytest, TestClient |

---

## Como executar

### 1. Backend

```bash
cd Trabalho-Academia-Backend

# Opcional: criar e ativar um ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações do banco
python -m alembic upgrade head

# Subir a API
python -m uvicorn main:app --reload
```

A API fica disponível em `http://127.0.0.1:8000` e a documentação interativa (Swagger) em `http://127.0.0.1:8000/docs`.

No primeiro acesso, o banco SQLite é criado automaticamente e o catálogo de exercícios (em português) é populado sozinho.

### 2. Frontend

```bash
cd Trabalho-Academia-Frontend
```

Abra o `index.html` com qualquer servidor estático — por exemplo a extensão **Live Server** do VS Code (porta 5500) — ou use:

```bash
python -m http.server 5500
```

Acesse `http://127.0.0.1:5500`.

> O frontend já está configurado para consumir a API em `http://127.0.0.1:8000`.
> Para alterar, edite a constante `URL_BACKEND` em `js/auth.js`.

### 3. Dados de demonstração (opcional)

Para criar academias (ForgeFit) e personais trainers de exemplo e vincular alunos a eles:

```bash
cd Trabalho-Academia-Backend
python popular_personais.py
```

Contas de personal criadas pelo script usam a senha:

```
personais: <email cadastrado> / personal123
```

---

## Autenticação e perfis

O sistema usa **JWT Bearer** (`Authorization: Bearer <token>`), obtido via `POST /auth/login`.

Existem dois perfis de usuário:

| Perfil | Campo `admin` | Acesso |
|--------|---------------|--------|
| `aluno` | `false` | Treinos, progresso, objetivo e "Meu Personal" |
| `personal` | `true` | Tudo do aluno + catálogo de alunos, criação de treinos, academias e atuação |

---

## API (principais endpoints)

### Públicos

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/criar_conta` | Cria conta (aluno ou personal, com `especialidade`/`bio` opcionais) |
| POST | `/auth/login` | Autentica e retorna o token JWT |
| GET | `/personais/` | Catálogo público de personal trainers (`?academia_id=` filtra por academia) |
| GET | `/academias/` | Lista academias |
| GET | `/exercicios/` | Catálogo de exercícios (filtros por nome, categoria, equipamento, músculo) |

### Autenticados

| Método | Rota | Acesso | Descrição |
|--------|------|--------|-----------|
| GET | `/alunos/meu-personal` | aluno | Personal vinculado ao aluno logado (academias e horários) |
| GET/POST | `/treinos/` | ambos | Lista/cria treinos |
| DELETE | `/treinos/{id}` | ambos | Exclui treino |
| GET | `/treinos/aluno/{usuario_id}` | personal | Treinos de um aluno |
| GET/POST | `/progresso/` | aluno | Dashboard e registro de treino realizado |
| GET | `/progresso/historico` | aluno | Histórico de treinos realizados |
| GET | `/progresso/relatorio-mensal` | aluno | Relatório mensal |
| GET/POST | `/objetivos/` | aluno | Objetivo do aluno |
| GET | `/objetivos/aluno/{usuario_id}` | personal | Objetivo de um aluno |

### Personais (admin)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/personais/me` | Perfil completo do personal (vínculos ativos e inativos) |
| PATCH | `/personais/me` | Atualiza `especialidade`/`bio` |
| POST | `/personais/me/academias` | Adiciona academia + dias + horários à própria atuação |
| PATCH | `/personais/academias/{id}` | Edita dias/horários/ativo de um vínculo |
| DELETE | `/personais/academias/{id}` | Remove um vínculo |
| POST | `/academias/` | Cadastra uma nova academia |
| GET | `/alunos/` | Lista todos os alunos (com `personal_id`) |
| PATCH | `/alunos/{id}/personal` | Vincula (`personal_id`) ou desvincula (`null`) um aluno |

---

## Modelo de dados

- **usuarios** — alunos e personais (campo `admin` diferencia; `personal_id` vincula o aluno ao seu personal).
- **exercicios_catalogo** — catálogo de exercícios com nome, categoria, equipamento e músculos.
- **treinos** e **treino_exercicios** — treinos e seus exercícios (séries, repetições, carga, ordem).
- **treinos_realizados** — registros de treinos concluídos para o progresso.
- **objetivos_aluno** — meta de treinos por período.
- **academias** — academias da rede.
- **personal_academia** — vínculo personal ↔ academia com dias da semana, horários e status ativo.

---

## Padrões de projeto aplicados

- **Strategy** — `app/patterns/strategy_filtros.py`: filtros do catálogo de exercícios (nome, categoria, equipamento, músculo) como estratégias intercambiáveis, permitindo adicionar novos filtros sem alterar o controller.
- **Template Method** — `app/patterns/template_method_relatorio.py`: relatórios de progresso (semanal e mensal) com o mesmo esqueleto de passos, variando apenas a implementação de cada etapa.

---

## Testes

```bash
cd Trabalho-Academia-Backend
python -m pytest tests/ -v
```

Cobertura principal (15 testes): cadastro de usuário, catálogo de personais, filtros por academia, permissões de admin, vínculo aluno↔personal e gestão de atuação do personal.

---

## Observações para publicar no GitHub

- O arquivo `Trabalho-Academia-Backend/.env` contém a `SECRET_KEY` e a conexão do banco. **Não o suba ao repositório** — adicione `*.env` ao `.gitignore` e crie um `.env.example` com as chaves sem valores reais.
- O banco `app/database/banco.db` não deve ser versionado (ele é criado automaticamente na primeira execução).

---

## Licença

Projeto acadêmico — uso livre para fins educacionais.